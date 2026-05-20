import uuid, re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse, ParsedIntent, ProviderResult, ProviderChatRequest, ProviderChatResponse, ProviderParsedIntent
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from utils.tracer import AgentTrace
from agents.karoo_agent import chat_with_agent, execute_tool_and_respond
from agents.tool_executor import ToolExecutor
from agents.intent_filter import is_negative_response, is_casual_message
from agents.context_extractor import extract_slots_from_history, build_context_summary

router = APIRouter()

# ============================================================
# SERVER-SIDE BOOKING FLOW (bypasses unreliable AI)
# ============================================================

SERVICE_KEYWORDS = {
    "electrician": ["electrician", "bijli", "wiring", "fan", "light", "switch", "meter"],
    "plumber": ["plumber", "nala", "pipe", "water", "tap", "tank", "leak", "nahni"],
    "ac_technician": ["ac", "air conditioner", "cooling", "hvac", "gas"],
    "tutor": ["tutor", "teacher", "parhao", "padhai", "tuition"],
    "cleaner": ["cleaner", "safai", "clean", "maid"],
    "carpenter": ["carpenter", "barhai", "wood", "furniture", "almirah"],
    "painter": ["painter", "rang", "paint", "color"],
    "mechanic": ["mechanic", "gaari", "car", "engine", "repair"],
    "cook": ["cook", "bawarchi", "khana", "cook"],
    "security_guard": ["guard", "security", "watchman", "chowkidar"],
}

BOOKING_INTENT_KEYWORDS = ["chahiye", "book", "kal", "bajhe", "baje", "chahye", "need", "want", "required"]
SELECTION_KEYWORDS = ["1", "2", "3", "pehla", "dusra", "teesra", "select", "choose", "ye wala", "isko", "book karo"]


def _detect_service_type(message: str) -> Optional[str]:
    """Detect service type from user message."""
    msg_lower = message.lower()
    for service, keywords in SERVICE_KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                return service
    return None


def _detect_location(message: str) -> Optional[str]:
    """Extract location from message using common patterns."""
    msg_lower = message.lower()
    # Common Islamabad/Rawalpindi areas
    areas = ["islamabad", "rawalpindi", "f11", "f10", "f8", "f7", "f6", "g11", "g10", "g8", "g6",
             "e11", "i8", "i10", "blue area", "dha", "bahria", "gulberg", "faisal town",
             "karachi", "lahore", "peshawar", "quetta", "multan", "sialkot", "gujranwala"]
    for area in areas:
        if area in msg_lower:
            return area.title()
    return None


def _detect_booking_time(message: str) -> str:
    """Parse booking time from message. Returns ISO format datetime."""
    msg_lower = message.lower()
    now = datetime.utcnow()

    # Check for "kal" (tomorrow)
    if "kal" in msg_lower:
        target_date = now + timedelta(days=1)
    elif "parson" in msg_lower or "day after" in msg_lower:
        target_date = now + timedelta(days=2)
    else:
        target_date = now

    # Check for time patterns like "10 bajhe", "3 pm", "10:00"
    time_match = re.search(r'(\d{1,2})\s*(bajhe|baje|am|pm|:)?\s*(\d{2})?', msg_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(3)) if time_match.group(3) else 0
        if "pm" in msg_lower and hour < 12:
            hour += 12
        target_time = target_date.replace(hour=hour, minute=minute, second=0)
    else:
        # Default to 10 AM
        target_time = target_date.replace(hour=10, minute=0, second=0)

    return target_time.strftime("%Y-%m-%dT%H:%M:%S")


def _was_providers_shown_recently(history: List[Dict]) -> bool:
    """Check if providers were shown in recent conversation."""
    for msg in history[-4:]:
        content = msg.get("content", "").lower()
        if "provider" in content or "available" in content or "match" in content:
            return True
    return False


