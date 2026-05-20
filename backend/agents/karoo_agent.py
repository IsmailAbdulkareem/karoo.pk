import os
import json
from typing import Optional, Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configure OpenRouter client (compatible with OpenAI SDK)
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Define functions in OpenAI format (compatible with OpenRouter)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_providers",
            "description": "Search for service providers based on service type and location. Returns list of available providers with ratings and pricing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_type": {
                        "type": "string",
                        "description": "Type of service needed (electrician, plumber, ac_technician, tutor, cleaner, carpenter, painter, mechanic, cook, security_guard)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location where service is needed (e.g., G-11, DHA, Karachi)"
                    }
                },
                "required": ["service_type", "location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Create a new booking for a service provider. Requires provider_id, service_type, location, and scheduled_at.",
            "parameters": {
                "type": "object",
                "properties": {
                    "provider_id": {
                        "type": "string",
                        "description": "The ID of the provider to book"
                    },
                    "service_type": {
                        "type": "string",
                        "description": "Type of service needed (electrician, plumber, ac_technician, tutor, cleaner, carpenter, painter, mechanic, cook, security_guard)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location where service is needed"
                    },
                    "scheduled_at": {
                        "type": "string",
                        "description": "Date and time for the booking (ISO 8601 format, e.g., '2026-05-21T10:00:00')"
                    },
                    "note": {
                        "type": "string",
                        "description": "Optional note for the booking"
                    },
                    "booked_via": {
                        "type": "string",
                        "description": "Optional field to indicate booking source (e.g., 'chat')"
                    }
                },
                "required": ["provider_id", "service_type", "location", "scheduled_at"]
            }
        }
    }
]

USER_SYSTEM_PROMPT = """You are Karoo AI assistant for Pakistan's informal economy service booking platform.

CRITICAL RULES - FOLLOW EXACTLY:

1. **CHECK CONVERSATION HISTORY FIRST**: Before asking ANY question, scan ALL previous messages to see if user already provided service_type or location.

2. **Extract from ANY previous message**: If user said "electrician" or "plumber" or "G-11" or "Karachi" in ANY previous message, USE IT. Don't ask again.

3. **Only ask if TRULY missing**:
   - If service_type found in history → DON'T ask for service
   - If location found in history → DON'T ask for location
   - If BOTH found → IMMEDIATELY call search_providers tool

4. **Never ask same question twice**: If you asked "kaunsi service?" and user answered, NEVER ask again.

5. **Understand user intent**:
   - "mujhe plumber chahiye" = service_type is "plumber"
   - "electrician" = service_type is "electrician"
   - "G-11", "Karachi", "DHA" = location
   - If user says "nahi" or "no" after you suggest something, they are rejecting it

6. **When you have BOTH service_type AND location**: IMMEDIATELY use search_providers tool. Don't ask anything else.

Available services: plumber, electrician, ac_technician, tutor, cleaner, carpenter, painter, mechanic, cook, security_guard

PERSONALITY:
- Respond to greetings naturally (hello, kese ho, etc.)
- If user is just chatting, respond conversationally - do NOT call tools
- Keep responses in Roman Urdu/Urdu/English mix
- Be warm and friendly."""

PROVIDER_SYSTEM_PROMPT = """You are Karoo Partner AI, a helpful assistant for service providers in Pakistan.

Your job is to help providers find jobs, check bookings, and track earnings.

IMPORTANT RULES:
1. Providers speak in Urdu, Roman Urdu, or English - understand all three
2. Understand these intents:
   - Finding jobs: "Koi naya kaam hai?", "Open requests dikhaao"
   - Checking bookings: "Aaj ki bookings?", "Kal ka schedule?"
   - Checking earnings: "Kitne paise kamaye?", "Total earnings?"
3. Use the appropriate tool based on intent:
   - search_service_requests for finding jobs
   - get_provider_bookings for checking schedule
   - calculate_provider_earnings for earnings
4. Present results in a friendly way in Roman Urdu/Urdu mix
5. Keep responses concise and helpful

Provider info will be provided in the context."""


