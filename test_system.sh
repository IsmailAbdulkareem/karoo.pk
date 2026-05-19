#!/bin/bash

# Karoo System Test Script
# Run this to verify all features work before demo

echo "🧪 Starting Karoo System Tests..."
echo ""

# Test 1: Backend Health
echo "Test 1: Backend Health Check"
curl http://localhost:8000/ || echo "❌ Backend not running!"
echo ""

# Test 2: Database Migrations
echo "Test 2: Checking if all migrations are applied"
echo "Run these SQL files in order:"
echo "  1. backend/add_pricing_columns.sql"
echo "  2. backend/add_disputes_table.sql"
echo "  3. backend/add_scheduling_columns.sql"
echo "  4. backend/add_complexity_columns.sql"
echo "  5. backend/add_service_progress_table.sql"
echo ""

# Test 3: Environment Variables
echo "Test 3: Checking environment variables"
if [ -f backend/.env ]; then
    echo "✅ .env file exists"
    grep -q "GEMINI_API_KEY" backend/.env && echo "✅ GEMINI_API_KEY set" || echo "❌ GEMINI_API_KEY missing!"
    grep -q "GOOGLE_MAPS_API_KEY" backend/.env && echo "✅ GOOGLE_MAPS_API_KEY set" || echo "❌ GOOGLE_MAPS_API_KEY missing!"
else
    echo "❌ .env file not found!"
fi
echo ""

# Test 4: Dependencies
echo "Test 4: Checking Python dependencies"
cd backend
pip list | grep "google-generativeai" && echo "✅ Gemini SDK installed" || echo "❌ Gemini SDK missing!"
pip list | grep "fastapi" && echo "✅ FastAPI installed" || echo "❌ FastAPI missing!"
cd ..
echo ""

echo "🎬 Manual Tests Required:"
echo ""
echo "1. User Flow:"
echo "   - Register as user"
echo "   - Chat: 'Mujhe electrician chahiye G-11 mein urgent'"
echo "   - Verify providers shown with prices"
echo "   - Book a provider"
echo "   - Check notifications"
echo ""
echo "2. Provider Flow:"
echo "   - Register as provider"
echo "   - Accept booking"
echo "   - Update status (en_route, arrived, in_progress)"
echo "   - Submit completion checklist"
echo "   - Mark as completed"
echo ""
echo "3. Dispute Flow:"
echo "   - Create dispute after completion"
echo "   - Verify auto-resolution"
echo ""
echo "4. Check Backend Logs:"
echo "   - Look for [GEMINI AGENT] traces"
echo "   - Verify pricing calculations"
echo "   - Check scheduling conflict detection"
echo ""
echo "✅ System test checklist complete!"
