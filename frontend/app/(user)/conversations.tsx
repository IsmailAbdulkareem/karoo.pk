import React, { useState, useEffect } from 'react'
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { router } from 'expo-router'
import { conversationsAPI } from '../../lib/api'
import EmptyState from '../../components/EmptyState'
import type { Conversation } from '../../lib/types'

export default function ConversationsScreen() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchConversations()
  }, [])

  const fetchConversations = async () => {
    setLoading(true)
    try {
      const res = await conversationsAPI.list()
      setConversations(res || [])
    } catch (err: any) {
      const errorMsg = err.message || 'Conversations load nahi ho sakeen. Dobara try karein.'
      Alert.alert('Error', errorMsg)
      console.error('Error fetching conversations:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchConversations()
  }

  const formatTimeAgo = (dateStr?: string) => {
    if (!dateStr) return ''
    try {
      const diffMs = new Date().getTime() - new Date(dateStr).getTime()
      const mins = Math.floor(diffMs / 60000)
      if (mins < 1) return 'Abhi'
      if (mins < 60) return `${mins}m pehle`
      const hrs = Math.floor(mins / 60)
      if (hrs < 24) return `${hrs}h pehle`
      return `${Math.floor(hrs / 24)}d pehle`
    } catch {
      return ''
    }
  }

  return (
    <View className="flex-1 bg-gray-950">
      {loading && !refreshing ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <FlatList
          data={conversations}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => {
            const hasUnread = item.user_unread_count > 0
            return (
              <TouchableOpacity
                onPress={() => router.push(`/conversation/${item.id}`)}
                className="bg-gray-900 border-b border-gray-800 px-4 py-4 flex-row items-center"
              >
                {/* Avatar placeholder */}
                <View className="w-12 h-12 rounded-full bg-emerald-500 items-center justify-center mr-3">
                  <Text className="text-white font-bold text-lg">
                    {item.other_party_name?.charAt(0).toUpperCase() || '?'}
                  </Text>
                </View>

                {/* Content */}
                <View className="flex-1">
                  <View className="flex-row justify-between items-center mb-1">
                    <Text className={`font-bold text-base ${hasUnread ? 'text-white' : 'text-gray-300'}`}>
                      {item.other_party_name || 'Unknown'}
                    </Text>
                    <Text className="text-gray-500 text-xs">
                      {formatTimeAgo(item.last_message_at)}
                    </Text>
                  </View>

                  <View className="flex-row items-center">
                    <Text
                      className={`flex-1 text-sm ${hasUnread ? 'text-gray-300 font-medium' : 'text-gray-500'}`}
                      numberOfLines={1}
                    >
                      {item.last_message || 'Koi message nahi'}
                    </Text>
                    {hasUnread && (
                      <View className="bg-emerald-500 rounded-full w-5 h-5 items-center justify-center ml-2">
                        <Text className="text-white text-xs font-bold">{item.user_unread_count}</Text>
                      </View>
                    )}
                  </View>
                </View>
              </TouchableOpacity>
            )
          }}
          onRefresh={handleRefresh}
          refreshing={refreshing}
          className="flex-1"
          ListEmptyComponent={
            <EmptyState
              emoji="💬"
              title="Koi conversation nahi"
              subtitle="Jab aap kisi provider ke saath booking karenge, tab yahan chat kar sakte hain."
            />
          }
        />
      )}
    </View>
  )
}