async def chat_with_agent(
    message: str,
    conversation_history: List[Dict[str, str]],
    role: str = "user",
    provider_context: Optional[Dict[str, Any]] = None,
    context_summary: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main agent function that handles both user and provider conversations using OpenRouter.

    Args:
        message: User's message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        role: "user" or "provider"
        provider_context: Provider info (id, service_type, area) if role is provider
        context_summary: Extracted context from history (service_type, location)

    Returns:
        Dict with reply, tool_calls, and extracted data
    """
    try:
        BOOKING_KEYWORDS = ["book", "select", "choose", "kara do", "kar do",
                            "confirm", "book karo", "ko book", "ye wala",
                            "pehla", "dusra", "teesra", "1", "2", "3"]

        # Select system prompt based on role
        system_prompt = PROVIDER_SYSTEM_PROMPT if role == "provider" else USER_SYSTEM_PROMPT

        # Add provider context to system prompt if available
        if role == "provider" and provider_context:
            system_prompt += f"\n\nProvider Info:\n- ID: {provider_context.get('id')}\n- Service: {provider_context.get('service_type')}\n- Area: {provider_context.get('area')}"

        # Add context summary if available
        if context_summary:
            system_prompt += f"\n\n{context_summary}"

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({"role": "user", "content": message})

        # Detect if user wants to book (force tool calling to prevent AI faking it)
        message_lower = message.lower()
        wants_to_book = any(kw in message_lower for kw in BOOKING_KEYWORDS)
        has_providers = any("provider" in m.get("content","").lower() or "area" in m.get("content","").lower() for m in conversation_history[-4:])
        force_tools = wants_to_book and has_providers

        # Call OpenRouter with function calling
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b:free",
            messages=messages,
            tools=TOOLS,
            tool_choice="required" if force_tools else "auto"
        )

        print(f"[OPENROUTER AGENT] Response: {response}")

        message_response = response.choices[0].message

        # Check if model wants to call functions
        if message_response.tool_calls:
            function_calls = []
            for tool_call in message_response.tool_calls:
                function_calls.append({
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                })

            print(f"[OPENROUTER AGENT] Function calls detected: {function_calls}")

            return {
                "reply": None,
                "tool_calls": function_calls,
                "needs_tool_execution": True,
                "messages": messages,
                "assistant_message": message_response
            }

        # No function calls, return text response
        reply_text = message_response.content
        if not reply_text:
            reply_text = "Mujhe samajh nahi aaya, thoda clear likhein."

        return {
            "reply": reply_text,
            "tool_calls": [],
            "needs_tool_execution": False,
            "messages": messages
        }

    except Exception as e:
        print(f"[OPENROUTER AGENT] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "reply": "Maaf kijiye, kuch masla aa gaya. Dobara try karein.",
            "tool_calls": [],
            "needs_tool_execution": False,
            "error": str(e)
        }


async def execute_tool_and_respond(
    tool_calls: List[Dict[str, Any]],
    messages: List[Dict[str, str]],
    assistant_message: Any,
    tool_executor: Any,
    role: str = "user",
    provider_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute tool calls and get final response from OpenRouter agent.

    Args:
        tool_calls: List of tool calls to execute
        messages: Conversation messages so far
        assistant_message: The assistant message with tool calls
        tool_executor: Object with methods matching tool names
        role: "user" or "provider"
        provider_context: Provider info if role is provider

    Returns:
        Dict with final reply and tool results
    """
    try:
        # Execute all tool calls
        tool_results = []

        # Add assistant message with tool calls to messages
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"])
                    }
                }
                for tc in tool_calls
            ]
        })

        for tc in tool_calls:
            tool_name = tc["name"]
            tool_args = tc["arguments"]
            tool_call_id = tc["id"]

            print(f"[OPENROUTER AGENT] Executing tool: {tool_name} with args: {tool_args}")

            # Execute the tool
            if hasattr(tool_executor, tool_name):
                result = await getattr(tool_executor, tool_name)(**tool_args)
                tool_results.append({
                    "name": tool_name,
                    "result": result
                })

                # Add tool response to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(result)
                })
            else:
                error_result = {"error": f"Tool {tool_name} not found"}
                tool_results.append({
                    "name": tool_name,
                    "result": error_result
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(error_result)
                })

        # Get final response from OpenRouter
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b:free",
            messages=messages
        )

        reply_text = response.choices[0].message.content
        if not reply_text:
            reply_text = "Mainne check kar liya hai. Upar diye gaye options dekh lein."

        return {
            "reply": reply_text,
            "tool_results": tool_results,
            "needs_tool_execution": False
        }

    except Exception as e:
        print(f"[OPENROUTER AGENT] Tool execution error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "reply": "Maaf kijiye, kuch masla aa gaya. Dobara try karein.",
            "tool_results": [],
            "error": str(e)
        }
