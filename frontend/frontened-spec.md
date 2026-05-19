# Karoo Frontend — Step by Step Spec

> Paste ONE step at a time into Claude Code.
> Wait for it to finish + test before moving to next step.

## Base URL
```
http://localhost:8000          (development)
https://ismail233290-karoo-pk.hf.space  (production)
```

## Packages Already Installed
- expo-router (file-based routing)
- nativewind + tailwindcss (styling)
- axios (API calls)
- @react-native-async-storage/async-storage (token storage)
- expo-location (GPS)

---

# STEP 1 — Base Setup (API Client + Auth Store + Folder Structure)

## Task
Create the foundation files. No UI yet.

## Folder Structure to Create
```
app/
  (auth)/
    login.tsx
    register.tsx
  (user)/
    chat.tsx
    browse.tsx
    bookings.tsx
    notifications.tsx
    profile.tsx
  (provider)/
    dashboard.tsx
    requests.tsx
    bookings.tsx
    notifications.tsx
    earnings.tsx
  worker/
    [id].tsx
  booking/
    confirm.tsx
    [id].tsx
  conversation/
    [id].tsx
  _layout.tsx
  index.tsx

lib/
  api.ts
  auth.ts
  storage.ts

components/
  ProviderCard.tsx
  BookingCard.tsx
  NotificationItem.tsx
  MessageBubble.tsx
  StarRating.tsx
  LoadingScreen.tsx
  EmptyState.tsx
```

## File: lib/storage.ts
```typescript
import AsyncStorage from '@react-native-async-storage/async-storage'

export const Storage = {
  async setToken(token: string) {
    await AsyncStorage.setItem('karoo_token', token)
  },
  async getToken(): Promise<string | null> {
    return await AsyncStorage.getItem('karoo_token')
  },
  async setUser(user: any) {
    await AsyncStorage.setItem('karoo_user', JSON.stringify(user))
  },
  async getUser(): Promise<any | null> {
    const user = await AsyncStorage.getItem('karoo_user')
    return user ? JSON.parse(user) : null
  },
  async setRole(role: string) {
    await AsyncStorage.setItem('karoo_role', role)
  },
  async getRole(): Promise<string | null> {
    return await AsyncStorage.getItem('karoo_role')
  },
  async clear() {
    await AsyncStorage.multiRemove(['karoo_token', 'karoo_user', 'karoo_role'])
  }
}
```

## File: lib/api.ts
```typescript
import axios from 'axios'
import { Storage } from './storage'

const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Auto-attach JWT token to every request
api.interceptors.request.use(async (config) => {
  const token = await Storage.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await Storage.clear()
      // redirect to login handled in components
    }
    return Promise.reject(error)
  }
)

// API helper functions
export const authAPI = {
  register: (data: any) => api.post('/auth/register', data),
  login: (data: any) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

export const chatAPI = {
  send: (message: string, user_lat?: number, user_lng?: number) =>
    api.post('/api/chat', { message, user_lat, user_lng }),
  history: () => api.get('/api/chat/history'),
  providerChat: (message: string) =>
    api.post('/api/chat/provider', { message }),
}

export const workersAPI = {
  list: (params?: any) => api.get('/api/workers', { params }),
  getById: (id: string) => api.get(`/api/workers/${id}`),
  updateProfile: (data: any) => api.put('/api/workers/profile', data),
  updateAvailability: (is_online: boolean, is_available: boolean) =>
    api.put(`/api/workers/availability?is_online=${is_online}&is_available=${is_available}`),
}

export const bookingsAPI = {
  create: (data: any) => api.post('/api/bookings', data),
  myBookings: () => api.get('/api/bookings/my'),
  accept: (id: string) => api.put(`/api/bookings/${id}/accept`),
  reject: (id: string) => api.put(`/api/bookings/${id}/reject`),
  cancel: (id: string) => api.put(`/api/bookings/${id}/cancel`),
  complete: (id: string) => api.put(`/api/bookings/${id}/complete`),
  earnings: () => api.get('/api/bookings/earnings'),
}

export const requestsAPI = {
  create: (data: any) => api.post('/api/requests', data),
  open: (params?: any) => api.get('/api/requests/open', { params }),
  accept: (id: string) => api.put(`/api/requests/${id}/accept`),
  my: () => api.get('/api/requests/my'),
}

export const notificationsAPI = {
  list: () => api.get('/api/notifications'),
  markRead: (id: string) => api.put(`/api/notifications/${id}/read`),
  markAllRead: () => api.put('/api/notifications/read-all'),
}

export const ratingsAPI = {
  submit: (data: any) => api.post('/api/ratings', data),
  providerRatings: (id: string) => api.get(`/api/ratings/provider/${id}`),
  userRatings: (id: string) => api.get(`/api/ratings/user/${id}`),
  pending: () => api.get('/api/ratings/pending'),
}

export const conversationsAPI = {
  list: () => api.get('/api/conversations'),
  messages: (id: string) => api.get(`/api/conversations/${id}/messages`),
  send: (id: string, message: string) =>
    api.post(`/api/conversations/${id}/messages`, { message }),
}
```

