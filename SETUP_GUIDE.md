# Karoo Setup Guide

Complete setup instructions for running Karoo locally.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account
- Google Gemini API key

---

## Part 1: Supabase Database Setup (15 minutes)

### Step 1: Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in:
   - Name: `karoo-app`
   - Database Password: (save this securely)
   - Region: Choose closest to you
4. Wait 2-3 minutes for project creation

### Step 2: Get Connection Details

1. In your project dashboard, click "Settings" (gear icon)
2. Go to "API" section
3. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (for frontend)
   - **service_role** key (for backend - keep secret!)

### Step 3: Apply SQL Migrations

You need to run 5 SQL migration files in order. Here's how:

1. **Open SQL Editor:**
   - In Supabase dashboard, click "SQL Editor" in left sidebar
   - Click "New query"

2. **Run migrations in this exact order:**

#### Migration 1: Pricing Columns
```sql
-- Copy entire contents of: backend/add_pricing_columns.sql
-- Paste into SQL Editor
-- Click "Run" button (or press Ctrl+Enter)
```

Open `backend/add_pricing_columns.sql` in your code editor, copy all contents, paste into Supabase SQL Editor, and run.

#### Migration 2: Disputes Table
```sql
-- Copy entire contents of: backend/add_disputes_table.sql
-- Paste into SQL Editor
-- Click "Run"
```

#### Migration 3: Scheduling Columns
```sql
-- Copy entire contents of: backend/add_scheduling_columns.sql
-- Paste into SQL Editor
-- Click "Run"
```

#### Migration 4: Complexity Columns
```sql
-- Copy entire contents of: backend/add_complexity_columns.sql
-- Paste into SQL Editor
-- Click "Run"
```

#### Migration 5: Service Progress Table
```sql
-- Copy entire contents of: backend/add_service_progress_table.sql
-- Paste into SQL Editor
-- Click "Run"
```

### Step 4: Verify Migrations

Run this verification query in SQL Editor:

```sql
-- Check if all new columns exist
SELECT 
  table_name,
  column_name,
  data_type
FROM information_schema.columns
WHERE table_name IN ('bookings', 'disputes', 'service_progress', 'scheduling_conflicts', 'waitlist')
  AND column_name IN (
    'final_price', 'price_breakdown', 'job_complexity', 'urgency',
    'current_status', 'quality_checklist', 'dispute_type', 'resolution_status'
  )
ORDER BY table_name, column_name;
```

**Expected result:** Should return multiple rows showing the new columns.

If you see errors like "column already exists", that's okay - it means the migration was already applied.

---

## Part 2: Google Gemini API Setup (5 minutes)

### Step 1: Get Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Select "Create API key in new project" (or choose existing project)
5. Copy the API key (starts with `AIza...`)

**Important:** Keep this key secret! Never commit it to Git.

### Step 2: Configure Backend Environment

1. Navigate to `backend/` folder
2. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

3. Open `backend/.env` in your editor
4. Fill in all values:

```env
# Supabase (from Part 1, Step 2)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key-here

# Google Gemini (from Part 2, Step 1)
GEMINI_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXX

# Google Maps (optional - for distance calculations)
GOOGLE_MAPS_API_KEY=your-google-maps-key-here

# JWT (generate a random secret)
JWT_SECRET=your-random-secret-here-min-32-chars
JWT_EXPIRE_HOURS=24
```

**To generate JWT_SECRET:**
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Or just use a random string like:
# my-super-secret-jwt-key-2024-karoo-app-production
```

### Step 3: Configure Frontend Environment

1. Navigate to `frontend/` folder
2. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

3. Open `frontend/.env` in your editor
4. Fill in:

```env
# Supabase (use anon public key, NOT service_role)
EXPO_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-public-key-here

# Backend API (when running locally)
EXPO_PUBLIC_API_URL=http://localhost:8000
```

---

## Part 3: Install Dependencies (10 minutes)

### Backend Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import google.generativeai as genai; print('Gemini SDK installed:', genai.__version__)"
```

Should output: `Gemini SDK installed: 0.8.3`

### Frontend Dependencies

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list expo react-native
```

---

## Part 4: Run the Application (5 minutes)

### Start Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test backend:**
Open http://localhost:8000/docs in your browser. You should see the Swagger API documentation.

### Start Frontend

In a new terminal:

```bash
cd frontend
npm start
```

**Expected output:**
```
› Metro waiting on exp://192.168.x.x:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web

