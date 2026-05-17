import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read schema file
with open('../database_schema.sql', 'r') as f:
    schema_sql = f.read()

# Split into individual statements
statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

print(f"Executing {len(statements)} SQL statements...")

for i, statement in enumerate(statements, 1):
    if statement:
        try:
            # Use rpc to execute raw SQL
            result = supabase.rpc('exec_sql', {'query': statement}).execute()
            print(f"✓ Statement {i}/{len(statements)} executed")
        except Exception as e:
            print(f"✗ Statement {i} failed: {str(e)[:100]}")

print("\nSchema creation complete!")
