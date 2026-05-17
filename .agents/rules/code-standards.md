---
trigger: always_on
---

Always use async/await in FastAPI.
Use Pydantic for all request and response models.
All endpoints need JWT auth except /auth routes.
Check user role inside endpoint before executing.
Wrap all Supabase calls in try/except.
Return meaningful Urdu-friendly error messages.
Add docstring to every function and class.
Never hardcode secrets — always use .env variables.