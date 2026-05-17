---
description: Scaffolds complete Karoo FastAPI project — folder structure, routes, Supabase client, JWT auth, CORS, schemas, and requirements.txt. Run once at project start.
---

Set up the complete Karoo FastAPI backend project with the following requirements:

PROJECT CONTEXT:
Karoo is an AI-powered service booking platform for Pakistan's informal economy. 
Users can book plumbers, electricians, tutors and other home service providers 
through AI chat, manual browsing, or by posting open requests. Providers can 
accept AI-matched bookings or browse and pick open jobs themselves.

FOLDER STRUCTURE TO CREATE:
backend/
├── main.py
├── requirements.txt
├── .env.example
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── chat.py
│   ├── workers.py
│   ├── requests.py
│   ├── bookings.py
│   ├── notifications.py
│   └── reviews.py
├── agents/
│   ├── __init__.py
│   ├── antigravity_agent.py
│   └── ranking.py
├── mcp/
│   ├── __init__.py
│   ├── server.py
│   └── tools/
│       ├── __init__.py
│       ├── search_providers.py
│       ├── create_booking.py
│       ├── check_availability.py
│       ├── get_open_requests.py
│       └── search_web.py
├── db/
│   ├── __init__.py
│   └── supabase_client.py
└── models/
    ├── __init__.py
    └── schemas.py

REQUIREMENTS.TXT MUST INCLUDE:
fastapi==0.110.0
uvicorn==0.29.0
supabase==2.4.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
httpx==0.27.0
pydantic==2.6.0
google-generativeai==0.5.0
python-multipart==0.0.9

MAIN.PY REQUIREMENTS:
- FastAPI app with title "Karoo API"
- CORS middleware allowing all origins (for development)
- Include all routers with prefixes: /auth, /api/chat, /api/workers, /api/requests, /api/bookings, /api/notifications, /api/reviews
- Health check endpoint GET / returning {"status": "Karoo API running"}
- Global exception handler for unhandled errors

SUPABASE CLIENT (db/supabase_client.py):
- Load SUPABASE_URL and SUPABASE_KEY from .env
- Create and export a single supabase client instance
- Add a test_connection() function

JWT AUTH UTILITY:
- Create auth/jwt_handler.py
- Functions: create_token(user_id, role), verify_token(token)
- JWT expiry from .env JWT_EXPIRE_HOURS
- Dependency function get_current_user() for protected routes

.ENV.EXAMPLE:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-api-key
JWT_SECRET=your-random-secret-key
JWT_EXPIRE_HOURS=24

SCHEMAS (models/schemas.py):
Create Pydantic models for:
- UserRegister: name, phone, email, password, city, role
- UserLogin: phone, password
- TokenResponse: access_token, token_type, role
- ChatMessage: message, user_id
- BookingCreate: provider_id, service_type, location, scheduled_at, note, booked_via
- BookingStatusUpdate: status
- ServiceRequestCreate: service_type, location, scheduled_at, budget, description
- ProviderUpdate: service_type, area, rate_per_hour, bio, is_available
- ReviewCreate: booking_id, provider_id, rating, comment
- NotificationRead: is_read

After creating all files, run:
pip install -r requirements.txt
uvicorn main:app --reload

Confirm all files created and server starts successfully on port 8000.