async def _server_side_booking_flow(
    message: str,
    history: List[Dict],
    user_id: str
) -> Optional[Dict]:
    """
    Complete server-side booking flow. Bypasses AI for reliability.
    Returns None if no booking intent detected (fall back to AI).
    """
    msg_lower = message.lower()

    # Step 1: Check if user is selecting a provider (providers were shown before)
    if _was_providers_shown_recently(history):
        is_selection = any(kw in msg_lower for kw in SELECTION_KEYWORDS)
        if is_selection:
            # Extract provider name from message
            providers_result = supabase.table("providers").select("*, users(name)").execute()
            providers = providers_result.data or []

            # Try to find which provider user selected
            selected_provider = None
            for p in providers:
                pname = (p.get("users") or {}).get("name", "")
                if pname and pname.lower() in msg_lower:
                    selected_provider = p
                    break

            # If no name match, try number selection (1, 2, 3)
            if not selected_provider:
                # Get providers from last assistant message
                for msg in reversed(history[-6:]):
                    if msg.get("role") == "assistant":
                        content = msg.get("content", "")
                        # Extract provider names from the message
                        for p in providers:
                            pname = (p.get("users") or {}).get("name", "")
                            if pname and pname in content:
                                # Check if this provider is mentioned first or with selection keyword
                                idx = msg_lower.find(pname.lower())
                                if idx >= 0 and idx < 100:
                                    selected_provider = p
                                    break
                        if selected_provider:
                            break

            if selected_provider:
                # Create booking directly
                scheduled_at = _detect_booking_time(message)
                service_type = selected_provider.get("service_type", "")
                location = selected_provider.get("area", "")

                booking_data = {
                    "user_id": user_id,
                    "provider_id": selected_provider["id"],
                    "service_type": service_type,
                    "location": location,
                    "scheduled_at": scheduled_at,
                    "booked_via": "chat",
                    "status": "pending"
                }

                result = supabase.table("bookings").insert(booking_data).execute()
                if result.data:
                    booking_id = result.data[0]["id"]
                    provider_name = (selected_provider.get("users") or {}).get("name", "Provider")

                    # Send notification
                    try:
                        from utils.notifications import notify_booking_created
                        prov_user_id = selected_provider.get("user_id")
                        user_res = supabase.table("users").select("name").eq("id", user_id).execute()
                        user_name = user_res.data[0]["name"] if user_res.data else "User"
                        if prov_user_id:
                            import asyncio
                            asyncio.ensure_future(notify_booking_created(
                                booking_id, user_id, prov_user_id,
                                provider_name, user_name, ""
                            ))
                    except Exception as e:
                        print(f"[CHAT] Notification error: {e}")

                    return {
                        "reply": f"✅ **Booking Confirmed!**\n\nProvider: {provider_name}\nService: {service_type}\nTime: {scheduled_at}\n\nBooking ID: {booking_id}\n\nAapki booking confirm ho gayi hai!",
                        "providers": [],
                        "booking_created": True,
                        "booking_id": booking_id
                    }

    # Step 2: Check for new booking request (direct booking without prior provider display)
    has_booking_intent = any(kw in msg_lower for kw in BOOKING_INTENT_KEYWORDS)
    if has_booking_intent:
        service_type = _detect_service_type(message)
        location = _detect_location(message)

        if service_type and location:
            # Search providers directly
            query = supabase.table("providers").select("*, users(name)").eq("service_type", service_type).eq("is_available", True)
            providers_result = query.execute()
            providers = providers_result.data or []

            if providers:
                # Pick the first available provider (or could rank them)
                selected_provider = providers[0]
                scheduled_at = _detect_booking_time(message)
                service_type = selected_provider.get("service_type", "")
                location = selected_provider.get("area", "")

                booking_data = {
                    "user_id": user_id,
                    "provider_id": selected_provider["id"],
                    "service_type": service_type,
                    "location": location,
                    "scheduled_at": scheduled_at,
                    "booked_via": "chat",
                    "status": "pending"
                }

                result = supabase.table("bookings").insert(booking_data).execute()
                if result.data:
                    booking_id = result.data[0]["id"]
                    provider_name = (selected_provider.get("users") or {}).get("name", "Provider")

                    # Send notification
                    try:
                        from utils.notifications import notify_booking_created
                        prov_user_id = selected_provider.get("user_id")
                        user_res = supabase.table("users").select("name").eq("id", user_id).execute()
                        user_name = user_res.data[0]["name"] if user_res.data else "User"
                        if prov_user_id:
                            import asyncio
                            asyncio.ensure_future(notify_booking_created(
                                booking_id, user_id, prov_user_id,
                                provider_name, user_name, ""
                            ))
                    except Exception as e:
                        print(f"[CHAT] Notification error: {e}")

                    return {
                        "reply": f"✅ **Booking Confirmed!**\n\nProvider: {provider_name}\nService: {service_type}\nTime: {scheduled_at}\n\nBooking ID: {booking_id}\n\nAapki booking confirm ho gayi hai!",
                        "providers": [],
                        "booking_created": True,
                        "booking_id": booking_id
                    }

    # Step 3: If no booking intent, fall back to AI
    return None  # No booking intent, fall back to AI

