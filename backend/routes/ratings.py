from fastapi import APIRouter, HTTPException, Depends
from models.schemas import RatingCreate, RatingResponse
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user

router = APIRouter()

@router.post("")
async def create_rating(
    rating: RatingCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit a rating after booking completion.
    Both user and provider can rate each other (bidirectional).
    """
    try:
        # Get booking
        booking_result = supabase.table("bookings").select("*").eq("id", rating.booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mili")

        booking = booking_result.data[0]

        # Check booking status
        if booking["status"] != "completed":
            raise HTTPException(status_code=400, detail="Sirf complete bookings rate ho sakti hain")

        # Check if current user already rated this booking
        existing_rating = supabase.table("ratings").select("*").eq("booking_id", rating.booking_id).eq("rater_id", current_user["user_id"]).execute()
        if existing_rating.data:
            raise HTTPException(status_code=400, detail="Tumne pehle hi rate kar diya hai")

        # Insert rating
        rating_data = {
            "booking_id": rating.booking_id,
            "rater_id": current_user["user_id"],
            "rater_role": current_user["role"],
            "ratee_id": rating.ratee_id,
            "stars": rating.stars,
            "review_text": rating.review_text,
            "tags": rating.tags or []
        }
        result = supabase.table("ratings").insert(rating_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Rating create nahi hui")

        # Update target's score
        if current_user["role"] == "user":
            # User rating a provider
            all_ratings = supabase.table("ratings").select("stars").eq("ratee_id", rating.ratee_id).eq("rater_role", "user").execute()

            if all_ratings.data:
                avg_stars = sum(r["stars"] for r in all_ratings.data) / len(all_ratings.data)
                total_count = len(all_ratings.data)

                supabase.table("providers").update({
                    "rating": round(avg_stars, 2),
                    "total_ratings": total_count
                }).eq("user_id", rating.ratee_id).execute()

        elif current_user["role"] == "provider":
            # Provider rating a user
            all_ratings = supabase.table("ratings").select("stars").eq("ratee_id", rating.ratee_id).eq("rater_role", "provider").execute()

            if all_ratings.data:
                avg_stars = sum(r["stars"] for r in all_ratings.data) / len(all_ratings.data)
                total_count = len(all_ratings.data)

                supabase.table("users").update({
                    "reliability_score": round(avg_stars, 2),
                    "total_ratings": total_count
                }).eq("id", rating.ratee_id).execute()

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/provider/{provider_user_id}")
async def get_provider_ratings(
    provider_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all ratings for a provider (reviews from users).
    """
    try:
        result = supabase.table("ratings").select("id, stars, review_text, tags, rater_role, created_at").eq("ratee_id", provider_user_id).eq("rater_role", "user").order("created_at", desc=True).execute()

        return result.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_ratings(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get reliability ratings for a user (provider only).
    Shows how reliable the user is based on provider ratings.
    """
    try:
        # Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers user ratings dekh sakte hain")

        result = supabase.table("ratings").select("id, stars, review_text, tags, rater_role, created_at").eq("ratee_id", user_id).eq("rater_role", "provider").order("created_at", desc=True).execute()

        # Calculate average reliability score
        avg_score = 0.0
        if result.data:
            avg_score = sum(r["stars"] for r in result.data) / len(result.data)

        return {
            "ratings": result.data,
            "average_reliability_score": round(avg_score, 2),
            "total_ratings": len(result.data)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/pending")
async def get_pending_ratings(current_user: dict = Depends(get_current_user)):
    """
    Get bookings that need rating from current user.
    Returns completed bookings where current user hasn't rated yet.
    """
    try:
        # Get completed bookings for current user
        if current_user["role"] == "user":
            bookings_result = supabase.table("bookings").select("*, providers(*, users(name))").eq("user_id", current_user["user_id"]).eq("status", "completed").order("created_at", desc=True).execute()
        else:
            # Provider: get provider record first
            provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
            if not provider_result.data:
                raise HTTPException(status_code=404, detail="Provider record nahi mila")

            provider_id = provider_result.data[0]["id"]
            bookings_result = supabase.table("bookings").select("*, users(name)").eq("provider_id", provider_id).eq("status", "completed").order("created_at", desc=True).execute()

        # Filter bookings where current user hasn't rated yet
        pending_bookings = []
        for booking in bookings_result.data:
            # Check if current user has rated this booking
            rating_check = supabase.table("ratings").select("id").eq("booking_id", booking["id"]).eq("rater_id", current_user["user_id"]).execute()

            if not rating_check.data:
                pending_bookings.append(booking)

        return pending_bookings

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
