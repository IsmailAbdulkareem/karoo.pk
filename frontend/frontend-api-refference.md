# Karoo App — Frontend API Reference

> **Base URL (Local):** `http://localhost:8000`
> **Base URL (Production):** `https://ismail233290-karoo-pk.hf.space`
> **Format:** All requests/responses are `application/json`
> **Auth:** JWT Bearer token required on all endpoints **except** `/auth/register` and `/auth/login`

---

## 🔐 Authentication Header

```
Authorization: Bearer <access_token>
```

---

## 1. AUTH — `/auth`

### `POST /auth/register`
Register a new user or provider. No auth required.

**Request Body:**
```json
{
  "name": "Ali Khan",
  "phone": "03001234567",
  "password": "mypassword",
  "email": "ali@email.com",       // optional
  "city": "Islamabad",             // optional
  "role": "user"                   // "user" | "provider"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "user",
  "user_id": "uuid-string"
}
```

**Errors:** `400` Phone already registered

---

### `POST /auth/login`
Login with phone and password. No auth required.

**Request Body:**
```json
{
  "phone": "03001234567",
  "password": "mypassword"
}
```

**Response:** Same as register response.

**Errors:** `404` User not found | `401` Wrong password

---

### `GET /auth/me`
Get current logged-in user's profile. 🔒 Auth required.

**Response:**
```json
{
  "id": "uuid",
  "name": "Ali Khan",
  "phone": "03001234567",
  "email": "ali@email.com",
  "role": "user",
  "city": "Islamabad",
  "created_at": "2026-05-17T..."
}
```

---

## 2. AI CHAT — `/api/chat`

### `POST /api/chat`
Main AI chat for users to find providers via natural language. 🔒 User only.

**Request Body:**
```json
{
  "message": "Mujhe plumber chahiye G-11 mein",
  "user_lat": 33.6844,   // optional
  "user_lng": 73.0479    // optional
}
```

**Response:**
```json
{
  "reply": "G-11 mein 3 plumber available hain",
  "needs_clarification": false,
  "intent": {
    "service_type": "plumber",
    "location": "G-11",
    "time": null,
    "confidence": 0.95
  },
  "providers": [
    {
      "id": "uuid",
      "name": "Babar Plumber",
      "service_type": "plumber",
      "area": "G-11",
      "rating": 4.5,
      "rate_per_hour": 800,
      "is_available": true,
      "bio": "10 saal ka tajruba",
      "eta_minutes": 15,
      "match_score": 0.92
    }
  ],
  "agent_trace": "=== KAROO AGENT TRACE ===..."
}
```

> If `needs_clarification: true`, show `reply` as a follow-up prompt to user.

---

### `GET /api/chat/history`
Get chat history for current user. 🔒 Auth required.

**Response:** Array of message objects:
```json
[
  { "id": "uuid", "user_id": "uuid", "role": "user", "content": "...", "created_at": "..." },
  { "id": "uuid", "user_id": "uuid", "role": "bot",  "content": "...", "created_at": "..." }
]
```

---

### `POST /api/chat/provider`
AI chat for providers to find jobs, check bookings, check earnings. 🔒 Provider only.

**Request Body:**
```json
{ "message": "Koi naya kaam hai?" }
```

**Supported intents (Urdu/Roman Urdu/English):**
| Intent | Example messages |
|--------|-----------------|
| `find_requests` | "Koi kaam hai?", "New jobs?", "Koi request hai?" |
| `check_bookings` | "Aaj ki bookings?", "Meri bookings dikhao", "Today's schedule" |
| `check_earnings` | "Kitna kamaya?", "Meri earnings?", "Total income?" |

**Response:**
```json
{
  "reply": "Aapki 2 bookings hain.",
  "intent": {
    "intent_type": "check_bookings",
    "service_type": "plumber",
    "area": null,
    "time_filter": "today",
    "confidence": 0.92
  },
  "results": [...],
  "agent_trace": "..."
}
```

---

## 3. BOOKINGS — `/api/bookings`

### `POST /api/bookings`
Create a new booking. 🔒 User only.

