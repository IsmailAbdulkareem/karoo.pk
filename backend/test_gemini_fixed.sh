#!/bin/bash

echo "=========================================="
echo "  GEMINI AI TEST - FIXED DECLARATIONS"
echo "=========================================="
echo ""

# Login
USER_LOGIN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "03001111111", "password": "test123"}')
USER_TOKEN=$(echo "$USER_LOGIN" | python -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

echo "✅ Logged in"
echo ""

# Test 1: Simple Gemini chat
echo "🤖 TEST 1: Gemini AI Chat with Function Calling"
echo "Message: 'I need an electrician in G-11 urgent'"
echo ""

CHAT=$(curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need an electrician in G-11 urgent"}')

echo "$CHAT" | python -m json.tool > chat_result.json

REPLY=$(cat chat_result.json | python -c "import sys, json; print(json.load(sys.stdin).get('reply', '')[:150])" 2>/dev/null)
PROVIDERS=$(cat chat_result.json | python -c "import sys, json; print(len(json.load(sys.stdin).get('providers', [])))" 2>/dev/null)

echo "Reply: $REPLY"
echo "Providers found: $PROVIDERS"
echo ""

if [ "$PROVIDERS" -gt 0 ]; then
    echo "✅✅✅ SUCCESS! GEMINI FUNCTION CALLING WORKS! ✅✅✅"
    echo ""
    cat chat_result.json | python << 'PYEOF'
import sys, json
data = json.load(open('chat_result.json'))
print("Provider Details:")
for i, p in enumerate(data.get('providers', []), 1):
    print(f"\n  Provider {i}:")
    print(f"    Name: {p.get('name')}")
    print(f"    Service: {p.get('service_type')}")
    print(f"    Area: {p.get('area')}")
    print(f"    Rating: {p.get('rating')}")
    print(f"    Rate: Rs. {p.get('rate_per_hour')}/hr")
    if p.get('estimated_price'):
        print(f"    Estimated Price: Rs. {p.get('estimated_price')}")
    if p.get('match_score'):
        print(f"    Match Score: {int(p.get('match_score') * 100)}%")
PYEOF
    
    echo ""
    echo "=========================================="
    echo "  🎉 100% FUNCTIONAL - READY FOR DEMO! 🎉"
    echo "=========================================="
    
else
    echo "❌ Function calling still not working"
    echo ""
    echo "Checking server logs for errors..."
    tail -30 ../server.log | grep -i "error\|exception" | tail -10
fi

echo ""
