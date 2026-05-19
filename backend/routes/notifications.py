from fastapi import APIRouter, HTTPException, Depends
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user

router = APIRouter()

@router.get("")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    """
    Get notifications for current user.
    Returns notifications list directly.
    """
    try:
        # Get notifications
        result = supabase.table("notifications").select("*").eq("user_id", current_user["user_id"]).order("created_at", desc=True).limit(50).execute()

        # Return just the array for frontend compatibility
        return result.data or []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a single notification as read.
    """
    try:
        result = supabase.table("notifications").update({"is_read": True}).eq("id", notification_id).eq("user_id", current_user["user_id"]).execute()

        return {"message": "Mark as read"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    """
    Mark all notifications as read for current user.
    """
    try:
        result = supabase.table("notifications").update({"is_read": True}).eq("user_id", current_user["user_id"]).execute()

        return {"message": "Sab notifications read ho gayi"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
