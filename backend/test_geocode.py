import asyncio
from mcp.tools.geocode import geocode_location

async def test():
    print("Testing Google Maps Geocoding API...\n")
    
    result = await geocode_location("F-10 Islamabad")
    print(f"Result: {result}")

asyncio.run(test())
