from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from models.schemas import ConversationCreate, MessageCreate, MessageResponse, ConversationResponse
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from typing import List, Dict
import json

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"[WEBSOCKET] User {user_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"[WEBSOCKET] User {user_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                print(f"[WEBSOCKET] Sent message to user {user_id}")
            except Exception as e:
                print(f"[WEBSOCKET] Error sending to {user_id}: {e}")
                self.disconnect(user_id)

manager = ConnectionManager()

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conv: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a conversation for a booking.
    Auto-created when booking is confirmed, but can be manually created.
    """
    try:
        # Get booking details
        booking_result = supabase.table("bookings").select("*, providers(user_id)").eq("id", conv.booking_id).execute()
        if not booking_result.data:
            raise HTTPException(status_code=404, detail="Booking nahi mila")

        booking = booking_result.data[0]
        user_id = booking["user_id"]
        provider_user_id = booking["providers"]["user_id"]

        # Check if user is part of this booking
        if current_user["user_id"] not in [user_id, provider_user_id]:
            raise HTTPException(status_code=403, detail="Aap is booking ka hissa nahi hain")

        # Check if conversation already exists
        existing = supabase.table("conversations").select("*").eq("booking_id", conv.booking_id).execute()
        if existing.data:
            return existing.data[0]

        # Create new conversation
        conversation_data = {
            "booking_id": conv.booking_id,
            "user_id": user_id,
            "provider_id": provider_user_id
        }
        result = supabase.table("conversations").insert(conversation_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Conversation create nahi hui")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("", response_model=List[ConversationResponse])
async def get_my_conversations(current_user: dict = Depends(get_current_user)):
    """
    Get all conversations for current user (user or provider).
    Includes other party's name and avatar.
    """
    try:
        # Get conversations where user is participant
        if current_user["role"] == "user":
            result = supabase.table("conversations").select("*").eq("user_id", current_user["user_id"]).order("last_message_at", desc=True).execute()
        else:
            # Provider - first get provider ID
            provider_result = supabase.table("providers").select("id").eq("user_id", current_user["user_id"]).execute()
            if not provider_result.data:
                return []

            provider_id = provider_result.data[0]["id"]
            result = supabase.table("conversations").select("*").eq("provider_id", provider_id).order("last_message_at", desc=True).execute()

        # Enrich with other party info
        conversations = []
        for conv in result.data:
            # Get other party's user info
            if current_user["role"] == "user":
                # User is viewing, so get provider's user info
                other_user_id = conv.get("provider_id")
            else:
                # Provider is viewing, so get customer's user info
                other_user_id = conv.get("user_id")

            # Fetch other party's name and avatar
            if other_user_id:
                user_result = supabase.table("users").select("name, avatar_url").eq("user_id", other_user_id).execute()
                if user_result.data:
                    conv["other_party_name"] = user_result.data[0].get("name", "Unknown")
                    conv["other_party_avatar"] = user_result.data[0].get("avatar_url")
                else:
                    conv["other_party_name"] = "Unknown"
                    conv["other_party_avatar"] = None
            else:
                conv["other_party_name"] = "Unknown"
                conv["other_party_avatar"] = None

            conversations.append(conv)

        return conversations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all messages in a conversation.
    Auto-marks messages as read for current user.
    """
    try:
        # Verify user is part of conversation
        conv_result = supabase.table("conversations").select("user_id, provider_id").eq("id", conversation_id).execute()
        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation nahi mila")

        conv = conv_result.data[0]
        if current_user["user_id"] not in [conv["user_id"], conv["provider_id"]]:
            raise HTTPException(status_code=403, detail="Aap is conversation ka hissa nahi hain")

        # Get messages
        messages_result = supabase.table("conversation_messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()

        # Mark messages as read for current user
        unread_messages = [m["id"] for m in messages_result.data if not m["is_read"] and m["sender_id"] != current_user["user_id"]]
        if unread_messages:
            supabase.table("conversation_messages").update({"is_read": True}).in_("id", unread_messages).execute()

            # Reset unread count
            if current_user["role"] == "user":
                supabase.table("conversations").update({"user_unread_count": 0}).eq("id", conversation_id).execute()
            else:
                supabase.table("conversations").update({"provider_unread_count": 0}).eq("id", conversation_id).execute()

        return messages_result.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message in a conversation.
    Notifies other party via WebSocket if connected.
    """
    try:
        # Verify user is part of conversation
        conv_result = supabase.table("conversations").select("user_id, provider_id").eq("id", conversation_id).execute()
        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation nahi mila")

        conv = conv_result.data[0]
        if current_user["user_id"] not in [conv["user_id"], conv["provider_id"]]:
            raise HTTPException(status_code=403, detail="Aap is conversation ka hissa nahi hain")

        # Determine sender role and recipient
        sender_role = current_user["role"]
        recipient_id = conv["provider_id"] if current_user["user_id"] == conv["user_id"] else conv["user_id"]

        # Insert message
        message_data = {
            "conversation_id": conversation_id,
            "sender_id": current_user["user_id"],
            "sender_role": sender_role,
            "message": message.message,
            "is_read": False
        }
        result = supabase.table("conversation_messages").insert(message_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Message send nahi hui")

        new_message = result.data[0]

        # Send via WebSocket to recipient if connected
        await manager.send_message(recipient_id, {
            "type": "new_message",
            "conversation_id": conversation_id,
            "message": new_message
        })

        return new_message

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time messaging.
    Connect: ws://localhost:8000/api/conversations/ws/{user_id}?token=JWT_TOKEN
    """
    try:
        # Verify JWT token from query params
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008, reason="Token missing")
            return

        # TODO: Verify token and extract user_id (simplified for now)
        await manager.connect(user_id, websocket)

        try:
            while True:
                # Keep connection alive and listen for messages
                data = await websocket.receive_text()
                # Echo back for heartbeat
                await websocket.send_json({"type": "pong", "data": data})
        except WebSocketDisconnect:
            manager.disconnect(user_id)
    except Exception as e:
        print(f"[WEBSOCKET] Error: {e}")
        manager.disconnect(user_id)
