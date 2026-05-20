import React, { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, ScrollView, Alert, ActivityIndicator, TextInput } from 'react-native'
import { router } from 'expo-router'
import { Feather } from '@expo/vector-icons'
import { authAPI, workersAPI } from '../../lib/api'
import { storage } from '../../lib/storage'

export default function ProviderEditProfileScreen() {
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    name: '',
    email: '',
    city: '',
    service_type: '',
  })

  const services = [
    { label: 'Electrician', value: 'electrician' },
    { label: 'Plumber', value: 'plumber' },
    { label: 'AC Technician', value: 'ac_technician' },
    { label: 'Tutor', value: 'tutor' },
    { label: 'Cleaner', value: 'cleaner' },
    { label: 'Carpenter', value: 'carpenter' },
    { label: 'Painter', value: 'painter' },
    { label: 'Mechanic', value: 'mechanic' },
    { label: 'Cook', value: 'cook' },
    { label: 'Security Guard', value: 'security_guard' },
  ]

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    setLoading(true)
    try {
      const userData = await authAPI.me()
      setProfile(userData)
      setForm({
        name: userData.name || '',
        email: userData.email || '',
        city: userData.city || '',
        service_type: userData.service_type || '',
      })
    } catch (err) {
      console.error('Error fetching profile:', err)
      Alert.alert('Error', 'Profile load nahi ho sakee. Dobara try karein.')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!form.name.trim()) {
      Alert.alert('Error', 'Name enter karein')
      return
    }
    if (!form.service_type) {
      Alert.alert('Error', 'Service type select karein')
      return
    }

    setSaving(true)
    try {
      // TODO: Create update profile endpoint in backend
      // For now, just show success message
      Alert.alert('Success', 'Profile update request received. Backend endpoint pending.')
      router.back()
    } catch (err: any) {
      Alert.alert('Error', 'Profile update nahi ho saki')
    } finally {
      setSaving(false)
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
    <ScrollView className="flex-1 bg-gray-950 px-6 py-6" contentContainerStyle={{ paddingBottom: 40 }}>
      <Text className="text-white font-bold text-lg mb-6">Edit Profile</Text>

      {/* Name Field */}
      <View className="mb-5">
        <Text className="text-gray-400 text-sm font-bold mb-2">Full Name</Text>
        <TextInput
          className="bg-gray-900 border border-gray-800 text-white px-4 py-3 rounded-xl"
          placeholder="Your name"
          placeholderTextColor="#6b7280"
          value={form.name}
          onChangeText={(text) => setForm({ ...form, name: text })}
        />
      </View>

      {/* Email Field */}
      <View className="mb-5">
        <Text className="text-gray-400 text-sm font-bold mb-2">Email Address</Text>
        <TextInput
          className="bg-gray-900 border border-gray-800 text-white px-4 py-3 rounded-xl"
          placeholder="your@email.com"
          placeholderTextColor="#6b7280"
          value={form.email}
          onChangeText={(text) => setForm({ ...form, email: text })}
          keyboardType="email-address"
        />
      </View>

      {/* City Field */}
      <View className="mb-5">
        <Text className="text-gray-400 text-sm font-bold mb-2">City</Text>
        <TextInput
          className="bg-gray-900 border border-gray-800 text-white px-4 py-3 rounded-xl"
          placeholder="Your city"
          placeholderTextColor="#6b7280"
          value={form.city}
          onChangeText={(text) => setForm({ ...form, city: text })}
        />
      </View>

      {/* Service Type Selector */}
      <View className="mb-6">
        <Text className="text-gray-400 text-sm font-bold mb-3">Service Type</Text>
        <View className="flex-row flex-wrap gap-2">
          {services.map((service) => (
            <TouchableOpacity
              key={service.value}
              onPress={() => setForm({ ...form, service_type: service.value })}
              className={`px-4 py-2 rounded-full border ${
                form.service_type === service.value
                  ? 'bg-emerald-500 border-emerald-500'
                  : 'bg-gray-900 border-gray-800'
              }`}
            >
              <Text
                className={
                  form.service_type === service.value
                    ? 'text-white font-bold text-sm'
                    : 'text-gray-400 text-sm'
                }
              >
                {service.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Action Buttons */}
      <TouchableOpacity
        onPress={handleSave}
        disabled={saving}
        className="bg-emerald-500 py-4 rounded-xl items-center mb-3 shadow-lg shadow-black/10"
      >
        <View className="flex-row items-center">
          <Feather name="check" size={16} color="white" style={{ marginRight: 8 }} />
          <Text className="text-white font-bold text-base">
            {saving ? 'Saving...' : 'Save Changes'}
          </Text>
        </View>
      </TouchableOpacity>

      <TouchableOpacity
        onPress={() => router.back()}
        className="bg-gray-900 border border-gray-800 py-4 rounded-xl items-center"
      >
        <Text className="text-gray-400 font-bold text-base">Cancel</Text>
      </TouchableOpacity>
    </ScrollView>
  )
}
