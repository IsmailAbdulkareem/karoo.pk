import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello")
    print(f"✓ API Key is valid!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ API Key test failed: {e}")