› Press r │ reload app
› Press m │ toggle menu
```

**Options:**
- Press `w` to open in web browser (easiest for testing)
- Press `a` to open in Android emulator
- Press `i` to open in iOS simulator
- Scan QR code with Expo Go app on your phone

---

## Part 5: Create Test Data (10 minutes)

### Option 1: Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Follow these steps:

#### Create Test Provider

1. **POST /auth/register**
   ```json
   {
     "name": "Ali Khan",
     "phone": "03001234567",
     "password": "test123",
     "role": "provider"
   }
   ```
   Click "Execute"

2. **POST /auth/login**
   ```json
   {
     "phone": "03001234567",
     "password": "test123"
   }
   ```
   Copy the `access_token` from response

3. **Click "Authorize" button at top**
   - Paste token in format: `Bearer your-token-here`
   - Click "Authorize"

4. **PUT /api/workers/profile**
   ```json
   {
     "service_type": "electrician",
     "area": "G-11",
     "rate_per_hour": 600,
     "bio": "10 years experience in electrical work",
     "is_available": true,
     "is_online": true
   }
   ```

#### Create Test User

1. **POST /auth/register**
   ```json
   {
     "name": "Test User",
     "phone": "03009876543",
     "password": "test123",
     "role": "user"
   }
   ```

2. **POST /auth/login**
   ```json
   {
     "phone": "03009876543",
     "password": "test123"
   }
   ```
   Copy the token and authorize again

### Option 2: Using cURL

```bash
# Register provider
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Ali Khan","phone":"03001234567","password":"test123","role":"provider"}'

# Login and get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"03001234567","password":"test123"}'

# Update provider profile (replace TOKEN)
curl -X PUT http://localhost:8000/api/workers/profile \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"service_type":"electrician","area":"G-11","rate_per_hour":600,"is_available":true}'
```

---

## Part 6: Test the System (15 minutes)

### Test 1: Chat with Gemini

1. Open frontend (web or mobile)
2. Login as user (03009876543 / test123)
3. Go to Chat tab
4. Type: `"Mujhe electrician chahiye G-11 mein urgent"`
5. **Expected:** Gemini responds with provider card showing Ali Khan

**Check backend logs for:**
```
[GEMINI AGENT] Function calls detected: search_providers
[PRICING] Calculated: Rs.XXX
[RANKING] Ali Khan → score: 0.XX
```

### Test 2: Book Provider

1. Click "Book Now" on provider card
2. Fill in:
   - Location: "House 123, Street 45, G-11/3"
   - Scheduled Time: (tomorrow's date and time)
   - Urgency: "Urgent"
   - Budget: 1000
3. Click "Confirm Booking"
4. **Expected:** Success message, redirected to bookings page

### Test 3: Provider Accepts Booking

1. Logout and login as provider (03001234567 / test123)
2. Go to Bookings tab
3. Click on pending booking
4. Click "Accept"
5. **Expected:** Status changes to "accepted"

### Test 4: Track Progress

1. As provider, click "Update Status"
2. Select "En Route"
3. **Expected:** User gets notification

---

## Troubleshooting

### Backend Issues

**Error: "GEMINI_API_KEY not set"**
- Check `backend/.env` file exists
- Verify GEMINI_API_KEY is set correctly
- Restart backend server

**Error: "Module 'openai' not found"**
- Run: `pip uninstall openai -y`
- Run: `pip install google-generativeai==0.8.3`

**Error: "Connection to Supabase failed"**
- Verify SUPABASE_URL and SUPABASE_KEY in .env
- Check if Supabase project is active
- Try pinging the URL in browser

**Error: "Column 'final_price' does not exist"**
- SQL migrations not applied
- Go back to Part 1, Step 3 and run migrations

### Frontend Issues

**Error: "Network request failed"**
- Check if backend is running on http://localhost:8000
- Verify EXPO_PUBLIC_API_URL in frontend/.env
- Try: `EXPO_PUBLIC_API_URL=http://192.168.x.x:8000` (your local IP)

**Error: "Supabase client error"**
- Check EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY
- Make sure you're using anon key, not service_role key

### Gemini API Issues

**Error: "API key not valid"**
- Regenerate key at https://aistudio.google.com/app/apikey
- Make sure no extra spaces in .env file
- Format: `GEMINI_API_KEY=AIzaXXXXXX` (no quotes)

**Error: "Quota exceeded"**
- Check quota at https://aistudio.google.com/app/apikey
- Free tier: 15 requests/minute, 1500 requests/day
- Wait or upgrade to paid tier

---

## Quick Reference

### Backend Commands
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

### Frontend Commands
```bash
cd frontend
npm start
# Press 'w' for web, 'a' for Android, 'i' for iOS
```

### Test Credentials
- **User:** 03009876543 / test123
- **Provider:** 03001234567 / test123

### Important URLs
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Supabase Dashboard: https://supabase.com/dashboard
- Gemini API Keys: https://aistudio.google.com/app/apikey

---

## Next Steps

1. ✅ Complete setup (you're done!)
2. 📹 Record demo video (see DEMO_VIDEO_GUIDE.md)
3. 📋 Final checks (see FINAL_CHECKLIST.md)
4. 🚀 Submit to hackathon

---

**Need help?** Check FINAL_CHECKLIST.md for common issues and solutions.
