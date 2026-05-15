from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    PROVIDER = "provider"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    EN_ROUTE = "en_route"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class UserCreate(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    password: str
    city: Optional[str] = None

class UserLogin(BaseModel):
    phone: str
    password: str

class ProviderCreate(BaseModel):
    name: str
    phone: str
    service_type: str
    area: str
    rate_per_hour: int
    bio: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    user_id: str
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None

class BookingCreate(BaseModel):
    provider_id: str
    service_type: str
    location: str
    user_lat: float
    user_lng: float
    scheduled_at: datetime
    note: Optional[str] = None

class RatingCreate(BaseModel):
    booking_id: str
    ratee_id: str
    stars: int = Field(ge=1, le=5)
    review_text: Optional[str] = None
    tags: Optional[List[str]] = None
