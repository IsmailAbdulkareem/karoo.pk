# Karoo Backend — Step by Step Spec

> Paste ONE step at a time into Claude Code.
> Wait for it to finish + test before moving to next step.

---

# STEP 1 — Project Setup + Base Files

## Context
Karoo is an AI-powered service booking app for Pakistan's informal economy.
Backend: FastAPI (Python), Database: Supabase, AI: Gemini API.

## Task
Set up the base FastAPI project. Do NOT write any route logic yet.

## Create these files exactly:

### File: main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Karoo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "Karoo API running", "version": "1.0.0"}
```

### File: requirements.txt
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
supabase==2.9.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
requests==2.32.3
python-dotenv==1.0.1
pydantic==2.9.2
pydantic-settings==2.6.0
google-generativeai==0.8.3
httpx==0.27.0
```

### File: .env.example
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
JWT_SECRET=your-random-secret-key
JWT_EXPIRE_HOURS=24
```

### Folder structure to create (empty __init__.py in each):
```
routes/
agents/
mcp/
mcp/tools/
db/
utils/
models/
```

## After creating:
Run: uvicorn main:app --reload
Test: GET http://localhost:8000/ must return {"status": "Karoo API running"}

---

# STEP 2 — Supabase Client + All Schemas

## Context
This step creates the database connection and ALL Pydantic models.
No routes yet — just connection and data models.

## Task
Create db/supabase_client.py and models/schemas.py

### File: db/supabase_client.py
```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
```

### File: models/schemas.py
Create ALL these Pydantic models:

AUTH MODELS:
- UserRegister: name(str), phone(str), email(Optional[str]), password(str), city(Optional[str]), role(str="user")
- UserLogin: phone(str), password(str)
- TokenResponse: access_token(str), token_type(str="bearer"), role(str), user_id(str)

CHAT MODELS:
- ChatRequest: message(str), user_lat(Optional[float]), user_lng(Optional[float])
- ParsedIntent: service_type(Optional[str]), location(Optional[str]), time(Optional[str]), confidence(float=0.0), location_lat(Optional[float]), location_lng(Optional[float])
- ProviderResult: id(str), name(str), service_type(str), area(str), rating(float), rate_per_hour(Optional[int]), is_available(bool), bio(Optional[str]), eta_minutes(Optional[int]), match_score(Optional[float])
- ChatResponse: reply(str), intent(Optional[ParsedIntent]), providers(List[ProviderResult]=list), needs_clarification(bool=False), agent_trace(str="")

BOOKING MODELS:
- BookingCreate: provider_id(str), service_type(str), location(str), scheduled_at(str), note(Optional[str]), booked_via(str="browse"), user_lat(Optional[float]), user_lng(Optional[float]), eta_minutes(Optional[int])
- BookingStatusUpdate: status(str)

PROVIDER MODELS:
- ProviderUpdate: service_type(Optional[str]), area(Optional[str]), rate_per_hour(Optional[int]), bio(Optional[str]), is_available(Optional[bool]), is_online(Optional[bool])

SERVICE REQUEST MODELS:
- ServiceRequestCreate: service_type(str), location(str), scheduled_at(Optional[str]), budget(Optional[int]), description(Optional[str])

RATING MODELS:
- RatingCreate: booking_id(str), ratee_id(str), stars(int), review_text(Optional[str]), tags(Optional[List[str]]=[])
- RatingResponse: id(str), stars(int), review_text(Optional[str]), tags(List[str]), rater_role(str), created_at(str)

NOTIFICATION MODELS:
- NotificationItem: id(str), title(str), body(str), type(str), is_read(bool), created_at(str)

## After creating:
Import supabase in Python shell and print it — should not throw error.

---

# STEP 3 — JWT Utils + Auth Routes

## Context
JWT tokens carry user_id and role.
Same backend serves both users and providers — role decides which UI shows.
Passwords hashed with bcrypt.

## Task
Create utils/jwt_handler.py and routes/auth.py
Then register auth router in main.py

### File: utils/jwt_handler.py
```python
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
```

### File: routes/auth.py

Implement these 3 endpoints:

POST /auth/register
- Request body: UserRegister schema
- Check if phone already exists in users table → 400 "Yeh phone already registered hai"
- Hash password with passlib bcrypt
- Insert into users table: name, phone, email, password_hash, city, role
- If role == "provider": also insert row in providers table with user_id, service_type="", area="", is_available=False
- Create JWT token with user_id and role
- Return TokenResponse

POST /auth/login
- Request body: UserLogin schema
- Query users table WHERE phone = phone
- If not found → 404 "User nahi mila"
- Verify password with bcrypt → 401 "Password galat hai" if wrong
- Create JWT token
- Return TokenResponse

GET /auth/me (protected with get_current_user)
- Query users table WHERE id = current_user["user_id"]
- Return user dict (exclude password_hash)

### Update main.py:
- Import auth router
- Add: app.include_router(auth.router, prefix="/auth", tags=["Auth"])

## Error pattern to follow in EVERY endpoint:
```python
try:
    # logic
    result = supabase.table("...").select("*").execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Nahi mila")
    return result.data