async def get_conversation_history(user_id: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Fetch recent conversation history for context.
    Returns list of {"role": "user/assistant", "content": "..."}
    """
    try:
        result = supabase.table("messages").select("role, content").eq("user_id", user_id).order("created_at", desc=False).limit(limit).execute()

        history = []
        for msg in result.data:
            role = "assistant" if msg["role"] == "bot" else "user"
            history.append({"role": role, "content": msg["content"]})

        return history
    except Exception as e:
        print(f"[CHAT] Error fetching history: {e}")
        return []


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Main AI chat endpoint using Google Gemini API.
    Maintains conversation context and uses MCP tools for geocoding and provider search.
    """
    try:
        # Slice conversation history to last 6 messages as per requirement
        # (will be applied after fetching history below)
        pass
        # 1. Check role
        if current_user["role"] != "user":
            raise HTTPException(status_code=403, detail="Sirf users chat kar sakte hain")

        # 2. Initialize trace
        tracer = AgentTrace(
            goal="Handle user booking request via AI agent",
            steps_planned=["Get Context", "Agent Processing", "Tool Execution", "Response"],
            user_id=current_user["user_id"],
            user_message=request.message
        )

        # 3. Get conversation history for context (load last 10 messages)
        conversation_history = await get_conversation_history(current_user["user_id"], limit=10)
        tracer.add_step("Fetch Context", "get_history", current_user["user_id"], f"{len(conversation_history)} messages", "SUCCESS", 100)

        # 3a. Extract slots from history to help agent
        slots = extract_slots_from_history(conversation_history)
        context_summary = build_context_summary(slots)
        tracer.add_step("Extract Slots", "context_extractor", conversation_history, slots, "SUCCESS", 50)

        # 4. Save user message
        supabase.table("messages").insert({
            "user_id": current_user["user_id"],
            "role": "user",
            "content": request.message
        }).execute()

        # 5. TRY SERVER-SIDE BOOKING FLOW FIRST (bypasses unreliable AI)
        server_booking_result = await _server_side_booking_flow(
            message=request.message,
            history=conversation_history,
            user_id=current_user["user_id"]
        )

        if server_booking_result:
            # Server-side booking flow handled it
            reply = server_booking_result["reply"]
            providers = server_booking_result["providers"]

            # Save user message
            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "user",
                "content": request.message
            }).execute()

            # Save bot response
            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "bot",
                "content": reply,
                "agent_trace": tracer.to_string()
            }).execute()

            tracer.complete("SUCCESS")
            return ChatResponse(
                reply=reply,
                providers=providers,
                needs_clarification=not server_booking_result.get("booking_created"),
                agent_trace=tracer.to_string(),
                booking_created=server_booking_result.get("booking_created", False),
                booking_id=server_booking_result.get("booking_id")
            )

        # 6. Fall back to AI agent
        agent_response = await chat_with_agent(
            message=request.message,
            conversation_history=conversation_history,
            role="user",
            context_summary=context_summary  # Pass extracted context
        )
        # Extract serializable data for tracer
        trace_data = {
            "needs_tool_execution": agent_response.get("needs_tool_execution"),
            "tool_calls": agent_response.get("tool_calls", []),
            "reply": agent_response.get("reply")
        }
        tracer.add_step("Agent Processing", "karoo_agent", request.message, trace_data, "SUCCESS", 800)

        # 7. Check if agent needs to execute tools
        if agent_response.get("needs_tool_execution"):
            tool_executor = ToolExecutor(user_id=current_user["user_id"])

            # Execute tools and get final response
            final_response = await execute_tool_and_respond(
                tool_calls=agent_response["tool_calls"],
                messages=agent_response["messages"],
                assistant_message=agent_response["assistant_message"],
                tool_executor=tool_executor,
                role="user"
            )
            tracer.add_step("Tool Execution", "execute_tools", agent_response["tool_calls"], final_response, "SUCCESS", 600)

            reply = final_response["reply"]
            tool_results = final_response.get("tool_results", [])

            # Extract providers and possible booking results from tool calls
            providers = []
            booking_info = None
            for tr in tool_results:
                # 1️⃣ Provider search
                if tr["name"] == "search_providers" and tr["result"].get("success"):
                    provider_data = tr["result"].get("providers", [])
                    for p in provider_data:
                        providers.append(ProviderResult(
                            id=p["id"],
                            name=p["name"],
                            service_type=p["service_type"],
                            area=p["area"],
                            rating=p["rating"],
                            rate_per_hour=p.get("rate_per_hour"),
                            is_available=p["is_available"],
                            bio=p.get("bio"),
                            eta_minutes=p.get("eta_minutes"),
                            match_score=p.get("match_score")
                        ))
                # 2️⃣ Booking creation
                if tr["name"] == "create_booking" and tr["result"].get("success"):
                    booking_info = {
                        "booking_id": tr["result"].get("booking_id"),
                        "message": tr["result"].get("message")
                    }

            # Fallback: AI said booked but didn't call create_booking
            if not booking_info and reply and "book" in reply.lower() and "error" not in reply.lower():
                fallback = await _try_create_booking_from_reply(reply, current_user["user_id"])
                if fallback:
                    print(f"[CHAT] Server-side fallback booking created (tool branch): {fallback}")

            # Save bot response
            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "bot",
                "content": reply,
                "agent_trace": tracer.to_string()
            }).execute()

            tracer.complete("SUCCESS")
            return ChatResponse(
                reply=reply,
                providers=providers,
                needs_clarification=False,
                agent_trace=tracer.to_string()
            )

        else:
            # No tool execution needed, just return agent's reply
            reply = agent_response["reply"]

            # Fallback: if AI faked booking confirmation without calling create_booking, create it
            if "book" in reply.lower() and "error" not in reply.lower():
                fallback = await _try_create_booking_from_reply(reply, current_user["user_id"])
                if fallback:
                    print(f"[CHAT] Server-side fallback booking created: {fallback}")

            # Save bot response
            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "bot",
                "content": reply,
                "agent_trace": tracer.to_string()
            }).execute()

            tracer.complete("SUCCESS")
            return ChatResponse(
                reply=reply,
                providers=[],
                needs_clarification=True,  # Agent is asking for more info
                agent_trace=tracer.to_string(),
                booking_created=False,
                booking_id=None
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[CHAT] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


async def _try_create_booking_from_reply(reply: str, user_id: str) -> Optional[dict]:
    """When AI fakes a booking without calling create_booking, create it server-side."""
    try:
        # Look for any provider name mentioned in the reply
        try:
            providers = supabase.table("providers").select("id, users(name)").execute()
            if not providers.data:
                return None

            for p in providers.data or []:
                try:
                    uname = (p.get("users") or {}).get("name", "")
                    if uname and uname.lower() in reply.lower():
                        # Found a provider name in the reply
                        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT10:00:00")
                        result = supabase.table("bookings").insert({
                            "user_id": user_id,
                            "provider_id": p["id"],
                            "service_type": p.get("service_type", ""),
                            "location": p.get("area", ""),
                            "scheduled_at": tomorrow,
                            "booked_via": "chat",
                            "status": "pending"
                        }).execute()
                        if result.data:
                            return {"booking_id": result.data[0]["id"], "provider_name": uname}
                except Exception as e:
                    print(f"[CHAT] Individual provider booking error: {e}")
                    continue
        except Exception as e:
            print(f"[CHAT] Providers lookup error: {e}")
    except Exception as e:
        print(f"[CHAT] Critical fallback booking error: {e}")
    return None


@router.get("/history")
async def get_chat_history(current_user: dict = Depends(get_current_user)):
    """
    Get chat history for current user.
    """
    try:
        result = supabase.table("messages").select("*").eq("user_id", current_user["user_id"]).order("created_at", desc=False).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.delete("/history")
async def clear_chat_history(current_user: dict = Depends(get_current_user)):
    """
    Clear all chat history for current user.
    """
    try:
        supabase.table("messages").delete().eq("user_id", current_user["user_id"]).execute()
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/provider", response_model=ProviderChatResponse)
async def provider_chat(
    request: ProviderChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    AI chat endpoint for providers using Google Gemini API.
    Helps providers find jobs, check bookings, and track earnings.
    """
    try:
        # 1. Check role
        if current_user["role"] != "provider":
            raise HTTPException(status_code=403, detail="Sirf providers ye feature use kar sakte hain")

        # 2. Get provider profile
        provider_res = supabase.table("providers").select("*").eq("user_id", current_user["user_id"]).execute()
        if not provider_res.data:
            raise HTTPException(status_code=404, detail="Provider profile nahi mila")

        provider = provider_res.data[0]
        provider_context = {
            "id": provider["id"],
            "service_type": provider.get("service_type", ""),
            "area": provider.get("area", "")
        }

        # 3. Initialize trace
        tracer = AgentTrace(
            goal="Provider natural language query",
            steps_planned=["Get Context", "Agent Processing", "Tool Execution"],
            user_id=current_user["user_id"],
            user_message=request.message
        )

        # 4. Get conversation history (load last 10 messages)
        conversation_history = await get_conversation_history(current_user["user_id"], limit=10)
        tracer.add_step("Fetch Context", "get_history", current_user["user_id"], f"{len(conversation_history)} messages", "SUCCESS", 100)

        # 5. Save user message
        supabase.table("messages").insert({
            "user_id": current_user["user_id"],
            "role": "user",
            "content": request.message
        }).execute()

        # 6. Call agent
        agent_response = await chat_with_agent(
            message=request.message,
            conversation_history=conversation_history,
            role="provider",
            provider_context=provider_context
        )
        # Extract serializable data for tracer
        trace_data = {
            "needs_tool_execution": agent_response.get("needs_tool_execution"),
            "tool_calls": agent_response.get("tool_calls", []),
            "reply": agent_response.get("reply")
        }
        tracer.add_step("Agent Processing", "karoo_agent", request.message, trace_data, "SUCCESS", 800)

        # 7. Execute tools if needed
        if agent_response.get("needs_tool_execution"):
            tool_executor = ToolExecutor()

            final_response = await execute_tool_and_respond(
                tool_calls=agent_response["tool_calls"],
                messages=agent_response["messages"],
                assistant_message=agent_response["assistant_message"],
                tool_executor=tool_executor,
                role="provider",
                provider_context=provider_context
            )
            tracer.add_step("Tool Execution", "execute_tools", agent_response["tool_calls"], final_response, "SUCCESS", 600)

            reply = final_response["reply"]
            tool_results = final_response.get("tool_results", [])

            # Extract results from tool calls
            results = []
            intent_type = None

            for tr in tool_results:
                if tr["name"] == "search_service_requests":
                    intent_type = "find_requests"
                    if tr["result"].get("success"):
                        results = tr["result"].get("requests", [])
                elif tr["name"] == "get_provider_bookings":
                    intent_type = "check_bookings"
                    if tr["result"].get("success"):
                        results = tr["result"].get("bookings", [])
                elif tr["name"] == "calculate_provider_earnings":
                    intent_type = "check_earnings"
                    if tr["result"].get("success"):
                        results = [tr["result"]]  # Wrap in list for frontend

            # Save bot response
            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "bot",
                "content": reply,
                "agent_trace": tracer.to_string()
            }).execute()

            tracer.complete("SUCCESS")
            return ProviderChatResponse(
                reply=reply,
                intent=ProviderParsedIntent(intent_type=intent_type, confidence=1.0),
                results=results,
                agent_trace=tracer.to_string()
            )

        else:
            # No tool execution, just clarification
            reply = agent_response["reply"]

            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "bot",
                "content": reply,
                "agent_trace": tracer.to_string()
            }).execute()

            tracer.complete("SUCCESS")
            return ProviderChatResponse(
                reply=reply,
                intent=ProviderParsedIntent(confidence=0.5),
                results=[],
                agent_trace=tracer.to_string()
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[PROVIDER CHAT] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
