import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, TouchableOpacity, Switch, ActivityIndicator, Alert } from 'react-native'
import { router } from 'expo-router'
import { authAPI, workersAPI, bookingsAPI, notificationsAPI } from '../../lib/api'
import { auth as Auth } from '../../lib/auth'

export default function ProviderDashboardScreen() {
  const [provider, setProvider] = useState<any>(null)
  const [stats, setStats] = useState({ todayCount: 0, totalEarned: 0, rating: 5.0 })
  const [isOnline, setIsOnline] = useState(false)
  const [isAvailable, setIsAvailable] = useState(false)
  const [unreadNotifications, setUnreadNotifications] = useState(0)
  const [recentBookings, setRecentBookings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [toggling, setToggling] = useState(false)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      // 1. Fetch current user profile first
      const user = await authAPI.me()

      // For provider, we need to get their provider profile
      // Since backend doesn't have a 'me' endpoint for workers, we'll use the user data
      setProvider(user)
      setIsOnline(user.is_online || false)
      setIsAvailable(user.is_available || false)
      setStats((prev) => ({ ...prev, rating: user.rating || 5.0 }))

      // 2. Fetch bookings to count today's & calculate total earnings
      const allBookings = await bookingsAPI.myBookings()
      setRecentBookings((allBookings || []).slice(0, 3))

      const today = new Date().toDateString()
      const todayCount = (allBookings || []).filter((b: any) => {
        if (!b.scheduled_at) return false
        return new Date(b.scheduled_at).toDateString() === today && b.status !== 'cancelled'
      }).length

      // 3. Fetch earnings details
      const earningsRes = await bookingsAPI.earnings()
      setStats({
        todayCount,
        totalEarned: earningsRes?.total_earned_pkr || 0,
        rating: user?.rating || 5.0,
      })

      // 4. Fetch notifications unread
      const notifRes = await notificationsAPI.list()
      setUnreadNotifications(notifRes?.notifications?.filter((n: any) => !n.is_read).length || 0)

    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }


  const handleToggleOnline = async (value: boolean) => {
    setToggling(true)
    try {
      await workersAPI.updateAvailability(value, value)
      setIsOnline(value)
      setIsAvailable(value)
      Alert.alert('✅ Status Updated', value ? 'Aap ab online hain aur naye orders le sakte hain!' : 'Aap offline ho chuke hain.')
    } catch (err: any) {
      console.error(err)
      Alert.alert('Masla', 'Status update karne mein masla hua.')
    } finally {
      setToggling(false)
    }
  }

  const handleLogout = async () => {
    Alert.alert('Logout', 'Kya aap logout karna chahte hain?', [
      { text: 'Nahi', style: 'cancel' },
      { text: 'Haan', style: 'destructive', onPress: () => Auth.logout() },
    ])
  }

  const formatService = (service: string) => {
    if (!service) return ''
    return service
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (loading) {
    return (
      <View className="flex-1 bg-gray-950 justify-center items-center">
        <ActivityIndicator size="large" color="#10b981" />
      </View>
    )
  }

  return (
    <ScrollView className="flex-1 bg-gray-950 px-6 py-10" contentContainerStyle={{ paddingBottom: 40 }}>
      {/* Header section */}
      <View className="flex-row justify-between items-center mb-8 bg-gray-900 border border-gray-800 rounded-3xl p-5 shadow-lg shadow-black/40">
        <View className="flex-row items-center">
          <TouchableOpacity onPress={handleLogout} className="mr-3 p-2 bg-gray-800 rounded-xl">
            <Text className="text-gray-400 font-bold text-xs">🚪 Out</Text>
          </TouchableOpacity>
          <View>
            <Text className="text-white font-black text-lg">{provider?.name || 'Worker Partner'}</Text>
            <Text className="text-emerald-400 text-xs font-bold">
              {formatService(provider?.service_type || 'plumber')}
            </Text>
          </View>
        </View>

        <TouchableOpacity
          onPress={() => router.push('/(provider)/notifications')}
          className="relative p-2.5 bg-gray-850 rounded-xl border border-gray-800"
        >
          <Text className="text-lg">🔔</Text>
          {unreadNotifications > 0 && (
            <View className="absolute -top-1 -right-1 bg-emerald-500 w-5 h-5 rounded-full items-center justify-center border border-gray-900">
              <Text className="text-white text-[9px] font-black">{unreadNotifications}</Text>
            </View>
          )}
        </TouchableOpacity>
      </View>

      {/* Online / Offline status switcher card */}
      <View className="bg-gray-900 border border-gray-800 rounded-3xl p-5 mb-6 flex-row items-center justify-between shadow-md shadow-black/20">
        <View className="flex-1 pr-4">
          <Text className="text-white font-extrabold text-base mb-0.5">Online Status</Text>
          <Text className="text-gray-400 text-xs leading-relaxed">
            {isOnline ? 'Online hoon — naye kaam automatic receive ho rahe hain!' : 'Kaam band hai, online switcher dabayein'}
          </Text>
        </View>
        {toggling ? (
          <ActivityIndicator color="#10b981" />
        ) : (
          <Switch
            value={isOnline}
            onValueChange={handleToggleOnline}
            trackColor={{ false: '#374151', true: '#059669' }}
            thumbColor={isOnline ? '#34d399' : '#9ca3af'}
          />
        )}
      </View>

      {/* Numerical core metrics stats Row */}
      <View className="flex-row justify-between mb-6">
        <View className="w-[31%] bg-gray-900 border border-gray-800 rounded-2xl p-3 items-center shadow-sm">
          <Text className="text-2xl mb-1">📅</Text>
          <Text className="text-white font-extrabold text-lg">{stats.todayCount}</Text>
          <Text className="text-gray-500 text-[9px] font-bold uppercase mt-0.5">Today Jobs</Text>
        </View>

        <View className="w-[31%] bg-gray-900 border border-gray-800 rounded-2xl p-3 items-center shadow-sm">
          <Text className="text-2xl mb-1">💰</Text>
          <Text className="text-white font-extrabold text-base" numberOfLines={1}>PKR {stats.totalEarned}</Text>
          <Text className="text-gray-500 text-[9px] font-bold uppercase mt-0.5">Earned</Text>
        </View>

        <View className="w-[31%] bg-gray-900 border border-gray-800 rounded-2xl p-3 items-center shadow-sm">
          <Text className="text-2xl mb-1">⭐</Text>
          <Text className="text-white font-extrabold text-lg">{stats.rating.toFixed(1)}</Text>
          <Text className="text-gray-500 text-[9px] font-bold uppercase mt-0.5">Rating</Text>
        </View>
      </View>

      {/* Grid Quick Navigation options */}
      <Text className="text-white font-extrabold text-lg mb-3 px-1">Quick Actions</Text>
      <View className="flex-row flex-wrap justify-between mb-6">
        <TouchableOpacity
          onPress={() => router.push('/(provider)/requests')}
          className="w-[48%] bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4 items-center"
        >
          <Text className="text-3xl mb-2">📋</Text>
          <Text className="text-white font-extrabold text-sm text-center">Open Requests</Text>
          <Text className="text-gray-500 text-[10px] text-center mt-0.5">Pick available jobs</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => router.push('/(provider)/bookings')}
          className="w-[48%] bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4 items-center"
        >
          <Text className="text-3xl mb-2">📅</Text>
          <Text className="text-white font-extrabold text-sm text-center">My Bookings</Text>
          <Text className="text-gray-500 text-[10px] text-center mt-0.5">Manage schedule</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => router.push('/(provider)/earnings')}
          className="w-[48%] bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4 items-center"
        >
          <Text className="text-3xl mb-2">💰</Text>
          <Text className="text-white font-extrabold text-sm text-center">Earnings</Text>
          <Text className="text-gray-500 text-[10px] text-center mt-0.5">Track PKR logs</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => router.push('/(provider)/chat')}
          className="w-[48%] bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4 items-center"
        >
          <Text className="text-3xl mb-2">🤖</Text>
          <Text className="text-white font-extrabold text-sm text-center">Provider AI</Text>
          <Text className="text-gray-500 text-[10px] text-center mt-0.5">Urdu AI assistant</Text>
        </TouchableOpacity>
      </View>

      {/* Bottom recent jobs summary list */}
      <Text className="text-white font-extrabold text-lg mb-3 px-1">Recent Bookings</Text>
      {recentBookings.length === 0 ? (
        <View className="bg-gray-900 border border-gray-800 rounded-3xl p-5 items-center">
          <Text className="text-gray-400 text-sm">Koi booking abhi tak nahi mili.</Text>
        </View>
      ) : (
        recentBookings.map((booking) => (
          <TouchableOpacity
            key={booking.id}
            onPress={() => router.push('/(provider)/bookings')}
            className="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-3 flex-row justify-between items-center"
          >
            <View>
              <Text className="text-white font-bold text-sm mb-1">{booking.user_name || 'Customer'}</Text>
              <Text className="text-gray-400 text-xs">📍 {booking.location}</Text>
            </View>
            <View className="bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full">
              <Text className="text-emerald-400 text-xs font-black uppercase">{booking.status}</Text>
            </View>
          </TouchableOpacity>
        ))
      )}
    </ScrollView>
  )
}
