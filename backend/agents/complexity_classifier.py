from typing import Dict, List
import re


class ComplexityClassifier:
    """
    Classifies service jobs as basic, intermediate, or complex.
    Used for better provider matching and pricing.
    """

    def __init__(self):
        # Keywords that indicate complexity
        self.complex_keywords = {
            "plumber": ["installation", "pipe replacement", "sewer", "main line", "water heater install"],
            "electrician": ["rewiring", "panel upgrade", "circuit installation", "outdoor wiring", "generator"],
            "ac_technician": ["installation", "compressor", "refrigerant", "duct work", "central ac"],
            "carpenter": ["custom furniture", "staircase", "deck building", "framing", "structural"],
            "painter": ["exterior", "multi-story", "textured", "commercial", "industrial"],
            "mechanic": ["engine", "transmission", "major repair", "overhaul", "rebuild"],
            "tutor": ["advanced", "university", "exam prep", "multiple subjects", "special needs"],
            "cleaner": ["deep clean", "post-construction", "industrial", "carpet shampooing", "window cleaning"],
            "cook": ["catering", "event", "multiple courses", "special diet", "large party"],
            "security_guard": ["armed", "night shift", "event security", "multiple locations", "high risk"]
        }

        self.intermediate_keywords = {
            "plumber": ["leak repair", "drain cleaning", "faucet replacement", "toilet repair"],
            "electrician": ["outlet installation", "light fixture", "ceiling fan", "switch replacement"],
            "ac_technician": ["servicing", "gas refill", "filter replacement", "thermostat"],
            "carpenter": ["door installation", "cabinet repair", "shelf installation", "minor repairs"],
            "painter": ["single room", "touch up", "interior walls", "small area"],
            "mechanic": ["oil change", "brake service", "tire replacement", "battery"],
            "tutor": ["high school", "homework help", "test prep", "single subject"],
            "cleaner": ["regular cleaning", "bathroom", "kitchen", "dusting", "mopping"],
            "cook": ["daily meals", "home cooking", "simple dishes", "meal prep"],
            "security_guard": ["day shift", "residential", "office", "standard patrol"]
        }

    def classify_job(
        self,
        service_type: str,
        description: str = "",
        urgency: str = "normal",
        location_type: str = "residential"
    ) -> Dict:
        """
        Classify job as basic/intermediate/complex.

        Args:
            service_type: Type of service
            description: Job description from user
            urgency: Urgency level
            location_type: residential, commercial, industrial

        Returns:
            {
                "complexity": "basic|intermediate|complex",
                "factors": ["reason1", "reason2"],
                "recommended_experience": 2,
                "estimated_duration": 90,
                "requires_tools": ["tool1", "tool2"],
                "requires_certification": false
            }
        """
        description_lower = description.lower()
        complexity_score = 0
        factors = []

        # Check for complex keywords
        complex_kw = self.complex_keywords.get(service_type, [])
        for keyword in complex_kw:
            if keyword in description_lower:
                complexity_score += 2
                factors.append(f"complex_task: {keyword}")

        # Check for intermediate keywords
        intermediate_kw = self.intermediate_keywords.get(service_type, [])
        for keyword in intermediate_kw:
            if keyword in description_lower:
                complexity_score += 1
                factors.append(f"intermediate_task: {keyword}")

        # Emergency jobs are typically more complex
        if urgency == "emergency":
            complexity_score += 1
            factors.append("emergency_urgency")

        # Commercial/industrial locations add complexity
        if location_type in ["commercial", "industrial"]:
            complexity_score += 1
            factors.append(f"{location_type}_location")

        # Check for quantity indicators (multiple items = more complex)
        quantity_patterns = [
            r'\d+\s+(rooms?|floors?|units?|items?|pieces?)',
            r'(multiple|several|many|all)',
            r'(entire|whole|complete)'
        ]
        for pattern in quantity_patterns:
            if re.search(pattern, description_lower):
                complexity_score += 1
                factors.append("multiple_items")
                break

        # Determine final complexity
        if complexity_score >= 3:
            complexity = "complex"
            recommended_experience = 5
            estimated_duration = 180
            requires_certification = True
        elif complexity_score >= 1:
            complexity = "intermediate"
            recommended_experience = 2
            estimated_duration = 90
            requires_certification = False
        else:
            complexity = "basic"
            recommended_experience = 0
            estimated_duration = 60
            requires_certification = False

        # Determine required tools based on service type and complexity
        required_tools = self._get_required_tools(service_type, complexity)

        return {
            "complexity": complexity,
            "factors": factors,
            "recommended_experience": recommended_experience,
            "estimated_duration": estimated_duration,
            "requires_tools": required_tools,
            "requires_certification": requires_certification,
            "complexity_score": complexity_score
        }

    def _get_required_tools(self, service_type: str, complexity: str) -> List[str]:
        """
        Get list of required tools based on service type and complexity.
        """
        tool_requirements = {
            "plumber": {
                "basic": ["wrench", "plunger"],
                "intermediate": ["pipe wrench", "snake", "torch"],
                "complex": ["pipe cutter", "threading machine", "pressure tester"]
            },
            "electrician": {
                "basic": ["screwdriver", "wire stripper", "multimeter"],
                "intermediate": ["drill", "fish tape", "voltage tester"],
                "complex": ["conduit bender", "cable puller", "thermal camera"]
            },
            "ac_technician": {
                "basic": ["screwdriver", "wrench"],
                "intermediate": ["manifold gauge", "vacuum pump", "leak detector"],
                "complex": ["recovery machine", "brazing torch", "micron gauge"]
            },
            "carpenter": {
                "basic": ["hammer", "saw", "measuring tape"],
                "intermediate": ["power drill", "circular saw", "level"],
                "complex": ["table saw", "miter saw", "router", "nail gun"]
            },
            "painter": {
                "basic": ["brush", "roller", "tray"],
                "intermediate": ["ladder", "drop cloths", "sprayer"],
                "complex": ["scaffolding", "airless sprayer", "safety equipment"]
            },
            "mechanic": {
                "basic": ["wrench set", "jack", "oil pan"],
                "intermediate": ["socket set", "torque wrench", "diagnostic scanner"],
                "complex": ["engine hoist", "transmission jack", "specialty tools"]
            }
        }

        return tool_requirements.get(service_type, {}).get(complexity, [])

    def match_provider_to_complexity(
        self,
        job_complexity: str,
        provider_experience: int,
        provider_specializations: List[str],
        provider_certifications: List[str],
        provider_tools: List[str],
        required_tools: List[str]
    ) -> Dict:
        """
        Calculate how well a provider matches the job complexity.

        Returns:
            {
                "match_score": 0.0-1.0,
                "can_handle": true/false,
                "missing_requirements": [],
                "recommendation": "perfect|good|acceptable|not_recommended"
            }
        """
        match_score = 1.0
        missing_requirements = []
        can_handle = True

        # Check experience requirement
        experience_requirements = {
            "basic": 0,
            "intermediate": 2,
            "complex": 5
        }

        required_experience = experience_requirements.get(job_complexity, 0)
        if provider_experience < required_experience:
            experience_gap = required_experience - provider_experience
            match_score -= (experience_gap * 0.15)
            missing_requirements.append(f"needs {experience_gap} more years experience")
            if experience_gap > 2:
                can_handle = False

        # Check tools
        if required_tools:
            missing_tools = [tool for tool in required_tools if tool not in provider_tools]
            if missing_tools:
                tool_penalty = len(missing_tools) * 0.1
                match_score -= tool_penalty
                missing_requirements.append(f"missing tools: {', '.join(missing_tools)}")
                if len(missing_tools) > 2:
                    can_handle = False

        # Check certifications for complex jobs
        if job_complexity == "complex" and not provider_certifications:
            match_score -= 0.2
            missing_requirements.append("no certifications")

        # Ensure score is between 0 and 1
        match_score = max(0.0, min(1.0, match_score))

        # Determine recommendation
        if match_score >= 0.9:
            recommendation = "perfect"
        elif match_score >= 0.7:
            recommendation = "good"
        elif match_score >= 0.5:
            recommendation = "acceptable"
        else:
            recommendation = "not_recommended"

        return {
            "match_score": round(match_score, 2),
            "can_handle": can_handle,
            "missing_requirements": missing_requirements,
            "recommendation": recommendation
        }


# Singleton instance
complexity_classifier = ComplexityClassifier()


# Helper function for easy import
def classify_job_complexity(
    service_type: str,
    description: str = "",
    urgency: str = "normal",
    location_type: str = "residential"
) -> Dict:
    """
    Classify a job's complexity.
    Wrapper around ComplexityClassifier.classify_job()
    """
    return complexity_classifier.classify_job(
        service_type=service_type,
        description=description,
        urgency=urgency,
        location_type=location_type
    )
