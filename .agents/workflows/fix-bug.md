---
description: Debugs errors in Karoo backend or frontend. Finds root cause, applies fix, checks same bug elsewhere in codebase, adds logging to prevent repeat failures.
---

Debug and fix the current error in the Karoo project.

STEP 1 - GATHER INFORMATION:
Ask me:
1. Paste the full error message or stack trace
2. Which file and function is causing it?
3. What were you trying to do when it happened?
4. Is it a backend (FastAPI) or frontend (Expo) error?

STEP 2 - ANALYZE:
- Read the full stack trace carefully
- Identify the exact line causing the error
- Identify the root cause (not just the symptom)
- Check if related files have the same issue

STEP 3 - COMMON KAROO BUG PATTERNS TO CHECK:

FastAPI errors:
- Supabase client not initialized → check db/supabase_client.py
- JWT token missing from header → check get_current_user dependency
- Pydantic validation error → check request body matches schema
- CORS error → check main.py CORS middleware configuration
- 422 Unprocessable Entity → request body fields missing or wrong type

Supabase errors:
- Row not found → check if .data is empty before accessing
- Permission denied → check if using service_role key not anon key
- Foreign key violation → check if referenced record exists first

Expo/React Native errors:
- Network request failed → check API_URL in .env points to correct backend
- Undefined is not an object → check API response structure before accessing
- AsyncStorage error → check if token exists before parsing

STEP 4 - FIX:
- Apply the fix directly to the file
- Add try/except if missing
- Add console.log or print statements for debugging
- Add input validation if needed

STEP 5 - VERIFY:
- Show the fixed code
- Explain what was wrong and why
- Show how to test the fix
- Check 3 other places in codebase where same bug might exist
- Add comment in code explaining why this fix was needed