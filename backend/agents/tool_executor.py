import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from mcp.tools.geocode import geocode_location as mcp_geocode
from db.supabase_client import supabase
from agents.ranking import rank_providers
from utils.notifications import notify_booking_created


class ToolExecutor:
    """
    Executes MCP tools and database queries for the Karoo agent.
    """

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id

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

    def _send_booking_notifications(self, booking_id: str, provider_id: str):
        """Send push notifications for a new booking."""
        try:
            prov = supabase.table("providers").select("user_id").eq("id", provider_id).execute()
            if prov.data and self.user_id:
                provider_user_id = prov.data[0]["user_id"]
                user_res = supabase.table("users").select("name").eq("id", self.user_id).execute()
                user_name = user_res.data[0]["name"] if user_res.data else "User"
                prov_user_res = supabase.table("users").select("name").eq("id", provider_user_id).execute()
                provider_name = prov_user_res.data[0]["name"] if prov_user_res.data else "Provider"
                import asyncio
                asyncio.ensure_future(notify_booking_created(
                    booking_id, self.user_id, provider_user_id,
                    provider_name, user_name, ""
                ))
        except Exception as e:
            print(f"[TOOL EXECUTOR] Notification error: {e}")

    async def _resolve_provider_id(self, provider_id: str) -> Optional[str]:
        """Resolve a provider name or ID to a valid UUID."""
        try:
            uuid.UUID(provider_id)
            return provider_id
        except (ValueError, AttributeError):
            pass
        result = supabase.table("providers").select("id, users(name)").execute()
        for p in result.data or []:
            user_name = ""
            if p.get("users"):
                user_name = p["users"].get("name", "")
            elif p.get("user_id"):
                user_res = supabase.table("users").select("name").eq("id", p["user_id"]).execute()
                if user_res.data:
                    user_name = user_res.data[0].get("name", "")
            if user_name.lower() in provider_id.lower():
                return p["id"]
        return None

    async def create_booking(
        self,
        provider_id: str,
        service_type: str,
        location: str,
        scheduled_at: str,
        note: Optional[str] = None,
        booked_via: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new booking for a provider.
        Resolves provider name to UUID if needed.
        """
        try:
            resolved_id = await self._resolve_provider_id(provider_id)
            if not resolved_id:
                return {
                    "success": False,
                    "error": f"Provider '{provider_id}' nahi mila. Pehle providers search karein."
                }

            booking_data = {
                "user_id": self.user_id,
                "provider_id": resolved_id,
                "service_type": service_type,
                "location": location,
                "scheduled_at": scheduled_at,
                "note": note,
                "booked_via": booked_via or "chat",
                "status": "pending"
            }
            result = supabase.table("bookings").insert(booking_data).execute()
            if result.data:
                booking_id = result.data[0]["id"]
                self._send_booking_notifications(booking_id, resolved_id)
                return {
                    "success": True,
                    "booking_id": booking_id,
                    "message": "Booking created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create booking"
                }
        except Exception as e:
            print(f"[TOOL EXECUTOR] Create booking error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
