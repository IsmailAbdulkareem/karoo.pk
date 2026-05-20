import React, { useState, useEffect } from 'react'
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { bookingsAPI } from '../../lib/api'
import { BookingCard } from '../../components/BookingCard'
import EmptyState from '../../components/EmptyState'
import type { Booking } from '../../lib/types'

type TabType = 'pending' | 'confirmed' | 'completed'

export default function ProviderBookingsScreen() {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [activeTab, setActiveTab] = useState<TabType>('confirmed') // confirmed is standard tab for active jobs
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchBookings()
  }, [])

  const fetchBookings = async () => {
    setLoading(true)
    try {
      const res = await bookingsAPI.myBookings()
      setBookings(res || [])
    } catch (err: any) {
      const errorMsg = err.message || 'Bookings load nahi ho sakeen. Dobara try karein.'
      Alert.alert('Error', errorMsg)
      console.error('Error fetching bookings:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchBookings()
  }

  const handleAcceptBooking = async (id: string) => {
    try {
      await bookingsAPI.accept(id)
      Alert.alert('✅ Kamyab', 'Booking accept ho gayi!')
      fetchBookings()
    } catch (err: any) {
      console.error(err)
      const errorMsg = err.response?.data?.detail || 'Booking accept karne mein masla hua.'
      Alert.alert('Masla', errorMsg)
    }
  }

  const handleRejectBooking = async (id: string) => {
    Alert.alert(
      'Reject Booking?',
      'Kya aap sach mein ye booking reject karna chahte hain?',
      [
        { text: 'Nahi', style: 'cancel' },
        {
          text: 'Haan, Reject',
          style: 'destructive',
          onPress: async () => {
            try {
              await bookingsAPI.reject(id)
              Alert.alert('✅ Rejected', 'Booking reject kar di gayi.')
              fetchBookings()
            } catch (err: any) {
              console.error(err)
              const errorMsg = err.response?.data?.detail || 'Booking reject karne mein masla hua.'
              Alert.alert('Masla', errorMsg)
            }
          },
        },
      ]
    )
  }

  const handleCompleteBooking = async (id: string) => {
    Alert.alert(
      'Kaam Mukammal?',
      'Kya kaam mukammal/complete ho chuka hai?',
      [
        { text: 'Nahi', style: 'cancel' },
        {
          text: 'Haan, Complete',
          onPress: async () => {
            try {
              await bookingsAPI.complete(id)
              Alert.alert('🎉 Mubarak!', 'Aapne ye booking complete kar li hai! Customer rating karein.')
              fetchBookings()
            } catch (err: any) {
              console.error(err)
              const msg = err.response?.data?.detail || 'Booking complete karne mein masla hua.'
              Alert.alert('Masla', msg)
            }
          },
        },
      ]
    )
  }

  const getFilteredBookings = () => {
    return bookings.filter((booking) => {
      if (activeTab === 'pending') {
        return booking.status === 'pending'
      } else if (activeTab === 'confirmed') {
        return booking.status === 'accepted'
      } else {
        return booking.status === 'completed' || booking.status === 'cancelled' || booking.status === 'rejected'
      }
    })
  }

  const filtered = getFilteredBookings()

  return (
    <View className="flex-1 bg-gray-950 px-4 pt-4">
      {/* Top Segmented Tabs */}
      <View className="flex-row bg-gray-900 border border-gray-800 p-1.5 rounded-xl mb-5">
        {(['pending', 'confirmed', 'completed'] as TabType[]).map((tab) => {
          const isActive = activeTab === tab
          return (
            <TouchableOpacity
              key={tab}
              onPress={() => setActiveTab(tab)}
              className={`flex-1 py-3 rounded-lg items-center ${isActive ? 'bg-emerald-500' : 'bg-transparent'}`}
            >
              <Text className={`font-bold text-xs capitalize ${isActive ? 'text-white' : 'text-gray-400'}`}>
                {tab === 'confirmed' ? 'Active ✅' : tab}
              </Text>
            </TouchableOpacity>
          )
        })}
      </View>

      {/* Main List */}
      {loading && !refreshing ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <FlatList
          data={filtered}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <BookingCard
              booking={item}
              role="provider"
              onAccept={handleAcceptBooking}
              onReject={handleRejectBooking}
              onComplete={handleCompleteBooking}
            />
          )}
          onRefresh={handleRefresh}
          refreshing={refreshing}
          className="flex-1"
          contentContainerStyle={{ paddingBottom: 24 }}
          ListEmptyComponent={
            <EmptyState
              emoji="📋"
              title={
                activeTab === 'pending'
                  ? 'Koi pending booking nahi'
                  : activeTab === 'confirmed'
                    ? 'Koi active booking nahi'
                    : 'Koi mukammal booking nahi'
              }
              subtitle="Apna status online rakhein taake naye orders automatic aaein."
            />
          }
        />
      )}
    </View>
  )
}
