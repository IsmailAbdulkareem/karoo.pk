from pydantic import BaseModel, Field
from typing import Optional, List

# ============================================
# AUTH MODELS
# ============================================

class UserRegister(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    password: str
    city: Optional[str] = None
    role: str = "user"

class UserLogin(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str

# ============================================
# CHAT MODELS
# ============================================

class ChatRequest(BaseModel):
    message: str
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None

class ParsedIntent(BaseModel):
    service_type: Optional[str] = None
    location: Optional[str] = None
    time: Optional[str] = None
    confidence: float = 0.0
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

class ProviderResult(BaseModel):
    id: str
    name: str
    service_type: str
    area: str
    rating: float
    rate_per_hour: Optional[int] = None
    is_available: bool
    bio: Optional[str] = None
    eta_minutes: Optional[int] = None
    match_score: Optional[float] = None

class ChatResponse(BaseModel):
    reply: str
    intent: Optional[ParsedIntent] = None
    providers: List[ProviderResult] = []
    needs_clarification: bool = False
    agent_trace: str = ""

# ============================================
# BOOKING MODELS
# ============================================

class BookingCreate(BaseModel):
    provider_id: str
    service_type: str
    location: str
    scheduled_at: str
    note: Optional[str] = None
    booked_via: str = "browse"
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None
    eta_minutes: Optional[int] = None

class BookingStatusUpdate(BaseModel):
    status: str

# ============================================
# PROVIDER MODELS
# ============================================

class ProviderUpdate(BaseModel):
    service_type: Optional[str] = None
    area: Optional[str] = None
    rate_per_hour: Optional[int] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None
    is_online: Optional[bool] = None

# ============================================
# SERVICE REQUEST MODELS
# ============================================

class ServiceRequestCreate(BaseModel):
    service_type: str
    location: str
    scheduled_at: Optional[str] = None
    budget: Optional[int] = None
    description: Optional[str] = None

# ============================================
# RATING MODELS
# ============================================

class RatingCreate(BaseModel):
    booking_id: str
    ratee_id: str
    stars: int = Field(ge=1, le=5)
    review_text: Optional[str] = None
    tags: Optional[List[str]] = []

class RatingResponse(BaseModel):
    id: str
    stars: int
    review_text: Optional[str] = None
    tags: List[str]
    rater_role: str
    created_at: str

# ============================================
# NOTIFICATION MODELS
# ============================================

class NotificationItem(BaseModel):
    id: str
    title: str
    body: str
    type: str
    is_read: bool
    created_at: str
