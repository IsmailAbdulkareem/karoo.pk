---
description: Creates complete Expo React Native screen with NativeWind styling, API calls, loading and error states, pull-to-refresh, and optional Supabase Realtime updates.
---

Create a new Expo React Native screen for the Karoo frontend.

Ask me:
1. Screen name? (e.g. Browse Workers, Provider Notifications, Booking Confirm)
2. Which folder? (user) or (provider)?
3. What data does it fetch from backend? Which endpoint?
4. Does it need real-time updates from Supabase? (yes/no)
5. What actions can user take on this screen?

DESIGN SYSTEM TO FOLLOW:
- Background: bg-gray-950
- Cards: bg-gray-900 rounded-2xl
- Primary color: bg-emerald-500 (Karoo brand)
- Text primary: text-white
- Text secondary: text-gray-400
- Border: border-gray-800
- Font: Use Text with className for all text

SCREEN TEMPLATE:
import { useState, useEffect } from 'react'
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native'
import { api } from '@/lib/api'

export default function ScreenName() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    try {
      const response = await api.get('/endpoint')
      setData(response.data)
    } catch (err) {
      setError('Kuch masla aa gaya. Dobara try karo.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  if (loading) return <View className="flex-1 bg-gray-950 items-center justify-center"><ActivityIndicator color="#10b981" /></View>
  if (error) return <View className="flex-1 bg-gray-950 items-center justify-center"><Text className="text-red-400">{error}</Text></View>

  return (
    <View className="flex-1 bg-gray-950">
      {/* Screen content */}
    </View>
  )
}

API INTEGRATION:
Use lib/api.ts Axios instance for all calls.
Show loading spinner while fetching.
Show error message in Urdu if request fails.
Pull-to-refresh on all list screens.

REALTIME (if needed):
Import realtime.ts subscription helper.
Subscribe to correct Supabase channel.
Update state when new data arrives.
Show "New notification" badge/banner.

After generating:
1. Complete screen component file
2. Any reusable components needed (create in /components)
3. Add navigation link from correct tab
4. Show API response shape expected from backend
5. Test checklist: loading state, error state, empty state, data state