**Request Body:**
```json
{
  "provider_id": "uuid",
  "service_type": "plumber",
  "location": "G-11 Islamabad",
  "scheduled_at": "2026-05-20 10:00",
  "note": "Pipe leak hai kitchen mein",   // optional
  "booked_via": "browse",                 // "browse" | "chat" | "request"
  "budget": 2000,                         // optional — user's max budget PKR
  "agreed_rate": 1500,                    // optional — negotiated rate PKR
  "user_lat": 33.68,                      // optional
  "user_lng": 73.04,                      // optional
  "eta_minutes": 20                       // optional
}
```

**Response:** Created booking object. Status starts as `"pending"`.

**Side effect:** Sends notifications to both user and provider.

---

### `GET /api/bookings/my`
Get bookings for current user. 🔒 Auth required.
- **User:** sees their own bookings with provider details
- **Provider:** sees bookings assigned to them with customer details

**Response:** Array of booking objects sorted newest first.

**Booking object:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "provider_id": "uuid",
  "service_type": "plumber",
  "location": "G-11",
  "scheduled_at": "2026-05-20 10:00",
  "status": "pending",
  "budget": 2000,
  "agreed_rate": 1500,
  "note": "...",
  "booked_via": "browse",
  "created_at": "..."
}
```

**Status values:** `pending` → `confirmed` → `completed` | `cancelled`

---

### `GET /api/bookings/earnings`
Get provider earnings summary. 🔒 Provider only.

**Response:**
```json
{
  "provider_id": "uuid",
  "total_completed_jobs": 5,
  "total_earned_pkr": 7500,
  "rate_per_hour": 800,
  "message": "Aapne 5 kaam mukammal kiye aur total PKR 7500 kamaye!",
  "earnings_breakdown": [
    {
      "booking_id": "uuid",
      "service_type": "plumber",
      "location": "G-11",
      "customer_name": "Ali Khan",
      "scheduled_at": "...",
      "agreed_rate": 1500,
      "budget": 2000,
      "earned": 1500
    }
  ]
}
```

> Earnings priority: `agreed_rate` > `budget` > provider's `rate_per_hour`

---

### `PUT /api/bookings/{booking_id}/accept`
Accept a pending booking. 🔒 Provider only.

**Response:** Updated booking object with `status: "confirmed"`.

**Side effects:**
- Sends confirmation notifications to both parties
- Auto-creates a conversation for messaging

**Errors:** `400` Already updated | `403` Not your booking

---

### `PUT /api/bookings/{booking_id}/reject`
Reject/cancel a booking (pending or confirmed). 🔒 Provider only.

**Response:** Updated booking with `status: "cancelled"`.

**Side effect:** Sends cancellation notification to user.

---

### `PUT /api/bookings/{booking_id}/cancel`
Cancel a booking. 🔒 User only. Can cancel `pending` or `confirmed` bookings.

**Response:**
```json
{
  "message": "Booking cancel ho gayi",
  "booking": { ...booking object... }
}
```

**Errors:** `400` Cannot cancel completed/already-cancelled booking

---

### `PUT /api/bookings/{booking_id}/complete`
Mark a confirmed booking as completed. 🔒 Provider only.

**Response:** Updated booking with `status: "completed"`.

**Side effect:** Sends completion notification. User can now rate provider.

---

## 4. WORKERS (PROVIDERS) — `/api/workers`

### `GET /api/workers`
Browse available providers with optional filters. 🔒 Auth required.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `service_type` | string | e.g. `plumber`, `electrician` |
| `area` | string | e.g. `G-11`, `DHA` |
| `min_rating` | float | Minimum rating e.g. `4.0` |

**Example:** `GET /api/workers?service_type=plumber&area=G-11&min_rating=4.0`

**Response:** Array of provider objects sorted by rating descending:
```json
[
  {
    "id": "uuid",
    "name": "Babar Plumber",
    "service_type": "plumber",
    "area": "G-11",
    "rating": 4.7,
    "rate_per_hour": 800,
    "is_available": true,
    "bio": "10 saal ka tajruba",
    "eta_minutes": null,
    "match_score": null
  }
]
```

**Available service types:** `plumber`, `electrician`, `ac_technician`, `tutor`, `cleaner`, `carpenter`, `painter`, `mechanic`, `cook`, `security_guard`

---

### `GET /api/workers/{provider_id}`
Get single provider's full profile with recent reviews. 🔒 Auth required.

**Response:**
```json
{
  "id": "uuid",
  "name": "Babar Plumber",
  "service_type": "plumber",
  "area": "G-11",
  "rating": 4.7,
  "rate_per_hour": 800,
  "is_available": true,
  "bio": "...",
  "total_ratings": 23,
  "recent_ratings": [
    { "stars": 5, "review_text": "Bahut acha kaam kiya", "tags": ["punctual"], "rater_role": "user", "created_at": "..." }
  ]
}
```

---

### `PUT /api/workers/profile`
Update provider profile. 🔒 Provider only.

**Request Body (all fields optional):**
```json
{
  "service_type": "plumber",
  "area": "G-11",
  "rate_per_hour": 800,
  "bio": "10 saal ka tajruba",
  "is_available": true,
  "is_online": true
}
```

**Response:**
```json
{ "message": "Profile update ho gaya", "provider": { ...provider object... } }
```

---

### `PUT /api/workers/availability`
Quick toggle for provider online/available status. 🔒 Provider only.

**Query Parameters:**
```
PUT /api/workers/availability?is_online=true&is_available=true
```

**Response:** `{ "message": "Status update ho gaya" }`

---

## 5. SERVICE REQUESTS — `/api/requests`

Open marketplace where users post jobs and providers pick them up.

### `POST /api/requests`
Post an open service request. 🔒 User only.

**Request Body:**
```json
{
  "service_type": "plumber",
  "location": "F-10 Islamabad",
  "scheduled_at": "2026-05-20 10:00",  // optional
  "budget": 1500,                        // optional
  "description": "Bathroom mein pipe leak hai"  // optional
}
```

**Response:** Created service request object with `status: "open"`.

**Side effect:** Notifies all matching providers.

---

### `GET /api/requests/open`
Browse all open service requests. 🔒 Provider only.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `service_type` | string | Filter by service |
| `area` | string | Filter by location |

**Response:** Array of open requests with customer name and phone.

---

### `PUT /api/requests/{request_id}/accept`
Accept an open request. 🔒 Provider only.

**Response:** Auto-created booking object.

**Side effects:**
- Request status → `"taken"`
- New booking created with `status: "pending"`
- User gets notification "Provider Mil Gaya!"

---

### `GET /api/requests/my`
Get current user's posted requests. 🔒 User only.

**Response:** Array of service request objects.

---

## 6. NOTIFICATIONS — `/api/notifications`

### `GET /api/notifications`
Get notifications for current user (last 50). 🔒 Auth required.

**Response:**
```json
{
  "notifications": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "Booking Confirm Ho Gayi! ✅",
      "body": "Babar Plumber aa raha hai",
      "type": "booking_accepted",
      "ref_id": "booking-uuid",
      "is_read": false,
      "created_at": "..."
    }
  ],
  "unread_count": 3
}
```

**Notification types:**
| type | When triggered |
|------|---------------|
| `booking_created` | User creates booking |
| `booking_accepted` | Provider accepts |
| `booking_cancelled` | Either party cancels |
| `booking_completed` | Provider marks complete |
| `service_request` | User posts open request |
| `request_accepted` | Provider accepts request |

---

### `PUT /api/notifications/{notification_id}/read`
Mark one notification as read. 🔒 Auth required.

**Response:** `{ "message": "Mark as read" }`

---

### `PUT /api/notifications/read-all`
Mark all notifications as read. 🔒 Auth required.

**Response:** `{ "message": "Sab notifications read ho gayi" }`

---

## 7. RATINGS — `/api/ratings`

### `POST /api/ratings`
Submit a rating after booking completion. 🔒 Auth required. Both user and provider can rate each other.

**Request Body:**
```json
{
  "booking_id": "uuid",
  "ratee_id": "uuid-of-person-being-rated",
  "stars": 5,
  "review_text": "Bahut acha kaam kiya!",  // optional
  "tags": ["punctual", "professional"]      // optional
}
```

**Rules:**
- Booking must have `status: "completed"`
- Cannot rate twice for same booking
- User rating provider → updates provider's `rating` score
- Provider rating user → updates user's `reliability_score`

---

### `GET /api/ratings/provider/{provider_user_id}`
Get all reviews for a provider. 🔒 Auth required.

**Response:** Array of rating objects from users.

---

### `GET /api/ratings/user/{user_id}`
Get reliability ratings for a user. 🔒 Provider only.

**Response:**
```json
{
  "ratings": [...],
  "average_reliability_score": 4.3,
  "total_ratings": 7
}
```

---

### `GET /api/ratings/pending`
Get bookings that need a rating from current user. 🔒 Auth required.

**Response:** Array of completed bookings where current user hasn't rated yet. Use this to show "Rate your experience" prompts.

---

## 8. CONVERSATIONS & MESSAGING — `/api/conversations`

Real-time messaging between user and provider after booking is confirmed.

> **Note:** A conversation is auto-created when a provider accepts a booking. Manual creation is also supported.

### `POST /api/conversations`
Manually create a conversation for a booking. 🔒 Auth required.

**Request Body:**
```json
{ "booking_id": "uuid" }
```

**Response:** Conversation object (or existing one if already created).

---

### `GET /api/conversations`
Get all conversations for current user. 🔒 Auth required.

**Response:** Array of conversation objects:
```json
[
  {
    "id": "uuid",
    "booking_id": "uuid",
    "user_id": "uuid",
    "provider_id": "uuid",
    "last_message": "Thik hai, aa raha hoon",
    "last_message_at": "...",
    "user_unread_count": 2,
    "provider_unread_count": 0,
    "other_party_name": "Babar Plumber",
    "other_party_avatar": null,
    "created_at": "...",
    "updated_at": "..."
  }
]
```

---

### `GET /api/conversations/{conversation_id}/messages`
Get all messages in a conversation. 🔒 Auth required.

**Side effect:** Auto-marks received messages as read and resets unread count.

**Response:** Array of message objects:
```json
[
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "sender_id": "uuid",
    "sender_role": "user",
    "message": "Kab aao ge?",
    "is_read": true,
    "created_at": "..."
  }
]
```

---

### `POST /api/conversations/{conversation_id}/messages`
Send a message. 🔒 Auth required.

**Request Body:**
```json
{ "message": "Thik hai 10 baje aa raha hoon" }
```

**Response:** Sent message object.

**Side effect:** Delivers message to recipient via WebSocket if they are connected.

---

### `WebSocket /api/conversations/ws/{user_id}`
Real-time messaging connection. Pass JWT as query param.

**Connection URL:**
```
ws://localhost:8000/api/conversations/ws/{user_id}?token=YOUR_JWT
```

**Incoming event (new message):**
```json
{
  "type": "new_message",
  "conversation_id": "uuid",
  "message": { ...message object... }
}
```

**Heartbeat:** Send any text → server responds `{ "type": "pong" }`.

---

## 📊 Booking Status Flow

```
POST /bookings  →  pending
                      │
         ┌────────────┴────────────┐
         │                         │
  Provider accepts          Provider rejects
         │                   User cancels
         ▼                         │
     confirmed                 cancelled
         │
         │  Provider completes
         ▼
     completed  ← Can now submit ratings
