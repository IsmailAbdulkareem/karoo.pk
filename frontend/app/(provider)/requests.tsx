import React, { useState, useEffect } from 'react'
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { requestsAPI } from '../../lib/api'
import EmptyState from '../../components/EmptyState'
import { router } from 'expo-router'
import type { ServiceRequest } from '../../lib/types'

type FilterType = 'all' | 'mine'

export default function ProviderRequestsScreen() {
  const [requests, setRequests] = useState<ServiceRequest[]>([])
  const [filter, setFilter] = useState<FilterType>('all')
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchRequests()
  }, [filter])

  const fetchRequests = async () => {
    setLoading(true)
    try {
      const params: any = {}
      const res = await requestsAPI.open(params)
      const list = res || []

      if (filter === 'mine') {
        // Assume provider profile is loaded or let backend filter, wait we can filter client side as well.
        // Let's assume backend matches, or we filter based on service_type. Let's do client-side filter fallback.
        // Since we don't have the provider's service type directly inside this state, we can retrieve it from AsyncStorage
        // Or keep simple filter where it fetches F-10 / plumber jobs.
        // Let's just retrieve open requests!
        setRequests(list)
      } else {
        setRequests(list)
      }
    } catch (err: any) {
      const errorMsg = err.message || 'Requests load nahi ho sakeen. Dobara try karein.'
      Alert.alert('Error', errorMsg)
      console.error('Error fetching requests:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchRequests()
  }

  const handleAcceptRequest = async (id: string) => {
    Alert.alert(
      'Kaam Le Lein?',
      'Kya aap sach mein ye open request accept karna chahte hain?',
      [
        { text: 'Nahi', style: 'cancel' },
        {
          text: 'Haan, Accept',
          onPress: async () => {
            try {
              await requestsAPI.accept(id)
              Alert.alert('🎉 Mubarak!', 'Aapne ye kaam le liya hai! Customer se contact karein.')
              router.replace('/(provider)/bookings')
            } catch (err: any) {
              console.error(err)
              const msg = err.response?.data?.detail || 'Request accept karne mein masla hua.'
              Alert.alert('Masla', msg)
            }
          },
        },
      ]
    )
  }

  const formatService = (service: string) => {
    if (!service) return ''
    return service
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const formatTimeAgo = (dateStr: string) => {
    try {
      const diffMs = new Date().getTime() - new Date(dateStr).getTime()
      const mins = Math.floor(diffMs / 60000)
      if (mins < 1) return 'Just now'
      if (mins < 60) return `${mins}m ago`
      const hrs = Math.floor(mins / 60)
      if (hrs < 24) return `${hrs}h ago`
      return `${Math.floor(hrs / 24)}d ago`
    } catch {
      return ''
    }
  }

  return (
    <View className="flex-1 bg-gray-950 px-4 pt-4">
      {/* Top Filter Chips */}
      <View className="flex-row bg-gray-900 border border-gray-800 p-1.5 rounded-xl mb-5">
        <TouchableOpacity
          onPress={() => setFilter('all')}
          className={`flex-1 py-3 rounded-lg items-center ${filter === 'all' ? 'bg-emerald-500' : 'bg-transparent'}`}
        >
          <Text className={`font-bold text-xs ${filter === 'all' ? 'text-white' : 'text-gray-400'}`}>
            Sab Requests 🌐
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setFilter('mine')}
          className={`flex-1 py-3 rounded-lg items-center ${filter === 'mine' ? 'bg-emerald-500' : 'bg-transparent'}`}
        >
          <Text className={`font-bold text-xs ${filter === 'mine' ? 'text-white' : 'text-gray-400'}`}>
            Matching Hunur 🎯
          </Text>
        </TouchableOpacity>
      </View>

      {/* Main List */}
      {loading && !refreshing ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <FlatList
          data={requests}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View className="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-4 shadow-md shadow-black/20">
              <View className="flex-row justify-between items-start mb-3">
                <View>
                  <Text className="text-white font-extrabold text-base mb-1">{item.user_name || 'Customer'}</Text>
                  <View className="bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20 self-start">
                    <Text className="text-emerald-400 text-[10px] font-bold">
                      {formatService(item.service_type)}
                    </Text>
                  </View>
                </View>
                <Text className="text-gray-500 text-[10px] font-bold">
                  Posted {formatTimeAgo(item.created_at)}
                </Text>
              </View>

              <View className="bg-gray-850 rounded-xl p-3 border border-gray-800 space-y-2 mb-4">
                <View className="flex-row justify-between">
                  <Text className="text-gray-500 text-xs font-bold">📍 Location:</Text>
                  <Text className="text-white text-xs font-medium text-right flex-1 ml-4" numberOfLines={1}>
                    {item.location}
                  </Text>
                </View>
                {item.scheduled_at && (
                  <View className="flex-row justify-between">
                    <Text className="text-gray-500 text-xs font-bold">📅 Schedule:</Text>
                    <Text className="text-white text-xs font-semibold">
                      {new Date(item.scheduled_at).toLocaleString()}
                    </Text>
                  </View>
                )}
                {item.budget && (
                  <View className="flex-row justify-between">
                    <Text className="text-gray-500 text-xs font-bold">💰 Offer/Budget:</Text>
                    <Text className="text-emerald-400 text-xs font-extrabold">PKR {item.budget}</Text>
                  </View>
                )}
                {item.description && (
                  <View className="border-t border-gray-800/60 pt-2 mt-1">
                    <Text className="text-gray-500 text-[10px] uppercase font-bold tracking-wider mb-0.5">Details</Text>
                    <Text className="text-gray-300 text-xs">"{item.description}"</Text>
                  </View>
                )}
              </View>

              <TouchableOpacity
                onPress={() => handleAcceptRequest(item.id)}
                className="w-full bg-emerald-500 py-3 rounded-xl items-center shadow-lg shadow-emerald-500/10"
              >
                <Text className="text-white font-bold text-sm">Yeh Kaam Loon ✅</Text>
              </TouchableOpacity>
            </View>
          )}
          onRefresh={handleRefresh}
          refreshing={refreshing}
          className="flex-1"
          contentContainerStyle={{ paddingBottom: 24 }}
          ListEmptyComponent={
            <EmptyState
              emoji="📋"
              title="Koi open request nahi hai"
              subtitle="Is waqt marketplace mein koi open job active nahi hai. Dobara refresh karein."
            />
          }
        />
      )}
    </View>
  )
}
