#!/bin/bash

echo "=== Testing Karoo Application End-to-End ==="
echo ""

# Test 1: Register User
echo "1. Registering test user..."
USER_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "phone": "03001111111",
    "password": "test123",
    "role": "user"
  }')
echo "$USER_RESPONSE" | python -m json.tool
echo ""

# Test 2: Login User
echo "2. Logging in user..."
USER_LOGIN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "03001111111",
    "password": "test123"
  }')
USER_TOKEN=$(echo "$USER_LOGIN" | python -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
echo "User token: ${USER_TOKEN:0:50}..."
echo ""

# Test 3: Register Provider
echo "3. Registering test provider..."
PROVIDER_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ali Khan",
    "phone": "03002222222",
    "password": "test123",
    "role": "provider"
  }')
echo "$PROVIDER_RESPONSE" | python -m json.tool
echo ""

# Test 4: Login Provider
echo "4. Logging in provider..."
PROVIDER_LOGIN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "03002222222",
    "password": "test123"
  }')
PROVIDER_TOKEN=$(echo "$PROVIDER_LOGIN" | python -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
echo "Provider token: ${PROVIDER_TOKEN:0:50}..."
echo ""

# Test 5: Update Provider Profile
echo "5. Updating provider profile..."
PROFILE_UPDATE=$(curl -s -X PUT http://localhost:8000/api/workers/profile \
  -H "Authorization: Bearer $PROVIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "electrician",
    "area": "G-11",
    "rate_per_hour": 600,
    "bio": "10 years experience",
    "is_available": true,
    "is_online": true
  }')
echo "$PROFILE_UPDATE" | python -m json.tool
echo ""

# Test 6: List Providers
echo "6. Listing available providers..."
PROVIDERS=$(curl -s "http://localhost:8000/api/workers?service_type=electrician&area=G-11" \
  -H "Authorization: Bearer $USER_TOKEN")
echo "$PROVIDERS" | python -m json.tool | head -30
echo ""

echo "=== Basic Flow Tests Complete ==="
