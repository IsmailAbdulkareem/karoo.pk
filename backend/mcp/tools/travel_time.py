import os
import requests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

async def get_travel_time(provider_lat: float, provider_lng: float,
                          user_lat: float, user_lng: float) -> dict:
    """
    Get real driving travel time using Google Routes API.
    Returns eta_minutes (int).
    """
    try:
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_KEY,
            "X-Goog-FieldMask": "routes.duration"
        }
        body = {
            "origin": {"location": {"latLng": {"latitude": provider_lat, "longitude": provider_lng}}},
            "destination": {"location": {"latLng": {"latitude": user_lat, "longitude": user_lng}}},
            "travelMode": "DRIVE"
        }
        response = requests.post(url, json=body, headers=headers)
        data = response.json()

        duration_str = data["routes"][0]["duration"]
        eta_seconds = int(duration_str.replace("s", ""))
        eta_minutes = eta_seconds // 60

        print(f"[MCP TOOL] get_travel_time | Provider: ({provider_lat},{provider_lng}) -> ETA: {eta_minutes} min")
        return {"eta_minutes": eta_minutes}

    except Exception as e:
        print(f"[MCP TOOL] get_travel_time | Error: {e} | Using fallback")
        return {"eta_minutes": 999}
