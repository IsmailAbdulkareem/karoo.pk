import React, { useState, useEffect } from 'react'
import { View, Text, FlatList, ActivityIndicator, Alert } from 'react-native'
import { bookingsAPI } from '../../lib/api'
import EmptyState from '../../components/EmptyState'

interface EarningsBreakdown {
  booking_id: string
  customer_name: string
  service_type: string
  scheduled_at: string
  earned: number
}

interface EarningsData {
  total_earned_pkr: number
  total_completed_jobs: number
  rate_per_hour: number
  earnings_breakdown: EarningsBreakdown[]
}

export default function ProviderEarningsScreen() {
  const [earnings, setEarnings] = useState<EarningsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchEarnings()
  }, [])

  const fetchEarnings = async () => {
    setLoading(true)
    try {
      const res = await bookingsAPI.earnings()
      setEarnings(res)
    } catch (err: any) {
      const errorMsg = err.message || 'Earnings load nahi ho sakeen. Dobara try karein.'
      Alert.alert('Error', errorMsg)
      console.error('Error fetching earnings:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchEarnings()
  }

  const formatService = (service: string) => {
    if (!service) return ''
    return service
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <View className="flex-1 bg-gray-950 px-4 pt-4">
      {loading && !refreshing ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <View className="flex-1">
          {/* Top Summary Card (Emerald Gradient look) */}
          <View className="bg-emerald-500 rounded-3xl p-6 mb-6 shadow-lg shadow-emerald-500/10">
            <Text className="text-emerald-100 text-xs font-bold uppercase tracking-wider mb-1">Total Earnings</Text>
            <Text className="text-white font-black text-3xl mb-4">
              PKR {earnings?.total_earned_pkr || 0}
            </Text>

            <View className="flex-row justify-between border-t border-emerald-400/30 pt-3">
              <View>
                <Text className="text-emerald-100 text-[10px] uppercase font-bold tracking-wider mb-0.5">Completed Jobs</Text>
                <Text className="text-white font-extrabold text-base">{earnings?.total_completed_jobs || 0}</Text>
              </View>
              <View>
                <Text className="text-emerald-100 text-[10px] uppercase font-bold tracking-wider mb-0.5">Hourly Base Rate</Text>
                <Text className="text-white font-extrabold text-base">PKR {earnings?.rate_per_hour || 0}/hr</Text>
              </View>
            </View>
          </View>

          {/* Jobs Breakdown */}
          <Text className="text-white font-extrabold text-lg mb-3 px-1">Earnings Log / History</Text>
          <FlatList
            data={earnings?.earnings_breakdown || []}
            keyExtractor={(item, index) => item.booking_id || index.toString()}
            onRefresh={handleRefresh}
            refreshing={refreshing}
            renderItem={({ item }) => (
              <View className="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-3 flex-row justify-between items-center shadow-sm">
                <View className="flex-1 pr-4">
                  <Text className="text-white font-bold text-sm mb-1">{item.customer_name || 'Customer'}</Text>
                  <View className="flex-row items-center">
                    <Text className="text-emerald-400 text-xs font-bold mr-2">
                      {formatService(item.service_type)}
                    </Text>
                    {item.scheduled_at && (
                      <Text className="text-gray-500 text-[10px]">
                        • {new Date(item.scheduled_at).toLocaleDateString()}
                      </Text>
                    )}
                  </View>
                </View>

                <View className="items-end">
                  <Text className="text-white font-black text-base">
                    +PKR {item.earned}
                  </Text>
                  <Text className="text-gray-500 text-[9px] font-bold uppercase mt-0.5">Earned</Text>
                </View>
              </View>
            )}
            contentContainerStyle={{ paddingBottom: 24 }}
            ListEmptyComponent={
              <EmptyState
                icon="dollar-sign"
                title="Abhi koi earnings nahi hain"
                subtitle="Complete kiye gaye bookings ki financial details yahan show honge."
              />
            }
          />
        </View>
      )}
    </View>
  )
}