## File: lib/auth.ts
```typescript
import { Storage } from './storage'
import { authAPI } from './api'
import { router } from 'expo-router'

export const Auth = {
  async login(phone: string, password: string) {
    const res = await authAPI.login({ phone, password })
    const { access_token, role, user_id } = res.data
    await Storage.setToken(access_token)
    await Storage.setRole(role)
    await Storage.setUser({ user_id, role })
    return { role, user_id }
  },

  async register(data: any) {
    const res = await authAPI.register(data)
    const { access_token, role, user_id } = res.data
    await Storage.setToken(access_token)
    await Storage.setRole(role)
    await Storage.setUser({ user_id, role })
    return { role, user_id }
  },

  async logout() {
    await Storage.clear()
    router.replace('/')
  },

  async getRole(): Promise<string | null> {
    return await Storage.getRole()
  },

  async isLoggedIn(): Promise<boolean> {
    const token = await Storage.getToken()
    return !!token
  }
}
```

## File: app/_layout.tsx
```typescript
import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack screenOptions={{
        headerStyle: { backgroundColor: '#030712' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
        contentStyle: { backgroundColor: '#030712' },
      }}>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="(auth)/login" options={{ title: 'Login', headerShown: false }} />
        <Stack.Screen name="(auth)/register" options={{ title: 'Register', headerShown: false }} />
        <Stack.Screen name="(user)/chat" options={{ title: 'Karoo AI' }} />
        <Stack.Screen name="(user)/browse" options={{ title: 'Browse Workers' }} />
        <Stack.Screen name="(user)/bookings" options={{ title: 'My Bookings' }} />
        <Stack.Screen name="(user)/notifications" options={{ title: 'Notifications' }} />
        <Stack.Screen name="(provider)/dashboard" options={{ title: 'Dashboard', headerShown: false }} />
        <Stack.Screen name="(provider)/requests" options={{ title: 'Open Requests' }} />
        <Stack.Screen name="(provider)/bookings" options={{ title: 'My Bookings' }} />
        <Stack.Screen name="(provider)/notifications" options={{ title: 'Notifications' }} />
        <Stack.Screen name="(provider)/earnings" options={{ title: 'Earnings' }} />
        <Stack.Screen name="worker/[id]" options={{ title: 'Provider Profile' }} />
        <Stack.Screen name="booking/confirm" options={{ title: 'Confirm Booking' }} />
        <Stack.Screen name="booking/[id]" options={{ title: 'Booking Details' }} />
      </Stack>
    </>
  )
}
```

## Design System — Use These Classes Everywhere
```
Background:  bg-gray-950  (#030712)
Cards:       bg-gray-900  rounded-2xl p-4
Primary:     bg-emerald-500 (Karoo brand green)
Text main:   text-white
Text sub:    text-gray-400
Border:      border border-gray-800
Input:       bg-gray-800 text-white rounded-xl p-3
Button:      bg-emerald-500 rounded-xl py-3 text-white font-bold
Danger:      bg-red-500
```

