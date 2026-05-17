---
description: Generates a FastAPI endpoint with Pydantic models, JWT auth guard, Supabase query, role check, and error handling. Asks route, method, and purpose first.
---

Create a new FastAPI endpoint for the Karoo backend.

Ask me these questions one by one before writing any code:
1. What is the endpoint route? (e.g. /api/bookings/:id/accept)
2. What HTTP method? (GET, POST, PUT, DELETE)
3. What does this endpoint do? (describe in plain English)
4. Which route file should it go in? (auth, chat, workers, requests, bookings, notifications, reviews)
5. Is JWT authentication required? (yes/no)
6. If yes, who can access it? (user only, provider only, or both)

After I answer, generate the complete endpoint following these rules:

CODE STANDARDS:
- Use async def for all endpoint functions
- Add Pydantic model for request body if POST/PUT
- Add Pydantic model for response
- Use Depends(get_current_user) for auth
- Check role inside endpoint: if current_user["role"] != "provider": raise HTTPException(403)
- All Supabase calls wrapped in try/except
- Return meaningful error messages with correct HTTP status codes
- Add docstring to every function

ERROR HANDLING PATTERN:
try:
    result = supabase.table("table_name").select("*").execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Not found")
    return result.data
except HTTPException:
    raise
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

NOTIFICATION TRIGGER:
If this endpoint creates or updates a booking, also create notification records 
in the notifications table for both user and provider with appropriate title and body.

After writing the code:
1. Show me the complete endpoint code
2. Show me where exactly to paste it in the route file
3. Show the Pydantic models to add to schemas.py
4. Show example curl command to test it
5. List any new imports needed