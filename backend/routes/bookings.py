from fastapi import APIRouter, HTTPException
from models.schemas import BookingCreate, BookingStatus
from db.supabase_client import supabase

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

@router.post("")
async def create_booking(booking: BookingCreate):
    """Create a new booking"""
    # TODO: Create booking in Supabase
    # TODO: Calculate ETA using Google Routes API
    # TODO: Trigger Supabase Realtime notification to provider
    return {"message": "Create booking endpoint - to be implemented"}

@router.get("/my")
async def get_my_bookings(user_id: str):
    """Get bookings for current user"""
    # TODO: Verify JWT token
    # TODO: Fetch bookings from Supabase
    return {"message": "Get my bookings endpoint - to be implemented"}

@router.put("/{booking_id}/status")
async def update_booking_status(booking_id: str, status: BookingStatus):
    """Update booking status (provider only)"""
    # TODO: Verify JWT token and provider ownership
    # TODO: Update booking status in Supabase
    # TODO: Notify user via Supabase Realtime
    return {"message": "Update booking status endpoint - to be implemented"}
