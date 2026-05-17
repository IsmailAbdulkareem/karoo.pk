---
trigger: always_on
---

All user-facing messages must work in Urdu, Roman Urdu, 
and English. Error messages should be simple and friendly.
When Gemini extracts intent, confidence below 0.6 means 
ask clarifying question before proceeding.
Example friendly error: "Kuch masla aa gaya, dobara try karo"
Never return raw technical errors to frontend.