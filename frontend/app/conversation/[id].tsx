import React, { useState, useEffect, useRef } from 'react'
import { View, Text, FlatList, TextInput, TouchableOpacity, ActivityIndicator, Alert, KeyboardAvoidingView, Platform } from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { conversationsAPI } from '../../lib/api'
import { storage } from '../../lib/storage'
import type { ConversationMessage } from '../../lib/types'
import { Feather } from '@expo/vector-icons'

const WS_BASE_URL = 'wss://ismail233290-karoo-pk.hf.space'

export default function ConversationScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const flatListRef = useRef<FlatList>(null)

  useEffect(() => {
    if (!id) return

    fetchMessages()
    connectWebSocket()

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [id])

  const fetchMessages = async () => {
    if (!id) return
    setLoading(true)
    try {
      const res = await conversationsAPI.messages(id)
      setMessages(res || [])
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true })
      }, 100)
    } catch (err: any) {
      const errorMsg = err.message || 'Messages load nahi ho sakeen.'
      Alert.alert('Error', errorMsg)
      console.error('Error fetching messages:', err)
    } finally {
      setLoading(false)
    }
  }

  const connectWebSocket = async () => {
    try {
      const token = await storage.getToken()
      const user = await storage.getUser()
      if (!token || !user) return

      const websocket = new WebSocket(`${WS_BASE_URL}/api/conversations/ws/${user.id}?token=${token}`)

      websocket.onopen = () => {
        console.log('WebSocket connected')
      }

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'new_message' && data.conversation_id === id) {
            setMessages((prev) => [...prev, data.message])
            setTimeout(() => {
              flatListRef.current?.scrollToEnd({ animated: true })
            }, 100)
          }
        } catch (err) {
          console.error('WebSocket message parse error:', err)
        }
      }

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      websocket.onclose = () => {
        console.log('WebSocket disconnected')
      }

      setWs(websocket)

      const heartbeat = setInterval(() => {
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.send('ping')
        }
      }, 30000)

      return () => clearInterval(heartbeat)
    } catch (err) {
      console.error('WebSocket connection error:', err)
    }
  }

  const sendMessage = async () => {
    if (!inputText.trim() || !id) return

    setSending(true)
    try {
      const newMessage = await conversationsAPI.send(id, inputText.trim())
      setMessages((prev) => [...prev, newMessage])
      setInputText('')
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true })
      }, 100)
    } catch (err: any) {
      const errorMsg = err.message || 'Message send nahi ho saka.'
      Alert.alert('Error', errorMsg)
      console.error('Error sending message:', err)
    } finally {
      setSending(false)
    }
  }

  const renderMessage = ({ item }: { item: ConversationMessage }) => {
    const isMe = item.sender_role === 'user'
    return (
      <View className={`mb-3 px-4 ${isMe ? 'items-end' : 'items-start'}`}>
        <View
          className={`max-w-[75%] rounded-2xl px-4 py-3 ${
            isMe ? 'bg-emerald-500' : 'bg-gray-800 border border-gray-700'
          }`}
        >
          <Text className={`text-sm ${isMe ? 'text-white' : 'text-gray-200'}`}>
            {item.message}
          </Text>
          <Text className={`text-[10px] mt-1 ${isMe ? 'text-emerald-100' : 'text-gray-500'}`}>
            {new Date(item.created_at).toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        </View>
      </View>
    )
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-gray-950"
      keyboardVerticalOffset={100}
    >
      <View className="bg-gray-900 border-b border-gray-800 px-4 py-3 flex-row items-center">
        <TouchableOpacity onPress={() => router.back()} className="mr-3">
          <Feather name="arrow-left" size={24} color="#fff" />
        </TouchableOpacity>
        <Text className="text-white font-bold text-lg flex-1">Chat</Text>
      </View>

      {loading ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={renderMessage}
          className="flex-1"
          contentContainerStyle={{ paddingTop: 16, paddingBottom: 16 }}
          ListEmptyComponent={
            <View className="flex-1 justify-center items-center py-20">
              <Text className="text-gray-500 text-center">
                Koi message nahi hai.{'\n'}Pehla message bhejein!
              </Text>
            </View>
          }
        />
      )}

      <View className="bg-gray-900 border-t border-gray-800 px-4 py-3 flex-row items-center">
        <TextInput
          value={inputText}
          onChangeText={setInputText}
          placeholder="Message likhein..."
          placeholderTextColor="#6b7280"
          className="flex-1 bg-gray-800 text-white rounded-full px-4 py-3 mr-2"
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          onPress={sendMessage}
          disabled={!inputText.trim() || sending}
          className={`w-12 h-12 rounded-full items-center justify-center ${
            inputText.trim() && !sending ? 'bg-emerald-500' : 'bg-gray-800'
          }`}
        >
          {sending ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Feather name="send" size={20} color="#fff" />
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}
