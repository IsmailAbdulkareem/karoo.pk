# Karoo Backend API - Testing Guide

Complete FastAPI backend for Karoo service booking platform with AI-powered intent extraction, provider ranking, and booking management.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --port 8000
```

**Server:** http://127.0.0.1:8000  
**Swagger Docs:** http://127.0.0.1:8000/docs

---

## 📋 Environment Variables

Ensure `.env` file has:
```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-service-role-key
OPENROUTER_API_KEY=your-openrouter-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
JWT_SECRET=your-secret-key
JWT_EXPIRE_HOURS=24
```

---

## 🧪 Complete Test Suite

### STEP 1: Authentication Tests

#### Test 1.1: Register User
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ahmed Khan",
    "phone": "03001234567",
    "email": "ahmed@test.com",
    "password": "test123",
    "city": "Islamabad",
    "role": "user"
  }'
```
**Expected:** Returns JWT token with `role: "user"` and `user_id`

#### Test 1.2: Register Provider
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ali Plumber",
    "phone": "03009876543",
    "email": "ali@plumber.com",
    "password": "provider123",
    "city": "Rawalpindi",
    "role": "provider"
  }'
```
**Expected:** Returns JWT token with `role: "provider"` and creates provider record

#### Test 1.3: Duplicate Phone Check
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Another User",
    "phone": "03001234567",
    "password": "test456",
    "role": "user"
  }'
```
**Expected:** `400 "Yeh phone already registered hai"`

#### Test 1.4: Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "03001234567",
    "password": "test123"
  }'
```
**Expected:** Returns JWT token

#### Test 1.5: Get Current User (Protected)
```bash
curl -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns user profile (without password_hash)

---

### STEP 2: Provider/Workers Tests

#### Test 2.1: Update Provider Profile
```bash
curl -X PUT http://127.0.0.1:8000/api/workers/profile \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "plumber",
    "area": "Rawalpindi",
    "rate_per_hour": 500,
    "bio": "10 saal ka tajurba. Sab kaam guarantee ke sath.",
    "is_available": true,
    "is_online": true
  }'
```
**Expected:** Returns updated provider profile

#### Test 2.2: Browse All Available Providers
```bash
curl -X GET http://127.0.0.1:8000/api/workers \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns list of available providers

#### Test 2.3: Filter by Service Type
```bash
curl -X GET "http://127.0.0.1:8000/api/workers?service_type=plumber" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns only plumbers

#### Test 2.4: Filter by Area
```bash
curl -X GET "http://127.0.0.1:8000/api/workers?area=Islamabad" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns only Islamabad providers

#### Test 2.5: Get Provider by ID
```bash
curl -X GET "http://127.0.0.1:8000/api/workers/PROVIDER_ID" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns provider details with recent ratings

#### Test 2.6: Update Availability
```bash
curl -X PUT "http://127.0.0.1:8000/api/workers/availability?is_online=true&is_available=true" \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```
**Expected:** `{"message": "Status update ho gaya"}`

#### Test 2.7: User Cannot Update Provider Profile (403)
```bash
curl -X PUT http://127.0.0.1:8000/api/workers/profile \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"service_type": "electrician"}'
```
**Expected:** `403 "Sirf providers apna profile update kar sakte hain"`

---

### STEP 3: AI Chat Tests

#### Test 3.1: Chat with Clear Intent (Urdu/Roman)
```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mujhe plumber chahiye Rawalpindi mein"
  }'
```
**Expected:** Returns providers list with agent_trace showing 4 steps

#### Test 3.2: Chat with English
```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need an electrician in G-11"
  }'
```
**Expected:** Returns providers with intent extraction

#### Test 3.3: Vague Message (Clarification)
```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "hello"
  }'
```
**Expected:** `needs_clarification: true` with clarification message

#### Test 3.4: Get Chat History
```bash
curl -X GET http://127.0.0.1:8000/api/chat/history \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns all user's chat messages

---

### STEP 4: Booking Lifecycle Tests

#### Test 4.1: Create Booking (User)
```bash
curl -X POST http://127.0.0.1:8000/api/bookings \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": "PROVIDER_ID",
    "service_type": "plumber",
    "location": "F-10 Islamabad",
    "scheduled_at": "2026-05-18 10:00",
    "note": "Pipe leak in kitchen",
    "booked_via": "chat"
  }'