except HTTPException:
    raise
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
```

## After creating:
Test in Swagger http://localhost:8000/docs:
1. POST /auth/register with role="user" → should get token
2. POST /auth/register with same phone → should get 400
3. POST /auth/login → should get token
4. GET /auth/me with token → should get user profile

---

# STEP 4 — Providers/Workers Route

## Context
Users browse providers by service type and area.
Providers can update their own profile.
No AI here — plain database queries.

## Task
Create routes/workers.py and register in main.py

### File: routes/workers.py

Implement these endpoints:

GET /api/workers (protected)
- Query params: service_type(optional), area(optional), min_rating(optional, float)
- Query providers table
- For each provider, join users table to get name and avatar_url
- If service_type provided: filter WHERE service_type ILIKE %service_type%
- If area provided: filter WHERE area ILIKE %area%
- If min_rating provided: filter WHERE rating >= min_rating
- Always filter: is_available = true
- Order by rating DESC
- Return list of ProviderResult

GET /api/workers/:id (protected)
- Query providers table WHERE id = provider_id
- Join users table for name and avatar_url
- Query ratings table WHERE ratee_id = provider's user_id AND rater_role = "user"
- Return last 5 ratings with provider full profile

PUT /api/workers/profile (protected, provider only)
- Check current_user["role"] == "provider" → 403 if not
- Query providers table WHERE user_id = current_user["user_id"]
- Update with fields from ProviderUpdate schema (only update fields that are not None)
- Return updated provider profile

PUT /api/workers/availability (protected, provider only)
- Check role == "provider" → 403
- Body: {"is_online": bool, "is_available": bool}
- Update providers table WHERE user_id = current_user["user_id"]
- Return {"message": "Status update ho gaya"}

### Update main.py:
- Import workers router
- Add: app.include_router(workers.router, prefix="/api/workers", tags=["Workers"])

## After creating:
Test in Swagger:
1. GET /api/workers → list (empty is ok if no providers yet)
2. PUT /api/workers/profile with provider token → should update
3. GET /api/workers with service_type=plumber → filtered list

---

# STEP 5 — Gemini Intent Agent

## Context
This is the AI brain of Karoo.
User sends message in Urdu/Roman Urdu/English.
Gemini extracts: service_type, location, time, confidence.
If confidence < 0.6 or fields missing → return clarification needed.

## Task
Create agents/intent_agent.py only. No route yet.

### File: agents/intent_agent.py

```python
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

