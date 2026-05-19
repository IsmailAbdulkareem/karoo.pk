import requests
import jwt
from datetime import datetime, timedelta, timezone
import uuid

# Generate a JWT
JWT_SECRET = "d2755056c68e84248f0aad37c40be2570cf5d7c0134ad5b32e9e09f7e8f29b82"

payload = {
    "user_id": "6a5170c4-8a13-486d-8ef3-f7bd57b01eb3", # Real user ID from your database
    "role": "user",
    "phone": "+923001234567",
    "exp": datetime.now(timezone.utc) + timedelta(hours=24)
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Make the request
url = "http://localhost:8000/api/chat"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "message": "mujhe karachi mein plumber chahiye",
    "conversation_history": []
}

response = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
