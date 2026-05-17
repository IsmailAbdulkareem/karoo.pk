import os
import requests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

async def geocode_location(location_text: str) -> dict:
    """
    Convert area name to lat/lng using Google Geocoding API.
    Example: "F-10 Islamabad" → {"lat": 33.68, "lng": 73.04}
    """
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": f"{location_text}, Pakistan",
            "key": GOOGLE_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "OK":
            loc = data["results"][0]["geometry"]["location"]
            result = {"lat": loc["lat"], "lng": loc["lng"], "formatted": data["results"][0]["formatted_address"]}
            print(f"[MCP TOOL] geocode_location | Input: {location_text} | Output: {result}")
            return result
        else:
            print(f"[MCP TOOL] geocode_location | Failed: {data['status']}")
            return {"lat": None, "lng": None, "formatted": location_text}
    except Exception as e:
        print(f"[MCP TOOL] geocode_location | Error: {e}")
        return {"lat": None, "lng": None, "formatted": location_text}