INTENT_PROMPT = """
You are an AI assistant for Karoo, a service booking app in Pakistan.

Extract the following from the user message (which may be in Urdu, Roman Urdu, or English):
- service_type: what service they need. Map to one of: plumber, electrician, ac_technician, tutor, cleaner, carpenter, painter, mechanic, cook, security_guard. If unsure, use closest match.
- location: area or neighborhood they mentioned (e.g. F-10, G-11, DHA, Gulshan)
- time: when they need it (today, tomorrow, morning, evening, or specific time)
- confidence: float 0.0 to 1.0 — how confident you are in the extraction

Rules:
- If a field is not mentioned in the message, return null for that field
- confidence should be low (< 0.6) if message is very vague or unclear
- Always respond ONLY with valid JSON, no explanation, no markdown

User message: "{message}"

Respond with this exact JSON format:
{{"service_type": "...", "location": "...", "time": "...", "confidence": 0.95}}
"""

async def extract_intent(message: str) -> dict:
    """
    Extract service booking intent from user message.
    Supports Urdu, Roman Urdu, and English.
    Returns dict with service_type, location, time, confidence.
    """
    try:
        prompt = INTENT_PROMPT.format(message=message)
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response in case Gemini adds markdown
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        result = json.loads(text.strip())
        print(f"[INTENT AGENT] Input: '{message}' → Output: {result}")
        return result
        
    except json.JSONDecodeError:
        print(f"[INTENT AGENT] JSON parse failed, returning low confidence")
        return {"service_type": None, "location": None, "time": None, "confidence": 0.0}
    except Exception as e:
        print(f"[INTENT AGENT] Error: {e}")
        return {"service_type": None, "location": None, "time": None, "confidence": 0.0}
```

## After creating:
Test with this script (run in terminal):
```python
import asyncio
from agents.intent_agent import extract_intent

async def test():
    r1 = await extract_intent("Mujhe kal plumber chahiye F-10 mein")
    print("Test 1:", r1)
    
    r2 = await extract_intent("I need an electrician in DHA tomorrow morning")
    print("Test 2:", r2)
    
    r3 = await extract_intent("AC theek karwana hai")
    print("Test 3:", r3)

asyncio.run(test())
```
All 3 should return valid intent dicts.

---

# STEP 6 — Google Maps MCP Tools + Ranking Agent

## Context
Google Maps APIs convert location text to coordinates and calculate real travel time.
Ranking agent scores providers using 6 factors.

## Task
Create mcp/tools/geocode.py, mcp/tools/travel_time.py, agents/ranking.py

### File: mcp/tools/geocode.py
```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

async def geocode_location(location_text: str) -> dict:
    """
    Convert area name to lat/lng using Google Geocoding API.
    Example: "F-10 Islamabad" → {"lat": 33.68, "lng": 73.04}
    """
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": f"{location_text}, Pakistan",
            "key": GOOGLE_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            loc = data["results"][0]["geometry"]["location"]
            result = {"lat": loc["lat"], "lng": loc["lng"], "formatted": data["results"][0]["formatted_address"]}
            print(f"[MCP TOOL] geocode_location | Input: {location_text} | Output: {result}")
            return result
        else:
            print(f"[MCP TOOL] geocode_location | Failed: {data['status']}")
            return {"lat": None, "lng": None, "formatted": location_text}
    except Exception as e:
        print(f"[MCP TOOL] geocode_location | Error: {e}")
        return {"lat": None, "lng": None, "formatted": location_text}
```

### File: mcp/tools/travel_time.py
```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

async def get_travel_time(provider_lat: float, provider_lng: float,
                          user_lat: float, user_lng: float) -> dict:
    """
    Get real driving travel time using Google Routes API.
    Returns eta_minutes (int).
    """
    try:
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_KEY,
            "X-Goog-FieldMask": "routes.duration"
        }
        body = {
            "origin": {"location": {"latLng": {"latitude": provider_lat, "longitude": provider_lng}}},
            "destination": {"location": {"latLng": {"latitude": user_lat, "longitude": user_lng}}},
            "travelMode": "DRIVE"
        }
        response = requests.post(url, json=body, headers=headers)
        data = response.json()
        
        duration_str = data["routes"][0]["duration"]
        eta_seconds = int(duration_str.replace("s", ""))
        eta_minutes = eta_seconds // 60
        
        print(f"[MCP TOOL] get_travel_time | Provider: ({provider_lat},{provider_lng}) → ETA: {eta_minutes} min")
        return {"eta_minutes": eta_minutes}
        
    except Exception as e:
        print(f"[MCP TOOL] get_travel_time | Error: {e} | Using fallback")
        return {"eta_minutes": 999}
