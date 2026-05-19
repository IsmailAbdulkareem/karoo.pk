import React, { useState, useEffect, useCallback } from 'react'
import { View, Text, TextInput, FlatList, ScrollView, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { workersAPI } from '../../lib/api'
import ProviderCard from '../../components/ProviderCard'
import EmptyState from '../../components/EmptyState'
import { Feather } from '@expo/vector-icons'
import type { Provider } from '../../lib/types'

const SERVICE_CHIPS = [
  { label: 'All Services', value: 'all' },
  { label: 'Plumber', value: 'plumber' },
  { label: 'Electrician', value: 'electrician' },
  { label: 'AC Tech', value: 'ac_technician' },
  { label: 'Tutor', value: 'tutor' },
  { label: 'Cleaner', value: 'cleaner' },
  { label: 'Carpenter', value: 'carpenter' },
  { label: 'Painter', value: 'painter' },
  { label: 'Mechanic', value: 'mechanic' },
  { label: 'Cook', value: 'cook' },
  { label: 'Security', value: 'security_guard' },
]

export default function BrowseScreen() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [selectedService, setSelectedService] = useState('all')
  const [searchArea, setSearchArea] = useState('')
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchProviders()
  }, [selectedService])

  // Simple debounce logic for searchArea
  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchProviders()
    }, 500)

    return () => clearTimeout(delayDebounceFn)
  }, [searchArea])

  const fetchProviders = async () => {
    setLoading(true)
    setError(null)
    try {
      const params: any = {}
      if (selectedService !== 'all') {
        params.service_type = selectedService
      }
      if (searchArea.trim()) {
        params.area = searchArea.trim()
      }

      const res = await workersAPI.list(params)
      setProviders(res || [])
    } catch (err: any) {
      const errorMsg = err.message || 'Providers load nahi ho sake. Dobara try karein.'
      setError(errorMsg)
      Alert.alert('Error', errorMsg)
      console.error('Error fetching providers:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchProviders()
  }

  return (
    <View className="flex-1 bg-gray-950">
      {/* Header */}
      <View className="bg-gradient-to-r from-gray-900 to-gray-800 px-6 py-6 border-b border-emerald-500/20">
        <Text className="text-3xl font-bold text-white mb-2">Browse Providers</Text>
        <Text className="text-gray-400">Find the perfect service provider</Text>
      </View>

      <View className="px-4 pt-4">
        {/* Search area text input */}
        <View className="mb-4">
          <Text className="text-white text-base font-semibold mb-2">📍 Search by Area</Text>
          <View className="relative">
            <TextInput
              value={searchArea}
              onChangeText={setSearchArea}
              placeholder="Enter area (e.g., G-11, DHA, F-10)..."
              placeholderTextColor="#6b7280"
              className="bg-gray-800 text-white rounded-xl px-4 py-3.5 pl-11 border border-gray-700 focus:border-emerald-500 text-base"
            />
            <View className="absolute left-3 top-3.5">
              <Feather name="search" size={20} color="#10b981" />
            </View>
          </View>
        </View>

        {/* Horizontal Service Category Scroll */}
        <View className="mb-5">
          <Text className="text-white text-base font-semibold mb-3">🔧 Filter by Service</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{ paddingRight: 10 }}
          >
            {SERVICE_CHIPS.map((chip) => {
              const isActive = selectedService === chip.value
              return (
                <TouchableOpacity
                  key={chip.value}
                  onPress={() => setSelectedService(chip.value)}
                  className={`px-4 py-2.5 rounded-xl border mr-2.5 items-center justify-center shadow-sm ${
                    isActive
                      ? 'bg-gradient-to-r from-emerald-600 to-emerald-500 border-emerald-400'
                      : 'bg-gray-800 border-gray-700'
                  }`}
                >
                  <Text className={`text-sm font-bold ${isActive ? 'text-white' : 'text-gray-400'}`}>
                    {chip.label}
                  </Text>
                </TouchableOpacity>
              )
            })}
          </ScrollView>
        </View>
      </View>

      {/* Main List */}
      {loading && !refreshing ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <FlatList
          data={providers}
          keyExtractor={(item: any) => item.id}
          renderItem={({ item }) => <ProviderCard provider={item} />}
          onRefresh={handleRefresh}
          refreshing={refreshing}
          className="flex-1"
          contentContainerStyle={{ paddingBottom: 24 }}
          ListEmptyComponent={
            <EmptyState
              emoji="🔍"
              title="Koi Provider nahi mila"
              subtitle="Hamare pass abhi is selection ke liye koi online aur available provider nahi hai. Dobara check karein."
              buttonText="Reset Filters"
              onPress={() => {
                setSelectedService('all')
                setSearchArea('')
              }}
            />
          }
        />
      )}
    </View>
  )
}
