from fastapi import APIRouter, HTTPException
from db.supabase_client import supabase
from typing import Optional

router = APIRouter(prefix="/api/providers", tags=["Providers"])

@router.get("")
async def list_providers(service_type: Optional[str] = None, city: Optional[str] = None):
    """List all providers with optional filters"""
    # TODO: Query providers from Supabase
    # TODO: Apply filters for service_type and city
    return {"message": "List providers endpoint - to be implemented"}

@router.get("/{provider_id}")
async def get_provider(provider_id: str):
    """Get single provider details"""
    # TODO: Fetch provider from Supabase by ID
    return {"message": "Get provider endpoint - to be implemented"}

@router.put("/{provider_id}")
async def update_provider(provider_id: str):
    """Update provider profile (provider only)"""
    # TODO: Verify JWT token and provider ownership
    # TODO: Update provider in Supabase
    return {"message": "Update provider endpoint - to be implemented"}