```

---

## ❌ Common Error Responses

```json
{ "detail": "Token galat ya expire ho gaya" }   // 401 - Invalid/expired token
{ "detail": "Yeh booking tumhari nahi hai" }     // 403 - Forbidden
{ "detail": "Booking nahi mili" }               // 404 - Not found
{ "detail": "Server error: ..." }               // 500 - Internal error
```

---

## 🔄 Recommended Frontend Flow

### User Flow
1. `POST /auth/login` → save token
2. `GET /auth/me` → load profile
3. `POST /api/chat` → search providers via AI chat
4. `GET /api/workers?service_type=plumber` → browse providers
5. `GET /api/workers/{id}` → view provider profile
6. `POST /api/bookings` → book a provider
7. `GET /api/bookings/my` → track bookings
8. `GET /api/notifications` → check updates
9. `GET /api/conversations` → messaging with provider
10. `POST /api/ratings` → rate after completion

### Provider Flow
1. `POST /auth/login` → save token
2. `PUT /api/workers/profile` → setup profile
3. `PUT /api/workers/availability` → go online
4. `GET /api/requests/open` → browse open jobs
5. `PUT /api/requests/{id}/accept` → accept a job
6. `POST /api/chat/provider` → AI assistant for finding work
7. `GET /api/bookings/my` → see assigned bookings
8. `PUT /api/bookings/{id}/accept` → confirm direct bookings
9. `PUT /api/bookings/{id}/complete` → mark job done
10. `GET /api/bookings/earnings` → view earnings
