from datetime import datetime, timedelta
from typing import Dict, List, Optional
from db.supabase_client import supabase


class SchedulingEngine:
    """
    Intelligent scheduling engine for Karoo.
    Prevents double-booking, manages travel time buffers, suggests alternate slots.
    """

    def __init__(self):
        self.default_buffer_minutes = 15
        self.default_job_duration = 60

    async def check_availability(
        self,
        provider_id: str,
        requested_time: datetime,
        duration_minutes: int = 60
    ) -> Dict:
        """
        Check if provider is available at requested time.
        Considers: existing bookings, travel time, buffer time.

        Returns:
        {
            "available": true/false,
            "conflict": null or booking_id,
            "reason": "explanation",
            "alternate_slots": [...]
        }
        """
        try:
            # Calculate time window (requested time ± duration + buffer)
            start_window = requested_time - timedelta(minutes=self.default_buffer_minutes)
            end_window = requested_time + timedelta(minutes=duration_minutes + self.default_buffer_minutes)

            # Get all confirmed bookings for this provider in the time window
            result = supabase.table("bookings").select("*").eq("provider_id", provider_id).in_("status", ["pending", "confirmed"]).execute()

            conflicts = []
            for booking in result.data:
                booking_time = datetime.fromisoformat(booking["scheduled_at"].replace('Z', '+00:00'))
                booking_duration = booking.get("duration_minutes", self.default_job_duration)
                booking_travel = booking.get("travel_time_minutes", 0)
                booking_buffer = booking.get("buffer_time_minutes", self.default_buffer_minutes)

                # Calculate booking's time window
                booking_start = booking_time - timedelta(minutes=booking_travel + booking_buffer)
                booking_end = booking_time + timedelta(minutes=booking_duration + booking_buffer)

                # Check for overlap
                if not (end_window <= booking_start or start_window >= booking_end):
                    conflicts.append({
                        "booking_id": booking["id"],
                        "scheduled_at": booking["scheduled_at"],
                        "service_type": booking["service_type"]
                    })

            if conflicts:
                return {
                    "available": False,
                    "conflict": conflicts[0]["booking_id"],
                    "reason": f"Provider already has a booking at {conflicts[0]['scheduled_at']}",
                    "conflicts": conflicts,
                    "alternate_slots": await self.suggest_alternate_slots(
                        provider_id,
                        requested_time.date(),
                        duration_minutes
                    )
                }

            return {
                "available": True,
                "conflict": None,
                "reason": "Provider is available",
                "alternate_slots": []
            }

        except Exception as e:
            print(f"[SCHEDULING] Error checking availability: {e}")
            return {
                "available": False,
                "conflict": None,
                "reason": f"Error checking availability: {str(e)}",
                "alternate_slots": []
            }

    async def prevent_double_booking(
        self,
        provider_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Check for overlapping bookings including travel time buffer.
        Returns True if slot is free, False if conflict exists.
        """
        try:
            # Add buffer to both ends
            buffered_start = start_time - timedelta(minutes=self.default_buffer_minutes)
            buffered_end = end_time + timedelta(minutes=self.default_buffer_minutes)

            # Query for overlapping bookings
            result = supabase.table("bookings").select("id, scheduled_at, duration_minutes").eq("provider_id", provider_id).in_("status", ["pending", "confirmed"]).execute()

            for booking in result.data:
                booking_time = datetime.fromisoformat(booking["scheduled_at"].replace('Z', '+00:00'))
                booking_duration = booking.get("duration_minutes", self.default_job_duration)
                booking_end = booking_time + timedelta(minutes=booking_duration)

                # Check overlap
                if not (buffered_end <= booking_time or buffered_start >= booking_end):
                    return False

            return True

        except Exception as e:
            print(f"[SCHEDULING] Error in double-booking check: {e}")
            return False

    async def suggest_alternate_slots(
        self,
        provider_id: str,
        date: datetime.date,
        duration_minutes: int = 60
    ) -> List[Dict]:
        """
        Find available slots on given date.
        Returns list of {start, end} time slots.
        """
        try:
            # Get all bookings for this provider on this date
            date_start = datetime.combine(date, datetime.min.time())
            date_end = datetime.combine(date, datetime.max.time())

            result = supabase.table("bookings").select("scheduled_at, duration_minutes").eq("provider_id", provider_id).in_("status", ["pending", "confirmed"]).execute()

            # Filter bookings for this date
            bookings_today = []
            for booking in result.data:
                booking_time = datetime.fromisoformat(booking["scheduled_at"].replace('Z', '+00:00'))
                if date_start <= booking_time <= date_end:
                    bookings_today.append({
                        "start": booking_time,
                        "end": booking_time + timedelta(minutes=booking.get("duration_minutes", self.default_job_duration))
                    })

            # Sort bookings by start time
            bookings_today.sort(key=lambda x: x["start"])

            # Find gaps between bookings
            alternate_slots = []
            working_hours_start = datetime.combine(date, datetime.min.time().replace(hour=8))
            working_hours_end = datetime.combine(date, datetime.min.time().replace(hour=20))

            current_time = working_hours_start

            for booking in bookings_today:
                # Check if there's a gap before this booking
                gap_duration = (booking["start"] - current_time).total_seconds() / 60

                if gap_duration >= duration_minutes + (2 * self.default_buffer_minutes):
                    alternate_slots.append({
                        "start": current_time.isoformat(),
                        "end": (current_time + timedelta(minutes=duration_minutes)).isoformat()
                    })

                current_time = booking["end"] + timedelta(minutes=self.default_buffer_minutes)

            # Check if there's time after last booking
            if current_time < working_hours_end:
                gap_duration = (working_hours_end - current_time).total_seconds() / 60
                if gap_duration >= duration_minutes:
                    alternate_slots.append({
                        "start": current_time.isoformat(),
                        "end": (current_time + timedelta(minutes=duration_minutes)).isoformat()
                    })

            # Limit to 3 suggestions
            return alternate_slots[:3]

        except Exception as e:
            print(f"[SCHEDULING] Error suggesting alternate slots: {e}")
            return []

    async def auto_reschedule(
        self,
        booking_id: str,
        reason: str = "provider_cancelled"
    ) -> Dict:
        """
        Automatically reschedule if provider cancels.
        1. Find alternate provider
        2. If none, add to waitlist
        3. Notify user
        """
        try:
            # Get booking details
            booking_result = supabase.table("bookings").select("*").eq("id", booking_id).execute()
            if not booking_result.data:
                return {"success": False, "message": "Booking not found"}

            booking = booking_result.data[0]

            # Find alternate providers
            alternate_providers = supabase.table("providers").select("id, user_id, users(name)").eq("service_type", booking["service_type"]).eq("is_available", True).neq("id", booking["provider_id"]).limit(3).execute()

            if alternate_providers.data:
                # Try to book with first available provider
                for provider in alternate_providers.data:
                    requested_time = datetime.fromisoformat(booking["scheduled_at"].replace('Z', '+00:00'))
                    availability = await self.check_availability(
                        provider["id"],
                        requested_time,
                        booking.get("duration_minutes", self.default_job_duration)
                    )

                    if availability["available"]:
                        # Create new booking with alternate provider
                        new_booking_data = {
                            **booking,
                            "provider_id": provider["id"],
                            "status": "pending",
                            "note": f"Auto-rescheduled due to: {reason}"
                        }
                        del new_booking_data["id"]
                        del new_booking_data["created_at"]

                        new_booking = supabase.table("bookings").insert(new_booking_data).execute()

                        return {
                            "success": True,
                            "message": f"Rescheduled with {provider['users']['name']}",
                            "new_booking_id": new_booking.data[0]["id"],
                            "new_provider_name": provider["users"]["name"]
                        }

            # No alternate provider found - add to waitlist
            waitlist_data = {
                "user_id": booking["user_id"],
                "provider_id": booking["provider_id"],
                "service_type": booking["service_type"],
                "preferred_date": booking["scheduled_at"].split("T")[0],
                "status": "waiting"
            }

            supabase.table("booking_waitlist").insert(waitlist_data).execute()

            return {
                "success": False,
                "message": "No alternate provider available. Added to waitlist.",
                "waitlisted": True
            }

        except Exception as e:
            print(f"[SCHEDULING] Error in auto-reschedule: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    async def calculate_travel_time_buffer(
        self,
        provider_id: str,
        new_booking_time: datetime,
        new_booking_location: tuple
    ) -> int:
        """
        Calculate travel time from previous booking to new booking.
        Returns buffer time in minutes.
        """
        try:
            # Get previous booking before this time
            result = supabase.table("bookings").select("scheduled_at, user_lat, user_lng, duration_minutes").eq("provider_id", provider_id).in_("status", ["confirmed"]).execute()

            previous_bookings = []
            for booking in result.data:
                booking_time = datetime.fromisoformat(booking["scheduled_at"].replace('Z', '+00:00'))
                if booking_time < new_booking_time:
                    previous_bookings.append({
                        "time": booking_time,
                        "lat": booking.get("user_lat"),
                        "lng": booking.get("user_lng"),
                        "duration": booking.get("duration_minutes", self.default_job_duration)
                    })

            if not previous_bookings:
                return self.default_buffer_minutes

            # Get closest previous booking
            previous_bookings.sort(key=lambda x: x["time"], reverse=True)
            prev_booking = previous_bookings[0]

            # Calculate travel time (simplified - would use Google Routes API in production)
            if prev_booking["lat"] and prev_booking["lng"] and new_booking_location[0] and new_booking_location[1]:
                # Rough estimate: 3 minutes per km
                from math import radians, sin, cos, sqrt, atan2

                lat1, lon1 = radians(prev_booking["lat"]), radians(prev_booking["lng"])
                lat2, lon2 = radians(new_booking_location[0]), radians(new_booking_location[1])

                dlat = lat2 - lat1
                dlon = lon2 - lon1

                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distance_km = 6371 * c

                travel_time = int(distance_km * 3)  # 3 min per km
                return max(travel_time, self.default_buffer_minutes)

            return self.default_buffer_minutes

        except Exception as e:
            print(f"[SCHEDULING] Error calculating travel buffer: {e}")
            return self.default_buffer_minutes


# Singleton instance
scheduling_engine = SchedulingEngine()
