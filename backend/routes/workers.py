from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from models.schemas import ProviderUpdate, ProviderResult
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user

router = APIRouter()

@router.get("", response_model=list[ProviderResult])
async def get_workers(
    service_type: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Browse providers with optional filters.
    Returns list of available providers ordered by rating.
    """
    try:
        # Fetch all available providers
        result = supabase.table("providers").select("*, users(name, avatar_url)").eq("is_available", True).execute()

        # Filter in Python to avoid Supabase ILIKE issues
        filtered_data = result.data

        if service_type:
            filtered_data = [p for p in filtered_data
                           if p.get("service_type") and service_type.lower() in p["service_type"].lower()]

        if area:
            filtered_data = [p for p in filtered_data
                           if p.get("area") and area.lower() in p["area"].lower()]

        if min_rating:
            filtered_data = [p for p in filtered_data
                           if p.get("rating", 0.0) >= min_rating]

        # Sort by rating descending
        filtered_data.sort(key=lambda p: p.get("rating", 0.0), reverse=True)

        # Transform to ProviderResult
        providers = []
        for p in filtered_data:
            user_data = p.get("users", {})
            providers.append(ProviderResult(
                id=p["id"],
                name=user_data.get("name", "Unknown"),
                service_type=p.get("service_type", ""),
                area=p.get("area", ""),
                rating=p.get("rating", 0.0),
                rate_per_hour=p.get("rate_per_hour"),
                is_available=p.get("is_available", False),
                bio=p.get("bio"),
                eta_minutes=None,
                match_score=None
            ))

        return providers

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/{provider_id}")
async def get_worker_by_id(
    provider_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get single provider details with recent ratings.
    """
    try:
        # Get provider with user info
        provider_result = supabase.table("providers").select("*, users(name, avatar_url)").eq("id", provider_id).execute()

        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider nahi mila")

        provider = provider_result.data[0]

        # Get last 5 ratings for this provider
        ratings_result = supabase.table("ratings").select("*").eq("ratee_id", provider["user_id"]).eq("rater_role", "user").order("created_at", desc=True).limit(5).execute()

        # Build response
        user_data = provider.get("users", {})
        response = {
            "id": provider["id"],
            "name": user_data.get("name", "Unknown"),
            "service_type": provider.get("service_type", ""),
            "area": provider.get("area", ""),
            "rating": provider.get("rating", 0.0),
            "rate_per_hour": provider.get("rate_per_hour"),
            "is_available": provider.get("is_available", False),
            "bio": provider.get("bio"),
            "total_ratings": provider.get("total_ratings", 0),
            "recent_ratings": ratings_result.data
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/profile")
async def update_profile(
    update: ProviderUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update provider profile (provider only).
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers apna profile update kar sakte hain")

        # Get provider record
        provider_result = supabase.table("providers").select("*").eq("user_id", current_user["user_id"]).execute()

        if not provider_result.data:
            raise HTTPException(status_code=404, detail="Provider record nahi mila")

        provider_id = provider_result.data[0]["id"]

        # Build update dict (only non-None fields)
        update_data = {}
        if update.service_type is not None:
            update_data["service_type"] = update.service_type
        if update.area is not None:
            update_data["area"] = update.area
        if update.rate_per_hour is not None:
            update_data["rate_per_hour"] = update.rate_per_hour
        if update.bio is not None:
            update_data["bio"] = update.bio
        if update.is_available is not None:
            update_data["is_available"] = update.is_available
        if update.is_online is not None:
            update_data["is_online"] = update.is_online

        # Update provider
        result = supabase.table("providers").update(update_data).eq("id", provider_id).execute()

        return {"message": "Profile update ho gaya", "provider": result.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/availability")
async def update_availability(
    is_online: bool,
    is_available: bool,
    current_user: dict = Depends(get_current_user)
):
    """
    Update provider online/available status (provider only).
    Updates both users and providers tables for consistency.
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers status update kar sakte hain")

        # Try to update users table (if columns exist)
        try:
            supabase.table("users").update({
                "is_online": is_online,
                "is_available": is_available
            }).eq("id", current_user["user_id"]).execute()
        except Exception as e:
            # If users table update fails, just log it (columns might not exist yet)
            print(f"Warning: Could not update users table: {str(e)}")

        # Update providers table (primary source of truth)
        result = supabase.table("providers").update({
            "is_online": is_online,
            "is_available": is_available
        }).eq("user_id", current_user["user_id"]).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Provider nahi mila")

        return {"message": "Status update ho gaya"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
