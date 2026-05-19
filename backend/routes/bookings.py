from fastapi import APIRouter, HTTPException, Depends
from models.schemas import BookingCreate, BookingStatusUpdate
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from utils.notifications import (
    notify_booking_created,
    notify_booking_accepted,
    notify_booking_rejected,
    notify_booking_completed,
    notify_booking_cancelled_by_user,
    notify_booking_cancelled_by_provider
)
from agents.pricing_agent import calculate_booking_price
from datetime import datetime

router = APIRouter()

@router.post("")
async def create_booking(
    booking: BookingCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new booking (user only).
    Sends notifications to both user and provider.
    """
    try:
        # Check role
        if current_user["role"] != "user":
            raise HTTPException(status_code=403, detail="Sirf users booking create kar sakte hain")

        # Get provider
        provider_result = supabase.table("providers").select("*, users(name)").eq("id", booking.provider_id).execute()
        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider nahi mila")

        provider = provider_result.data[0]
        provider_user_id = provider["user_id"]
        provider_name = provider["users"]["name"]

        # Get user name and loyalty level
        user_result = supabase.table("users").select("name, loyalty_level").eq("id", current_user["user_id"]).execute()
        user_name = user_result.data[0]["name"] if user_result.data else "User"
        user_loyalty_level = user_result.data[0].get("loyalty_level", 0) if user_result.data else 0

        # Calculate dynamic pricing
        distance_km = booking.eta_minutes / 3.0 if booking.eta_minutes else 5.0  # Estimate: 3 min per km
        scheduled_time = datetime.fromisoformat(booking.scheduled_at.replace('Z', '+00:00')) if booking.scheduled_at else None

        # Determine urgency from booking data (default to normal)
        urgency = getattr(booking, 'urgency', 'normal')
        job_complexity = getattr(booking, 'job_complexity', 'basic')

        pricing = calculate_booking_price(
            service_type=booking.service_type,
            complexity=job_complexity,
            distance_km=distance_km,
            urgency=urgency,
            provider_rate=provider.get("base_rate"),
            user_loyalty_level=user_loyalty_level,
            scheduled_time=scheduled_time
        )

        print(f"[BOOKING] Calculated pricing: {pricing['final_price']} PKR (base: {pricing['base_price']}, distance: {pricing['distance_fee']}, urgency: {pricing['urgency_fee']})")

        # Insert booking with pricing data
        booking_data = {
            "user_id": current_user["user_id"],
            "provider_id": booking.provider_id,
            "service_type": booking.service_type,
            "location": booking.location,
            "scheduled_at": booking.scheduled_at,
            "note": booking.note,
            "booked_via": booking.booked_via,
            "budget": booking.budget,
            "agreed_rate": booking.agreed_rate or pricing["final_price"],
            "user_lat": booking.user_lat,
            "user_lng": booking.user_lng,
            "eta_minutes": booking.eta_minutes,
            "status": "pending",
            # Pricing fields
            "base_price": pricing["base_price"],
            "distance_fee": pricing["distance_fee"],
            "urgency_fee": pricing["urgency_fee"],
            "complexity_fee": pricing["complexity_fee"],
            "surge_multiplier": pricing["surge_multiplier"],
            "loyalty_discount": pricing["loyalty_discount"],
            "final_price": pricing["final_price"],
            "price_breakdown": pricing["breakdown"],
            "urgency": urgency,
            "job_complexity": job_complexity
        }
        print(f"[BOOKING] Creating booking: service={booking.service_type} budget={booking.budget} agreed_rate={booking.agreed_rate}")
        result = supabase.table("bookings").insert(booking_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Booking create nahi hui")

        booking_id = result.data[0]["id"]

        # Send notifications
        await notify_booking_created(
            booking_id,
            current_user["user_id"],
            provider_user_id,
            provider_name,
            user_name,
            booking.service_type
        )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/my")
async def get_my_bookings(current_user: dict = Depends(get_current_user)):
    """
    Get bookings for current user.
    Users see their bookings, providers see bookings for them.
    """
    try:
        if current_user["role"] == "user":
            # User: get bookings where user_id matches
            result = supabase.table("bookings").select("*, providers(*, users(name))").eq("user_id", current_user["user_id"]).order("created_at", desc=True).execute()
        else:
            # Provider: get provider record first, then bookings
            provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
            if not provider_result.data:
                raise HTTPException(status_code=404, detail="Provider record nahi mila")

            provider_id = provider_result.data[0]["id"]
            result = supabase.table("bookings").select("*, users(name)").eq("provider_id", provider_id).order("created_at", desc=True).execute()

        return result.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/{booking_id}/accept")
async def accept_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Accept a booking (provider only).
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers booking accept kar sakte hain")

        # Get provider record
        provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider record nahi mila")

        provider_id = provider_result.data[0]["id"]

        # Get booking
        booking_result = supabase.table("bookings").select("*, users(name), providers(users(name))").eq("id", booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Verify this booking belongs to this provider
        if booking["provider_id"] != provider_id:
            raise HTTPException(status_code=403, detail="Yeh booking tumhari nahi hai")

        # Check status
        if booking["status"] != "pending":
            raise HTTPException(status_code=400, detail="Yeh booking already update ho chuki hai")

        # Update status
        update_result = supabase.table("bookings").update({"status": "confirmed"}).eq("id", booking_id).execute()

        # Auto-create conversation for messaging
        try:
            existing_conv = supabase.table("conversations").select("id").eq("booking_id", booking_id).execute()
            if not existing_conv.data:
                conversation_data = {
                    "booking_id": booking_id,
                    "user_id": booking["user_id"],
                    "provider_id": current_user["user_id"]
                }
                supabase.table("conversations").insert(conversation_data).execute()
                print(f"[BOOKING] Auto-created conversation for booking {booking_id}")
        except Exception as conv_err:
            print(f"[BOOKING] Warning: Could not create conversation: {conv_err}")

        # Send notifications
        provider_name = booking["providers"]["users"]["name"]
        await notify_booking_accepted(
            booking_id,
            booking["user_id"],
            current_user["user_id"],
            provider_name,
            booking["scheduled_at"]
        )

        return update_result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/{booking_id}/cancel")
async def cancel_booking_by_user(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a booking (user only).
    Can cancel pending or confirmed bookings.
    """
    try:
        if current_user["role"] != "user":
            raise HTTPException(status_code=403, detail="Sirf users apni booking cancel kar sakte hain")

        # Get booking
        booking_result = supabase.table("bookings").select("*, providers(user_id, users(name))").eq("id", booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Verify this booking belongs to this user
        if booking["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Yeh booking tumhari nahi hai")

        # Can only cancel pending or confirmed bookings
        if booking["status"] not in ["pending", "confirmed"]:
            raise HTTPException(status_code=400, detail=f"Yeh booking cancel nahi ho sakti. Status: {booking['status']}")

        print(f"[BOOKING] User {current_user['user_id']} cancelling booking {booking_id} (was: {booking['status']})")

        # Update status
        update_result = supabase.table("bookings").update({"status": "cancelled"}).eq("id", booking_id).execute()

        # Get user name for notification
        user_result = supabase.table("users").select("name").eq("id", current_user["user_id"]).execute()
        user_name = user_result.data[0]["name"] if user_result.data else "User"
        provider_user_id = booking["providers"]["user_id"]

        await notify_booking_cancelled_by_user(
            booking_id,
            current_user["user_id"],
            provider_user_id,
            user_name,
            booking["service_type"]
        )

        return {"message": "Booking cancel ho gayi", "booking": update_result.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/{booking_id}/reject")
async def reject_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Reject a booking (provider only).
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers booking reject kar sakte hain")

        # Get provider record
        provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider record nahi mila")

        provider_id = provider_result.data[0]["id"]

        # Get booking
        booking_result = supabase.table("bookings").select("*, providers(users(name))").eq("id", booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Verify this booking belongs to this provider
        if booking["provider_id"] != provider_id:
            raise HTTPException(status_code=403, detail="Yeh booking tumhari nahi hai")

        # Provider can cancel both pending AND confirmed bookings
        if booking["status"] not in ["pending", "confirmed"]:
            raise HTTPException(status_code=400, detail=f"Yeh booking cancel nahi ho sakti. Status: {booking['status']}")

        # Update status
        update_result = supabase.table("bookings").update({"status": "cancelled"}).eq("id", booking_id).execute()

        # Get provider name
        provider_name = booking["providers"]["users"]["name"]

        # Use cancel notification instead of reject (better UX)
        await notify_booking_cancelled_by_provider(
            booking_id,
            booking["user_id"],
            current_user["user_id"],
            provider_name,
            booking["service_type"]
        )

        print(f"[BOOKING] Provider {current_user['user_id']} rejected/cancelled booking {booking_id}")
        return update_result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/{booking_id}/complete")
async def complete_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark booking as completed (provider only).
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers booking complete kar sakte hain")

        # Get provider record
        provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider record nahi mila")

        provider_id = provider_result.data[0]["id"]

        # Get booking
        booking_result = supabase.table("bookings").select("*, users(name)").eq("id", booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Verify this booking belongs to this provider
        if booking["provider_id"] != provider_id:
            raise HTTPException(status_code=403, detail="Yeh booking tumhari nahi hai")

        # Check status
        if booking["status"] != "confirmed":
            raise HTTPException(status_code=400, detail="Sirf confirmed bookings complete ho sakti hain")

        # Update status
        update_result = supabase.table("bookings").update({"status": "completed"}).eq("id", booking_id).execute()

        # Send notifications
        user_name = booking["users"]["name"]
        await notify_booking_completed(
            booking_id,
            booking["user_id"],
            current_user["user_id"],
            user_name
        )

        return update_result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/earnings")
async def get_provider_earnings(current_user: dict = Depends(get_current_user)):
    """
    Get earnings summary for a provider.
    Shows total earnings, this month, this week, and per-booking breakdown.
    Provider only endpoint.
    """
    try:
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers earnings dekh sakte hain")

        # Get provider record
        provider_result = supabase.table("providers").select("id, rate_per_hour").eq("user_id", current_user["user_id"]).execute()
        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider profile nahi mila")

        provider_id = provider_result.data[0]["id"]
        rate_per_hour = provider_result.data[0].get("rate_per_hour") or 0

        # Get all completed bookings
        result = supabase.table("bookings").select("id, service_type, location, scheduled_at, agreed_rate, budget, created_at, users(name)").eq("provider_id", provider_id).eq("status", "completed").order("created_at", desc=True).execute()

        bookings = result.data
        print(f"[EARNINGS] Provider {provider_id} has {len(bookings)} completed bookings")

        # Calculate earnings per booking
        # Priority: agreed_rate > budget > provider's own rate_per_hour
        total_earned = 0
        earnings_breakdown = []

        for b in bookings:
            earned = b.get("agreed_rate") or b.get("budget") or rate_per_hour
            total_earned += earned
            earnings_breakdown.append({
                "booking_id": b["id"],
                "service_type": b["service_type"],
                "location": b["location"],
                "customer_name": b["users"]["name"] if b.get("users") else "Unknown",
                "scheduled_at": b["scheduled_at"],
                "agreed_rate": b.get("agreed_rate"),
                "budget": b.get("budget"),
                "earned": earned
            })

        print(f"[EARNINGS] Total earned: PKR {total_earned}")

        return {
            "provider_id": provider_id,
            "total_completed_jobs": len(bookings),
            "total_earned_pkr": total_earned,
            "rate_per_hour": rate_per_hour,
            "earnings_breakdown": earnings_breakdown,
            "message": f"Aapne {len(bookings)} kaam mukammal kiye aur total PKR {total_earned} kamaye!"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
