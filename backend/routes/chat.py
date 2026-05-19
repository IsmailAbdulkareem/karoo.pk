from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse, ParsedIntent, ProviderResult, ProviderChatRequest, ProviderChatResponse, ProviderParsedIntent
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from utils.tracer import AgentTrace
from agents.karoo_agent import chat_with_agent, execute_tool_and_respond
from agents.tool_executor import ToolExecutor
from agents.intent_filter import is_negative_response, is_casual_message
from agents.context_extractor import extract_slots_from_history, build_context_summary
from typing import List, Dict

router = APIRouter()

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

        # 5. Call agent with conversation history (let agent think for all messages)
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
            tool_executor = ToolExecutor()

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

            # Extract providers from tool results
            providers = []
            for tr in tool_results:
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
                agent_trace=tracer.to_string()
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[CHAT] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


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
