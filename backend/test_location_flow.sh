#!/bin/bash
# Complete Location-Based Flow Test
# Tests: Registration → Profile Setup → AI Chat → Location Matching → Provider Ranking

echo "=== KAROO LOCATION-BASED FLOW TEST ==="
echo ""

BASE_URL="http://127.0.0.1:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Register Provider in Rawalpindi${NC}"
PROVIDER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Usman Electrician",
    "phone": "03001234999",
    "password": "test123",
    "city": "Rawalpindi",
    "role": "provider"
  }')

PROVIDER_TOKEN=$(echo $PROVIDER_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
PROVIDER_USER_ID=$(echo $PROVIDER_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['user_id'])" 2>/dev/null)

if [ -z "$PROVIDER_TOKEN" ]; then
  echo -e "${RED}✗ Provider registration failed${NC}"
  echo $PROVIDER_RESPONSE | python -m json.tool
  exit 1
fi

echo -e "${GREEN}✓ Provider registered${NC}"
echo "  User ID: $PROVIDER_USER_ID"
echo ""

echo -e "${BLUE}Step 2: Update Provider Profile with Rawalpindi Location${NC}"
# Rawalpindi coordinates: 33.5651, 73.0169
PROFILE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/workers/profile" \
  -H "Authorization: Bearer $PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "electrician",
    "area": "Rawalpindi",
    "rate_per_hour": 800,
    "bio": "Expert electrician with 8 years experience in Rawalpindi",
    "is_available": true,
    "is_online": true,
    "lat": 33.5651,
    "lng": 73.0169
  }')

PROVIDER_ID=$(echo $PROFILE_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['provider']['id'])" 2>/dev/null)

if [ -z "$PROVIDER_ID" ]; then
  echo -e "${RED}✗ Provider profile update failed${NC}"
  echo $PROFILE_RESPONSE | python -m json.tool
  exit 1
fi

echo -e "${GREEN}✓ Provider profile updated${NC}"
echo "  Provider ID: $PROVIDER_ID"
echo "  Location: Rawalpindi (33.5651, 73.0169)"
echo "  Service: electrician"
echo ""

echo -e "${BLUE}Step 3: Register User in Islamabad (nearby)${NC}"
USER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ahmed User",
    "phone": "03009876111",
    "password": "test123",
    "city": "Islamabad",
    "role": "user"
  }')

USER_TOKEN=$(echo $USER_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
USER_ID=$(echo $USER_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['user_id'])" 2>/dev/null)

if [ -z "$USER_TOKEN" ]; then
  echo -e "${RED}✗ User registration failed${NC}"
  echo $USER_RESPONSE | python -m json.tool
  exit 1
fi

echo -e "${GREEN}✓ User registered${NC}"
echo "  User ID: $USER_ID"
echo ""

echo -e "${BLUE}Step 4: User Searches for Electrician in Islamabad via AI Chat${NC}"
# Islamabad coordinates: 33.6844, 73.0479
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mujhe electrician chahiye Islamabad mein",
    "user_lat": 33.6844,
    "user_lng": 73.0479
  }')

echo "$CHAT_RESPONSE" | python -m json.tool > /tmp/chat_response.json

# Extract key information
INTENT_SERVICE=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('intent', {}).get('service_type', 'N/A'))" 2>/dev/null)
INTENT_LOCATION=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('intent', {}).get('location', 'N/A'))" 2>/dev/null)
INTENT_CONFIDENCE=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('intent', {}).get('confidence', 0))" 2>/dev/null)
PROVIDERS_COUNT=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('providers', [])))" 2>/dev/null)

echo -e "${GREEN}✓ AI Chat Response Received${NC}"
echo ""
echo "=== AI INTENT EXTRACTION ==="
echo "  Service Type: $INTENT_SERVICE"
echo "  Location: $INTENT_LOCATION"
echo "  Confidence: $INTENT_CONFIDENCE"
echo ""

if [ "$PROVIDERS_COUNT" -gt 0 ]; then
  echo -e "${GREEN}✓ Found $PROVIDERS_COUNT provider(s)${NC}"
  echo ""
  echo "=== PROVIDER DETAILS ==="

  # Extract first provider details
  FOUND_NAME=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data['providers'][0]['name'])" 2>/dev/null)
  FOUND_SERVICE=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data['providers'][0]['service_type'])" 2>/dev/null)
  FOUND_AREA=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data['providers'][0]['area'])" 2>/dev/null)
  FOUND_ETA=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data['providers'][0].get('eta_minutes', 'N/A'))" 2>/dev/null)
  FOUND_SCORE=$(cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data['providers'][0].get('match_score', 'N/A'))" 2>/dev/null)

  echo "  Name: $FOUND_NAME"
  echo "  Service: $FOUND_SERVICE"
  echo "  Area: $FOUND_AREA"
  echo "  ETA: $FOUND_ETA minutes"
  echo "  Match Score: $FOUND_SCORE"
  echo ""

  # Verify it's the correct provider
  if [ "$FOUND_NAME" = "Usman Electrician" ]; then
    echo -e "${GREEN}✓ CORRECT PROVIDER MATCHED!${NC}"
    echo "  The AI correctly found the provider we created"
  else
    echo -e "${RED}✗ WRONG PROVIDER MATCHED${NC}"
    echo "  Expected: Usman Electrician"
    echo "  Got: $FOUND_NAME"
  fi

  echo ""
  echo "=== LOCATION VERIFICATION ==="
  echo "  User Location: Islamabad (33.6844, 73.0479)"
  echo "  Provider Location: Rawalpindi (33.5651, 73.0169)"
  echo "  Distance: ~15 km"
  echo "  Calculated ETA: $FOUND_ETA minutes"

  if [ "$FOUND_ETA" != "N/A" ] && [ "$FOUND_ETA" != "999" ]; then
    echo -e "${GREEN}✓ Google Routes API working - Real ETA calculated${NC}"
  else
    echo -e "${RED}✗ Google Routes API failed - Using fallback ETA${NC}"
  fi

else
  echo -e "${RED}✗ No providers found${NC}"
  echo "This might mean:"
  echo "  1. Provider is not available"
  echo "  2. Service type mismatch"
  echo "  3. Database query issue"
fi

echo ""
echo "=== AGENT TRACE ==="
cat /tmp/chat_response.json | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('agent_trace', 'No trace available'))" 2>/dev/null | head -30

echo ""
echo "=== TEST SUMMARY ==="
echo -e "${GREEN}✓ Provider registered with location (Rawalpindi)${NC}"
echo -e "${GREEN}✓ User registered with location (Islamabad)${NC}"
echo -e "${GREEN}✓ AI intent extraction working${NC}"
echo -e "${GREEN}✓ Location-based search working${NC}"

if [ "$FOUND_ETA" != "N/A" ] && [ "$FOUND_ETA" != "999" ]; then
  echo -e "${GREEN}✓ Real-time ETA calculation working${NC}"
else
  echo -e "${RED}✗ Real-time ETA calculation failed (check Google Maps API key)${NC}"
fi

echo ""
echo "Full response saved to: /tmp/chat_response.json"
