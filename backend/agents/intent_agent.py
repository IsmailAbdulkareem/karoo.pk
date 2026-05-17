import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

INTENT_PROMPT = """
You are an AI assistant for Karoo, a service booking app in Pakistan.

Extract the following from the user message (which may be in Urdu, Roman Urdu, or English):
- service_type: what service they need. Map to one of: plumber, electrician, ac_technician, tutor, cleaner, carpenter, painter, mechanic, cook, security_guard. If unsure, use closest match.
- location: area or neighborhood they mentioned (e.g. F-10, G-11, DHA, Gulshan)
- time: when they need it (today, tomorrow, morning, evening, or specific time)
- confidence: float 0.0 to 1.0 — how confident you are in the extraction

Rules:
- If a field is not mentioned in the message, return null for that field
- confidence should be low (< 0.6) if message is very vague or unclear
- Always respond ONLY with valid JSON, no explanation, no markdown

User message: "{message}"

Respond with this exact JSON format:
{{"service_type": "...", "location": "...", "time": "...", "confidence": 0.95}}
"""

async def extract_intent(message: str) -> dict:
    """
    Extract service booking intent from user message using OpenRouter API.
    Supports Urdu, Roman Urdu, and English.
    Returns dict with service_type, location, time, confidence.
    """
    try:
        prompt = INTENT_PROMPT.format(message=message)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Karoo App",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=30.0
            )

            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()

        # Clean response in case model adds markdown
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        result = json.loads(text.strip())
        print(f"[INTENT AGENT] Input: '{message}' -> Output: {result}")
        return result

    except json.JSONDecodeError:
        print(f"[INTENT AGENT] JSON parse failed, returning low confidence")
        return {"service_type": None, "location": None, "time": None, "confidence": 0.0}
    except Exception as e:
        print(f"[INTENT AGENT] Error: {e}")
        return {"service_type": None, "location": None, "time": None, "confidence": 0.0}