```

### File: agents/ranking.py
```python
from mcp.tools.travel_time import get_travel_time

async def rank_providers(providers: list, user_lat: float = None, 
                         user_lng: float = None, user_budget: str = None) -> list:
    """
    Rank providers using 6-factor scoring formula.
    Fetches real travel time from Google Routes API for each provider.
    Returns top 3 providers sorted by score.
    """
    for p in providers:
        # Get real travel time if user location available
        eta = 30  # default fallback
        if user_lat and user_lng and p.get("lat") and p.get("lng"):
            travel = await get_travel_time(p["lat"], p["lng"], user_lat, user_lng)
            eta = travel["eta_minutes"]
        p["eta_minutes"] = eta
        
        # Price fit
        price_fit = 1.0
        if user_budget == "low" and p.get("rate_per_hour", 0) > 1000:
            price_fit = 0.3
        elif user_budget == "high" and p.get("rate_per_hour", 0) < 500:
            price_fit = 0.5

        # 6-factor scoring
        rating = p.get("rating", 0) / 5.0
        eta_score = 1 / (eta + 1)
        available = 1.0 if p.get("is_available") else 0.0
        on_time = p.get("on_time_score", 5.0) / 5.0
        recency = p.get("review_recency", 1.0)

        p["match_score"] = round(
            (rating    * 0.30) +
            (eta_score * 0.25) +
            (available * 0.15) +
            (on_time   * 0.15) +
            (price_fit * 0.10) +
            (recency   * 0.05), 3
        )
        
        print(f"[RANKING] {p.get('name', p['id'])} → score: {p['match_score']} | ETA: {eta}min | Rating: {p.get('rating',0)}")

    sorted_providers = sorted(providers, key=lambda x: x["match_score"], reverse=True)
    return sorted_providers[:3]
```

## After creating:
Test geocode manually:
```python
import asyncio
from mcp.tools.geocode import geocode_location
result = asyncio.run(geocode_location("F-10 Islamabad"))
print(result)  # should return lat/lng
```

---

# STEP 7 — Chat Route (AI Endpoint)

## Context
This is the main AI endpoint. It connects Gemini intent agent + Google Maps + Supabase providers + ranking.
Every step must be logged as agent trace.

## Task
Create utils/tracer.py and routes/chat.py

### File: utils/tracer.py
```python
import uuid
from datetime import datetime

class AgentTrace:
    def __init__(self, user_message: str):
        self.session_id = str(uuid.uuid4())[:8]
        self.user_message = user_message
        self.steps = []
        self.start_time = datetime.utcnow()

    def add_step(self, step_name: str, tool: str, input_data: any, output_data: any, status: str = "SUCCESS"):
        self.steps.append({
            "step": step_name,
            "tool": tool,
            "input": str(input_data)[:200],
            "output": str(output_data)[:200],
            "status": status
        })

    def to_string(self) -> str:
        elapsed = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        lines = [
            f"=== KAROO AGENT TRACE ===",
            f"Session: {self.session_id}",
            f"Input: {self.user_message}",
            ""
        ]
        for i, s in enumerate(self.steps, 1):
            lines.append(f"[STEP {i}] {s['step']}")
            lines.append(f"  Tool: {s['tool']}")
            lines.append(f"  Input: {s['input']}")
            lines.append(f"  Output: {s['output']}")
            lines.append(f"  Status: {s['status']}")
            lines.append("")
        lines.append(f"Total steps: {len(self.steps)}")
        lines.append(f"Total time: {elapsed:.0f}ms")
        lines.append("=== END TRACE ===")
        return "\n".join(lines)
