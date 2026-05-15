# 🤝 Karoo — AI Service Orchestrator

> AI-powered service booking agent for informal economy — find, book & track local services instantly.

**Hackathon:** Google Antigravity Hackathon — Challenge 2: AI Service Orchestrator for Informal Economy

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Architecture Overview](#architecture-overview)
4. [How Google Antigravity is Used](#how-google-antigravity-is-used)
5. [Google Cloud Services](#google-cloud-services)
6. [Real-Time Location with MCP](#real-time-location-with-mcp)
7. [Authentication Flow](#authentication-flow)
8. [User Flow](#user-flow)
9. [Provider Flow](#provider-flow)
10. [Bidirectional Rating System](#bidirectional-rating-system)
11. [Database Schema](#database-schema)
12. [API Endpoints](#api-endpoints)
13. [Team Work Distribution](#team-work-distribution)
14. [Project Structure](#project-structure)
15. [Setup & Installation](#setup--installation)
16. [Environment Variables](#environment-variables)
17. [Deployment](#deployment)
18. [Assumptions & Limitations](#assumptions--limitations)

---

## Project Overview

Karoo solves a real-world problem in Pakistan's informal economy. Plumbers, electricians, tutors, and home service providers operate through WhatsApp messages and phone calls — resulting in inefficient service matching and poor user experience.

**Karoo** is an agentic AI system that automates the full lifecycle of a service request:

- User types a request in **Urdu, Roman Urdu, or English**
- AI agent extracts intent (service type, location, time)
- System finds and ranks nearby providers using **real-time location via Google Cloud**
- Booking is simulated with confirmation and follow-up reminder
- Provider receives real-time notification and can accept/reject
- After service: **both user and provider rate each other** with a star system

### Example

```
User: "Mujhe kal subah F-10 mein plumber chahiye"

System detects:
  service_type → plumber
  location     → F-10 (geocoded to lat/lng via Google Geocoding API)
  time         → tomorrow morning

Result:
  Top 3 providers ranked by real travel time + rating + availability
  Booking confirmed → Provider notified → Reminder scheduled
  After completion: User rates Provider ⭐⭐⭐⭐ | Provider rates User ⭐⭐⭐⭐⭐
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Expo + React Native | Web + Mobile — single codebase |
| Styling | NativeWind (Tailwind for RN) | Responsive UI |
| Navigation | Expo Router | File-based routing |
| Backend | FastAPI (Python) | REST API server |
| AI Orchestration | **Google Antigravity** | Core agent logic (uses Gemini API internally) |
| Intent Parsing | Gemini API (via Antigravity) | Urdu/Roman Urdu NLP |
| Location Services | **Google Cloud — Routes, Geocoding, Places APIs** | Real-time travel time & provider matching |
| Database | Supabase (PostgreSQL) | Users, providers, bookings, ratings |
| Realtime | Supabase Realtime | Push notifications to provider |
| Auth | JWT + Supabase Auth | Secure token-based auth |
| Deployment | **Render** (backend) + Expo Go (mobile) | Free tier |

> **Note on Antigravity + Gemini:** Google Antigravity is the agentic orchestration platform. It uses your **Gemini API key** to power all LLM reasoning steps (intent parsing, ranking decisions, dispute handling). You configure the Gemini key once inside the Antigravity agent settings — Antigravity calls Gemini internally for every reasoning step.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Expo App (Frontend)                 │
│         Web Browser  +  Android/iOS App              │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP (JWT in headers)
                        ▼
┌─────────────────────────────────────────────────────┐
│                FastAPI Backend                       │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │      Google Antigravity Agent                │   │
│  │      (powered by Gemini API key)             │   │
│  │                                             │   │
│  │  1. Receives user message                   │   │
│  │  2. Calls Gemini → extract intent           │   │
│  │  3. Calls Google Routes API → travel times  │   │
│  │  4. Queries Supabase → match providers      │   │
│  │  5. Ranks by ETA, rating, availability      │   │
│  │  6. Returns structured response + trace     │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  MCP Tools (called by Antigravity agent)     │   │
│  │  • get_travel_time()  → Routes API           │   │
│  │  • geocode_location() → Geocoding API        │   │
│  │  • search_places()    → Places API           │   │
│  │  • query_providers()  → Supabase             │   │
│  │  • submit_rating()    → Supabase             │   │
│  └─────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Supabase (PostgreSQL)                   │
│   users | providers | bookings | ratings | messages  │
│                                                     │
│   Realtime channel → Provider App notified instantly │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│          Google Cloud APIs                           │
│   Geocoding API | Routes API | Places API            │
│   (all enabled from console.cloud.google.com)        │
└─────────────────────────────────────────────────────┘
```

### Request Flow

1. User types request in Expo Chat UI (Urdu/Roman Urdu/English)
2. `POST /api/request` sent with JWT token
3. Antigravity agent receives message
4. **Gemini API** (via Antigravity) extracts: `service_type`, `location`, `time`
5. If info missing → bot asks clarifying question
6. **Google Geocoding API** converts location text → lat/lng
7. **Google Routes API** calculates real travel time per provider
8. Supabase queried → providers ranked by ETA + rating + availability
9. Top 3 results returned to frontend
10. User selects provider → `POST /api/bookings`
11. Booking saved → Supabase Realtime fires
12. Provider app gets instant notification
13. Provider accepts/rejects → User notified
14. After service completion → **both sides submit star ratings**

---

## How Google Antigravity is Used

Google Antigravity is the **core orchestration platform** — not a wrapper. All agent reasoning and workflow execution happens inside Antigravity. It is powered by your **Gemini API key**, which you configure in the Antigravity project settings.

### Agent Responsibilities

```
Antigravity Agent Workflow:

  Input: "Mujhe bijli wala chahiye G-11 mein"
      │
      ▼
  [Step 1] Intent Extraction  ← Gemini API called by Antigravity
      │   Output: { service: "electrician", location: "G-11", time: null }
      │   Confidence: 0.87
      │
      ▼
  [Step 2] Clarification Check
      │   time = null → Ask user: "Kab chahiye?"
      │
      ▼
  [Step 3] Location Resolution  ← MCP Tool: geocode_location()
      │   "G-11 Islamabad" → { lat: 33.6844, lng: 73.0479 }
      │   Google Geocoding API
      │
      ▼
  [Step 4] Provider Discovery  ← MCP Tool: query_providers()
      │   Query Supabase providers WHERE service_type = "electrician"
      │
      ▼
  [Step 5] Travel Time Calculation  ← MCP Tool: get_travel_time()
      │   Google Routes API → real ETA per provider
      │   Provider A: 12 min  |  Provider B: 8 min
      │
      ▼
  [Step 6] Multi-Factor Ranking  ← Gemini API reasoning via Antigravity
      │   Score = (rating × 0.30) + (1/ETA × 0.25) + (availability × 0.15)
      │         + (on_time_score × 0.15) + (price_fit × 0.10) + (recency × 0.05)
      │   Result: Provider A ranked #1 despite longer travel time
      │   Reason: Higher reliability + AC specialization + better reviews
      │
      ▼
  [Step 7] Booking Simulation
      │   Create booking record in Supabase
      │   Trigger provider notification via Realtime
      │   Schedule reminder job
      │
      ▼
  [Step 8] Post-Service Rating Prompt  ← NEW
      │   After service completion:
      │   User prompted → rate provider (1–5 stars + comment)
      │   Provider prompted → rate user (1–5 stars + reliability note)
      │
      ▼
  Output: Confirmed booking + agent trace log + mutual ratings recorded
```

### Antigravity Logs

Every request produces a full agent trace:
- Workplan (what the agent planned to do)
- Task execution log (each step with input/output)
- Tool calls (Gemini, Supabase queries, Google Maps API calls)
- Decision reasoning (why provider X was ranked #1)
- Confidence scores for intent parsing
- Failure recovery (if a step fails, fallback action)

---

## Google Cloud Services

All services are enabled from [console.cloud.google.com](https://console.cloud.google.com/).

### APIs to Enable

| API | Console Name | Use in Karoo |
|---|---|---|
| **Geocoding API** | `geocoding-backend` | Convert "F-10", "G-13" → lat/lng coordinates |
| **Routes API** | `routes.googleapis.com` | Real-time travel time from provider to user |
| **Distance Matrix API** | `distance-matrix-backend` | Batch distance for multiple providers at once |
| **Places API** | `places-backend` | Validate and enrich location names |
| **Maps JavaScript API** | `maps-backend` | Show provider pins on map in app |
| **Geolocation API** | `geolocation` | Get user's device location automatically |

### How to Enable

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services → Library**
4. Search each API name above → click **Enable**
5. Go to **APIs & Services → Credentials** → Create API Key
6. Add the key to your `.env` as `GOOGLE_MAPS_API_KEY`

---

## Real-Time Location with MCP

Antigravity uses **MCP (Model Context Protocol) tools** to connect the agent to external services. Location-aware provider matching works like this:

### MCP Tool Definitions (in Antigravity editor)

```python
@tool
def geocode_location(location_text: str) -> dict:
    """Convert area name to lat/lng using Google Geocoding API"""
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": f"{location_text}, Islamabad, Pakistan", "key": GOOGLE_MAPS_API_KEY}
    result = requests.get(url, params=params).json()
    location = result["results"][0]["geometry"]["location"]
    return {"lat": location["lat"], "lng": location["lng"]}

@tool
def get_travel_time(provider_lat: float, provider_lng: float,
                    user_lat: float, user_lng: float) -> dict:
    """Get real-time travel time using Google Routes API"""
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    body = {
        "origin": {"location": {"latLng": {"latitude": provider_lat, "longitude": provider_lng}}},
        "destination": {"location": {"latLng": {"latitude": user_lat, "longitude": user_lng}}},
        "travelMode": "DRIVE"
    }
    result = requests.post(url, json=body, headers={"X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
                                                     "X-Goog-FieldMask": "routes.duration"}).json()
    return {
        "eta_minutes": int(result["routes"][0]["duration"].replace("s", "")) // 60
    }

@tool
def query_providers(service_type: str, user_lat: float, user_lng: float) -> list:
    """Fetch providers from Supabase and enrich with travel times"""
    providers = supabase.table("providers").select("*").eq("service_type", service_type).execute()
    for p in providers.data:
        travel = get_travel_time(p["lat"], p["lng"], user_lat, user_lng)
        p["eta_minutes"] = travel["eta_minutes"]
    return providers.data
```

### Agent Ranking Formula

```python
def rank_providers(providers: list, user_budget: str) -> list:
    for p in providers:
        price_fit = 1 if user_budget == "low" and p["rate_per_hour"] < 1000 else 0.5
        p["score"] = (
            p["rating"]          * 0.30 +
            (1 / p["eta_minutes"]) * 0.25 +
            p["is_available"]    * 0.15 +
            p["on_time_score"]   * 0.15 +
            price_fit            * 0.10 +
            p["review_recency"]  * 0.05
        )
    return sorted(providers, key=lambda x: x["score"], reverse=True)
```

The Antigravity agent calls these MCP tools at each step, and the full call chain is logged in the trace output.

---

## Authentication Flow

### User Registration

```
1. User fills: name, phone, email, password, city
2. POST /auth/register
3. Backend hashes password (bcrypt)
4. Creates user in Supabase (role = "user")
5. SMS OTP sent to phone (Supabase Auth)
6. POST /auth/verify-otp → JWT token returned
7. Token saved in AsyncStorage on device
8. User redirected to Chat UI
```

### Provider Registration

```
1. Provider fills: name, phone, service_category, area, CNIC photo
2. POST /auth/provider/register
3. Creates user in Supabase (role = "provider", status = "pending")
4. SMS OTP verification (same flow)
5. JWT token returned with role = "provider"
6. Provider sees Dashboard UI (different from user UI)
```

### JWT Token Structure

```json
{
  "user_id": "uuid-here",
  "role": "user" | "provider",
  "phone": "+92300xxxxxxx",
  "exp": 1234567890
}
```

---

## User Flow

### Screens

```
Landing Page → Login/Signup → Chat UI → Provider Results → Booking Confirm → Rate Provider
```

### Chat UI
- User types in any language (Urdu / Roman Urdu / English)
- Bot extracts intent or asks follow-up questions
- Provider cards appear inside chat (with real ETA from Google Routes API)
- Tap provider → Booking confirmation screen
- After booking: confirmation message + estimated arrival time (live)

### Provider Results Screen
Each provider card shows:
- Name + Profile photo
- Service type + Rating (stars)
- **Real travel time** (e.g., "12 min away") via Google Routes API
- Rate per hour (PKR)
- Availability status
- "Book Now" button

### Post-Service Rating Screen (NEW)
After the provider marks the job as complete:
- User sees: ⭐ Rate your provider (1–5 stars)
- Text field: "Tell us about your experience"
- Submit → provider's rating updated in DB
- Provider simultaneously sees: ⭐ Rate this customer (1–5 stars)
- Note field: reliability, communication, payment behavior

---

## Provider Flow

### Provider Dashboard Screens

```
Notifications → My Bookings → My Schedule → My Profile → Rate Customer
```

### Incoming Notification
- Supabase Realtime push with: user name, service, location, ETA distance, time
- **Accept** → booking confirmed, user notified, calendar updated
- **Reject** → next provider offered to user

### My Schedule
- Calendar view of upcoming bookings
- Provider can mark slots as Available / Busy
- Prevents double-booking via agent scheduling logic

### Post-Service Rating (Provider Side — NEW)
After marking a job complete:
- Provider prompted to rate the customer (1–5 stars)
- Notes: was the customer on time, cooperative, payment ready?
- This builds a **User Reliability Score** used in future bookings
  - Providers can see user score before accepting a job
  - Protects providers from problematic customers

---

## Bidirectional Rating System

Karoo implements a **mutual trust and accountability** layer through two-way ratings.

### How It Works

```
Job Completed
      │
      ├──► User rates Provider
      │         • 1–5 stars
      │         • Written review (optional)
      │         • Tags: punctual, professional, quality work, overpriced
      │         • Updates: provider.rating (rolling avg)
      │
      └──► Provider rates User
                • 1–5 stars
                • Notes: reliable, cooperative, clear instructions
                • Updates: user.reliability_score (rolling avg)
```

### Rating Rules
- Rating window opens when booking status = `completed`
- Window closes after **72 hours** — ratings locked after that
- Neither party sees the other's rating until both have submitted (blind review)
- Minimum 3 completed bookings before rating affects matching algorithm
- Ratings below ⭐2 trigger an optional dispute or comment flag

### Impact on Future Matching
- **Provider rating** → primary ranking factor (30% weight in agent scoring)
- **User reliability score** → shown to provider before accepting a booking
  - Score < 3.0 → agent adds a warning note in provider notification
  - Score < 2.0 → provider has option to auto-decline
- Both scores are shown transparently in the app

### Review Recency Weighting
Older reviews matter less. The agent applies:
```
effective_rating = (recent_30_day_avg × 0.6) + (all_time_avg × 0.4)
```

---

## Database Schema

### `users`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
name            TEXT NOT NULL
phone           TEXT UNIQUE NOT NULL
email           TEXT
password_hash   TEXT NOT NULL
city            TEXT
role            TEXT CHECK (role IN ('user', 'provider')) DEFAULT 'user'
reliability_score FLOAT DEFAULT 5.0   -- NEW: user's score rated by providers
total_ratings   INTEGER DEFAULT 0     -- NEW: number of times user was rated
avatar_url      TEXT
created_at      TIMESTAMP DEFAULT now()
```

### `providers`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id         UUID REFERENCES users(id)
service_type    TEXT NOT NULL
area            TEXT NOT NULL
lat             FLOAT                  -- Google Geocoding API result
lng             FLOAT                  -- Google Geocoding API result
rating          FLOAT DEFAULT 0        -- updated from ratings table
total_ratings   INTEGER DEFAULT 0
on_time_score   FLOAT DEFAULT 5.0
review_recency  FLOAT DEFAULT 1.0      -- decay factor based on review dates
rate_per_hour   INTEGER
is_available    BOOLEAN DEFAULT true
bio             TEXT
created_at      TIMESTAMP DEFAULT now()
```

### `bookings`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id         UUID REFERENCES users(id)
provider_id     UUID REFERENCES providers(id)
service_type    TEXT NOT NULL
location        TEXT NOT NULL
user_lat        FLOAT                  -- from Geolocation API
user_lng        FLOAT
scheduled_at    TIMESTAMP NOT NULL
status          TEXT CHECK (status IN ('pending','confirmed','en_route','completed','cancelled','disputed')) DEFAULT 'pending'
eta_minutes     INTEGER                -- from Google Routes API at booking time
note            TEXT
created_at      TIMESTAMP DEFAULT now()
```

### `ratings` (NEW TABLE)
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
booking_id      UUID REFERENCES bookings(id)
rater_id        UUID REFERENCES users(id)      -- who gave the rating
ratee_id        UUID REFERENCES users(id)      -- who received the rating
rater_role      TEXT CHECK (rater_role IN ('user', 'provider'))
stars           INTEGER CHECK (stars BETWEEN 1 AND 5)
review_text     TEXT
tags            TEXT[]                          -- e.g. ["punctual","professional"]
created_at      TIMESTAMP DEFAULT now()
```

### `messages`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id         UUID REFERENCES users(id)
role            TEXT CHECK (role IN ('user', 'bot')) NOT NULL
content         TEXT NOT NULL
parsed_intent   JSONB                  -- { service, location, time, confidence }
agent_trace     TEXT                   -- Antigravity trace log for this message
created_at      TIMESTAMP DEFAULT now()
```

---

## API Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | User registration |
| POST | `/auth/login` | Login → returns JWT |
| POST | `/auth/verify-otp` | Phone OTP verification |
| POST | `/auth/provider/register` | Provider registration |

### Chat / AI

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/request` | ✅ | Send message → Antigravity agent processes |
| GET | `/api/messages/:user_id` | ✅ | Get chat history |

**Request Body for `/api/request`:**
```json
{
  "message": "Mujhe kal plumber chahiye F-10 mein",
  "user_id": "uuid",
  "user_lat": 33.6844,
  "user_lng": 73.0479
}
```

**Response:**
```json
{
  "intent": {
    "service_type": "plumber",
    "location": "F-10",
    "location_geocoded": { "lat": 33.6844, "lng": 73.0479 },
    "time": "tomorrow morning",
    "confidence": 0.92
  },
  "providers": [
    {
      "id": "uuid",
      "name": "Ali Plumbing",
      "rating": 4.7,
      "eta_minutes": 12,
      "rate_per_hour": 800,
      "is_available": true,
      "match_score": 0.84,
      "ranking_reason": "Highest reliability score + AC specialization"
    }
  ],
  "agent_trace": "Step 1: Intent parsed... Step 2: Geocoded F-10..."
}
```

### Providers

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/providers` | ✅ | List providers (filter by service, city) |
| GET | `/api/providers/:id` | ✅ | Get single provider |
| PUT | `/api/providers/:id` | ✅ Provider only | Update profile |

### Bookings

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/bookings` | ✅ | Create booking |
| GET | `/api/bookings/my` | ✅ | Get my bookings |
| PUT | `/api/bookings/:id/status` | ✅ Provider only | Accept / Reject / En-route / Complete |

### Ratings (NEW)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/ratings` | ✅ | Submit rating after booking completion |
| GET | `/api/ratings/provider/:id` | ✅ | Get all ratings for a provider |
| GET | `/api/ratings/user/:id` | ✅ | Get user reliability score + reviews |

**Request Body for `/api/ratings`:**
```json
{
  "booking_id": "uuid",
  "ratee_id": "uuid",
  "stars": 4,
  "review_text": "Bahut acha kaam kiya, time par aya",
  "tags": ["punctual", "professional"]
}
```

---

## Team Work Distribution

### Ismail — Backend

- [ ] FastAPI project setup (folder structure, requirements.txt, .env)
- [ ] Supabase connection + table creation (including `ratings` table)
- [ ] Auth endpoints (register, login, JWT, OTP)
- [ ] Google Antigravity agent setup + Gemini API key configuration
- [ ] MCP tool definitions (geocode_location, get_travel_time, query_providers)
- [ ] Google Cloud APIs setup (Geocoding, Routes, Places)
- [ ] Provider matching + ranking algorithm (6-factor scoring)
- [ ] Booking creation + status update endpoints
- [ ] Bidirectional rating endpoints + score update logic
- [ ] Supabase Realtime notifications
- [ ] Deploy backend on **Render**
- [ ] Share Swagger docs URL with frontend teammate

### Dost — Frontend

- [ ] Expo project setup (NativeWind, Expo Router)
- [ ] Landing page (web)
- [ ] Auth screens (Login + Signup for User and Provider)
- [ ] Chat UI screen (message bubbles, input bar)
- [ ] Provider results screen (cards with real ETA, match score)
- [ ] Booking confirmation screen
- [ ] Provider dashboard (notifications, accept/reject)
- [ ] Provider schedule screen
- [ ] **Rating screen** — user rates provider (star widget + tags)
- [ ] **Rating screen** — provider rates user (star widget + notes)
- [ ] Display user reliability score on provider notification card
- [ ] Connect all screens to Ismail's API endpoints
- [ ] Test on Expo Go (mobile)

### Both Together

- [ ] Create GitHub repo (`Karoo-app`) with `/backend` and `/frontend` folders
- [ ] Agree on API contract (endpoints + request/response format) before coding
- [ ] Create Supabase project + share keys
- [ ] Enable Google Cloud APIs + share `GOOGLE_MAPS_API_KEY`
- [ ] Final demo video recording (3-5 minutes)
- [ ] README finalization

---

## Project Structure

```
Karoo-app/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── routes/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── providers.py
│   │   ├── bookings.py
│   │   └── ratings.py           ← NEW
│   ├── agents/
│   │   ├── intent_agent.py      ← Antigravity agent (Gemini-powered)
│   │   ├── ranking_agent.py
│   │   └── mcp_tools.py         ← Google Maps MCP tools
│   ├── db/
│   │   └── supabase_client.py
│   └── models/
│       └── schemas.py
│
├── frontend/
│   ├── app/
│   │   ├── index.tsx             ← Landing page
│   │   ├── (auth)/
│   │   │   ├── login.tsx
│   │   │   └── signup.tsx
│   │   ├── (user)/
│   │   │   ├── chat.tsx          ← Main chat UI
│   │   │   ├── results.tsx
│   │   │   ├── booking.tsx
│   │   │   └── rate-provider.tsx ← NEW: post-service rating
│   │   └── (provider)/
│   │       ├── dashboard.tsx
│   │       ├── notifications.tsx
│   │       ├── profile.tsx
│   │       └── rate-user.tsx     ← NEW: provider rates customer
│   ├── components/
│   │   ├── MessageBubble.tsx
│   │   ├── ProviderCard.tsx
│   │   ├── BookingStatus.tsx
│   │   └── StarRating.tsx        ← NEW: reusable star widget
│   ├── lib/
│   │   └── api.ts
│   └── package.json
│
└── README.md
```

---

## Setup & Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`
Swagger docs at: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npx expo start
```

- Press `w` for web browser
- Press `a` for Android emulator
- Scan QR code with **Expo Go** app for physical device

---

## Environment Variables

### Backend `.env`

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-key              # used by Antigravity for all LLM steps
ANTIGRAVITY_API_KEY=your-antigravity-key    # Antigravity project credentials
GOOGLE_MAPS_API_KEY=your-google-cloud-key   # Geocoding + Routes + Places APIs
JWT_SECRET=your-random-secret-key
JWT_EXPIRE_HOURS=24
```

> **Google Cloud Key:** Go to [console.cloud.google.com](https://console.cloud.google.com/) → APIs & Services → Credentials → Create API Key.
> Enable: Geocoding API, Routes API, Places API, Distance Matrix API, Maps JavaScript API.

### Frontend `.env`

```env
EXPO_PUBLIC_API_URL=http://localhost:8000        # development
EXPO_PUBLIC_API_URL=https://karoo.onrender.com   # production (Render)
EXPO_PUBLIC_GOOGLE_MAPS_KEY=your-google-cloud-key
```

---

## Deployment

| Service | Platform | Cost |
|---------|----------|------|
| Backend API | **Render** (Web Service) | Free tier |
| Database | Supabase | Free tier |
| Mobile App | Expo Go | Free |
| Web App | Expo (web build) | Free |
| Google Cloud APIs | Google Cloud | Free tier (generous limits) |

### Deploy Backend to Render

1. Push your backend to GitHub
2. Go to [render.com](https://render.com) → New → **Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Add all environment variables under **Environment** tab
6. Click **Deploy** → your API will be live at `https://karoo.onrender.com`

---

## Assumptions & Limitations

### Assumptions
- Provider GPS coordinates are stored after geocoding their area (e.g., "F-10") using Google Geocoding API at registration time
- User's real-time location is fetched from device via Expo Location + Google Geolocation API
- Travel time is calculated at booking time, not updated continuously en route
- SMS OTP is simulated in development (real integration possible via Supabase Auth or Twilio)
- Booking payment is out of scope — only scheduling is handled
- Rating window is 72 hours after job completion

### Limitations
- No continuous GPS tracking of provider while en route (ETA is calculated once at booking)
- No in-app chat between user and provider after booking
- No payment gateway integration (JazzCash / EasyPaisa planned for v2)
- Background push notifications use Supabase Realtime, not FCM (app must be open)
- Google Routes API has rate limits — Distance Matrix is used as batch fallback

### Future Improvements
- FCM push notifications for background alerts
- Live en-route provider tracking (continuous location updates)
- In-app messaging between user and provider
- Payment integration (JazzCash / EasyPaisa)
- Provider background verification system
- Admin dashboard for platform management
- AI-powered demand forecasting for providers (best times to be available)

---

## Hackathon Deliverables Checklist

- [ ] Working prototype — Mobile App (Expo Go)
- [ ] Working prototype — Web App (optional)
- [ ] Demo video (3–5 minutes)
- [ ] Google Antigravity agent trace / logs
- [ ] This README

---

## Team

| Name | Role |
|------|------|
| Ismail Abdul Kareem | Backend + AI Agent + Google Cloud |
| [Teammate Name] | Frontend (Expo) |

---

*Built for Google Antigravity Hackathon — Challenge 2*