## After creating:
Run: npx expo start --web
Confirm no import errors in terminal.

---

# STEP 2 — Landing + Auth Screens

## Task
Create: app/index.tsx, app/(auth)/login.tsx, app/(auth)/register.tsx

## File: app/index.tsx (Landing Page)
```
Full screen landing page with dark background.

Top section:
- App name "Karoo" in large emerald text
- Tagline: "Pakistan ka AI Service Platform"
- Subtext: "Plumber, electrician, AC technician — sab milenge AI se"

Middle section (3 feature cards):
- 🤖 "AI Chat" — Urdu mein baat karo
- 🔍 "Browse" — Apne aap dhundho
- ⭐ "Rated" — Verified providers

Bottom section:
- Green button: "Service Dhundho" → navigate to /(auth)/login
- Outline button: "Provider Hoon" → navigate to /(auth)/register?role=provider
- Small text: "Already registered? Login"

On mount: Check if already logged in
  - If logged in + role=user → redirect to /(user)/chat
  - If logged in + role=provider → redirect to /(provider)/dashboard
```

## File: app/(auth)/login.tsx
```
Dark screen, centered card.

Header: "Karoo mein Khush Amdeed 👋"
Subtext: "Apne phone number se login karo"

Form fields:
- Phone input: placeholder "03001234567"
  keyboardType="phone-pad"
- Password input: placeholder "Password"
  secureTextEntry={true}

Primary button: "Login Karo"
On press:
  setLoading(true)
  try:
    call Auth.login(phone, password)
    if role == "user" → router.replace('/(user)/chat')
    if role == "provider" → router.replace('/(provider)/dashboard')
  catch:
    show error message from API (already in Urdu)
  finally:
    setLoading(false)

Loading state: show ActivityIndicator on button

Bottom text: "Account nahi hai? Register karo"
Link → /(auth)/register

Error display: red text below button
```

## File: app/(auth)/register.tsx
```
Dark screen with scroll.

Header: "Karoo mein Account Banao"

Role selector at top (two big buttons side by side):
  [👤 User]  [🔧 Provider]
  Selected one has emerald background, other outline.
  Default: check route params for ?role=provider

Common fields for both:
- Full Name input
- Phone Number input (keyboardType phone-pad)
- Password input (secureTextEntry)
- City input (optional)

Additional fields shown ONLY when role=provider:
- Service Type (dropdown/picker):
  Options: plumber, electrician, ac_technician, tutor, 
           cleaner, carpenter, painter, mechanic, cook
- Area input: "Aap kahan available ho?"
- Rate per hour: keyboardType numeric placeholder "PKR per hour"
- Bio: multiline, "Apne baare mein batao"

Submit button: "Account Banao"
On press:
  call Auth.register(formData)
  if role=user → router.replace('/(user)/chat')
  if role=provider → router.replace('/(provider)/dashboard')

Error shown in red below button.
Bottom: "Already registered? Login karo" → /(auth)/login
```

## After creating:
Test in browser:
1. Landing page dikh raha hai?
2. Login form submit karo → redirects?
3. Register as user → /(user)/chat
4. Register as provider → /(provider)/dashboard

---

# STEP 3 — User: AI Chat Screen

## Task
Create app/(user)/chat.tsx
This is the MAIN screen — most important for hackathon demo.

## UI Layout
```
Header bar:
  Left: Hamburger/back icon
  Center: "Karoo AI 🤖"
  Right: Bell icon (notifications) with unread badge

Messages area (FlatList, inverted):
  Bot message bubble (left aligned, gray-800 bg)
  User message bubble (right aligned, emerald-600 bg)
  Provider cards appear inside bot message when found

Bottom input bar:
  Text input: "Apni zaroorat batao..."
  Send button (emerald, arrow icon)
  Loading indicator while AI processes
```