```

### File: routes/chat.py

Implement these endpoints:

POST /api/chat (protected, user only)
Request: ChatRequest schema

Logic:
```
1. Check role == "user" → 403 if provider

2. Initialize AgentTrace(message)

3. Save user message to messages table:
   {user_id, role="user", content=message}

4. Call extract_intent(message)
   tracer.add_step("Intent Extraction", "gemini_parse", message, intent_result)

5. If confidence < 0.6 OR service_type is None:
   Save bot message to messages table
   Return ChatResponse(
     reply="Aap kaunsi service chahiye? Maslan: plumber, electrician, AC technician, tutor",
     needs_clarification=True,
     agent_trace=tracer.to_string()
   )

6. If location is None:
   Return ChatResponse(
     reply="Aap ki location kya hai? Maslan: F-10, G-11, DHA",
     needs_clarification=True,
     agent_trace=tracer.to_string()
   )

7. Geocode location:
   Call geocode_location(intent["location"])
   tracer.add_step("Location Geocoding", "geocode_location", intent["location"], geocode_result)
   
   user_lat = user_lat from request OR geocode_result["lat"]
   user_lng = user_lng from request OR geocode_result["lng"]

8. Query providers from Supabase:
   supabase.table("providers")
     .select("*, users(name, avatar_url)")
     .eq("service_type", intent["service_type"])
     .eq("is_available", True)
     .execute()
   tracer.add_step("Provider Search", "supabase_query", intent["service_type"], f"{len(providers)} found")

9. If no providers found:
   Return ChatResponse(
     reply=f"Sorry, {intent['service_type']} abhi {intent['location']} mein available nahi hai",
     needs_clarification=False,
     agent_trace=tracer.to_string()
   )

10. Call rank_providers(providers, user_lat, user_lng)
    tracer.add_step("Provider Ranking", "ranking_agent", len(providers), f"Top 3 selected")

11. Build ProviderResult list from top 3

12. Build reply message:
    f"{intent['location']} mein {len(top3)} {intent['service_type']} available hain"

13. Save bot response to messages table:
    {user_id, role="bot", content=reply, parsed_intent=intent, agent_trace=trace_string}

14. Return ChatResponse(
      reply=reply,
      intent=ParsedIntent(**intent),
      providers=top3,
      needs_clarification=False,
      agent_trace=tracer.to_string()
    )
```

GET /api/chat/history (protected)
- Query messages WHERE user_id = current_user["user_id"]
- Order by created_at ASC
- Return list

### Update main.py:
- Import chat router
- Add: app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

## After creating:
Test in Swagger:
1. POST /api/chat with message="Mujhe plumber chahiye F-10 mein"
   → should return providers list + agent_trace string
2. POST /api/chat with message="hello"
   → should return needs_clarification=True

---

# STEP 8 — Bookings Route

## Context
Users create bookings. Providers accept/reject/complete.
Every status change creates notifications for BOTH sides.

## Task
Create utils/notifications.py and routes/bookings.py

### File: utils/notifications.py
```python
from db.supabase_client import supabase

async def create_notification(user_id: str, title: str, body: str, 
                               type: str, ref_id: str = None):
    try:
        supabase.table("notifications").insert({
            "user_id": user_id,
            "title": title,
            "body": body,
            "type": type,
            "ref_id": ref_id
        }).execute()
    except Exception as e:
        print(f"[NOTIFICATION ERROR] {e}")

async def notify_booking_created(booking_id, user_id, provider_user_id, 
                                  provider_name, user_name, service_type):
    await create_notification(user_id, 
        "Booking Bhej Di Gayi ✅",
        f"{provider_name} ko tumhari {service_type} request mili",
        "booking_created", booking_id)
    await create_notification(provider_user_id,
        "Naya Booking Request! 🔔",
        f"{user_name} ko {service_type} chahiye",
        "booking_created", booking_id)

