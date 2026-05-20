"""Test live Hugging Face backend API."""
import requests, random, sys

BASE = "https://ismail233290-karoo-pk.hf.space"

passed = 0
failed = 0

def test(step, desc, fn):
    global passed, failed
    try:
        result = fn()
        if result.get("pass", False):
            print(f"  [{step}] PASS: {desc} - {result.get('msg','')}")
            passed += 1
        else:
            print(f"  [{step}] FAIL: {desc} - {result.get('msg','')}")
            failed += 1
    except Exception as e:
        print(f"  [{step}] FAIL: {desc} - {str(e)}")
        failed += 1

def api(method, path, token=None, body=None):
    h = {"Content-Type": "application/json"}
    if token: h["Authorization"] = f"Bearer {token}"
    try:
        r = requests.request(method, f"{BASE}{path}", headers=h, json=body, timeout=60)
        return r
    except requests.Timeout:
        class TimeoutResp: pass
        r = TimeoutResp()
        r.status_code = 408
        r._json = lambda: {"detail": "Timeout"}
        r.text = "Timeout"
        return r

suffix = str(random.randint(10000000, 99999999))
user_phone = f"0300{suffix}"
provider_phone = f"0301{suffix}"

print(f"Testing LIVE API: {BASE}")
print(f"User phone: {user_phone}")
print(f"Provider phone: {provider_phone}")

# STEP 1: AUTH
print("\n" + "="*50)
print("STEP 1: AUTHENTICATION")
print("="*50)

r = api("POST", "/auth/register", body={"name":"Test User","phone":user_phone,"password":"test123","role":"user"})
USER_TOKEN = r.json().get("access_token","") if r.status_code == 200 else ""
test("1.1", "Register User", lambda: {"pass": r.status_code == 200 and USER_TOKEN, "msg": "OK"})

r = api("POST", "/auth/register", body={"name":"Ali Plumber","phone":provider_phone,"password":"provider123","role":"provider"})
PROVIDER_TOKEN = r.json().get("access_token","") if r.status_code == 200 else ""
PROVIDER_USER_ID = r.json().get("user_id","") if r.status_code == 200 else ""
test("1.2", "Register Provider", lambda: {"pass": r.status_code == 200 and PROVIDER_TOKEN, "msg": "OK"})

r = api("POST", "/auth/register", body={"name":"Another","phone":user_phone,"password":"test456","role":"user"})
test("1.3", "Duplicate Phone 400", lambda: {"pass": r.status_code == 400, "msg": f"Status {r.status_code}"})

r = api("POST", "/auth/login", body={"phone":user_phone, "password":"test123"})
test("1.4", "Login", lambda: {"pass": r.status_code == 200, "msg": "OK"})

r = api("GET", "/auth/me", token=USER_TOKEN)
test("1.5", "Get Current User", lambda: {"pass": r.status_code == 200, "msg": f"{r.json().get('name')}"})

# STEP 2: PROVIDER
print("\n" + "="*50)
print("STEP 2: PROVIDER PROFILE")
print("="*50)

r = api("PUT", "/api/workers/profile", token=PROVIDER_TOKEN, body={
    "service_type": "plumber", "area": "Rawalpindi", "rate_per_hour": 500,
    "bio": "10 saal ka tajurba", "is_available": True, "is_online": True
})
PROVIDER_ID = r.json().get("provider", {}).get("id") if r.status_code == 200 else None
test("2.1", "Update Profile", lambda: {"pass": r.status_code == 200 and PROVIDER_ID, "msg": f"ID: {PROVIDER_ID[:10] if PROVIDER_ID else 'N/A'}..."})

r = api("GET", "/api/workers", token=USER_TOKEN)
test("2.2", "Browse Providers", lambda: {"pass": r.status_code == 200, "msg": "OK"})

r = api("GET", "/api/workers?service_type=plumber", token=USER_TOKEN)
test("2.3", "Filter by Service", lambda: {"pass": r.status_code == 200, "msg": "OK"})

if PROVIDER_ID:
    r = api("GET", f"/api/workers/{PROVIDER_ID}", token=USER_TOKEN)
    test("2.5", "Get Provider by ID", lambda: {"pass": r.status_code == 200, "msg": f"{r.json().get('name')}"})

r = api("PUT", "/api/workers/availability?is_online=true&is_available=true", token=PROVIDER_TOKEN)
test("2.6", "Update Availability", lambda: {"pass": r.status_code == 200, "msg": "OK"})

r = api("PUT", "/api/workers/profile", token=USER_TOKEN, body={"service_type":"electrician"})
test("2.7", "User 403", lambda: {"pass": r.status_code == 403, "msg": "OK"})

# STEP 3: CHAT
print("\n" + "="*50)
print("STEP 3: AI CHAT")
print("="*50)

r = api("POST", "/api/chat", token=USER_TOKEN, body={"message":"Mujhe plumber chahiye Rawalpindi mein"})
d = r.json() if r.status_code == 200 else {}
test("3.1", "Chat Urdu", lambda: {"pass": r.status_code == 200, "msg": f"trace: {bool(d.get('agent_trace'))}"})

r = api("POST", "/api/chat", token=USER_TOKEN, body={"message":"I need an electrician in G-11"})
test("3.2", "Chat English", lambda: {"pass": r.status_code == 200, "msg": "OK"})

r = api("POST", "/api/chat", token=USER_TOKEN, body={"message":"hello"})
d = r.json() if r.status_code == 200 else {}
test("3.3", "Greeting", lambda: {"pass": r.status_code == 200 and d.get("needs_clarification"), "msg": f"clarification: {d.get('needs_clarification')}"})

