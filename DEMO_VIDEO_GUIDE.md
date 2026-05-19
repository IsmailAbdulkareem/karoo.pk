 Demo Video Recording Guide

## Setup (15 minutes)

### 1. Prepare Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Keep terminal visible to show Gemini traces.

### 2. Prepare Frontend
```bash
cd frontend
npm start
# Press 'w' for web browser
```

### 3. Create Test Data
Run these in Swagger (http://localhost:8000/docs):

**Create Test Provider:**
```json
POST /auth/register
{
  "name": "Ali Khan",
  "phone": "03001234567",
  "password": "test123",
  "role": "provider"
}

POST /auth/login
{
  "phone": "03001234567",
  "password": "test123"
}
// Copy the token

PUT /api/workers/profile (with provider token)
{
  "service_type": "electrician",
  "area": "G-11",
  "rate_per_hour": 600,
  "bio": "10 years experience",
  "is_available": true,
  "is_online": true
}
```

**Create Test User:**
```json
POST /auth/register
{
  "name": "Test User",
  "phone": "03009876543",
  "password": "test123",
  "role": "user"
}
```

---

## Recording (30 minutes)

### Screen Layout
```
┌─────────────────────────────────────────┐
│  Browser (Frontend)                     │
│  - Chat interface                       │
│  - Provider cards                       │
│  - Booking flow                         │
├─────────────────────────────────────────┤
│  Terminal (Backend Logs)                │
│  - Gemini traces                        │
│  - Pricing calculations                 │
│  - Tool executions                      │
└─────────────────────────────────────────┘
```

### Recording Steps

**[0:00-0:30] Introduction**
- Show title slide: "Karoo - AI Service Orchestrator"
- "Built with Google Gemini for Pakistan's informal economy"

**[0:30-1:00] Problem + Solution**
- Show WhatsApp chaos screenshot
- Explain: "70M workers, no platform, no transparency"
- Show Karoo architecture diagram

**[1:00-2:30] Live Demo**

1. **Open chat, type:**
   ```
   "Mujhe electrician chahiye G-11 mein urgent"
   ```

2. **Point to backend logs:**
   ```
   [GEMINI AGENT] Function calls detected: search_providers
   [PRICING] Base: Rs.600, Distance: Rs.50, Urgent: Rs.180
   [RANKING] Ali Khan → score: 0.91
   ```

3. **Show provider cards with:**
   - Match score: 0.91
   - ETA: 8 minutes
   - Price breakdown: Rs.830

4. **Book provider**

5. **Show notifications:**
   - "Booking confirmed"
   - "Provider is en route"

6. **Switch to provider view:**
   - Accept booking
   - Update status: "en_route" → "arrived" → "in_progress"
   - Submit checklist
   - Mark completed

7. **Show ratings:**
   - Both parties rate each other

**[2:30-3:30] Technical Deep Dive**

Point to terminal and explain:
- "Gemini extracts intent from mixed Urdu/English"
- "6-factor ranking algorithm"
- "Dynamic pricing with transparency"
- "Scheduling prevents double-booking"
- "Dispute auto-resolution"

**[3:30-4:00] Impact**
- "70M market in Pakistan"
- "Scalable to other countries"
- "Reduces support burden with AI"

**[4:00-4:30] Closing**
- "Thank you!"
- Show GitHub repo
- Show contact info

---

## Recording Tools

### Option 1: OBS Studio (Recommended)
- Free and professional
- Download: https://obsproject.com/
- Can record screen + webcam
- Good quality

### Option 2: Built-in Screen Recorder
- **Windows:** Win + G (Game Bar)
- **Mac:** Cmd + Shift + 5
- **Linux:** SimpleScreenRecorder

### Tips
1. **Practice first** - Do 2-3 dry runs
2. **Speak clearly** - Explain what's happening
3. **Keep it moving** - Don't pause too long
4. **Show, don't tell** - Let the demo speak
5. **Time yourself** - Stay within 3-5 minutes

---

## After Recording

### 1. Edit (Optional)
- Trim beginning/end
- Add title slide
- Add closing slide
- Export as MP4

### 2. Upload
- YouTube (unlisted)
- Google Drive (public link)
- Vimeo

### 3. Test Link
- Open in incognito window
- Verify it plays
- Check audio/video quality

---

## Backup Plan

If live demo fails:
1. Have screenshots ready
2. Pre-record backend logs
3. Show architecture diagrams
4. Explain features verbally

---

## Final Checklist

Before recording:
- [ ] Backend running with logs visible
- [ ] Frontend running in browser
- [ ] Test data created (user + provider)
- [ ] All features tested once
- [ ] Script memorized
- [ ] Recording software tested
- [ ] Backup plan ready

During recording:
- [ ] Speak clearly
- [ ] Point to important parts
- [ ] Show Gemini traces
- [ ] Demonstrate key features
- [ ] Stay within time limit

After recording:
- [ ] Video plays correctly
- [ ] Audio is clear
- [ ] All features shown
- [ ] Upload and get link
- [ ] Test link works

---

## Common Issues

**Issue:** Backend not responding
**Fix:** Restart server, check .env file

**Issue:** Gemini API error
**Fix:** Verify GEMINI_API_KEY is set correctly

**Issue:** No providers showing
**Fix:** Create test provider with is_available=true

**Issue:** Pricing not showing
**Fix:** Run add_pricing_columns.sql migration

**Issue:** Recording lag
**Fix:** Close other apps, reduce screen resolution

---

Good luck! 🎬
