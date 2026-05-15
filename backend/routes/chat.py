from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest
from db.supabase_client import supabase
import os

router = APIRouter(prefix="/api", tags=["Chat & AI"])

@router.post("/request")
async def process_chat_request(request: ChatRequest):
    """
    Process user message through Google Antigravity agent
    - Extract intent via Gemini API
    - Geocode location
    - Match providers using Google Routes API
    - Return ranked results with agent trace
    """
    # TODO: Implement Antigravity agent integration
    # TODO: Call MCP tools for geocoding and travel time
    # TODO: Query providers from Supabase
    # TODO: Rank providers using multi-factor scoring
    # TODO: Store message and agent trace in database
    return {
        "message": "Chat request endpoint - to be implemented",
        "intent": {},
        "providers": [],
        "agent_trace": ""
    }

@router.get("/messages/{user_id}")
async def get_chat_history(user_id: str):
    """Get chat history for a user"""
    # TODO: Fetch messages from Supabase
    return {"message": "Chat history endpoint - to be implemented"}
