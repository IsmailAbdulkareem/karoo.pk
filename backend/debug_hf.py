"""Debug live HF API responses."""
import requests, sys

BASE = "https://ismail233290-karoo-pk.hf.space"

# Root
r = requests.get(f"{BASE}/", timeout=60)
print(f"Root: status={r.status_code}, body={r.text[:200]}")

# Register
r = requests.post(f"{BASE}/auth/register", json={
    "name": "Debug User", "phone": "03009998877",
    "password": "test123", "role": "user"
}, timeout=120)
print(f"\nRegister: status={r.status_code}")
if r.status_code == 200:
    d = r.json()
    print(f"  Keys: {list(d.keys())}")
    print(f"  access_token present: {'access_token' in d}")
    if 'access_token' in d:
        print(f"  Token preview: {d['access_token'][:30]}...")
else:
    print(f"  Error: {r.text[:500]}")
    # Try login anyway
    r2 = requests.post(f"{BASE}/auth/login", json={
        "phone": "03009998877", "password": "test123"
    }, timeout=120)
    print(f"\nLogin: status={r2.status_code}")
    if r2.status_code == 200:
        d2 = r2.json()
        print(f"  Keys: {list(d2.keys())}")
        print(f"  access_token present: {'access_token' in d2}")
    else:
        print(f"  Error: {r2.text[:500]}")

# Test health endpoint
r = requests.get(f"{BASE}/health", timeout=30)
print(f"\nHealth: {r.status_code} - {r.text[:100]}")
