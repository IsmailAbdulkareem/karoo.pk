import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { bookingsAPI, conversationsAPI } from '../../lib/api'
import { storage } from '../../lib/storage'
import { Feather } from '@expo/vector-icons'

export default function BookingDetailsScreen() {
  const { id } = useLocalSearchParams()
  const [booking, setBooking] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [userId, setUserId] = useState<string | null>(null)
  const [userRole, setUserRole] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      fetchBookingDetails()
    }
  }, [id])

  const fetchBookingDetails = async () => {
    setLoading(true)
    try {
      const userStr = await storage.getUser()
      const user = userStr ? JSON.parse(userStr) : null
      if (user) {
        setUserId(user.id || user.user_id)
        setUserRole(user.role)
      }

      const res = await bookingsAPI.myBookings()
      const found = res.data?.find((b: any) => b.id === id)
      setBooking(found || null)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    Alert.alert('Cancel Booking', 'Kya aap ye booking cancel karna chahte hain?', [
      { text: 'Nahi', style: 'cancel' },
      {
        text: 'Haan, Cancel',
        style: 'destructive',
        onPress: async () => {
          try {
            await bookingsAPI.cancel(booking.id)
            Alert.alert('✅ Kamyab', 'Booking cancel ho gayi.')
            fetchBookingDetails()
          } catch (err: any) {
            console.error(err)
            Alert.alert('Masla', err.response?.data?.detail || 'Cancel karne mein masla hua.')
          }
        },
      },
    ])
  }

  const handleAccept = async () => {
    try {
      await bookingsAPI.accept(booking.id)
      Alert.alert('✅ Accepted', 'Booking accept ho gayi!')
      fetchBookingDetails()
    } catch (err: any) {
      console.error(err)
      Alert.alert('Masla', err.response?.data?.detail || 'Accept karne mein masla hua.')
    }
  }

  const handleReject = async () => {
    Alert.alert('Reject Booking', 'Kya aap ye booking reject karna chahte hain?', [
      { text: 'Nahi', style: 'cancel' },
      {
        text: 'Haan, Reject',
        style: 'destructive',
        onPress: async () => {
          try {
            await bookingsAPI.reject(booking.id)
            Alert.alert('✅ Rejected', 'Booking reject ho gayi.')
            fetchBookingDetails()
          } catch (err: any) {
            console.error(err)
            Alert.alert('Masla', err.response?.data?.detail || 'Reject karne mein masla hua.')
          }
        },
      },
    ])
  }

  const handleComplete = async () => {
    Alert.alert('Mark Completed', 'Kya kaam mukammal ho chuka hai?', [
      { text: 'Nahi', style: 'cancel' },
      {
        text: 'Haan, Complete',
        onPress: async () => {
          try {
            await bookingsAPI.complete(booking.id)
            Alert.alert('🎉 Mubarak!', 'Aapne ye job completed mark kar di hai!')
            fetchBookingDetails()
          } catch (err: any) {
            console.error(err)
            Alert.alert('Masla', err.response?.data?.detail || 'Complete karne mein masla hua.')
          }
        },
      },
    ])
  }

  const handleOpenChat = async () => {
    try {
      // Direct messaging uses conversation endpoints. Check if conversation already exists
      const res = await conversationsAPI.list()
      const existing = res.data?.find((c: any) => c.booking_id === booking.id)

      if (existing) {
        router.push(`/conversation/${existing.id}`)
      } else {
        // Create new conversation
        const createRes = await api_conversations_create_fallback(booking.id)
        if (createRes) {
          router.push(`/conversation/${createRes.id}`)
        }
      }
    } catch (err) {
      console.error(err)
      Alert.alert('Masla', 'Chat start karne mein masla hua.')
    }
  }

  const api_conversations_create_fallback = async (bookingId: string) => {
    try {
      // In api.ts, conversationsAPI doesn't have create helper? Let's check conversationsAPI helper
      // Wait, in api.ts we have list, messages, send under conversationsAPI, but not create!
      // Let's call the raw axios client since conversations create is POST /api/conversations { booking_id }
      const { api } = require('../../lib/api')
      const res = await api.post('/api/conversations', { booking_id: bookingId })
      return res.data
    } catch {
      return null
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

  if (!booking) {
    return (
      <View className="flex-1 bg-gray-950 justify-center items-center px-6">
        <Text className="text-white text-lg font-bold mb-4">Booking nahi mil saki</Text>
        <TouchableOpacity
          onPress={() => router.back()}
          className="bg-emerald-500 px-6 py-3 rounded-xl"
        >
          <Text className="text-white font-bold">Wapas Jaein</Text>
        </TouchableOpacity>
      </View>
    )
  }

  const isUser = userRole === 'user'

  return (
    <ScrollView className="flex-1 bg-gray-950 px-6 py-6" contentContainerStyle={{ paddingBottom: 40 }}>
      {/* Booking Header Status Card */}
      <View className="bg-gray-900 border border-gray-800 rounded-3xl p-5 mb-6 shadow-lg shadow-black/40">
        <View className="flex-row justify-between items-start mb-4">
          <View>
            <Text className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-1">Booking Status</Text>
            <Text className="text-emerald-400 font-black text-xl uppercase">{booking.status}</Text>
          </View>
          <View className="bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full">
            <Text className="text-emerald-400 text-xs font-bold">
              {formatService(booking.service_type)}
            </Text>
          </View>
        </View>

        <View className="space-y-2 border-t border-gray-850 pt-3">
          <View className="flex-row justify-between text-sm">
            <Text className="text-gray-400">Scheduled Time:</Text>
            <Text className="text-white font-bold">
              {booking.scheduled_at ? new Date(booking.scheduled_at).toLocaleString() : 'Urgent / As soon as possible'}
            </Text>
          </View>
          <View className="flex-row justify-between text-sm">
            <Text className="text-gray-400">Agreed Price:</Text>
            <Text className="text-white font-black">PKR {booking.agreed_rate || booking.budget || 'Hourly rate dynamic'}</Text>
          </View>
          <View className="flex-row justify-between text-sm">
            <Text className="text-gray-400">Location Address:</Text>
            <Text className="text-white font-medium text-right flex-1 ml-4" numberOfLines={2}>
              {booking.location}
            </Text>
          </View>
          {booking.note && (
            <View className="border-t border-gray-850 pt-2 mt-2">
              <Text className="text-gray-500 text-[10px] font-bold uppercase mb-0.5">Instructions Note:</Text>
              <Text className="text-gray-300 text-xs">"{booking.note}"</Text>
            </View>
          )}
        </View>
      </View>

      {/* Partner Details Section */}
      <View className="bg-gray-900 border border-gray-800 rounded-3xl p-5 mb-6 shadow-md shadow-black/20">
        <Text className="text-white font-extrabold text-base mb-3 border-b border-gray-850 pb-2">
          {isUser ? 'Provider Details' : 'Customer Details'}
        </Text>
        <Text className="text-white font-black text-lg mb-1">
          {isUser ? booking.provider_name || 'Provider Partner' : booking.user_name || 'Customer Partner'}
        </Text>
        <View className="flex-row items-center mb-3">
          <Feather name="phone" size={14} color="#9ca3af" />
          <Text className="text-gray-400 text-xs ml-2">
            {isUser ? booking.provider_phone || 'Verified Phone' : booking.user_phone || 'Verified Phone'}
          </Text>
        </View>

        {booking.status === 'accepted' && (
          <TouchableOpacity
            onPress={handleOpenChat}
            accessibilityRole="button"
            accessibilityLabel="Open direct chat with partner"
            className="w-full bg-emerald-500 py-4 rounded-xl items-center shadow-lg shadow-emerald-500/10 flex-row justify-center space-x-2"
          >
            <Feather name="message-circle" size={20} color="#fff" />
            <Text className="text-white font-bold text-sm ml-2">Direct Chat Kholien</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Action Buttons depending on user role and booking status */}
      <View className="space-y-3">
        {isUser ? (
          // USER ACTIONS
          <>
            {(booking.status === 'pending' || booking.status === 'accepted') && (
              <TouchableOpacity
                onPress={handleCancel}
                accessibilityRole="button"
                accessibilityLabel="Cancel this booking"
                className="w-full bg-red-500/10 border border-red-500/30 py-4 rounded-xl items-center mb-3"
              >
                <Text className="text-red-400 font-bold text-base">Booking Cancel Karo</Text>
              </TouchableOpacity>
            )}

            {booking.status === 'completed' && (
              <TouchableOpacity
                accessibilityRole="button"
                accessibilityLabel="Rate your experience with the provider"
                onPress={() =>
                  router.push({
                    pathname: '/rating/provider',
                    params: {
                      booking_id: booking.id,
                      provider_id: booking.provider_id,
                      provider_name: booking.provider_name,
                    },
                  })
                }
                className="w-full bg-emerald-500 py-4 rounded-xl items-center shadow-lg shadow-emerald-500/20 mb-3"
              >
                <Text className="text-white font-bold text-base">Rate Your Experience</Text>
              </TouchableOpacity>
            )}
          </>
        ) : (
          // PROVIDER ACTIONS
          <>
            {booking.status === 'pending' && (
              <View className="flex-row space-x-3 mb-3">
                <TouchableOpacity
                  onPress={handleReject}
                  accessibilityRole="button"
                  accessibilityLabel="Reject this booking"
                  className="flex-1 border border-red-500/30 py-4 rounded-xl bg-red-500/5 items-center justify-center mr-2"
                >
                  <Text className="text-red-400 font-bold text-base">Reject</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  onPress={handleAccept}
                  accessibilityRole="button"
                  accessibilityLabel="Accept this booking"
                  className="flex-1 bg-emerald-500 py-4 rounded-xl items-center justify-center"
                >
                  <Text className="text-white font-bold text-base">Accept</Text>
                </TouchableOpacity>
              </View>
            )}

            {booking.status === 'accepted' && (
              <TouchableOpacity
                onPress={handleComplete}
                accessibilityRole="button"
                accessibilityLabel="Mark this booking as complete"
                className="w-full bg-emerald-500 py-4 rounded-xl items-center shadow-lg shadow-emerald-500/20 mb-3"
              >
                <Text className="text-white font-bold text-base">Complete Mark Karo</Text>
              </TouchableOpacity>
            )}

            {booking.status === 'completed' && (
              <TouchableOpacity
                accessibilityRole="button"
                accessibilityLabel="Rate the customer partner"
                onPress={() =>
                  router.push({
                    pathname: '/rating/user',
                    params: {
                      booking_id: booking.id,
                      user_id: booking.user_id,
                      user_name: booking.user_name,
                    },
                  })
                }
                className="w-full bg-emerald-500 py-4 rounded-xl items-center shadow-lg shadow-emerald-500/20 mb-3"
              >
                <Text className="text-white font-bold text-base">Rate Customer Partner</Text>
              </TouchableOpacity>
            )}
          </>
        )}
      </View>
    </ScrollView>
  )
}
