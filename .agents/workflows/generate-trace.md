---
description: Produces formatted agent trace log for hackathon judges. Shows workplan, MCP tool calls, decisions, timing, and outcome. Saves to JSON and API response.
---

Generate a complete formatted agent trace for the Karoo AI system.

Ask me:
1. What user message or action triggered this trace?
2. Which MCP tools were called?
3. What was the final output?

Then generate a trace in this exact format:

=== KAROO AGENT TRACE ===
Timestamp: {datetime}
Session ID: {uuid}
User ID: {user_id}

--- WORKPLAN ---
Goal: {what agent is trying to achieve}
Steps planned:
  1. Extract intent from user message
  2. Search available providers
  3. Check provider availability
  4. Rank by score
  5. Return top results
  6. Create booking if user confirms

--- STEP EXECUTION ---

[STEP 1] Intent Extraction
  Tool called: gemini_parse
  Input: "{user_message}"
  Output: {
    "service_type": "plumber",
    "location": "F-10",
    "time": "tomorrow morning",
    "confidence": 0.94
  }
  Status: SUCCESS
  Time: 312ms

[STEP 2] Provider Search
  Tool called: search_providers
  Input: { "service": "plumber", "area": "F-10" }
  Supabase query: SELECT * FROM providers WHERE service_type='plumber' AND area='F-10' AND is_available=true
  Output: 5 providers found
  Status: SUCCESS
  Time: 187ms

[STEP 3] Availability Check
  Tool called: check_availability
  Input: { "provider_ids": [...], "time": "tomorrow 10am" }
  Output: 3 providers available
  Status: SUCCESS
  Time: 143ms

[STEP 4] Ranking Decision
  Algorithm: score = (rating × 0.5) + (1/distance × 0.3) + (reviews × 0.2)
  Results:
    Ali Khan:    score=0.91  rating=4.8  distance=1.2km  → RANK 1
    Usman Co:    score=0.84  rating=4.5  distance=2.1km  → RANK 2
    Tariq Fix:   score=0.79  rating=4.3  distance=2.8km  → RANK 3
  Decision: Ali Khan selected as primary recommendation
  Time: 12ms

[STEP 5] Response Generated
  Output: 3 provider cards returned to frontend
  Status: SUCCESS
  Time: 8ms

--- SUMMARY ---
Total steps: 5
Total time: 662ms
Tools called: gemini_parse, search_providers, check_availability
Decision made: Ranked 3 providers, Ali Khan recommended
Outcome: SUCCESS

=== END TRACE ===

Save this trace to:
- backend/logs/traces/{session_id}.json (machine readable)
- Print to terminal during development
- Return agent_trace field in API response for frontend to display

Also create backend/utils/tracer.py with:
- AgentTrace class
- add_step() method
- to_json() method
- to_string() method (human readable)