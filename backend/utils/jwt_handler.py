import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET")
EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", 24))
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_token(user_id: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=EXPIRE_HOURS)
    payload = {"user_id": user_id, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token galat ya expire ho gaya")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return verify_token(token)
