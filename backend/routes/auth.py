from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from models.schemas import UserRegister, UserLogin, TokenResponse
from db.supabase_client import supabase
from utils.jwt_handler import create_token, get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """
    Register a new user or provider.
    If role=provider, also creates a provider record.
    """
    try:
        # Check if phone already exists
        existing = supabase.table("users").select("id").eq("phone", user.phone).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Yeh phone already registered hai")

        # Hash password (truncate to 72 bytes for bcrypt)
        password_hash = pwd_context.hash(user.password[:72])

        # Insert user
        user_data = {
            "name": user.name,
            "phone": user.phone,
            "email": user.email,
            "password_hash": password_hash,
            "city": user.city,
            "role": user.role
        }
        result = supabase.table("users").insert(user_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="User create nahi hua")

        user_id = result.data[0]["id"]

        # If provider, create provider record
        if user.role == "provider":
            provider_data = {
                "user_id": user_id,
                "service_type": "",
                "area": "",
                "is_available": False
            }
            supabase.table("providers").insert(provider_data).execute()

        # Create JWT token
        token = create_token(user_id, user.role)

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role=user.role,
            user_id=user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with phone and password.
    Returns JWT token.
    """
    try:
        # Query user by phone
        result = supabase.table("users").select("*").eq("phone", credentials.phone).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="User nahi mila")

        user = result.data[0]

        # Verify password
        if not pwd_context.verify(credentials.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Password galat hai")

        # Create JWT token
        token = create_token(user["id"], user["role"])

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role=user["role"],
            user_id=user["id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile (protected endpoint).
    """
    try:
        result = supabase.table("users").select("*").eq("id", current_user["user_id"]).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="User nahi mila")

        user = result.data[0]
        # Remove password_hash from response
        user.pop("password_hash", None)

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
