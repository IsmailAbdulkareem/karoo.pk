import React from 'react'
import { View, Text, TouchableOpacity } from 'react-native'
import { router } from 'expo-router'

interface NotificationProps {
  id: string
  title: string
  body: string
  type: string
  ref_id?: string
  is_read: boolean
  created_at: string
}

interface NotificationItemProps {
  notification: NotificationProps
  onPress: (id: string, ref_id?: string) => void
}

export default function NotificationItem({ notification, onPress }: NotificationItemProps) {
  // Get icon and color based on notification type
  const getTypeMetadata = (type: string) => {
    switch (type) {
      case 'booking_created':
        return { emoji: '📋', bg: 'bg-yellow-500/10' }
      case 'booking_accepted':
        return { emoji: '✅', bg: 'bg-emerald-500/10' }
      case 'booking_cancelled':
      case 'booking_rejected':
        return { emoji: '❌', bg: 'bg-red-500/10' }
      case 'booking_completed':
        return { emoji: '🏁', bg: 'bg-blue-500/10' }
      case 'service_request':
        return { emoji: '🔔', bg: 'bg-purple-500/10' }
      default:
        return { emoji: '📢', bg: 'bg-gray-500/10' }
    }
  }

  const { emoji, bg } = getTypeMetadata(notification.type)

  const formatTimeAgo = (dateStr: string) => {
    try {
      const created = new Date(dateStr).getTime()
      const now = new Date().getTime()
      const diffMs = now - created

      const diffMins = Math.floor(diffMs / 60000)
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`

      const diffHrs = Math.floor(diffMins / 60)
      if (diffHrs < 24) return `${diffHrs}h ago`

      const diffDays = Math.floor(diffHrs / 24)
      return `${diffDays}d ago`
    } catch {
      return ''
    }
  }

  return (
    <TouchableOpacity
      onPress={() => onPress(notification.id, notification.ref_id)}
      className={`flex-row items-center py-4 px-4 border-b border-gray-800/60 ${notification.is_read ? 'bg-transparent' : 'bg-emerald-500/5'}`}
    >
      {/* Icon Circle */}
      <View className={`w-10 h-10 rounded-full ${bg} items-center justify-center mr-3`}>
        <Text className="text-lg">{emoji}</Text>
      </View>

      {/* Content */}
      <View className="flex-1 pr-4">
        <Text className={`text-white text-sm ${notification.is_read ? 'font-medium text-gray-300' : 'font-extrabold'}`}>
          {notification.title}
        </Text>
        <Text className="text-gray-400 text-xs mt-1" numberOfLines={2}>
          {notification.body}
        </Text>
        <Text className="text-gray-500 text-[10px] mt-1.5 font-bold">
          {formatTimeAgo(notification.created_at)}
        </Text>
      </View>

      {/* Unread indicator */}
      {!notification.is_read && (
        <View className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
      )}
    </TouchableOpacity>
  )
}
