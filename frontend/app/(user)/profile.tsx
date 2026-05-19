import React, { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, ScrollView, Alert, ActivityIndicator, Platform } from 'react-native'
import { authAPI } from '../../lib/api'
import { auth } from '../../lib/auth'
import { storage } from '../../lib/storage'

export default function UserProfileScreen() {
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    setLoading(true)
    try {
      // Fetch fresh user data from API
      const userData = await authAPI.me()
      setProfile(userData)
      // Update local storage
      await storage.setUser(JSON.stringify(userData))
    } catch (err) {
      console.error('Error fetching profile:', err)
      Alert.alert('Error', 'Profile load nahi ho sakee. Dobara try karein.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    if (Platform.OS === 'web') {
      if (window.confirm('Kya aap logout karna chahte hain?')) {
        auth.logout()
      }
    } else {
      Alert.alert('Logout', 'Kya aap logout karna chahte hain?', [
        { text: 'Nahi', style: 'cancel' },
        { text: 'Haan', style: 'destructive', onPress: () => auth.logout() },
      ])
    }
  }

  if (loading) {
    return (
      <View className="flex-1 bg-gray-950 justify-center items-center">
        <ActivityIndicator size="large" color="#10b981" />
      </View>
    )
  }

  return (
    <ScrollView className="flex-1 bg-gray-950 px-6 py-10">
      <View className="items-center mb-8 bg-gray-900 border border-gray-800 rounded-3xl p-6 shadow-lg shadow-black/40">
        <View className="w-20 h-20 rounded-full bg-emerald-500/10 border border-emerald-500/20 items-center justify-center mb-4">
          <Text className="text-emerald-400 font-extrabold text-2xl">
            {profile?.name ? profile.name.slice(0, 2).toUpperCase() : 'U'}
          </Text>
        </View>

        <Text className="text-white font-black text-2xl mb-1">{profile?.name || 'User Partner'}</Text>
        <Text className="text-emerald-400 text-sm font-bold capitalize mb-4">{profile?.role || 'user'}</Text>

        <View className="w-full border-t border-gray-800/60 pt-4 mt-2 space-y-3">
          <View className="flex-row justify-between">
            <Text className="text-gray-400 text-sm">Phone Number:</Text>
            <Text className="text-white font-bold text-sm">{profile?.phone || 'N/A'}</Text>
          </View>
          {profile?.email && (
            <View className="flex-row justify-between">
              <Text className="text-gray-400 text-sm">Email Address:</Text>
              <Text className="text-white font-bold text-sm">{profile.email}</Text>
            </View>
          )}
          {profile?.city && (
            <View className="flex-row justify-between">
              <Text className="text-gray-400 text-sm">City:</Text>
              <Text className="text-white font-bold text-sm">{profile.city}</Text>
            </View>
          )}
        </View>
      </View>

      <TouchableOpacity
        onPress={handleLogout}
        className="bg-red-500/10 border border-red-500/30 py-4 rounded-xl items-center shadow-lg shadow-black/10"
      >
        <Text className="text-red-400 font-bold text-base">Logout Partner 🚪</Text>
      </TouchableOpacity>
    </ScrollView>
  )
}
