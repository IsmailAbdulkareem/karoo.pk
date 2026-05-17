from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse, ParsedIntent, ProviderResult
from db.supabase_client import supabase
from utils.jwt_handler import get_current_user
from utils.tracer import AgentTrace
from agents.intent_agent import extract_intent
from agents.ranking import rank_providers
from mcp.tools.geocode import geocode_location

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Main AI chat endpoint.
    Orchestrates: Intent extraction → Geocoding → Provider search → Ranking
    Returns providers with agent trace.
    """
    try:
        # 1. Check role
        if current_user["role"] != "user":
            raise HTTPException(status_code=403, detail="Sirf users chat kar sakte hain")

        # 2. Initialize trace
        tracer = AgentTrace(request.message)

        # 3. Save user message
        supabase.table("messages").insert({
            "user_id": current_user["user_id"],
            "role": "user",
            "content": request.message
        }).execute()

        # 4. Extract intent
        intent_result = await extract_intent(request.message)
        tracer.add_step("Intent Extraction", "gemini_parse", request.message, intent_result)

        # 5. Check confidence
        if intent_result["confidence"] < 0.6 or intent_result["service_type"] is None:
            reply = "Aap kaunsi service chahiye? Maslan: plumber, electrician, AC technician, tutor"
            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "bot",
                "content": reply
            }).execute()
            return ChatResponse(
                reply=reply,
                needs_clarification=True,
                agent_trace=tracer.to_string()
            )

        # 6. Check location
        if intent_result["location"] is None:
            reply = "Aap ki location kya hai? Maslan: F-10, G-11, DHA"
            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "bot",
                "content": reply
            }).execute()
            return ChatResponse(
                reply=reply,
                needs_clarification=True,
                agent_trace=tracer.to_string()
            )

        # 7. Geocode location
        geocode_result = await geocode_location(intent_result["location"])
        tracer.add_step("Location Geocoding", "geocode_location", intent_result["location"], geocode_result)

        user_lat = request.user_lat or geocode_result["lat"]
        user_lng = request.user_lng or geocode_result["lng"]

        # 8. Query providers
        providers_result = supabase.table("providers").select("*, users(name, avatar_url)").eq("service_type", intent_result["service_type"]).eq("is_available", True).execute()

        tracer.add_step("Provider Search", "supabase_query", intent_result["service_type"], f"{len(providers_result.data)} found")

        # 9. Check if providers found
        if not providers_result.data:
            reply = f"Sorry, {intent_result['service_type']} abhi {intent_result['location']} mein available nahi hai"
            supabase.table("messages").insert({
                "user_id": current_user["user_id"],
                "role": "bot",
                "content": reply
            }).execute()
            return ChatResponse(
                reply=reply,
                needs_clarification=False,
                agent_trace=tracer.to_string()
            )

        # 10. Rank providers
        providers_list = []
        for p in providers_result.data:
            user_data = p.get("users", {})
            providers_list.append({
                "id": p["id"],
                "name": user_data.get("name", "Unknown"),
                "service_type": p.get("service_type", ""),
                "area": p.get("area", ""),
                "rating": p.get("rating", 0.0),
                "rate_per_hour": p.get("rate_per_hour"),
                "is_available": p.get("is_available", False),
                "bio": p.get("bio"),
                "lat": p.get("lat"),
                "lng": p.get("lng"),
                "on_time_score": p.get("on_time_score", 5.0),
                "review_recency": p.get("review_recency", 1.0)
            })

        top3 = await rank_providers(providers_list, user_lat, user_lng)
        tracer.add_step("Provider Ranking", "ranking_agent", len(providers_list), f"Top 3 selected")

        # 11. Build ProviderResult list
        provider_results = []
        for p in top3:
            provider_results.append(ProviderResult(
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

        # 12. Build reply
        reply = f"{intent_result['location']} mein {len(top3)} {intent_result['service_type']} available hain"

        # 13. Save bot response
        supabase.table("messages").insert({
            "user_id": current_user["user_id"],
            "role": "bot",
            "content": reply,
            "parsed_intent": intent_result,
            "agent_trace": tracer.to_string()
        }).execute()

        # 14. Return response
        return ChatResponse(
            reply=reply,
            intent=ParsedIntent(**intent_result),
            providers=provider_results,
            needs_clarification=False,
            agent_trace=tracer.to_string()
        )

    except HTTPException:
        raise
    except Exception as e:
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
