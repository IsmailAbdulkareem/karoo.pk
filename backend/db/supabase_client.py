import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing required environment variables: SUPABASE_URL and SUPABASE_KEY must be set. "
        "Please configure them in your Hugging Face Space settings."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