async def notify_booking_accepted(booking_id, user_id, provider_user_id, 
                                   provider_name, scheduled_at):
    await create_notification(user_id,
        "Booking Confirm Ho Gayi! ✅",
        f"{provider_name} aa raha hai {scheduled_at} ko",
        "booking_accepted", booking_id)
    await create_notification(provider_user_id,
        "Job Confirm",
        "Tumne booking accept kar li",
        "booking_accepted", booking_id)

async def notify_booking_rejected(booking_id, user_id, provider_user_id, provider_name):
    await create_notification(user_id,
        "Booking Reject Ho Gayi ❌",
        f"{provider_name} available nahi hai. Doosra provider choose karo.",
        "booking_rejected", booking_id)
    await create_notification(provider_user_id,
        "Booking Reject Ki",
        "Tumne yeh booking reject kar di",
        "booking_rejected", booking_id)

async def notify_booking_completed(booking_id, user_id, provider_user_id, user_name):
    await create_notification(user_id,
        "Kaam Mukammal! ⭐",
        "Please apna experience rate karo",
        "booking_completed", booking_id)
    await create_notification(provider_user_id,
        "Job Complete",
        f"{user_name} ki service complete ho gayi. Rate the customer.",
        "booking_completed", booking_id)
```

### File: routes/bookings.py

Implement these endpoints:

POST /api/bookings (protected, user only)
- Check role == "user" → 403
- Get provider from providers table → 404 if not found
- Get provider's user_id (for notifications)
- Get user's name from users table
- Get provider's name from users table (join)
- Insert booking with status=pending, booked_via from request
- Call notify_booking_created()
- Return created booking

GET /api/bookings/my (protected)
- If role=user: query bookings WHERE user_id = current_user["user_id"]
- If role=provider:
  - Get provider row WHERE user_id = current_user["user_id"]
  - Query bookings WHERE provider_id = provider["id"]
- Order by created_at DESC
- Return list

PUT /api/bookings/:id/accept (protected, provider only)
- Check role == "provider" → 403
- Get booking → 404
- Verify booking's provider is this provider (get provider by user_id first)
- Check status == "pending" → 400 "Yeh booking already update ho chuki hai"
- Update status = confirmed
- Get user name and provider name for notification
- Call notify_booking_accepted()
- Return updated booking

PUT /api/bookings/:id/reject (protected, provider only)
- Same checks as accept
- Update status = cancelled
- Call notify_booking_rejected()
- Return updated booking

PUT /api/bookings/:id/complete (protected, provider only)
- Same checks
- Check status == "confirmed" → 400 if not
- Update status = completed
- Call notify_booking_completed()
- Return updated booking

### Update main.py:
- Import bookings router
- Add: app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])

## After creating:
Test in Swagger:
1. POST /api/bookings (user token) → pending booking created
2. PUT /api/bookings/:id/accept (provider token) → confirmed
3. GET /api/bookings/my (both tokens) → correct list

---

# STEP 9 — Ratings (Bidirectional)

## Context
After booking completed, BOTH sides rate each other.
User rates provider (1-5 stars).
Provider rates user (reliability score 1-5).
Blind review — neither sees the other's rating until both submit.

## Task
Create routes/ratings.py

### File: routes/ratings.py

POST /api/ratings (protected)
- Request: RatingCreate schema
- Get booking → 404 if not found
- Check booking status == "completed" → 400 if not "Sirf complete bookings rate ho sakti hain"
- Check if current user already rated this booking:
  Query ratings WHERE booking_id = booking_id AND rater_id = current_user["user_id"]
  → 400 "Tumne pehle hi rate kar diya hai"
- Insert rating:
  rater_id = current_user["user_id"]
  rater_role = current_user["role"]
- After insert, update target's score:
  If rater_role == "user" (rating a provider):
    Query all ratings WHERE ratee_id = ratee_id AND rater_role = "user"
    Calculate average stars
    Update providers table: rating = avg, total_ratings = count
  If rater_role == "provider" (rating a user):
    Query all ratings WHERE ratee_id = ratee_id AND rater_role = "provider"
    Calculate average stars
    Update users table: reliability_score = avg, total_ratings = count
- Return created rating

GET /api/ratings/provider/:provider_user_id (protected)
- Query ratings WHERE ratee_id = provider_user_id AND rater_role = "user"
- Order by created_at DESC
- Return list of RatingResponse

GET /api/ratings/user/:user_id (protected, provider only)
- Check role == "provider" → 403
- Query ratings WHERE ratee_id = user_id AND rater_role = "provider"
- Return list + average reliability_score

GET /api/ratings/pending (protected)
- Get bookings with status=completed for current user
- For each, check if current user has rated
- Return list of bookings that still need rating
- This tells frontend: "show rating prompt for these"

### Update main.py:
- Import ratings router
- Add: app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])

## After creating:
Test in Swagger:
1. POST /api/ratings (user token, after completing a booking)
2. POST /api/ratings (provider token, same booking) 
3. GET /api/ratings/provider/:id → list of reviews

---

# STEP 10 — Notifications + Service Requests Routes

## Context
Final two routes.
Notifications: read/unread management.
Service requests: users post open requests, providers browse and accept.

## Task
Create routes/notifications.py and routes/requests.py

### File: routes/notifications.py

GET /api/notifications (protected)
- Query notifications WHERE user_id = current_user["user_id"]
- Order by created_at DESC, limit 50
- Count unread: WHERE is_read = false
- Return: {"notifications": [...], "unread_count": int}

PUT /api/notifications/:id/read (protected)
- Update notifications SET is_read=true 
  WHERE id = id AND user_id = current_user["user_id"]
- Return {"message": "Mark as read"}

PUT /api/notifications/read-all (protected)
- Update ALL: is_read=true WHERE user_id = current_user["user_id"]
- Return {"message": "Sab notifications read ho gayi"}

### File: routes/requests.py

POST /api/requests (protected, user only)
- Check role == "user" → 403
- Insert into service_requests with status=open, user_id
- Query providers WHERE service_type = request.service_type
  (to notify relevant providers)
- For each matching provider get their user_id
- Call create_notification() for each provider:
  title="Naya Kaam! 📋", body=f"{service_type} ki zaroorat hai {location} mein"
- Return created request

GET /api/requests/open (protected, provider only)
- Check role == "provider" → 403
- Query params: service_type(optional), area(optional)
- Query service_requests WHERE status=open
- Apply filters if provided (ILIKE)
- Order by created_at DESC
- Return list

PUT /api/requests/:id/accept (protected, provider only)
- Check role == "provider" → 403
- Get request → 404
- Check status == "open" → 400 "Yeh request already le li gayi hai"
- Update request status = taken
- Get provider row by user_id
- Create booking automatically:
  user_id from request, provider_id from provider row
  service_type, location from request, booked_via="request"
- Notify user: title="Provider Mil Gaya! ✅", body=f"Tumhari request accept ho gayi"
- Return created booking

GET /api/requests/my (protected, user only)
- Check role == "user" → 403
- Query service_requests WHERE user_id = current_user["user_id"]
- Order by created_at DESC
- Return list

### Update main.py:
- Import both routers
- Add both to app

## Final main.py should have ALL these routers:
```python
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(workers.router, prefix="/api/workers", tags=["Workers"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(requests.router, prefix="/api/requests", tags=["Requests"])
```

## FINAL TEST — Run all in Swagger in order:
1. Register user → get token
2. Register provider → get token
3. POST /api/chat → get providers with agent trace
4. POST /api/bookings → create booking
5. PUT /api/bookings/:id/accept → provider accepts
6. PUT /api/bookings/:id/complete → mark done
7. POST /api/ratings (user) → rate provider
8. POST /api/ratings (provider) → rate user
9. GET /api/notifications (both) → see notifications
10. POST /api/requests → user posts open request
11. GET /api/requests/open (provider) → see request
12. PUT /api/requests/:id/accept → provider accepts

ALL 12 must pass before telling frontend teammate to connect! ✅
