from fastapi import APIRouter, HTTPException, Depends
from models.schemas import UserCreate, UserLogin, ProviderCreate
from db.supabase_client import supabase
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register_user(user: UserCreate):
    """Register a new user"""
    # TODO: Implement user registration with Supabase
    # TODO: Send OTP for phone verification
    return {"message": "User registration endpoint - to be implemented"}

@router.post("/login")
async def login(credentials: UserLogin):
    """Login user and return JWT token"""
    # TODO: Implement login with phone + password
    # TODO: Verify credentials against Supabase
    # TODO: Return JWT token
    return {"message": "Login endpoint - to be implemented"}

@router.post("/provider/register")
async def register_provider(provider: ProviderCreate):
    """Register a new service provider"""
    # TODO: Implement provider registration
    # TODO: Geocode provider area using Google Geocoding API
    # TODO: Store lat/lng coordinates
    return {"message": "Provider registration endpoint - to be implemented"}

@router.post("/verify-otp")
async def verify_otp(phone: str, otp: str):
    """Verify phone OTP"""
    # TODO: Implement OTP verification with Supabase Auth
    return {"message": "OTP verification endpoint - to be implemented"}
