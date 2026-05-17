from fastapi import APIRouter, HTTPException, Depends
from models.schemas import BookingCreate, BookingStatusUpdate
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from utils.notifications import (
    notify_booking_created,
    notify_booking_accepted,
    notify_booking_rejected,
    notify_booking_completed
)

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

        # Get user name
        user_result = supabase.table("users").select("name").eq("id", current_user["user_id"]).execute()
        user_name = user_result.data[0]["name"] if user_result.data else "User"

        # Insert booking
        booking_data = {
            "user_id": current_user["user_id"],
            "provider_id": booking.provider_id,
            "service_type": booking.service_type,
            "location": booking.location,
            "scheduled_at": booking.scheduled_at,
            "note": booking.note,
            "booked_via": booking.booked_via,
            "user_lat": booking.user_lat,
            "user_lng": booking.user_lng,
            "eta_minutes": booking.eta_minutes,
            "status": "pending"
        }
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

        # Check status
        if booking["status"] != "pending":
            raise HTTPException(status_code=400, detail="Yeh booking already update ho chuki hai")

        # Update status
        update_result = supabase.table("bookings").update({"status": "cancelled"}).eq("id", booking_id).execute()

        # Send notifications
        provider_name = booking["providers"]["users"]["name"]
        await notify_booking_rejected(
            booking_id,
            booking["user_id"],
            current_user["user_id"],
            provider_name
        )

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
