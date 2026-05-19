import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_providers",
            "description": "Search for service providers based on service type and location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_type": {"type": "string"},
                    "location": {"type": "string"}
                },
                "required": ["service_type", "location"]
            }
        }
    }
]

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[{"role": "user", "content": "I need a plumber in Karachi"}],
        tools=TOOLS,
        tool_choice="auto"
    )
    print("SUCCESS")
    print(response)
except Exception as e:
    print("FAILED")
    print(e)
