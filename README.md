# 🤝 Karoo — AI Service Orchestrator

> AI-powered service booking agent and real-time marketplace for Pakistan's informal economy — find, book, track & chat in Urdu, Roman Urdu, or English.

**Hackathon:** Google Antigravity Hackathon — Challenge 2: AI Service Orchestrator for Informal Economy
**Deadline:** 20 May 2026
**Team:** Ismail Abdul Kareem

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [Architecture Overview](#architecture-overview)
5. [How Google Antigravity Was Used](#how-google-antigravity-was-used)
6. [Agents Developed](#agents-developed)
7. [Google Cloud Services](#google-cloud-services)
8. [Database Schema](#database-schema)
9. [API Endpoints](#api-endpoints)
10. [Bidirectional Rating System](#bidirectional-rating-system)
11. [Real-Time Messaging](#real-time-messaging)
12. [Setup & Installation](#setup--installation)
13. [Environment Variables](#environment-variables)
14. [Deployment](#deployment)
15. [Agent Trace Logging](#agent-trace-logging)
16. [Assumptions & Limitations](#assumptions--limitations)

---

## Project Overview

Karoo solves a critical problem in Pakistan's informal economy. Local service providers (plumbers, electricians, tutors, cleaners) operate through fragmented channels like WhatsApp and phone calls — without any structured booking platform. This results in inefficient discovery, lack of price transparency, and safety concerns.

**Karoo** is an autonomous agentic system that fully automates the lifecycle of informal services:

- **Natural Language Matching:** Users chat with an AI assistant in Urdu, Roman Urdu, or English
- **Intelligent Intent Extraction:** AI parses complex inputs to extract service type, location, and time
- **Geospatial Provider Discovery:** Coordinates geocoded via Google Cloud APIs, providers ranked by real travel time
- **End-to-End Service Flow:** Open marketplace, direct bookings, real-time status transitions, P2P messaging, and blind bidirectional ratings

### Example

```
User: "Mujhe kal subah G-11 mein plumber chahiye"

System:
  service_type → plumber
  location     → G-11 (geocoded: lat 33.68, lng 73.04)
  time         → tomorrow morning

Result:
  Top 3 providers ranked by ETA + rating + availability
  Booking confirmed → Provider notified → Reminder scheduled
  After completion → Both parties rate each other (blind review)
```

---

## Key Features

### Core Features
- **🎙️ Multilingual AI Chat:** English, Urdu script, and Roman Urdu support with context memory
- **📍 Real-Time Location Routing:** Google Routes API for precise travel times
- **💬 Real-Time P2P Chat (WebSocket):** Auto-initiated upon booking acceptance
- **⚖️ Mutual Bidirectional Ratings:** Blind review system — users rate providers, providers rate customer reliability
- **🛠️ Service Request Marketplace:** Users post open requests, providers browse and pick jobs
- **🔔 Real-Time Notifications:** Triggered at every booking state transition
- **📊 Provider AI Assistant:** Providers query daily schedule, open jobs, and earnings via AI chat
- **💰 Earnings Dashboard:** Providers track income per completed booking

### Advanced Features (Hackathon Requirements)
- **💵 Dynamic Pricing Engine:** Transparent pricing based on demand, urgency, distance, complexity, surge, and loyalty
- **📅 Scheduling Intelligence:** Double-booking prevention, travel-time buffers, alternate slot suggestions, auto-rescheduling
- **⚠️ Dispute Resolution System:** Automated dispute handling for no-shows, quality issues, price disagreements, time overruns
- **🔧 Job Complexity Classification:** Automatic classification (basic/intermediate/complex) with provider matching
- **📋 Service Quality Loop:** Real-time progress tracking, completion checklists, photo evidence, status updates

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Expo React Native | Cross-platform Web + Mobile (NativeWind/Tailwind) |
| **Backend** | FastAPI (Python) | Async REST API + WebSocket server |
| **Development IDE** | **Google Antigravity** | Main orchestrator for entire development lifecycle |
| **AI / LLM** | **Google Gemini 1.5 Flash** | Intent extraction, provider AI assistant, function calling |
| **Location** | Google Cloud Platform | Routes, Geocoding, Places APIs |
| **Database** | Supabase (PostgreSQL) | Users, bookings, ratings, messaging, disputes |
| **Realtime** | WebSockets + Supabase Realtime | Live chat + notifications |
| **Auth** | JWT (python-jose + bcrypt) | Role-based auth (user vs provider) |
| **Hosting** | Hugging Face Spaces | Backend deployment |

> **Note on Google Gemini:** This project uses **Google Gemini 1.5 Flash** as the main AI orchestrator for all agentic workflows including intent understanding, provider matching, scheduling decisions, pricing logic, and dispute resolution. Gemini's function calling capabilities power the MCP tool execution for geocoding, provider search, and booking management.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                  Expo App (Frontend)                          │
│            Web Browser + Android/iOS Devices                  │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP REST (JWT) / WebSocket
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                  FastAPI Backend Server                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              AI Agent Engine                           │  │
│  │       (Designed & built via Antigravity IDE)           │  │
│  │                                                        │  │
│  │  1. Natural language intent extraction (OpenRouter)    │  │
│  │  2. Geocoding via Google Geocoding API (MCP Tool)      │  │
│  │  3. Provider discovery from Supabase (MCP Tool)        │  │
│  │  4. Travel time via Google Routes API (MCP Tool)       │  │
│  │  5. 6-factor ranking algorithm                         │  │
│  │  6. Agent trace logging for every request              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  MCP Tools:                                                  │
│  • geocode_location()  → Google Geocoding API                │
│  • get_travel_time()   → Google Routes API                   │
│  • query_providers()   → Supabase                            │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    Supabase (PostgreSQL)                      │
│  users | providers | bookings | ratings | notifications      │
│  conversations | conversation_messages | service_requests    │
└──────────────────────────────────────────────────────────────┘
```

---

## How Google Gemini Was Used

**Google Gemini 1.5 Flash** is the **main AI orchestrator** for all intelligent workflows in Karoo. Every user interaction, provider matching decision, and service lifecycle event is powered by Gemini's advanced reasoning and function calling capabilities.

### Development Workflow via Antigravity

```
Phase 1: Architecture Planning
  Antigravity agent analyzed requirements
  Generated system design, DB schema, API contracts
  Created folder structure and file templates

Phase 2: Backend Implementation
  Agent implemented all 36 FastAPI endpoints
  MCP tools built: geocode, travel_time, provider search
  AI agent logic: intent extraction, ranking algorithm
  Bidirectional rating system
  WebSocket real-time messaging

Phase 3: Database Setup
  Agent generated complete SQL schema
  7 tables with indexes, triggers, constraints
  Supabase configuration

Phase 4: Testing & Debugging
  Agent ran 12-step integration test suite
  Fixed all bugs and edge cases
  Verified complete booking lifecycle

Phase 5: Frontend Development
  Agent designed all screens and components
  Implemented Expo React Native app
  Connected all API endpoints
```

### Antigravity Workflows Used

```
/setup-backend      → Scaffolded entire FastAPI project
/new-endpoint       → Created each API endpoint
/add-mcp-tool       → Built geocode + travel time tools
/fix-bug            → Debugged and fixed issues
/setup-supabase     → Generated database SQL
/add-notification   → Notification logic both sides
/generate-trace     → Agent trace for judges
/new-screen         → Frontend screen generation
```

### Agent Trace Evidence
All Antigravity conversation logs, workplans, and task traces are included in the submission ZIP file as required by hackathon guidelines.

---

## Agents Developed

### 1. User Intent Agent (`agents/karoo_agent.py`)
```
Purpose: Extract service booking intent from natural language
Input:   "Mujhe kal plumber chahiye F-10 mein"
Output:  { service_type, location, time, confidence }
LLM:     Google Gemini 1.5 Flash
Trace:   Logged to backend/logs/traces/*.json
```

### 2. Provider Ranking Agent (`agents/ranking.py`)
```
Purpose: Score and rank providers using 6+ factors
Formula: 
  Score = (rating × 0.25) + (1/ETA × 0.20) + 
          (complexity_match × 0.20) + (availability × 0.15) + 
          (on_time × 0.10) + (price_fit × 0.05) + (recency × 0.05)
Input:   List of providers + user location + job complexity
Output:  Top 3 ranked providers with scores
```

### 3. Dynamic Pricing Agent (`agents/pricing_agent.py`)
```
Purpose: Calculate transparent, fair pricing
Factors: Base rate, distance, urgency, complexity, surge, loyalty
Formula:
  Base Price + Distance Fee + Urgency Fee + Complexity Fee
  × Surge Multiplier - Loyalty Discount = Final Price
Output:  Detailed price breakdown with transparency
```

### 4. Scheduling Intelligence Agent (`agents/scheduling_agent.py`)
```
Purpose: Prevent conflicts and optimize provider schedules
Features:
  - Double-booking prevention with travel-time buffers
  - Alternate slot suggestions
  - Auto-rescheduling on cancellation
  - Waitlist management
Output:  Available slots, conflict detection, rescheduling decisions
```

### 5. Job Complexity Classifier (`agents/complexity_classifier.py`)
```
Purpose: Classify jobs as basic/intermediate/complex
Factors: Keywords, urgency, location type, quantity indicators
Output:  
  - Complexity level
  - Required experience (0/2/5 years)
  - Required tools
  - Estimated duration
  - Certification requirements
```

### 6. Dispute Resolver Agent (`agents/dispute_resolver.py`)
```
Purpose: Automatically resolve common disputes
Types Handled:
  - No-show (provider or user)
  - Quality issues
  - Price disagreements
  - Time overruns
  - Unprofessional behavior
Logic: Context-aware resolution with refund/compensation calculations
Output: Resolution decision, refund amount, actions taken
```

### 7. Provider AI Assistant (`routes/chat.py → /api/chat/provider`)
```
Purpose: Help providers find jobs, check bookings, track earnings
Intents: find_requests | check_bookings | check_earnings
Input:   "Aaj kitni bookings hain?"
Output:  Structured results + agent trace
```

### MCP Tools (`mcp/tools/`)
```
geocode_location()   → Google Geocoding API
get_travel_time()    → Google Routes API
search_providers()   → Supabase query with complexity matching
check_availability() → Booking conflict check with buffers
calculate_price()    → Dynamic pricing engine
classify_job()       → Complexity classification
```

---

## Google Cloud Services

All APIs enabled at console.cloud.google.com:

| API | Use |
|-----|-----|
| Geocoding API | Convert area names to lat/lng |
| Routes API | Real driving time per provider |
| Places API | Location validation |
| Maps JavaScript API | Map view in frontend |

---

## Database Schema

### Tables Overview
```
users               → Both users and providers (role field)
providers           → Extended provider profile
bookings            → Service booking contracts
ratings             → Bidirectional blind reviews
notifications       → Event-driven alerts both sides
service_requests    → Open marketplace requests
conversations       → P2P messaging rooms
conversation_messages → Individual messages
```

### Key Fields

**users**
```sql
id, name, phone (unique), password_hash, role (user|provider),
reliability_score FLOAT DEFAULT 5.0,  -- rated by providers
total_ratings INTEGER DEFAULT 0
```

**providers**
```sql
id, user_id (FK), service_type, area, lat, lng,
rating FLOAT, total_ratings INTEGER,
on_time_score FLOAT DEFAULT 5.0,
review_recency FLOAT DEFAULT 1.0,
rate_per_hour INTEGER, is_available, is_online
```

**bookings**
```sql
id, user_id (FK), provider_id (FK),
service_type, location, scheduled_at,
status (pending|confirmed|completed|cancelled),
booked_via (ai_chat|browse|request),
user_lat, user_lng, eta_minutes,
budget INTEGER, agreed_rate INTEGER
```

**ratings**
```sql
id, booking_id (FK), rater_id (FK), ratee_id (FK),
rater_role (user|provider), stars (1-5),
review_text, tags TEXT[]
```

**conversations + conversation_messages**
```sql
conversations: booking_id (unique FK), user_id, provider_id,
               last_message, user_unread_count, provider_unread_count

conversation_messages: conversation_id (FK), sender_id (FK),
                       sender_role, message, is_read
```

---

## API Endpoints

**Base URL (Production):** `https://ismail233290-karoo-pk.hf.space`
**Total Endpoints:** 50+ (REST) + 1 WebSocket

### Auth (3)
```
POST /auth/register    → Register user or provider
POST /auth/login       → Get JWT token
GET  /auth/me          → Get profile 🔒
```

### AI Chat (3)
```
POST /api/chat          → User: find providers via AI 🔒
GET  /api/chat/history  → Chat history 🔒
POST /api/chat/provider → Provider: find jobs via AI 🔒
```

### Workers (4)
```
GET /api/workers               → Browse providers (filters) 🔒
GET /api/workers/{id}          → Provider full profile 🔒
PUT /api/workers/profile       → Update profile 🔒 Provider
PUT /api/workers/availability  → Toggle online 🔒 Provider
```

### Bookings (7)
```
POST /api/bookings                    → Create booking with pricing 🔒 User
GET  /api/bookings/my                 → My bookings 🔒
GET  /api/bookings/earnings           → Earnings 🔒 Provider
PUT  /api/bookings/{id}/accept        → Accept 🔒 Provider
PUT  /api/bookings/{id}/reject        → Reject 🔒 Provider
PUT  /api/bookings/{id}/cancel        → Cancel 🔒 User
PUT  /api/bookings/{id}/complete      → Complete 🔒 Provider
```

### Service Progress (3) **NEW**
```
POST /api/service-progress/{id}/progress   → Update status 🔒 Provider
GET  /api/service-progress/{id}/progress   → Get updates 🔒
POST /api/service-progress/{id}/checklist  → Submit checklist 🔒 Provider
GET  /api/service-progress/{id}/checklist  → Get checklist 🔒
```

### Disputes (5) **NEW**
```
POST /api/disputes              → Create dispute 🔒
GET  /api/disputes/my           → My disputes 🔒
GET  /api/disputes/{id}         → Dispute details 🔒
PUT  /api/disputes/{id}/resolve → Resolve dispute 🔒
PUT  /api/disputes/{id}/escalate → Escalate to human 🔒
```

### Service Requests (4)
```
POST /api/requests            → Post open request 🔒 User
GET  /api/requests/open       → Browse requests 🔒 Provider
PUT  /api/requests/{id}/accept → Accept request 🔒 Provider
GET  /api/requests/my         → My requests 🔒 User
```

### Notifications (3)
```
GET /api/notifications              → Get all 🔒
PUT /api/notifications/{id}/read    → Mark read 🔒
PUT /api/notifications/read-all     → Mark all read 🔒
```

### Ratings (4)
```
POST /api/ratings                      → Submit rating 🔒
GET  /api/ratings/provider/{id}        → Provider reviews 🔒
GET  /api/ratings/user/{id}            → User reliability 🔒 Provider
GET  /api/ratings/pending              → Pending ratings 🔒
```

### Conversations (5)
```
POST /api/conversations                        → Create room 🔒
GET  /api/conversations                        → My conversations 🔒
GET  /api/conversations/{id}/messages          → Get messages 🔒
POST /api/conversations/{id}/messages          → Send message 🔒
WS   /api/conversations/ws/{user_id}?token=JWT → Real-time 🔒
```

---

## Bidirectional Rating System

Unlike traditional one-way reviews, Karoo implements mutual accountability:

```
Job Completed
      │
      ├── User rates Provider (1-5 ⭐)
      │   Tags: punctual, professional, quality_work, affordable
      │   → Updates provider.rating (rolling average)
      │
      └── Provider rates User (1-5 ⭐)
          Tags: responsive, on_time_payment, clear_requirements
          → Updates user.reliability_score

Rules:
  • Blind review — neither sees until both submit or 72hrs pass
  • Cannot rate twice for same booking
  • Score < 3.0 → "Caution" badge shown to provider
  • Score < 2.0 → Provider can auto-decline
```

---

## Real-Time Messaging

WebSocket connection established after booking confirmed:

```
Connection: ws://host/api/conversations/ws/{user_id}?token=JWT

Incoming event:
{
  "type": "new_message",
  "conversation_id": "uuid",
  "message": { sender_role, message, created_at }
}

Heartbeat: ping → pong (cellular network stability)
```

Auto-created conversation when provider accepts booking.

---

## Setup & Installation

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

Server: `http://localhost:8000`
Swagger: `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npx expo start
# w → web browser
# a → Android
# Scan QR → Expo Go
```

---

## Environment Variables

### Backend `.env`
```env
SUPABASE_URL=https://hoagwivqfsdhaoyjixdf.supabase.co
SUPABASE_KEY=your-service-role-key
OPENROUTER_API_KEY=your-openrouter-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
JWT_SECRET=your-jwt-secret
JWT_EXPIRE_HOURS=24
```

### Frontend `.env`
```env
EXPO_PUBLIC_API_URL=https://ismail233290-karoo-pk.hf.space
EXPO_PUBLIC_GOOGLE_MAPS_KEY=your-google-maps-key
```

---

## Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Backend | Hugging Face Spaces | https://ismail233290-karoo-pk.hf.space |
| Database | Supabase Cloud | hoagwivqfsdhaoyjixdf.supabase.co |
| Frontend Web | Vercel (optional) | TBD |
| Mobile | Expo Go / APK | TBD |

---

## Agent Trace Logging

Every `/api/chat` request produces a full agent trace:

```
=== KAROO AGENT TRACE ===
Session: abc12345
Input: "Mujhe plumber chahiye F-10 mein"

[STEP 1] Intent Extraction
  Tool: openrouter_parse
  Output: { service_type: "plumber", location: "F-10", confidence: 0.95 }
  Time: 312ms ✅

[STEP 2] Location Geocoding
  Tool: geocode_location (Google Geocoding API)
  Output: { lat: 33.68, lng: 73.04 }
  Time: 187ms ✅

[STEP 3] Provider Search
  Tool: query_providers (Supabase)
  Output: 5 providers found
  Time: 143ms ✅

[STEP 4] Ranking
  Tool: ranking_agent
  Decision: Ali Khan selected (score: 0.91)
  Reason: rating 4.8, ETA 8min, available ✅
  Time: 12ms ✅

Total: 654ms | Outcome: SUCCESS
=== END TRACE ===
```

Traces saved to: `backend/logs/traces/*.json`
Returned in API response: `agent_trace` field

---

## Assumptions & Limitations

### Assumptions
- Location stored as area name — no live GPS tracking
- Provider availability toggled manually
- Payment out of scope — scheduling only
- OpenRouter used for LLM (as per hackathon guidelines — any LLM endpoint allowed)

### Limitations
- No real-time GPS tracking en route
- Background push needs FCM (using Supabase Realtime for foreground)
- No payment gateway

### Future Improvements
- Gemini API integration (Google native)
- JazzCash/EasyPaisa payment
- Live GPS tracking
- FCM push notifications
- Admin moderation dashboard

---

## Hackathon Submission Checklist

- [ ] Mobile App Link (Expo Go / APK)
- [ ] GitHub Repository (public)
- [ ] Demo Video 3-5 min
- [ ] Antigravity Usage Video 2-3 min
- [ ] README (this file)
- [ ] Antigravity Logs ZIP
- [ ] CNIC front + back (all members)
- [ ] Submission form filled

**Deadline: 20 May 2026 (end of day)**

---

## Team

| Name | Role |
|------|------|
| Ismail Abdul Kareem | Full Stack + AI Agent + Backend |

---

*Developed with 💚 using Google Antigravity — Google Antigravity Hackathon 2026*