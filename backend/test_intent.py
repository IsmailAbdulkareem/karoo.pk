import asyncio
from agents.intent_agent import extract_intent

async def test():
    print("Testing Gemini Intent Agent...\n")
    
    r1 = await extract_intent("Mujhe kal plumber chahiye F-10 mein")
    print("Test 1 (Urdu/Roman):", r1)
    print()
    
    r2 = await extract_intent("I need an electrician in DHA tomorrow morning")
    print("Test 2 (English):", r2)
    print()
    
    r3 = await extract_intent("AC theek karwana hai")
    print("Test 3 (Vague):", r3)
    print()

asyncio.run(test())
