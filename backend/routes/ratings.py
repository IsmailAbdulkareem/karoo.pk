from fastapi import APIRouter, HTTPException
from models.schemas import RatingCreate
from db.supabase_client import supabase

router = APIRouter(prefix="/api/ratings", tags=["Ratings"])

@router.post("")
async def submit_rating(rating: RatingCreate):
    """Submit rating after booking completion"""
    # TODO: Verify booking is completed
    # TODO: Verify user hasn't already rated this booking
    # TODO: Store rating in Supabase
    # TODO: Update provider.rating or user.reliability_score
    return {"message": "Submit rating endpoint - to be implemented"}

@router.get("/provider/{provider_id}")
async def get_provider_ratings(provider_id: str):
    """Get all ratings for a provider"""
    # TODO: Fetch ratings from Supabase
    # TODO: Calculate effective_rating with recency weighting
    return {"message": "Get provider ratings endpoint - to be implemented"}

@router.get("/user/{user_id}")
async def get_user_reliability(user_id: str):
    """Get user reliability score and reviews"""
    # TODO: Fetch user ratings from Supabase
    # TODO: Return reliability_score and review summary
    return {"message": "Get user reliability endpoint - to be implemented"}