## Logic
```typescript
// On mount:
// 1. Load chat history from GET /api/chat/history
// 2. Show welcome message if no history:
//    "Assalam o Alaikum! Main Karoo AI hoon. 
//     Kaunsi service chahiye? Urdu ya English mein batao 😊"

// On send message:
// 1. Add user message to list immediately
// 2. Show typing indicator (3 dots animation)
// 3. Call chatAPI.send(message)
// 4. If needs_clarification=true:
//    Show bot reply only
// 5. If providers returned:
//    Show bot reply + ProviderCards inside chat
// 6. Provider card has "Book Karo" button:
//    router.push('/booking/confirm', { provider, service_type, location })
```

## Provider Card Inside Chat
```
Each provider card shows:
- Name + service type
- ⭐ Rating | 🕐 ETA minutes | 💰 PKR/hr
- Match score bar (visual)
- "Book Karo" button (emerald)
- "Profile Dekho" link
```

## Agent Trace Display
```
Below each AI response, small collapsible section:
"🔍 AI Trace dekho" → expand
Shows agent_trace string in monospace font
Gray-800 background, scrollable
This is for hackathon judges to see!
```

## After creating:
Test:
1. Send "Mujhe plumber chahiye Islamabad mein"
   → should show providers with Book button
2. Send "hello"
   → should show clarification message
3. Agent trace visible and expandable

---

# STEP 4 — User: Browse Workers Screen

## Task
Create app/(user)/browse.tsx and app/worker/[id].tsx

## File: app/(user)/browse.tsx
```
Header: "Workers Browse Karo 🔍"

Filter bar (horizontal scroll):
  Service type chips: All | Plumber | Electrician | AC | Tutor | Cleaner...
  Active chip: emerald background
  
Area search input:
  placeholder: "Area likho (G-11, DHA...)"
  Searches as you type (debounce 500ms)

Provider list (FlatList):
  Each item: ProviderCard component
  Pull to refresh
  Empty state: "Is area mein koi provider nahi mila"

On mount:
  call workersAPI.list()
  
On filter change:
  call workersAPI.list({ service_type, area })
```

## Component: components/ProviderCard.tsx
```
Card (bg-gray-900, rounded-2xl, p-4, mb-3):

Row 1:
  Left: Avatar circle (initials if no photo)
  Right top: Name (white, bold)
  Right sub: service_type badge (emerald small pill)
  
Row 2:
  ⭐ {rating}  |  📍 {area}  |  💰 PKR {rate_per_hour}/hr

Row 3 (if eta_minutes available):
  🕐 {eta_minutes} min door

Row 4:
  "Profile Dekho" outline button → /worker/[id]
  "Book Karo" emerald button → /booking/confirm

Available badge:
  Top right corner: green dot if is_available
```

## File: app/worker/[id].tsx
```
Route: /worker/PROVIDER_ID

On mount:
  call workersAPI.getById(id)
  call ratingsAPI.providerRatings(user_id of provider)

Display:
  Large avatar/initials circle
  Name (large, white)
  Service type badge
  Area, Rate per hour, Rating stars
  Bio text
  
Stats row:
  ⭐ {rating} avg  |  📋 {total_ratings} reviews  |  ✅ Available

Reviews section:
  Last 5 reviews listed
  Each: stars, text, tags, date

Sticky bottom bar:
  "Book Karo → " button (full width, emerald)
  → router.push('/booking/confirm', { provider details })
```

## After creating:
Test:
1. Browse screen loads providers
2. Filter by plumber → filtered list
3. Tap provider → profile screen
4. Ratings visible on profile

---

# STEP 5 — Booking Confirm + My Bookings

## Task
Create app/booking/confirm.tsx and app/(user)/bookings.tsx

