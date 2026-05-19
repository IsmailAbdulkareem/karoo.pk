import React, { useState, useEffect } from 'react'
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { notificationsAPI, bookingsAPI } from '../../lib/api'
import NotificationItem from '../../components/NotificationItem'
import EmptyState from '../../components/EmptyState'
import { router } from 'expo-router'

export default function ProviderNotificationsScreen() {
  const [notifications, setNotifications] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchNotifications()
  }, [])

  const fetchNotifications = async () => {
    setLoading(true)
    try {
      const res = await notificationsAPI.list()
      // API returns array directly or wrapped inside an object
      const list = Array.isArray(res)
        ? res
        : (res && Array.isArray(res.notifications) ? res.notifications : [])
      setNotifications(list)
    } catch (err: any) {
      const errorMsg = err?.message || 'Notifications load nahi ho sakeen.'
      Alert.alert('Error', errorMsg)
      console.error('Error fetching notifications:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchNotifications()
  }

  const handleMarkAllRead = async () => {
    try {
      await notificationsAPI.markAllRead()
      fetchNotifications()
    } catch (err) {
      console.error(err)
    }
  }

  const handleNotificationPress = async (id: string, refId?: string) => {
    try {
      await notificationsAPI.markRead(id)
      fetchNotifications()
      if (refId) {
        router.push('/(provider)/bookings')
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleAcceptBooking = async (bookingId: string) => {
    try {
      await bookingsAPI.accept(bookingId)
      Alert.alert('✅ Kamyab', 'Booking accept ho gayi!')
      fetchNotifications()
    } catch (err: any) {
      console.error(err)
      const errorMsg = err.response?.data?.detail || 'Booking accept karne mein masla hua.'
      Alert.alert('Masla', errorMsg)
    }
  }

  const handleRejectBooking = async (bookingId: string) => {
    try {
      await bookingsAPI.reject(bookingId)
      Alert.alert('✅ Rejected', 'Booking reject kar di gayi.')
      fetchNotifications()
    } catch (err: any) {
      console.error(err)
      const errorMsg = err.response?.data?.detail || 'Booking reject karne mein masla hua.'
      Alert.alert('Masla', errorMsg)
    }
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  return (
    <View className="flex-1 bg-gray-950">
      {/* Top Header Controls */}
      <View className="flex-row justify-between items-center px-4 py-3 bg-gray-900 border-b border-gray-800">
        <View className="flex-row items-center">
          <Text className="text-white font-bold text-sm">
            Unread Alerts:{' '}
            <Text className="text-emerald-400 font-extrabold">{unreadCount}</Text>
          </Text>
        </View>

        {unreadCount > 0 && (
          <TouchableOpacity
            onPress={handleMarkAllRead}
            className="bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20"
          >
            <Text className="text-emerald-400 font-bold text-xs">Sab Read Karo</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Main List */}
      {loading && !refreshing ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => {
            const isBookingCreated = item.type === 'booking_created' && item.ref_id
            return (
              <View className="bg-transparent">
                <NotificationItem
                  notification={item}
                  onPress={handleNotificationPress}
                />
                {isBookingCreated && !item.is_read && (
                  <View className="flex-row px-16 pb-4 space-x-3 bg-emerald-500/5 border-b border-gray-800/60">
                    <TouchableOpacity
                      onPress={() => handleRejectBooking(item.ref_id)}
                      className="flex-1 border border-red-500/40 py-2 rounded-lg items-center bg-red-500/5 mr-2"
                    >
                      <Text className="text-red-400 font-bold text-xs">Reject ❌</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      onPress={() => handleAcceptBooking(item.ref_id)}
                      className="flex-1 bg-emerald-505 py-2 rounded-lg items-center bg-emerald-500"
                    >
                      <Text className="text-white font-bold text-xs">Accept ✅</Text>
                    </TouchableOpacity>
                  </View>
                )}
              </View>
            )
          }}
          onRefresh={handleRefresh}
          refreshing={refreshing}
          className="flex-1"
          contentContainerStyle={{ paddingBottom: 24 }}
          ListEmptyComponent={
            <EmptyState
              emoji="🔔"
              title="Koi notification nahi"
              subtitle="Naye orders aur status updates ki notifications yahan milengi."
            />
          }
        />
      )}
    </View>
  )
}