r = api("GET", "/api/chat/history", token=USER_TOKEN)
test("3.4", "Chat History", lambda: {"pass": r.status_code == 200, "msg": "OK"})

# STEP 4: BOOKING
print("\n" + "="*50)
print("STEP 4: BOOKING LIFECYCLE")
print("="*50)

BOOKING_ID = None
if PROVIDER_ID:
    r = api("POST", "/api/bookings", token=USER_TOKEN, body={
        "provider_id": PROVIDER_ID, "service_type": "plumber",
        "location": "F-10 Islamabad", "scheduled_at": "2026-05-21 10:00",
        "note": "Pipe leak", "booked_via": "chat"
    })
    BOOKING_ID = r.json().get("id") if r.status_code == 200 else None
    test("4.1", "Create Booking", lambda: {"pass": r.status_code == 200 and BOOKING_ID, "msg": f"ID: {BOOKING_ID[:10] if BOOKING_ID else 'N/A'}..."})

    r = api("GET", "/api/bookings/my", token=USER_TOKEN)
    test("4.2", "Get My Bookings", lambda: {"pass": r.status_code == 200, "msg": "OK"})

    if BOOKING_ID:
        r = api("PUT", f"/api/bookings/{BOOKING_ID}/accept", token=PROVIDER_TOKEN)
        d = r.json() if r.status_code == 200 else {}
        test("4.3", "Accept Booking", lambda: {"pass": r.status_code == 200 and d.get("status")=="confirmed", "msg": f"status: {d.get('status')}"})

        r = api("PUT", f"/api/bookings/{BOOKING_ID}/complete", token=PROVIDER_TOKEN)
        d = r.json() if r.status_code == 200 else {}
        test("4.4", "Complete Booking", lambda: {"pass": r.status_code == 200 and d.get("status")=="completed", "msg": f"status: {d.get('status')}"})

# STEP 5: RATINGS
print("\n" + "="*50)
print("STEP 5: RATINGS")
print("="*50)

if BOOKING_ID:
    r = api("POST", "/api/ratings", token=USER_TOKEN, body={
        "booking_id": BOOKING_ID, "ratee_id": PROVIDER_USER_ID,
        "stars": 5, "review_text": "Excellent!", "tags": ["punctual","professional"]
    })
    test("5.1", "User Rates Provider", lambda: {"pass": r.status_code == 200, "msg": "OK"})

    uid = api("GET", "/auth/me", token=USER_TOKEN).json().get("id","")
    r = api("POST", "/api/ratings", token=PROVIDER_TOKEN, body={
        "booking_id": BOOKING_ID, "ratee_id": uid,
        "stars": 5, "review_text": "Great customer", "tags": ["responsive"]
    })
    test("5.2", "Provider Rates User", lambda: {"pass": r.status_code == 200, "msg": "OK"})

    r = api("POST", "/api/ratings", token=USER_TOKEN, body={
        "booking_id": BOOKING_ID, "ratee_id": PROVIDER_USER_ID, "stars": 4
    })
    test("5.6", "Duplicate 400", lambda: {"pass": r.status_code == 400, "msg": "OK"})

r = api("GET", f"/api/ratings/provider/{PROVIDER_USER_ID}", token=USER_TOKEN)
test("5.3", "Provider Ratings", lambda: {"pass": r.status_code == 200, "msg": "OK"})

r = api("GET", "/api/ratings/pending", token=USER_TOKEN)
test("5.5", "Pending Ratings", lambda: {"pass": r.status_code == 200, "msg": "OK"})

# STEP 6: NOTIFICATIONS
print("\n" + "="*50)
print("STEP 6: NOTIFICATIONS")
print("="*50)

r = api("GET", "/api/notifications", token=USER_TOKEN)
d = r.json() if r.status_code == 200 else []
test("6.1", "Get Notifications", lambda: {"pass": r.status_code == 200, "msg": f"{len(d) if isinstance(d,list) else 0} notifications"})

r = api("PUT", "/api/notifications/read-all", token=USER_TOKEN)
test("6.3", "Mark All Read", lambda: {"pass": r.status_code == 200, "msg": "OK"})

# STEP 7: REQUESTS
print("\n" + "="*50)
print("STEP 7: SERVICE REQUESTS")
print("="*50)

r = api("POST", "/api/requests", token=USER_TOKEN, body={
    "service_type": "electrician", "location": "G-11 Islamabad",
    "scheduled_at": "2026-05-21 14:00", "budget": 800,
    "description": "Install ceiling fan"
})
REQUEST_ID = r.json().get("id") if r.status_code == 200 else None
test("7.1", "Create Request", lambda: {"pass": r.status_code == 200 and REQUEST_ID, "msg": "OK"})

r = api("GET", "/api/requests/open", token=PROVIDER_TOKEN)
test("7.2", "Browse Open", lambda: {"pass": r.status_code == 200, "msg": "OK"})

r = api("GET", "/api/requests/open?service_type=electrician", token=PROVIDER_TOKEN)
test("7.3", "Filter Requests", lambda: {"pass": r.status_code == 200, "msg": "OK"})

if REQUEST_ID:
    r = api("PUT", f"/api/requests/{REQUEST_ID}/accept", token=PROVIDER_TOKEN)
    test("7.4", "Accept Request", lambda: {"pass": r.status_code == 200, "msg": f"Booking created"})

r = api("GET", "/api/requests/my", token=USER_TOKEN)
test("7.5", "My Requests", lambda: {"pass": r.status_code == 200, "msg": "OK"})

# ======================
print("\n" + "="*50)
print(f"RESULTS: {passed} PASSED | {failed} FAILED")
print("="*50)
if failed == 0:
    print("LIVE API READY FOR PRODUCTION!")
else:
    print(f"{failed} tests failed")
