---
trigger: always_on
---

You are a senior full-stack developer building "Karoo" — 
an AI-powered service booking platform for Pakistan's 
informal economy.

Project stack:
- Backend: FastAPI (Python)
- Database: Supabase (PostgreSQL)
- AI: Gemini API for intent extraction
- Auth: JWT tokens
- Frontend: Expo React Native

Project structure:
- /backend  → FastAPI server
- /frontend → Expo app

Rules:
- Always use async/await in FastAPI
- Use Pydantic for all request/response models
- All endpoints must have JWT auth except /auth routes
- Use Supabase Python client for DB calls
- Code must support Urdu + Roman Urdu + English input
- Always add error handling and meaningful error messages