from typing import Dict, Any, Optional
from datetime import datetime
from mcp.tools.geocode import geocode_location as mcp_geocode
from db.supabase_client import supabase
from agents.ranking import rank_providers


class ToolExecutor:
    """
    Executes MCP tools and database queries for the Karoo agent.
    """

    async def geocode_location(self, location: str) -> Dict[str, Any]:
        """
        Geocode a location name to coordinates using MCP tool.
        """
        try:
            result = await mcp_geocode(location)
            return {
                "success": True,
                "location": location,
                "lat": result.get("lat"),
                "lng": result.get("lng"),
                "formatted_address": result.get("formatted_address", location)
            }
        except Exception as e:
            print(f"[TOOL EXECUTOR] Geocode error: {e}")
            return {
                "success": False,
                "error": str(e),
                "location": location
            }

    async def search_providers(
        self,
        service_type: str,
        location: Optional[str] = None,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Search for providers by service type and rank them by proximity.
        """
        try:
            # Query providers from database
            query = supabase.table("providers").select("*, users(name, avatar_url)")
            query = query.eq("service_type", service_type).eq("is_available", True)

            providers_result = query.execute()

            if not providers_result.data:
                return {
                    "success": True,
                    "providers": [],
                    "count": 0,
                    "message": f"No {service_type} available"
                }

            # Format providers
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

            # Rank providers if user location is available
            if user_lat and user_lng:
                top_providers = await rank_providers(providers_list, user_lat, user_lng)
            else:
                # Return top 3 by rating if no location
                top_providers = sorted(providers_list, key=lambda x: x["rating"], reverse=True)[:3]

            return {
                "success": True,
                "providers": top_providers,
                "count": len(top_providers),
                "service_type": service_type,
                "location": location
            }

        except Exception as e:
            print(f"[TOOL EXECUTOR] Search providers error: {e}")
            return {
                "success": False,
                "error": str(e),
                "providers": [],
                "count": 0
            }

    async def search_service_requests(
        self,
        service_type: str,
        area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for open service requests (for providers to find jobs).
        """
        try:
            query = supabase.table("service_requests").select("*, users(name, phone)")
            query = query.eq("status", "open").eq("service_type", service_type)

            if area:
                query = query.eq("location", area)

            requests_result = query.execute()

            return {
                "success": True,
                "requests": requests_result.data,
                "count": len(requests_result.data),
                "service_type": service_type,
                "area": area
            }

        except Exception as e:
            print(f"[TOOL EXECUTOR] Search requests error: {e}")
            return {
                "success": False,
                "error": str(e),
                "requests": [],
                "count": 0
            }

    async def get_provider_bookings(
        self,
        provider_id: str,
        time_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get bookings for a provider with optional time filter.
        """
        try:
            query = supabase.table("bookings").select("*, users(name, phone)")
            query = query.eq("provider_id", provider_id)

            if time_filter == "today":
                today_str = datetime.utcnow().strftime("%Y-%m-%d")
                tomorrow_str = datetime.utcnow().strftime("%Y-%m-%d") + "T23:59:59"
                query = query.gte("scheduled_at", today_str).lte("scheduled_at", tomorrow_str)

            bookings_result = query.execute()

            return {
                "success": True,
                "bookings": bookings_result.data,
                "count": len(bookings_result.data),
                "provider_id": provider_id,
                "time_filter": time_filter
            }

        except Exception as e:
            print(f"[TOOL EXECUTOR] Get bookings error: {e}")
            return {
                "success": False,
                "error": str(e),
                "bookings": [],
                "count": 0
            }

    async def calculate_provider_earnings(
        self,
        provider_id: str
    ) -> Dict[str, Any]:
        """
        Calculate total earnings for a provider from completed bookings.
        """
        try:
            # Get provider's rate
            provider_res = supabase.table("providers").select("rate_per_hour").eq("id", provider_id).execute()
            rate_per_hour = 0
            if provider_res.data:
                rate_per_hour = provider_res.data[0].get("rate_per_hour", 0)

            # Get completed bookings
            earnings_res = supabase.table("bookings").select("agreed_rate, budget").eq("provider_id", provider_id).eq("status", "completed").execute()
            completed = earnings_res.data

            # Calculate total
            total = sum(b.get("agreed_rate") or b.get("budget") or rate_per_hour for b in completed)

            return {
                "success": True,
                "total_earned_pkr": total,
                "total_completed_jobs": len(completed),
                "provider_id": provider_id,
                "completed_bookings": completed
            }

        except Exception as e:
            print(f"[TOOL EXECUTOR] Calculate earnings error: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_earned_pkr": 0,
                "total_completed_jobs": 0
            }