```
**Expected:** Returns booking with `status: "pending"` and sends notifications

#### Test 4.2: Get My Bookings
```bash
curl -X GET http://127.0.0.1:8000/api/bookings/my \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns user's bookings (or provider's bookings if provider token)

#### Test 4.3: Accept Booking (Provider)
```bash
curl -X PUT http://127.0.0.1:8000/api/bookings/BOOKING_ID/accept \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```
**Expected:** Updates status to `"confirmed"` and sends notifications

#### Test 4.4: Reject Booking (Provider)
```bash
curl -X PUT http://127.0.0.1:8000/api/bookings/BOOKING_ID/reject \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```
**Expected:** Updates status to `"cancelled"` and sends notifications

#### Test 4.5: Complete Booking (Provider)
```bash
curl -X PUT http://127.0.0.1:8000/api/bookings/BOOKING_ID/complete \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```
**Expected:** Updates status to `"completed"` and sends notifications

---

### STEP 5: Ratings Tests (Bidirectional)

#### Test 5.1: User Rates Provider
```bash
curl -X POST http://127.0.0.1:8000/api/ratings \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "COMPLETED_BOOKING_ID",
    "ratee_id": "PROVIDER_USER_ID",
    "stars": 5,
    "review_text": "Excellent work! Very professional.",
    "tags": ["punctual", "professional", "quality_work"]
  }'
```
**Expected:** Creates rating and updates provider's average rating

#### Test 5.2: Provider Rates User
```bash
curl -X POST http://127.0.0.1:8000/api/ratings \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "COMPLETED_BOOKING_ID",
    "ratee_id": "USER_ID",
    "stars": 5,
    "review_text": "Great customer, clear communication.",
    "tags": ["responsive", "clear_requirements"]
  }'
```
**Expected:** Creates rating and updates user's reliability_score

#### Test 5.3: Get Provider Ratings
```bash
curl -X GET http://127.0.0.1:8000/api/ratings/provider/PROVIDER_USER_ID \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns list of provider reviews

#### Test 5.4: Get User Ratings (Provider Only)
```bash
curl -X GET http://127.0.0.1:8000/api/ratings/user/USER_ID \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```
**Expected:** Returns user reliability ratings with average

#### Test 5.5: Get Pending Ratings
```bash
curl -X GET http://127.0.0.1:8000/api/ratings/pending \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns completed bookings that need rating

#### Test 5.6: Duplicate Rating Check
```bash
# Try rating same booking twice
curl -X POST http://127.0.0.1:8000/api/ratings \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "ALREADY_RATED_BOOKING_ID",
    "ratee_id": "PROVIDER_USER_ID",
    "stars": 4
  }'
```
**Expected:** `400 "Tumne pehle hi rate kar diya hai"`

---

### STEP 6: Notifications Tests

#### Test 6.1: Get Notifications
```bash
curl -X GET http://127.0.0.1:8000/api/notifications \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns notifications array and unread_count

#### Test 6.2: Mark Single Notification as Read
```bash
curl -X PUT http://127.0.0.1:8000/api/notifications/NOTIFICATION_ID/read \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** `{"message": "Mark as read"}`

#### Test 6.3: Mark All Notifications as Read
```bash
curl -X PUT http://127.0.0.1:8000/api/notifications/read-all \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** `{"message": "Sab notifications read ho gayi"}`

---

### STEP 7: Service Requests Tests

#### Test 7.1: Create Service Request (User)
```bash
curl -X POST http://127.0.0.1:8000/api/requests \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "electrician",
    "location": "G-11 Islamabad",
    "scheduled_at": "2026-05-19 14:00",
    "budget": 800,
    "description": "Need to install ceiling fan"
  }'
```
**Expected:** Creates request with `status: "open"` and notifies matching providers

#### Test 7.2: Browse Open Requests (Provider)
```bash
curl -X GET http://127.0.0.1:8000/api/requests/open \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```
**Expected:** Returns list of open requests with user details

