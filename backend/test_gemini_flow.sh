#!/bin/bash

echo "=== Testing Gemini AI & Booking Flow ==="
echo ""

# Get tokens from previous test
USER_LOGIN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "03001111111", "password": "test123"}')
USER_TOKEN=$(echo "$USER_LOGIN" | python -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

PROVIDER_LOGIN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "03002222222", "password": "test123"}')
PROVIDER_TOKEN=$(echo "$PROVIDER_LOGIN" | python -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

# Test 7: Chat with Gemini AI
echo "7. Testing Gemini AI chat (Urdu/English mixed)..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mujhe electrician chahiye G-11 mein urgent"
  }')
echo "$CHAT_RESPONSE" | python -m json.tool | head -50
echo ""

# Extract provider ID from chat response
PROVIDER_ID=$(echo "$CHAT_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('providers', [{}])[0].get('id', ''))" 2>/dev/null)
echo "Provider ID from chat: $PROVIDER_ID"
echo ""

# Test 8: Create Booking with Dynamic Pricing
echo "8. Creating booking with dynamic pricing..."
BOOKING_RESPONSE=$(curl -s -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"provider_id\": \"$PROVIDER_ID\",
    \"service_type\": \"electrician\",
    \"location\": \"House 123, Street 45, G-11/3, Islamabad\",
    \"scheduled_at\": \"2026-05-20T10:00:00\",
    \"note\": \"Need urgent electrical work\",
    \"booked_via\": \"chat\",
    \"urgency\": \"urgent\",
    \"budget\": 1000
  }")
echo "$BOOKING_RESPONSE" | python -m json.tool
BOOKING_ID=$(echo "$BOOKING_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo ""
echo "Booking ID: $BOOKING_ID"
echo ""

# Test 9: Provider accepts booking
echo "9. Provider accepting booking..."
ACCEPT_RESPONSE=$(curl -s -X PUT "http://localhost:8000/api/bookings/$BOOKING_ID/accept" \
  -H "Authorization: Bearer $PROVIDER_TOKEN")
echo "$ACCEPT_RESPONSE" | python -m json.tool
echo ""

# Test 10: Update service progress
echo "10. Updating service progress (en_route)..."
PROGRESS_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/service-progress/$BOOKING_ID/progress" \
  -H "Authorization: Bearer $PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "en_route",
    "notes": "On my way to location"
  }')
echo "$PROGRESS_RESPONSE" | python -m json.tool
echo ""

# Test 11: Check notifications
echo "11. Checking user notifications..."
NOTIFICATIONS=$(curl -s http://localhost:8000/api/notifications \
  -H "Authorization: Bearer $USER_TOKEN")
echo "$NOTIFICATIONS" | python -m json.tool | head -30
echo ""

echo "=== Gemini AI & Booking Flow Tests Complete ==="
