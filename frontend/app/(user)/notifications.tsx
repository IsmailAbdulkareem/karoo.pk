import React, { useState, useEffect, useCallback } from 'react'
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { useFocusEffect } from 'expo-router'
import { notificationsAPI } from '../../lib/api'
import NotificationItem from '../../components/NotificationItem'
import EmptyState from '../../components/EmptyState'
import { router } from 'expo-router'
import { Feather } from '@expo/vector-icons'
import type { Notification } from '../../lib/types'

export default function UserNotificationsScreen() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  const fetchNotifications = useCallback(async () => {
    setLoading(true)
    try {
      const res = await notificationsAPI.list()
      // API returns array directly or wrapped inside an object
      const list = Array.isArray(res)
        ? res
        : (res && Array.isArray(res.notifications) ? res.notifications : [])
      setNotifications(list)
    } catch (err: any) {
      const errorMsg = err.message || 'Notifications load nahi ho sakeen. Dobara try karein.'
      Alert.alert('Error', errorMsg)
      console.error('Error fetching notifications:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  // Auto-refresh when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      fetchNotifications()
    }, [fetchNotifications])
  )

  const handleRefresh = () => {
    setRefreshing(true)
    fetchNotifications()
  }

  const handleMarkAllRead = async () => {
    try {
      await notificationsAPI.markAllRead()
      fetchNotifications()
    } catch (err: any) {
      const errorMsg = err.message || 'Mark all read karne mein masla hua.'
      Alert.alert('Error', errorMsg)
      console.error('Error marking all read:', err)
    }
  }

  const handleNotificationPress = async (id: string, refId?: string) => {
    try {
      await notificationsAPI.markRead(id)
      fetchNotifications()
      if (refId) {
        // Redirect to user bookings to see details
        router.push('/(user)/bookings')
      }
    } catch (err: any) {
      const errorMsg = err.message || 'Notification mark karne mein masla hua.'
      Alert.alert('Error', errorMsg)
      console.error('Error marking notification read:', err)
    }
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  return (
    <View className="flex-1 bg-gray-950">
      {/* Header */}
      <View className="bg-gradient-to-r from-gray-900 to-gray-800 px-6 py-6 border-b border-emerald-500/20">
        <View className="flex-row items-center justify-between mb-2">
          <View>
            <Text className="text-3xl font-bold text-white mb-2">Notifications</Text>
            <Text className="text-gray-400">Stay updated with your bookings</Text>
          </View>
          <TouchableOpacity onPress={() => router.back()}>
            <Feather name="x" size={24} color="#10b981" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Unread Counter & Actions */}
      <View className="flex-row justify-between items-center px-6 py-4 bg-gray-900/50 border-b border-gray-800">
        <View className="flex-row items-center">
          <View className="w-10 h-10 rounded-full bg-emerald-500/20 items-center justify-center mr-3">
            <Feather name="bell" size={20} color="#10b981" />
          </View>
          <View>
            <Text className="text-white font-bold text-base">
              {unreadCount} Unread
            </Text>
            <Text className="text-gray-500 text-xs">
              {notifications.length} total notifications
            </Text>
          </View>
        </View>

        {unreadCount > 0 && (
          <TouchableOpacity
            onPress={handleMarkAllRead}
            className="bg-gradient-to-r from-emerald-600 to-emerald-500 px-4 py-2.5 rounded-xl flex-row items-center shadow-lg"
          >
            <Feather name="check-circle" size={16} color="#fff" />
            <Text className="text-white font-bold text-sm ml-2">Mark All Read</Text>
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
          renderItem={({ item }) => (
            <NotificationItem
              notification={item}
              onPress={handleNotificationPress}
            />
          )}
          onRefresh={handleRefresh}
          refreshing={refreshing}
          className="flex-1"
          contentContainerStyle={{ paddingBottom: 24 }}
          ListEmptyComponent={
            <EmptyState
              icon="bell"
              title="Koi notification nahi"
              subtitle="Naye orders aur status updates ki notifications yahan milengi."
            />
          }
        />
      )}
    </View>
  )
}