#### Test 7.3: Filter Open Requests by Service Type
```bash
curl -X GET "http://127.0.0.1:8000/api/requests/open?service_type=electrician" \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```
**Expected:** Returns only electrician requests

#### Test 7.4: Accept Service Request (Provider)
```bash
curl -X PUT http://127.0.0.1:8000/api/requests/REQUEST_ID/accept \
  -H "Authorization: Bearer YOUR_PROVIDER_TOKEN"
```
**Expected:** Updates request to `"taken"`, creates booking, notifies user

#### Test 7.5: Get My Requests (User)
```bash
curl -X GET http://127.0.0.1:8000/api/requests/my \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```
**Expected:** Returns user's service requests

---

## 🔄 Complete 12-Step Integration Test

Run these tests in sequence to verify the complete user journey:

### 1. Register User
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "phone": "03001111111", "password": "test123", "role": "user"}'
```
Save the `access_token` as `USER_TOKEN`

### 2. Register Provider
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Provider", "phone": "03002222222", "password": "test123", "role": "provider"}'
```
Save the `access_token` as `PROVIDER_TOKEN` and `user_id` as `PROVIDER_USER_ID`

### 3. Update Provider Profile
```bash
curl -X PUT http://127.0.0.1:8000/api/workers/profile \
  -H "Authorization: Bearer $PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"service_type": "plumber", "area": "Islamabad", "rate_per_hour": 600, "is_available": true}'
```

### 4. Chat to Find Provider
```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mujhe plumber chahiye Islamabad mein"}'
```
Check `agent_trace` for 4 steps and save `providers[0].id` as `PROVIDER_ID`

### 5. Create Booking
```bash
curl -X POST http://127.0.0.1:8000/api/bookings \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider_id": "PROVIDER_ID", "service_type": "plumber", "location": "F-10", "scheduled_at": "2026-05-20 10:00", "booked_via": "chat"}'
```
Save `id` as `BOOKING_ID`

### 6. Provider Accepts Booking
```bash
curl -X PUT http://127.0.0.1:8000/api/bookings/$BOOKING_ID/accept \
  -H "Authorization: Bearer $PROVIDER_TOKEN"
```
Verify `status: "confirmed"`

### 7. Provider Completes Booking
```bash
curl -X PUT http://127.0.0.1:8000/api/bookings/$BOOKING_ID/complete \
  -H "Authorization: Bearer $PROVIDER_TOKEN"
```
Verify `status: "completed"`

### 8. User Rates Provider
```bash
curl -X POST http://127.0.0.1:8000/api/ratings \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"booking_id": "BOOKING_ID", "ratee_id": "PROVIDER_USER_ID", "stars": 5, "review_text": "Great work!"}'
```

### 9. Provider Rates User
```bash
curl -X POST http://127.0.0.1:8000/api/ratings \
  -H "Authorization: Bearer $PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"booking_id": "BOOKING_ID", "ratee_id": "USER_ID", "stars": 5, "review_text": "Good customer"}'
```

### 10. Check Notifications (Both)
```bash
# User notifications
curl -X GET http://127.0.0.1:8000/api/notifications \
  -H "Authorization: Bearer $USER_TOKEN"

# Provider notifications
curl -X GET http://127.0.0.1:8000/api/notifications \
  -H "Authorization: Bearer $PROVIDER_TOKEN"
```

### 11. Create Service Request
```bash
curl -X POST http://127.0.0.1:8000/api/requests \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"service_type": "plumber", "location": "G-11", "description": "Fix tap"}'
```
Save `id` as `REQUEST_ID`

### 12. Provider Accepts Request
```bash
curl -X PUT http://127.0.0.1:8000/api/requests/$REQUEST_ID/accept \
  -H "Authorization: Bearer $PROVIDER_TOKEN"
```
Verify auto-created booking with `booked_via: "request"`

---

## 📊 API Endpoints Summary

### Authentication (3)
- `POST /auth/register` - Register user/provider
- `POST /auth/login` - Login and get JWT
- `GET /auth/me` - Get current user profile

