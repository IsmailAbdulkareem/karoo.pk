from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from utils.notifications import create_notification

router = APIRouter()

# Service-specific checklists
SERVICE_CHECKLISTS = {
    "plumber": [
        "Fixed the issue",
        "Tested for leaks",
        "Cleaned work area",
        "Explained maintenance tips"
    ],
    "electrician": [
        "Completed wiring/repair",
        "Tested all connections",
        "Verified safety",
        "Provided usage instructions"
    ],
    "ac_technician": [
        "Serviced/repaired AC unit",
        "Tested cooling/heating",
        "Cleaned filters",
        "Explained maintenance schedule"
    ],
    "carpenter": [
        "Completed carpentry work",
        "Checked structural integrity",
        "Cleaned up debris",
        "Provided care instructions"
    ],
    "painter": [
        "Completed painting",
        "Cleaned brushes and area",
        "Checked for touch-ups",
        "Advised on drying time"
    ],
    "mechanic": [
        "Completed repair/service",
        "Test drove vehicle",
        "Checked all systems",
        "Provided maintenance advice"
    ],
    "tutor": [
        "Covered planned topics",
        "Assigned homework",
        "Answered questions",
        "Scheduled next session"
    ],
    "cleaner": [
        "Cleaned all areas",
        "Sanitized surfaces",
        "Disposed of trash",
        "Restocked supplies"
    ],
    "cook": [
        "Prepared meals",
        "Cleaned kitchen",
        "Stored leftovers properly",
        "Provided reheating instructions"
    ],
    "security_guard": [
        "Completed patrol",
        "Logged incidents",
        "Secured premises",
        "Handed over to next shift"
    ]
}


class ProgressUpdate(BaseModel):
    status: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    notes: Optional[str] = None
    photo_urls: Optional[List[str]] = []


class ChecklistSubmit(BaseModel):
    checklist_items: Dict[str, bool]
    notes: Optional[str] = None


@router.post("/{booking_id}/progress")
async def update_service_progress(
    booking_id: str,
    progress: ProgressUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update service progress (provider only).
    Provider marks: en_route, arrived, in_progress, completed.
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers progress update kar sakte hain")

        # Get provider record
        provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider record nahi mila")

        provider_id = provider_result.data[0]["id"]

        # Get booking
        booking_result = supabase.table("bookings").select("*").eq("id", booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Verify this booking belongs to this provider
        if booking["provider_id"] != provider_id:
            raise HTTPException(status_code=403, detail="Yeh booking tumhari nahi hai")

        # Insert progress update
        progress_data = {
            "booking_id": booking_id,
            "status": progress.status,
            "location_lat": progress.location_lat,
            "location_lng": progress.location_lng,
            "notes": progress.notes,
            "photo_urls": progress.photo_urls or [],
            "created_by": current_user["user_id"]
        }

        result = supabase.table("service_progress").insert(progress_data).execute()

        # Update booking current_status
        supabase.table("bookings").update({
            "current_status": progress.status
        }).eq("id", booking_id).execute()

        # Notify user
        status_messages = {
            "en_route": "Provider is on the way! 🚗",
            "arrived": "Provider has arrived at your location 📍",
            "in_progress": "Service work has started 🔧",
            "paused": "Service temporarily paused ⏸️",
            "completed": "Service completed! Please rate your experience ⭐"
        }

        message = status_messages.get(progress.status, f"Status updated: {progress.status}")

        await create_notification(
            booking["user_id"],
            "Service Update",
            message,
            "service_progress",
            booking_id
        )

        return {
            "message": "Progress updated successfully",
            "progress": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[SERVICE PROGRESS] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/{booking_id}/progress")
async def get_service_progress(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all progress updates for a booking.
    Both user and provider can view.
    """
    try:
        # Get booking to verify access
        booking_result = supabase.table("bookings").select("user_id, provider_id").eq("id", booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Verify user has access
        has_access = False
        if current_user["role"] == "user" and booking["user_id"] == current_user["user_id"]:
            has_access = True
        elif current_user["role"] == "provider":
            provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
            if provider_result.data and booking["provider_id"] == provider_result.data[0]["id"]:
                has_access = True

        if not has_access:
            raise HTTPException(status_code=403, detail="Aap is booking ka progress nahi dekh sakte")

        # Get all progress updates
        result = supabase.table("service_progress").select("*").eq("booking_id", booking_id).order("created_at", desc=False).execute()

        return {
            "booking_id": booking_id,
            "progress_updates": result.data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/{booking_id}/checklist")
async def submit_completion_checklist(
    booking_id: str,
    checklist: ChecklistSubmit,
    current_user: dict = Depends(get_current_user)
):
    """
    Provider submits completion checklist.
    Required before marking booking as completed.
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers checklist submit kar sakte hain")

        # Get provider record
        provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider record nahi mila")

        provider_id = provider_result.data[0]["id"]

        # Get booking
        booking_result = supabase.table("bookings").select("*").eq("id", booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Verify this booking belongs to this provider
        if booking["provider_id"] != provider_id:
            raise HTTPException(status_code=403, detail="Yeh booking tumhari nahi hai")

        # Check if all items are completed
        all_completed = all(checklist.checklist_items.values())

        # Update booking with checklist
        supabase.table("bookings").update({
            "completion_checklist": checklist.checklist_items,
            "checklist_completed": all_completed
        }).eq("id", booking_id).execute()

        # Notify user
        if all_completed:
            await create_notification(
                booking["user_id"],
                "Service Checklist Completed ✅",
                "Provider has completed all service tasks. Please review and rate.",
                "checklist_completed",
                booking_id
            )

        return {
            "message": "Checklist submitted successfully",
            "all_completed": all_completed,
            "checklist": checklist.checklist_items
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[CHECKLIST] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/{booking_id}/checklist")
async def get_service_checklist(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the service checklist for a booking.
    Returns template checklist based on service type.
    """
    try:
        # Get booking
        booking_result = supabase.table("bookings").select("service_type, completion_checklist, checklist_completed").eq("id", booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]
        service_type = booking["service_type"]

        # Get template checklist
        template_checklist = SERVICE_CHECKLISTS.get(service_type, [
            "Completed the service",
            "Cleaned work area",
            "Explained work done",
            "Answered questions"
        ])

        # If checklist already submitted, return it
        if booking.get("completion_checklist"):
            return {
                "booking_id": booking_id,
                "service_type": service_type,
                "checklist": booking["completion_checklist"],
                "completed": booking.get("checklist_completed", False),
                "is_submitted": True
            }

        # Return template
        template_dict = {item: False for item in template_checklist}

        return {
            "booking_id": booking_id,
            "service_type": service_type,
            "checklist": template_dict,
            "completed": False,
            "is_submitted": False
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
