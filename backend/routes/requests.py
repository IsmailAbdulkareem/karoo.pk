from fastapi import APIRouter, HTTPException, Depends, Query
from models.schemas import ServiceRequestCreate
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from utils.notifications import create_notification
from typing import Optional

router = APIRouter()

@router.post("")
async def create_service_request(
    request: ServiceRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create an open service request (user only).
    Notifies all providers matching the service type.
    """
    try:
        # Check role
        if current_user["role"] != "user":
            raise HTTPException(status_code=403, detail="Sirf users request post kar sakte hain")

        # Insert service request
        request_data = {
            "user_id": current_user["user_id"],
            "service_type": request.service_type,
            "location": request.location,
            "scheduled_at": request.scheduled_at,
            "budget": request.budget,
            "description": request.description,
            "status": "open"
        }
        result = supabase.table("service_requests").insert(request_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Request create nahi hui")

        # Query matching providers
        providers_result = supabase.table("providers").select("user_id").eq("service_type", request.service_type).execute()

        # Notify each matching provider
        for provider in providers_result.data:
            await create_notification(
                provider["user_id"],
                "Naya Kaam! 📋",
                f"{request.service_type} ki zaroorat hai {request.location} mein",
                "service_request",
                result.data[0]["id"]
            )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/open")
async def get_open_requests(
    current_user: dict = Depends(get_current_user),
    service_type: Optional[str] = Query(None),
    area: Optional[str] = Query(None)
):
    """
    Browse open service requests (provider only).
    Optional filters: service_type, area.
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers requests dekh sakte hain")

        # Fetch all open requests (without ilike which fails on some column types)
        result = supabase.table("service_requests").select("*, users(name, phone)").eq("status", "open").order("created_at", desc=True).execute()
        data = result.data

        # Filter in Python
        if service_type:
            data = [r for r in data if r.get("service_type") and service_type.lower() in r["service_type"].lower()]
        if area:
            data = [r for r in data if r.get("location") and area.lower() in r["location"].lower()]

        return data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/{request_id}/accept")
async def accept_service_request(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Accept an open service request (provider only).
    Automatically creates a booking.
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers request accept kar sakte hain")

        # Get request
        request_result = supabase.table("service_requests").select("*").eq("id", request_id).execute()
        if not request_result.data:
            raise HTTPException(status_code=404, detail="Request nahi mili")

        service_request = request_result.data[0]

        # Check status
        if service_request["status"] != "open":
            raise HTTPException(status_code=400, detail="Yeh request already le li gayi hai")

        # Get provider record
        provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider record nahi mila")

        provider_id = provider_result.data[0]["id"]

        # Update request status
        supabase.table("service_requests").update({"status": "taken"}).eq("id", request_id).execute()

        # Create booking automatically
        booking_data = {
            "user_id": service_request["user_id"],
            "provider_id": provider_id,
            "service_type": service_request["service_type"],
            "location": service_request["location"],
            "scheduled_at": service_request["scheduled_at"],
            "note": service_request["description"],
            "booked_via": "request",
            "status": "pending"
        }
        booking_result = supabase.table("bookings").insert(booking_data).execute()

        if not booking_result.data:
            raise HTTPException(status_code=500, detail="Booking create nahi hui")

        # Notify user
        await create_notification(
            service_request["user_id"],
            "Provider Mil Gaya! ✅",
            "Tumhari request accept ho gayi",
            "request_accepted",
            request_id
        )

        return booking_result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/my")
async def get_my_requests(current_user: dict = Depends(get_current_user)):
    """
    Get service requests for current user (user only).
    """
    try:
        # Check role
        if current_user["role"] != "user":
            raise HTTPException(status_code=403, detail="Sirf users apni requests dekh sakte hain")

        result = supabase.table("service_requests").select("*").eq("user_id", current_user["user_id"]).order("created_at", desc=True).execute()

        return result.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
