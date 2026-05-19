"""
Intent filter to detect casual messages vs service requests.
Prevents agent from over-executing tools on casual conversation.
"""

NEGATIVE_KEYWORDS = [
    "nahi", "no", "nai", "na", "cancel", "forget", "mat karo", "nahi chahiye",
    "band karo", "stop", "ruko", "wait", "bas", "enough"
]

CASUAL_KEYWORDS = [
    "hello", "hi", "hey", "salam", "assalam", "kia hal", "how are you",
    "kaise ho", "kya haal", "thanks", "thank you", "shukriya", "ok", "okay",
    "theek hai", "acha", "good", "great", "bye", "khuda hafiz"
]

SERVICE_KEYWORDS = [
    "plumber", "electrician", "ac", "tutor", "cleaner", "carpenter", "painter",
    "mechanic", "cook", "security", "chahiye", "need", "find", "dhoondo",
    "book", "service", "kaam", "help", "madad"
]


def is_negative_response(message: str) -> bool:
    """
    Check if message is a negative response (nahi, no, cancel, etc.)
    """
    message_lower = message.lower().strip()
    return any(keyword in message_lower for keyword in NEGATIVE_KEYWORDS)


def is_casual_message(message: str) -> bool:
    """
    Check if message is casual conversation (hello, how are you, etc.)
    """
    message_lower = message.lower().strip()

    # Check if it's a casual greeting
    if any(keyword in message_lower for keyword in CASUAL_KEYWORDS):
        # Make sure it's not also asking for a service
        has_service_intent = any(keyword in message_lower for keyword in SERVICE_KEYWORDS)
        return not has_service_intent

    return False


def should_search_providers(message: str) -> bool:
    """
    Determine if agent should search for providers based on message.
    Returns True only if message clearly requests a service.
    """
    message_lower = message.lower().strip()

    # Negative response - don't search
    if is_negative_response(message_lower):
        return False

    # Casual message - don't search
    if is_casual_message(message_lower):
        return False

    # Check if message has service intent
    has_service_keyword = any(keyword in message_lower for keyword in SERVICE_KEYWORDS)

    return has_service_keyword