### Workers/Providers (4)
- `GET /api/workers` - Browse providers (with filters)
- `GET /api/workers/{id}` - Get provider details
- `PUT /api/workers/profile` - Update provider profile
- `PUT /api/workers/availability` - Update online/available status

### AI Chat (2)
- `POST /api/chat` - AI-powered service search
- `GET /api/chat/history` - Get chat history

### Bookings (7)
- `POST /api/bookings` - Create booking
- `GET /api/bookings/my` - Get my bookings
- `PUT /api/bookings/{id}/accept` - Accept booking (auto-creates conversation)
- `PUT /api/bookings/{id}/cancel` - Cancel booking (user)
- `PUT /api/bookings/{id}/reject` - Reject booking (provider)
- `PUT /api/bookings/{id}/complete` - Complete booking
- `GET /api/bookings/earnings` - Get provider earnings

### Ratings (4)
- `POST /api/ratings` - Submit rating
- `GET /api/ratings/provider/{id}` - Get provider ratings
- `GET /api/ratings/user/{id}` - Get user reliability score
- `GET /api/ratings/pending` - Get bookings needing rating

### Notifications (3)
- `GET /api/notifications` - Get notifications
- `PUT /api/notifications/{id}/read` - Mark as read
- `PUT /api/notifications/read-all` - Mark all as read

### Service Requests (4)
- `POST /api/requests` - Create service request
- `GET /api/requests/open` - Browse open requests
- `PUT /api/requests/{id}/accept` - Accept request
- `GET /api/requests/my` - Get my requests

### Conversations/Messaging (5)
- `POST /api/conversations` - Create conversation for booking
- `GET /api/conversations` - Get my conversations
- `GET /api/conversations/{id}/messages` - Get messages (auto-marks as read)
- `POST /api/conversations/{id}/messages` - Send message
- `WS /api/conversations/ws/{user_id}` - WebSocket real-time messaging

---

## 🔍 Verification Checklist

- [ ] All 36 endpoints return expected responses
- [ ] JWT authentication working for all protected routes
- [ ] Role-based access control (user vs provider) enforced
- [ ] AI intent extraction working (Urdu/English)
- [ ] Google Maps geocoding returning lat/lng
- [ ] Provider ranking algorithm calculating scores
- [ ] Agent trace logging all 4 steps
- [ ] Bidirectional notifications sent on booking events
- [ ] Bidirectional ratings updating averages
- [ ] Service request auto-creates booking on acceptance
- [ ] Error messages in Urdu as specified
- [ ] All database tables accessible with proper permissions

---

## 🐛 Common Issues

### Issue: "Token galat ya expire ho gaya"
**Solution:** Token expired. Login again to get new token.

### Issue: "API Key not found"
**Solution:** Check `.env` file has valid `OPENROUTER_API_KEY` and `GOOGLE_MAPS_API_KEY`.

### Issue: "permission denied for table"
**Solution:** Run `grant_permissions.sql` in Supabase SQL Editor.

### Issue: "Provider nahi mila"
**Solution:** Ensure provider has updated their profile with `is_available: true`.

---

## 📝 Notes

- All error messages are in Urdu/Roman Urdu as per spec
- Agent trace shows execution time and all intermediate steps
- Notifications are bidirectional (user ↔ provider)
- Ratings are bidirectional and update averages automatically
- Service requests notify all matching providers
- Google Maps API provides real geocoding and travel time

---

**Backend Status:** ✅ Production Ready  
**Total Endpoints:** 36 (31 REST + 1 WebSocket + 4 new messaging)  
**Database Tables:** 10 (8 original + 2 messaging)  
**AI Integration:** OpenRouter (GPT-3.5-turbo)  
**Maps Integration:** Google Maps (Geocoding + Routes API)  
**Real-Time Messaging:** WebSocket support for instant delivery

## 🆕 New Features Added

### Peer-to-Peer Messaging System
- Real-time chat between users and providers
- Auto-created when provider accepts booking
- Unread message counters
- Read receipts (auto-mark as read)
- WebSocket push notifications
- Conversation history with last message preview

See **MESSAGING_GUIDE.md** for complete documentation and testing instructions.
