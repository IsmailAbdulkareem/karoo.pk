from typing import Dict, Optional
from datetime import datetime, timedelta

class DisputeResolver:
    """
    Automatic dispute resolution engine for Karoo.
    Handles common dispute scenarios with fair, transparent logic.
    """

    def __init__(self):
        pass

    async def auto_resolve(
        self,
        dispute: Dict,
        booking: Dict,
        provider_history: Dict,
        user_history: Dict
    ) -> Dict:
        """
        Automatically resolve disputes based on type and context.

        Args:
            dispute: Dispute details (type, description, etc.)
            booking: Booking details (price, time, status, etc.)
            provider_history: Provider's rating, completion rate, etc.
            user_history: User's reliability score, booking count, etc.

        Returns:
            Resolution decision with refund/compensation amounts
        """
        dispute_type = dispute["dispute_type"]

        if dispute_type == "no_show":
            return await self._resolve_no_show(dispute, booking, provider_history)

        elif dispute_type == "quality_issue":
            return await self._resolve_quality_issue(dispute, booking, provider_history)

        elif dispute_type == "price_disagreement":
            return await self._resolve_price_disagreement(dispute, booking)

        elif dispute_type == "time_overrun":
            return await self._resolve_time_overrun(dispute, booking)

        elif dispute_type == "unprofessional_behavior":
            return await self._resolve_unprofessional_behavior(dispute, booking, provider_history)

        else:
            # Complex cases escalate to human review
            return {
                "status": "escalated",
                "resolution": "This case requires human review. Our team will contact you within 24 hours.",
                "refund_amount": 0,
                "compensation_amount": 0,
                "requires_human_review": True
            }

    async def _resolve_no_show(
        self,
        dispute: Dict,
        booking: Dict,
        provider_history: Dict
    ) -> Dict:
        """
        Resolve no-show disputes.

        Logic:
        - If provider marked as en-route but never arrived: full refund to user
        - If provider has history of no-shows: full refund + warning
        - If first offense and valid reason: partial refund
        """
        raised_by = dispute["raised_by_role"]
        final_price = booking.get("final_price", booking.get("agreed_rate", 0))

        if raised_by == "user":
            # User claims provider didn't show up
            provider_rating = provider_history.get("rating", 5.0)
            provider_completion_rate = provider_history.get("completion_rate", 1.0)

            if provider_completion_rate < 0.8:
                # Provider has history of not completing jobs
                return {
                    "status": "resolved",
                    "resolution": "Full refund issued. Provider has been warned for repeated no-shows.",
                    "refund_amount": final_price,
                    "compensation_amount": int(final_price * 0.1),  # 10% compensation
                    "action_taken": "provider_warned"
                }
            else:
                # First offense or good history
                return {
                    "status": "resolved",
                    "resolution": "Full refund issued. We apologize for the inconvenience.",
                    "refund_amount": final_price,
                    "compensation_amount": 0,
                    "action_taken": "refund_only"
                }

        else:
            # Provider claims user wasn't available
            user_reliability = provider_history.get("reliability_score", 5.0)

            if user_reliability < 3.0:
                # User has history of not being available
                return {
                    "status": "resolved",
                    "resolution": "No refund. User has been warned for repeated unavailability.",
                    "refund_amount": 0,
                    "compensation_amount": int(final_price * 0.5),  # 50% compensation to provider
                    "action_taken": "user_warned"
                }
            else:
                # Benefit of doubt to user
                return {
                    "status": "escalated",
                    "resolution": "This case requires verification. Please provide proof of arrival.",
                    "refund_amount": 0,
                    "compensation_amount": 0,
                    "requires_human_review": True
                }

    async def _resolve_quality_issue(
        self,
        dispute: Dict,
        booking: Dict,
        provider_history: Dict
    ) -> Dict:
        """
        Resolve quality-related disputes.

        Logic:
        - If provider has low rating (<3.5): partial refund
        - If first complaint: warning only
        - If repeated complaints: refund + suspension consideration
        """
        provider_rating = provider_history.get("rating", 5.0)
        total_ratings = provider_history.get("total_ratings", 0)
        final_price = booking.get("final_price", booking.get("agreed_rate", 0))

        if provider_rating < 3.5 and total_ratings > 5:
            # Provider has consistently low ratings
            return {
                "status": "resolved",
                "resolution": "Partial refund issued due to quality concerns. Provider will be reviewed.",
                "refund_amount": int(final_price * 0.5),  # 50% refund
                "compensation_amount": 0,
                "action_taken": "provider_review_scheduled"
            }

        elif total_ratings < 5:
            # New provider, give benefit of doubt
            return {
                "status": "resolved",
                "resolution": "We've noted your feedback. Provider has been notified to improve service quality.",
                "refund_amount": int(final_price * 0.25),  # 25% goodwill refund
                "compensation_amount": 0,
                "action_taken": "provider_notified"
            }

        else:
            # Established provider with good history
            return {
                "status": "investigating",
                "resolution": "We're investigating this issue. Provider will contact you to resolve the matter.",
                "refund_amount": 0,
                "compensation_amount": 0,
                "action_taken": "investigation_started"
            }

    async def _resolve_price_disagreement(
        self,
        dispute: Dict,
        booking: Dict
    ) -> Dict:
        """
        Resolve price disagreement disputes.

        Logic:
        - If surge not disclosed: refund difference
        - If price breakdown available: show transparency
        - If significant overcharge: full refund
        """
        final_price = booking.get("final_price", 0)
        agreed_rate = booking.get("agreed_rate", 0)
        price_breakdown = booking.get("price_breakdown", {})
        surge_multiplier = booking.get("surge_multiplier", 1.0)

        if surge_multiplier > 1.0 and not price_breakdown:
            # Surge applied but not disclosed
            surge_amount = final_price - (final_price / surge_multiplier)
            return {
                "status": "resolved",
                "resolution": "Surge pricing was not properly disclosed. Refunding surge amount.",
                "refund_amount": int(surge_amount),
                "compensation_amount": 0,
                "action_taken": "surge_refunded"
            }

        elif final_price > agreed_rate * 1.5:
            # Significant overcharge
            overcharge = final_price - agreed_rate
            return {
                "status": "resolved",
                "resolution": "Price exceeded agreed rate significantly. Refunding difference.",
                "refund_amount": overcharge,
                "compensation_amount": 0,
                "action_taken": "overcharge_refunded"
            }

        else:
            # Price seems fair, show breakdown
            return {
                "status": "resolved",
                "resolution": f"Price breakdown: {price_breakdown}. All charges were disclosed upfront.",
                "refund_amount": 0,
                "compensation_amount": 0,
                "action_taken": "breakdown_provided"
            }

    async def _resolve_time_overrun(
        self,
        dispute: Dict,
        booking: Dict
    ) -> Dict:
        """
        Resolve time overrun disputes.

        Logic:
        - >30min late: 10% discount
        - >1hr late: 25% discount
        - >2hr late: 50% discount
        """
        description = dispute.get("description", "").lower()
        final_price = booking.get("final_price", booking.get("agreed_rate", 0))

        # Try to extract delay duration from description
        if "2 hour" in description or "2hr" in description or "120 min" in description:
            delay_minutes = 120
        elif "1 hour" in description or "1hr" in description or "60 min" in description:
            delay_minutes = 60
        elif "30 min" in description or "half hour" in description:
            delay_minutes = 30
        else:
            # Default to moderate delay
            delay_minutes = 45

        if delay_minutes >= 120:
            discount_percent = 0.5
            message = "Provider was over 2 hours late. 50% discount applied."
        elif delay_minutes >= 60:
            discount_percent = 0.25
            message = "Provider was over 1 hour late. 25% discount applied."
        elif delay_minutes >= 30:
            discount_percent = 0.10
            message = "Provider was over 30 minutes late. 10% discount applied."
        else:
            discount_percent = 0.0
            message = "Minor delay noted. No refund applicable for delays under 30 minutes."

        refund = int(final_price * discount_percent)

        return {
            "status": "resolved",
            "resolution": message,
            "refund_amount": refund,
            "compensation_amount": 0,
            "action_taken": "late_penalty_applied"
        }

    async def _resolve_unprofessional_behavior(
        self,
        dispute: Dict,
        booking: Dict,
        provider_history: Dict
    ) -> Dict:
        """
        Resolve unprofessional behavior disputes.

        Logic:
        - Serious cases: immediate escalation
        - Minor cases: warning + partial refund
        """
        description = dispute.get("description", "").lower()
        final_price = booking.get("final_price", booking.get("agreed_rate", 0))

        # Check for serious keywords
        serious_keywords = ["harassment", "threat", "abuse", "unsafe", "danger", "assault"]
        is_serious = any(keyword in description for keyword in serious_keywords)

        if is_serious:
            # Serious case - immediate escalation and full refund
            return {
                "status": "escalated",
                "resolution": "This is a serious matter. Full refund issued. Our team will contact you immediately.",
                "refund_amount": final_price,
                "compensation_amount": int(final_price * 0.2),  # 20% compensation
                "action_taken": "provider_suspended_pending_investigation",
                "requires_human_review": True,
                "priority": "urgent"
            }
        else:
            # Minor unprofessional behavior
            return {
                "status": "resolved",
                "resolution": "We apologize for the unprofessional behavior. Provider has been warned.",
                "refund_amount": int(final_price * 0.3),  # 30% refund
                "compensation_amount": 0,
                "action_taken": "provider_warned"
            }

    def should_blacklist(
        self,
        user_id: str,
        dispute_history: list
    ) -> bool:
        """
        Determine if a user/provider should be blacklisted.

        Criteria:
        - 3+ disputes in 30 days
        - 2+ serious violations
        - Pattern of fraudulent behavior
        """
        if len(dispute_history) >= 3:
            # Check if disputes are within 30 days
            recent_disputes = [
                d for d in dispute_history
                if (datetime.now() - datetime.fromisoformat(d["created_at"])).days <= 30
            ]

            if len(recent_disputes) >= 3:
                return True

        # Check for serious violations
        serious_disputes = [
            d for d in dispute_history
            if d.get("dispute_type") in ["unprofessional_behavior", "safety_concern"]
        ]

        if len(serious_disputes) >= 2:
            return True

        return False


# Singleton instance
dispute_resolver = DisputeResolver()