## File: app/booking/confirm.tsx
```
Receives params: provider_id, provider_name, service_type, 
                 rating, rate_per_hour, eta_minutes, location

Display booking summary card:
  "Booking Confirm Karo"
  
  Provider info:
    Name, service, rating, PKR/hr, ETA
  
  Form fields:
    📍 Location input (pre-filled from chat if available)
    📅 Date picker: "Kab chahiye?"
      Simple text input: "2026-05-20 10:00"
    💬 Note (optional): "Koi khaas baat?"
    💰 Budget (optional): "Max budget PKR"

  Total estimate: based on rate_per_hour

  Confirm button: "Book Karo ✅"
  On press:
    call bookingsAPI.create({
      provider_id, service_type, location,
      scheduled_at, note, booked_via, budget
    })
    on success:
      show success modal:
        ✅ "Booking ho gayi!"
        "Provider ko notification bhej di gayi"
        "My Bookings" button → /(user)/bookings
    on error:
      show error message
```

## File: app/(user)/bookings.tsx
```
Header: "Meri Bookings 📋"

Tab bar: [Active] [Completed] [Cancelled]

Bookings list using BookingCard component.

Pull to refresh.

Empty state per tab:
  Active: "Abhi koi booking nahi"
  Completed: "Koi complete booking nahi"
```

## Component: components/BookingCard.tsx
```
Card (bg-gray-900, rounded-2xl, p-4, mb-3):

Status badge top right:
  pending → yellow "Pending"
  confirmed → green "Confirmed ✅"
  completed → blue "Complete"
  cancelled → red "Cancelled"

Provider/User name (bold)
Service type + location
Scheduled time
Note (if exists)

Action buttons based on status:
  pending (user view): "Cancel" button (red outline)
  confirmed: "Details Dekho" button
  completed + not rated: "Rate Karo ⭐" button → rating screen
```

## After creating:
Test:
1. Confirm booking → success modal appears
2. My bookings shows the booking
3. Status badges correct colors
4. Cancel button works

---

# STEP 6 — Notifications Screen (Both Sides)

## Task
Create shared notifications component used by both user and provider.
Create app/(user)/notifications.tsx and app/(provider)/notifications.tsx

## Component: components/NotificationItem.tsx
```
Row (py-3, border-b border-gray-800):
  Left: Icon based on type:
    booking_created → 📋
    booking_accepted → ✅
    booking_cancelled → ❌
    booking_completed → 🏁
    service_request → 🔔
    
  Center:
    Title (white, bold if unread)
    Body (gray-400, text-sm)
    Time ago (gray-500, text-xs)
    
  Right: 
    Blue dot if is_read=false
    
On press: mark as read + navigate to relevant screen
  ref_id is booking_id → go to booking details
```

## File: app/(user)/notifications.tsx
```
Header row:
  "Notifications 🔔"
  "Sab Read Karo" button (top right) → markAllRead()

Unread count badge in header

FlatList of NotificationItem

Empty state: "Koi notification nahi"

On mount:
  call notificationsAPI.list()
  
Pull to refresh.
```

## File: app/(provider)/notifications.tsx
```
SAME as user notifications BUT:
For booking_created notifications:
  Show extra action buttons inline:
    [✅ Accept] [❌ Reject]
  
  On Accept: call bookingsAPI.accept(ref_id)
  On Reject: call bookingsAPI.reject(ref_id)
  
  After action: refresh notifications list
  Show success message: "Booking accept ho gayi"
```

## After creating:
Test:
1. User notifications show after booking created
2. Provider notifications show Accept/Reject buttons
3. Mark all read works
4. Unread count updates

---

# STEP 7 — Provider Side Screens

## Task
Create provider dashboard, open requests, bookings, earnings screens.

## File: app/(provider)/dashboard.tsx
```
This is provider's HOME screen.

Header: "Karoo Provider 👷"
Right: Bell icon with notification badge → /(provider)/notifications
Logout button (top left)

Stats row (3 cards):
  📋 Today's Bookings count
  💰 Total Earned (PKR)
  ⭐ My Rating

Online/Offline toggle:
  Big switch: "Online hoon — naye kaam le raha hoon"
  Calls workersAPI.updateAvailability()
  Green = online, Gray = offline

Quick actions grid (2x2):
  [🔔 Notifications] [📋 Open Requests]
  [📅 My Bookings]   [💰 Earnings]

Bottom: Recent bookings (last 3)
  Each shows status + user name + service

On mount:
  Load provider profile
  Load today's bookings count
  Load earnings
  Load unread notification count
```

