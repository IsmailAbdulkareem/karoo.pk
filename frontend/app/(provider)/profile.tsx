import React, { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, ScrollView, Alert, ActivityIndicator, Platform } from 'react-native'
import { router } from 'expo-router'
import { Feather } from '@expo/vector-icons'
import { authAPI } from '../../lib/api'
import { storage } from '../../lib/storage'

export default function ProviderProfileScreen() {
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    setLoading(true)
    try {
      // Fetch fresh provider data from API
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
    const doLogout = async () => {
      try {
        // Clear storage completely
        await storage.clearAll()
        // Use setTimeout to ensure storage is cleared before navigation
        await new Promise(resolve => setTimeout(resolve, 100))
        // Reset navigation stack and go to landing page
        router.dismissAll()
        router.replace('/')
      } catch (err) {
        console.error('Logout error:', err)
        Alert.alert('Error', 'Logout mein masla hua')
      }
    }
    if (Platform.OS === 'web') {
      if (window.confirm('Kya aap logout karna chahte hain?')) {
        doLogout()
      }
    } else {
      Alert.alert('Logout', 'Kya aap logout karna chahte hain?', [
        { text: 'Nahi', style: 'cancel' },
        { text: 'Haan', style: 'destructive', onPress: doLogout },
      ])
    }
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
      {/* Profile Header */}
      <View className="items-center mb-8 bg-gray-900 border border-gray-800 rounded-3xl p-6 shadow-lg shadow-black/40">
        <View className="w-20 h-20 rounded-full bg-emerald-500/10 border border-emerald-500/20 items-center justify-center mb-4">
          <Text className="text-emerald-400 font-extrabold text-2xl">
            {profile?.name ? profile.name.slice(0, 2).toUpperCase() : 'P'}
          </Text>
        </View>

        <Text className="text-white font-black text-2xl mb-1">{profile?.name || 'Service Partner'}</Text>
        <Text className="text-emerald-400 text-sm font-bold capitalize mb-4">
          {formatService(profile?.service_type || 'provider')}
        </Text>

        <View className="w-full border-t border-gray-800/60 pt-4 mt-2 space-y-3">
          <View className="flex-row justify-between items-center">
            <Text className="text-gray-400 text-sm">Phone Number:</Text>
            <Text className="text-white font-bold text-sm">{profile?.phone || 'N/A'}</Text>
          </View>
          {profile?.email && (
            <View className="flex-row justify-between items-center">
              <Text className="text-gray-400 text-sm">Email Address:</Text>
              <Text className="text-white font-bold text-sm">{profile.email}</Text>
            </View>
          )}
          {profile?.city && (
            <View className="flex-row justify-between items-center">
              <Text className="text-gray-400 text-sm">City:</Text>
              <Text className="text-white font-bold text-sm">{profile.city}</Text>
            </View>
          )}
          {profile?.rating !== undefined && (
            <View className="flex-row justify-between items-center">
              <Text className="text-gray-400 text-sm">Rating:</Text>
              <View className="flex-row items-center">
                <Feather name="star" size={14} color="#f59e0b" />
                <Text className="text-white font-bold text-sm ml-1">{profile.rating || 5.0}</Text>
              </View>
            </View>
          )}
        </View>
      </View>

      {/* Service Status Card */}
      <View className="bg-gray-900 border border-gray-800 rounded-3xl p-5 mb-6 shadow-lg shadow-black/20">
        <Text className="text-white font-bold text-base mb-3">Service Details</Text>
        <View className="space-y-3">
          <View className="flex-row justify-between">
            <Text className="text-gray-400 text-sm">Service Type:</Text>
            <Text className="text-emerald-400 font-bold text-sm">
              {formatService(profile?.service_type) || 'Not selected'}
            </Text>
          </View>
          <View className="flex-row justify-between">
            <Text className="text-gray-400 text-sm">Status:</Text>
            <Text className={`font-bold text-sm ${profile?.is_online ? 'text-emerald-400' : 'text-gray-500'}`}>
              {profile?.is_online ? '🟢 Online' : '🔴 Offline'}
            </Text>
          </View>
        </View>
      </View>

      {/* Action Buttons */}
      <TouchableOpacity
        onPress={() => router.push('/(provider)/edit-profile')}
        className="bg-emerald-500/10 border border-emerald-500/30 py-4 rounded-xl items-center mb-3 shadow-lg shadow-black/10"
      >
        <View className="flex-row items-center">
          <Feather name="edit-2" size={16} color="#10b981" style={{ marginRight: 8 }} />
          <Text className="text-emerald-400 font-bold text-base">Edit Profile</Text>
        </View>
      </TouchableOpacity>

      <TouchableOpacity
        onPress={handleLogout}
        accessibilityRole="button"
        accessibilityLabel="Logout from your account"
        className="bg-red-500/10 border border-red-500/30 py-4 rounded-xl items-center shadow-lg shadow-black/10"
      >
        <View className="flex-row items-center">
          <Feather name="log-out" size={16} color="#f87171" style={{ marginRight: 8 }} />
          <Text className="text-red-400 font-bold text-base">Logout</Text>
        </View>
      </TouchableOpacity>
    </ScrollView>
  )
}
