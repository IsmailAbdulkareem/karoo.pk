"""
Context extractor to help agent remember service_type and location from conversation history.
"""
import re
from typing import Dict, Optional, List

# Service type mappings (handle variations)
SERVICE_MAPPINGS = {
    "plumber": ["plumber", "plumbing", "pipe", "paani", "water"],
    "electrician": ["electrician", "electric", "bijli", "light", "wiring", "electrition", "electricion"],
    "ac_technician": ["ac", "air conditioner", "cooling", "thanda"],
    "tutor": ["tutor", "teacher", "parhai", "study"],
    "cleaner": ["cleaner", "cleaning", "safai"],
    "carpenter": ["carpenter", "wood", "furniture", "lakri"],
    "painter": ["painter", "paint", "rang"],
    "mechanic": ["mechanic", "car", "gaari"],
    "cook": ["cook", "cooking", "khana"],
    "security_guard": ["security", "guard", "chowkidar"]
}

# Common location patterns
LOCATION_PATTERNS = [
    r'\b[FGE]-\d+\b',  # F-10, G-11, E-7
    r'\bDHA\b',
    r'\bBahria\b',
    r'\bGulberg\b',
    r'\bJohar\b',
    r'\bKarachi\b',
    r'\bIslamabad\b',
    r'\bLahore\b',
    r'\bRawalpindi\b',
    r'\bPeshawar\b',
    r'\bQuetta\b',
    r'\bFaisalabad\b',
    r'\bMultan\b'
]


def extract_service_type(text: str) -> Optional[str]:
    """
    Extract service type from text using fuzzy matching.
    """
    text_lower = text.lower()

    for service, keywords in SERVICE_MAPPINGS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return service

    return None


def extract_location(text: str) -> Optional[str]:
    """
    Extract location from text using regex patterns.
    """
    for pattern in LOCATION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)

    return None


def extract_slots_from_history(conversation_history: List[Dict[str, str]]) -> Dict[str, Optional[str]]:
    """
    Extract service_type and location from entire conversation history.
    Returns dict with 'service_type' and 'location' keys.
    """
    service_type = None
    location = None

    # Scan all messages (newest first for recency)
    for msg in reversed(conversation_history):
        content = msg.get("content", "")

        # Extract service type if not found yet
        if not service_type:
            service_type = extract_service_type(content)

        # Extract location if not found yet
        if not location:
            location = extract_location(content)

        # Stop if both found
        if service_type and location:
            break

    return {
        "service_type": service_type,
        "location": location
    }


def build_context_summary(slots: Dict[str, Optional[str]]) -> str:
    """
    Build a context summary string for the agent.
    """
    parts = []

    if slots.get("service_type"):
        parts.append(f"Service needed: {slots['service_type']}")

    if slots.get("location"):
        parts.append(f"Location: {slots['location']}")

    if parts:
        return "EXTRACTED FROM HISTORY: " + " | ".join(parts)

    return "No service or location found in history yet."