## File: app/(provider)/requests.tsx
```
Header: "Open Requests 📋"

Filter chips: All | By my service type

FlatList of request cards:

Each request card (bg-gray-900, rounded-2xl):
  User name (first name only for privacy)
  Service type badge (emerald)
  📍 Location
  📅 Preferred time
  💰 Budget: PKR {budget} (if provided)
  ⏰ Posted {time ago}
  
  "Yeh Kaam Loon" button (full width, emerald)
  On press:
    Confirm dialog: "Kya aap yeh kaam lena chahte hain?"
    On confirm: call requestsAPI.accept(id)
    On success: 
      Show "Booking create ho gayi!" toast
      Remove from list
      Navigate to /(provider)/bookings

Empty state: "Abhi koi open request nahi"
Pull to refresh.
```

## File: app/(provider)/bookings.tsx
```
SAME as user bookings BUT provider view:

Tab bar: [Pending] [Confirmed] [Completed]

Each BookingCard shows:
  Customer name + service + location + time
  
Pending tab:
  Each card has [✅ Accept] [❌ Reject] buttons
  On Accept: bookingsAPI.accept(id) → refresh
  On Reject: bookingsAPI.reject(id) → refresh

Confirmed tab:
  Each card has [✅ Complete Karo] button
  On press: bookingsAPI.complete(id) → move to completed tab

Completed tab:
  Show completed jobs
  "Rate Customer" button if not rated
```

## File: app/(provider)/earnings.tsx
```
Header: "Meri Earnings 💰"

Summary card (emerald gradient):
  Total Earned: PKR {total}
  Total Jobs: {count}
  
List of completed bookings with earnings:
  Customer name | Service | Amount earned | Date
  
Note: earnings = agreed_rate ?? budget ?? rate_per_hour
```

## File: app/(provider)/chat.tsx (Provider AI Chat)
```
SAME UI as user chat BUT:

Welcome message:
  "Assalam o Alaikum! Main Karoo AI hoon.
   Koi kaam dhundna hai? Batao! 😊"

Input placeholder: "Koi kaam hai? Poocho..."

Calls chatAPI.providerChat(message) instead of chatAPI.send()

Response shows:
  If find_requests: list of open requests as cards
    Each card has "Accept Karo" button
  If check_bookings: list of bookings
  If check_earnings: earnings summary
```

## After creating:
Test:
1. Dashboard shows stats
2. Online toggle works
3. Open requests load
4. Accept request → booking created
5. Bookings tab shows correct items
6. Complete booking → moves to completed

---

# STEP 8 — Rating Screens + Bottom Navigation

## Task
Create rating screens and add bottom tab navigation.

## File: app/rating/provider.tsx
```
Route params: booking_id, provider_id, provider_name

"Rate your experience with {provider_name}"

Star selector (1-5):
  5 large stars, tap to select
  Selected: filled emerald, Unselected: gray outline

Tag chips (multi-select):
  [punctual] [professional] [quality_work] 
  [affordable] [friendly] [clean_work]
  
  Selected tags: emerald background

Review text (optional):
  multiline input: "Apna tajurba share karo..."
  max 200 chars, show counter

Submit button: "Rating Bhejo ⭐"
On press:
  call ratingsAPI.submit({
    booking_id, ratee_id: provider_id,
    stars, review_text, tags
  })
  on success: "Shukriya! Rating submit ho gayi" → go back

Skip button: "Baad mein Rate Karo" → go back
```

## File: app/rating/user.tsx (Provider rates customer)
```
SAME structure BUT:

"Is customer ko rate karo"

Tags:
  [responsive] [clear_requirements] [on_time_payment]
  [good_communication] [respectful]
  
Label: "Reliability Score"
```

## Bottom Navigation

