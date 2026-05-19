from datetime import datetime, time
from typing import Dict, Optional

# Base rates per service type (in PKR)
SERVICE_BASE_RATES = {
    "plumber": 500,
    "electrician": 600,
    "ac_technician": 800,
    "tutor": 400,
    "cleaner": 300,
    "carpenter": 700,
    "painter": 500,
    "mechanic": 900,
    "cook": 350,
    "security_guard": 400
}

# Distance rate per km
DISTANCE_RATE_PER_KM = 10

# Urgency multipliers
URGENCY_MULTIPLIERS = {
    "normal": 0.0,      # No extra charge
    "urgent": 0.3,      # +30%
    "emergency": 0.5    # +50%
}

# Complexity multipliers
COMPLEXITY_MULTIPLIERS = {
    "basic": 0.0,           # No extra charge
    "intermediate": 0.2,    # +20%
    "complex": 0.4          # +40%
}

# Peak hours: 8-10 AM and 5-8 PM
PEAK_HOURS = [
    (time(8, 0), time(10, 0)),
    (time(17, 0), time(20, 0))
]

SURGE_MULTIPLIER = 1.5


class PricingEngine:
    """
    Dynamic pricing engine for Karoo service bookings.
    Calculates transparent, fair pricing based on multiple factors.
    """

    def __init__(self):
        pass

    def is_peak_hour(self, scheduled_time: Optional[datetime] = None) -> bool:
        """
        Check if the scheduled time falls within peak hours.
        """
        if not scheduled_time:
            scheduled_time = datetime.now()

        current_time = scheduled_time.time()

        for start, end in PEAK_HOURS:
            if start <= current_time <= end:
                return True

        return False

    def calculate_loyalty_discount(self, user_loyalty_level: int) -> float:
        """
        Calculate loyalty discount percentage.
        5% per level, max 20%
        """
        return min(user_loyalty_level * 0.05, 0.20)

    def calculate_price(
        self,
        service_type: str,
        complexity: str = "basic",
        distance_km: float = 0.0,
        urgency: str = "normal",
        provider_rate: Optional[int] = None,
        user_loyalty_level: int = 0,
        scheduled_time: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate dynamic price with transparent breakdown.

        Args:
            service_type: Type of service (plumber, electrician, etc.)
            complexity: Job complexity (basic, intermediate, complex)
            distance_km: Distance from provider to user in kilometers
            urgency: Urgency level (normal, urgent, emergency)
            provider_rate: Provider's custom rate (overrides base rate)
            user_loyalty_level: User's loyalty level (0-4)
            scheduled_time: When the service is scheduled

        Returns:
            Dict with price breakdown and final price
        """
        # 1. Base price
        base_price = provider_rate if provider_rate else SERVICE_BASE_RATES.get(service_type, 500)

        # 2. Distance fee
        distance_fee = int(distance_km * DISTANCE_RATE_PER_KM)

        # 3. Urgency fee
        urgency_multiplier = URGENCY_MULTIPLIERS.get(urgency, 0.0)
        urgency_fee = int(base_price * urgency_multiplier)

        # 4. Complexity fee
        complexity_multiplier = COMPLEXITY_MULTIPLIERS.get(complexity, 0.0)
        complexity_fee = int(base_price * complexity_multiplier)

        # 5. Surge pricing (peak hours)
        is_peak = self.is_peak_hour(scheduled_time)
        surge_multiplier = SURGE_MULTIPLIER if is_peak else 1.0

        # 6. Calculate subtotal before discount
        subtotal = int((base_price + distance_fee + urgency_fee + complexity_fee) * surge_multiplier)

        # 7. Loyalty discount
        loyalty_discount_percent = self.calculate_loyalty_discount(user_loyalty_level)
        loyalty_discount = int(subtotal * loyalty_discount_percent)

        # 8. Final price
        final_price = subtotal - loyalty_discount

        # 9. Build breakdown text
        breakdown_parts = [
            f"Base Rate: Rs.{base_price}"
        ]

        if distance_fee > 0:
            breakdown_parts.append(f"Distance ({distance_km:.1f}km): Rs.{distance_fee}")

        if urgency_fee > 0:
            breakdown_parts.append(f"Urgency ({urgency}): Rs.{urgency_fee}")

        if complexity_fee > 0:
            breakdown_parts.append(f"Complexity ({complexity}): Rs.{complexity_fee}")

        if is_peak:
            surge_amount = subtotal - int((base_price + distance_fee + urgency_fee + complexity_fee))
            breakdown_parts.append(f"Peak Hour Surge (1.5x): Rs.{surge_amount}")

        if loyalty_discount > 0:
            breakdown_parts.append(f"Loyalty Discount ({int(loyalty_discount_percent * 100)}%): -Rs.{loyalty_discount}")

        breakdown_text = "\n".join(breakdown_parts)
        breakdown_text += f"\n\nTotal: Rs.{final_price}"

        return {
            "base_price": base_price,
            "distance_fee": distance_fee,
            "urgency_fee": urgency_fee,
            "complexity_fee": complexity_fee,
            "surge_multiplier": surge_multiplier,
            "is_peak_hour": is_peak,
            "loyalty_discount": loyalty_discount,
            "subtotal": subtotal,
            "final_price": final_price,
            "breakdown_text": breakdown_text,
            "breakdown": {
                "base_price": base_price,
                "distance_fee": distance_fee,
                "urgency_fee": urgency_fee,
                "complexity_fee": complexity_fee,
                "surge_multiplier": surge_multiplier,
                "loyalty_discount": loyalty_discount,
                "final_price": final_price
            }
        }

    def estimate_price_range(
        self,
        service_type: str,
        distance_km: float = 5.0
    ) -> Dict:
        """
        Estimate price range for a service (min to max).
        Useful for showing users expected price before booking.
        """
        # Minimum: basic job, normal urgency, no surge
        min_price = self.calculate_price(
            service_type=service_type,
            complexity="basic",
            distance_km=distance_km,
            urgency="normal",
            user_loyalty_level=0,
            scheduled_time=datetime(2026, 5, 19, 12, 0)  # Non-peak hour
        )

        # Maximum: complex job, emergency, peak hour
        max_price = self.calculate_price(
            service_type=service_type,
            complexity="complex",
            distance_km=distance_km,
            urgency="emergency",
            user_loyalty_level=0,
            scheduled_time=datetime(2026, 5, 19, 18, 0)  # Peak hour
        )

        return {
            "min_price": min_price["final_price"],
            "max_price": max_price["final_price"],
            "range_text": f"Rs.{min_price['final_price']} - Rs.{max_price['final_price']}"
        }


# Singleton instance
pricing_engine = PricingEngine()


# Helper function for easy import
def calculate_booking_price(
    service_type: str,
    complexity: str = "basic",
    distance_km: float = 0.0,
    urgency: str = "normal",
    provider_rate: Optional[int] = None,
    user_loyalty_level: int = 0,
    scheduled_time: Optional[datetime] = None
) -> Dict:
    """
    Calculate price for a booking.
    Wrapper around PricingEngine.calculate_price()
    """
    return pricing_engine.calculate_price(
        service_type=service_type,
        complexity=complexity,
        distance_km=distance_km,
        urgency=urgency,
        provider_rate=provider_rate,
        user_loyalty_level=user_loyalty_level,
        scheduled_time=scheduled_time
    )
