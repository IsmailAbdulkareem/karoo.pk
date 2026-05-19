import React, { useState, useEffect, useRef } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native'
import { chatAPI } from '../../lib/api'
import MessageBubble from '../../components/MessageBubble'
import BookingCard from '../../components/BookingCard'

interface ProviderMessageProps {
  id: string
  sender: 'user' | 'bot'
  text: string
  agent_trace?: string
  results?: any[]
  intent_type?: string
  created_at: string
}

export default function ProviderChatScreen() {
  const [messages, setMessages] = useState<ProviderMessageProps[]>([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)

  const flatListRef = useRef<FlatList>(null)

  useEffect(() => {
    // Welcome message
    setMessages([
      {
        id: 'welcome',
        sender: 'bot',
        text: 'Assalam o Alaikum Partner! Main Karoo AI Partner Assistant hoon. Aap apne kaam (bookings), kamai (earnings), ya market requests ke baare mein natural Roman Urdu ya English mein pooch sakte hain. (e.g. "Koi naya kaam hai?", "Aaj ki earnings?", "Kal ki schedule?") 😊',
        created_at: new Date().toISOString(),
      },
    ])
  }, [])

  const handleSendMessage = async () => {
    if (!inputText.trim()) return

    const userMessageText = inputText.trim()
    setInputText('')

    const userMsg: ProviderMessageProps = {
      id: Math.random().toString(),
      sender: 'user',
      text: userMessageText,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [userMsg, ...prev])
    setLoading(true)

    try {
      const res = await chatAPI.providerChat(userMessageText)
      const { reply, intent, results = [], agent_trace } = res.data

      const botMsg: ProviderMessageProps = {
        id: Math.random().toString(),
        sender: 'bot',
        text: reply,
        agent_trace: agent_trace || '',
        results: results || [],
        intent_type: intent?.intent_type || '',
        created_at: new Date().toISOString(),
      }

      setMessages((prev) => [botMsg, ...prev])
    } catch (err: any) {
      console.error(err)
      const errorMsg = err.response?.data?.detail || 'Kuch masla aa gaya, dobara try karo.'
      const botErrorMsg: ProviderMessageProps = {
        id: Math.random().toString(),
        sender: 'bot',
        text: errorMsg,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [botErrorMsg, ...prev])
    } finally {
      setLoading(false)
    }
  }

  // Format service type nicely
  const formatService = (service: string) => {
    if (!service) return ''
    return service
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  // Render provider chat results list
  const renderResults = (intentType: string, results: any[]) => {
    if (!results || results.length === 0) return null

    if (intentType === 'find_requests') {
      return (
        <View className="w-full mt-3 self-stretch bg-gray-900/60 p-4 border border-gray-800 rounded-2xl">
          <Text className="text-gray-400 font-bold text-xs mb-3">Open Marketplace Requests:</Text>
          {results.slice(0, 3).map((item, index) => (
            <View key={item.id || index} className="bg-gray-950 p-3 rounded-xl border border-gray-850 mb-2">
              <Text className="text-white font-extrabold text-sm mb-1">{item.user_name || 'Customer'}</Text>
              <Text className="text-emerald-400 text-xs font-bold mb-1.5">{formatService(item.service_type)}</Text>
              <Text className="text-gray-400 text-xs mb-1">📍 {item.location}</Text>
              {item.budget && <Text className="text-emerald-400 text-xs font-bold">Budget: PKR {item.budget}</Text>}
            </View>
          ))}
        </View>
      )
    }

    if (intentType === 'check_bookings') {
      return (
        <View className="w-full mt-3 self-stretch">
          <Text className="text-gray-400 font-bold text-xs mb-2">Matching Bookings:</Text>
          {results.slice(0, 2).map((item, index) => (
            <BookingCard key={item.id || index} booking={item} role="provider" />
          ))}
        </View>
      )
    }

    if (intentType === 'check_earnings') {
      const summary = results[0] || {}
      return (
        <View className="w-full mt-3 self-stretch bg-emerald-500 rounded-2xl p-4 shadow-md shadow-emerald-500/10">
          <Text className="text-emerald-100 text-xs font-bold uppercase tracking-wider mb-0.5">Total Earnings Summary</Text>
          <Text className="text-white font-black text-2xl mb-2">PKR {summary.total_earned_pkr || 0}</Text>
          <Text className="text-emerald-500 text-xs font-extrabold bg-white/95 py-1 px-3.5 rounded-lg self-start">
            Completed: {summary.total_completed_jobs || 0} jobs
          </Text>
        </View>
      )
    }

    return null
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      className="flex-1 bg-gray-950"
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {/* Dynamic Header */}
      <View className="flex-row justify-between items-center px-6 py-4 bg-gray-900 border-b border-gray-800">
        <View className="flex-row items-center">
          <Text className="text-2xl mr-2">👷 Partner</Text>
          <View>
            <Text className="text-white font-extrabold text-lg">Partner AI Chat</Text>
            <Text className="text-emerald-400 text-xs font-bold">Manage by Voice/Natural Chat</Text>
          </View>
        </View>
      </View>

      {/* Main Messages FlatList */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View className="flex-col">
            <MessageBubble
              sender={item.sender === 'user' ? 'user' : 'bot'}
              text={item.text}
              agent_trace={item.agent_trace}
              created_at={item.created_at}
            />
            {!item.sender || item.sender === 'bot' ? (
              <View className="max-w-[85%] self-start w-full px-4 mb-4">
                {renderResults(item.intent_type || '', item.results || [])}
              </View>
            ) : null}
          </View>
        )}
        contentContainerStyle={{ paddingHorizontal: 16, paddingVertical: 20 }}
        inverted
        className="flex-1"
        ListFooterComponent={
          loading ? (
            <View className="flex-row items-center py-4 bg-transparent pl-4 mb-2 space-x-2">
              <ActivityIndicator size="small" color="#10b981" />
              <Text className="text-gray-500 font-bold text-xs">Partner AI typing...</Text>
            </View>
          ) : null
        }
      />

      {/* Bottom Message Input Bar */}
      <View className="p-4 bg-gray-900 border-t border-gray-800 flex-row items-center space-x-3 pb-6">
        <TextInput
          value={inputText}
          onChangeText={setInputText}
          placeholder="Apna sawaal likhein (e.g. kitne paise kamaye)..."
          placeholderTextColor="#6b7280"
          className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 border border-gray-700 focus:border-emerald-500 text-base"
          onSubmitEditing={handleSendMessage}
        />
        <TouchableOpacity
          onPress={handleSendMessage}
          disabled={loading || !inputText.trim()}
          className={`p-3.5 rounded-xl bg-emerald-500 items-center justify-center shadow-md ${
            !inputText.trim() ? 'opacity-50' : 'active:opacity-80'
          }`}
        >
          <Text className="text-white font-extrabold text-base">➔</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}