### For User — Update app/(user)/_layout.tsx
```typescript
import { Tabs } from 'expo-router'

export default function UserLayout() {
  return (
    <Tabs screenOptions={{
      tabBarStyle: { backgroundColor: '#111827', borderTopColor: '#1f2937' },
      tabBarActiveTintColor: '#10b981',
      tabBarInactiveTintColor: '#6b7280',
    }}>
      <Tabs.Screen name="chat" options={{
        title: 'AI Chat',
        tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🤖</Text>
      }} />
      <Tabs.Screen name="browse" options={{
        title: 'Browse',
        tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🔍</Text>
      }} />
      <Tabs.Screen name="bookings" options={{
        title: 'Bookings',
        tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>📋</Text>
      }} />
      <Tabs.Screen name="notifications" options={{
        title: 'Alerts',
        tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🔔</Text>
      }} />
    </Tabs>
  )
}
```

### For Provider — Update app/(provider)/_layout.tsx
```typescript
// Same Tabs structure with:
// dashboard, requests, bookings, notifications, earnings
```

## After creating:
Test complete user journey:
1. Register → login
2. Chat → find provider → book
3. Check notifications
4. Browse workers → view profile → book
5. Check my bookings

Test provider journey:
1. Login as provider
2. Set online
3. See notification → accept
4. Complete booking
5. Check earnings

---

# STEP 9 — Final Polish + Vercel Deploy

## Task
Add loading states, error handling, and deploy.

## Loading Screen Component
```
components/LoadingScreen.tsx:

Full screen, bg-gray-950:
  Center: Animated spinner (emerald color)
  Below: "Loading..." text in gray

Use this when:
- App first loads (checking auth)
- Any full page data fetch
```

## Empty State Component
```
components/EmptyState.tsx:
Props: emoji, title, subtitle, buttonText?, onPress?

Center aligned:
  Large emoji (text-6xl)
  Title (white, text-xl, font-bold)
  Subtitle (gray-400, text-center)
  Optional button (emerald)
```

## Toast Messages
```
Add simple toast for success/error:
Use Alert.alert() from react-native for simplicity

Success: Alert.alert("✅ Kamyab!", message)
Error:   Alert.alert("❌ Kuch Masla!", error.message)
```

## .env File
```
EXPO_PUBLIC_API_URL=https://ismail233290-karoo-pk.hf.space
```

## Vercel Deploy
```bash
# 1. Build web version
npx expo export --platform web

# 2. Install Vercel CLI
npm i -g vercel

# 3. Deploy
vercel --prod

# Settings:
# Framework: Other
# Build Command: npx expo export --platform web
# Output Directory: dist
# Install Command: npm install
```

## vercel.json (create in frontend root)
```json
{
  "buildCommand": "npx expo export --platform web",
  "outputDirectory": "dist",
  "framework": null,
  "rewrites": [{ "source": "/(.*)", "destination": "/" }]
}
```

## Final Test Checklist
```
[ ] Landing page loads
[ ] User register + login works
[ ] Provider register + login works
[ ] AI chat finds providers
[ ] Agent trace visible in chat
[ ] Browse workers + filter works
[ ] Provider profile page
[ ] Book a provider flow
[ ] Provider gets notification
[ ] Provider accepts via notification
[ ] My bookings shows correct status
[ ] Provider completes booking
[ ] Rating screen appears
[ ] Provider earnings shows
[ ] Open requests + accept works
[ ] Deployed on Vercel
[ ] Works on mobile browser
```

---

## DEMO ORDER (for hackathon video)

```
1. Show landing page (10 sec)
2. Register as user (15 sec)
3. Type in AI chat: "Mujhe plumber chahiye G-11 mein"
   Show agent trace expanding (20 sec) ← KEY MOMENT
4. Book the top provider (15 sec)
5. Switch to provider account
6. Show notification + Accept (15 sec)
7. Show real-time notification on user side (10 sec)
8. Complete booking (10 sec)
9. Rate each other (15 sec)
10. Show Antigravity trace logs (20 sec) ← JUDGES LOVE THIS
Total: ~2.5 minutes, leaves time for narration
```