import React, { useState } from 'react'
import { View, Text, TouchableOpacity, ScrollView } from 'react-native'
import { Feather } from '@expo/vector-icons'
import ProviderCard from './ProviderCard'

interface ProviderProps {
  id: string
  name: string
  service_type: string
  rating: number
  total_ratings?: number
  area?: string
  rate_per_hour: number
  is_available: boolean
  eta_minutes?: number
}

interface MessageBubbleProps {
  sender: 'user' | 'bot' | 'provider'
  text: string
  agent_trace?: string
  providers?: ProviderProps[]
  created_at?: string
}

export default function MessageBubble({
  sender,
  text,
  agent_trace,
  providers = [],
  created_at,
}: MessageBubbleProps) {
  const [traceExpanded, setTraceExpanded] = useState(false)
  const isUser = sender === 'user'

  const formatTime = (timeStr?: string) => {
    if (!timeStr) return ''
    try {
      const date = new Date(timeStr)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch {
      return ''
    }
  }

  return (
    <View className={`flex-col mb-4 max-w-[85%] ${isUser ? 'self-end items-end' : 'self-start items-start'}`}>
      {/* Sender name label */}
      <Text className="text-[10px] text-gray-500 font-bold mb-1 px-1 uppercase tracking-wider">
        {isUser ? 'Aap' : sender === 'provider' ? 'Provider' : 'Karoo AI'}
      </Text>

      {/* Bubble Container */}
      <View
        className={`rounded-2xl px-4 py-3 shadow-md shadow-black/10 ${
          isUser
            ? 'bg-emerald-600 rounded-tr-none'
            : 'bg-gray-900 border border-gray-800 rounded-tl-none'
        }`}
      >
        <Text className={`text-base leading-relaxed ${isUser ? 'text-white font-medium' : 'text-gray-100'}`}>
          {text}
        </Text>

        {created_at && (
          <Text className={`text-[9px] mt-1 text-right font-bold uppercase tracking-wider ${isUser ? 'text-emerald-200' : 'text-gray-500'}`}>
            {formatTime(created_at)}
          </Text>
        )}
      </View>

      {/* Collapsible Agent Trace section for Bot Messages */}
      {!isUser && agent_trace ? (
        <View className="w-full mt-2 bg-gray-900 border border-gray-800 rounded-xl overflow-hidden self-stretch">
          <TouchableOpacity
            onPress={() => setTraceExpanded(!traceExpanded)}
            className="flex-row justify-between items-center px-3 py-2 bg-gray-850 border-b border-gray-800"
          >
            <View className="flex-row items-center">
              <Feather name="search" size={12} color="#9ca3af" style={{ marginRight: 4 }} />
              <Text className="text-gray-400 font-bold text-xs">
                {traceExpanded ? 'AI Trace chupaen' : 'AI Trace dekho'}
              </Text>
            </View>
            <Feather name={traceExpanded ? 'chevron-up' : 'chevron-down'} size={14} color="#6b7280" />
          </TouchableOpacity>

          {traceExpanded && (
            <ScrollView style={{ maxHeight: 150 }} className="p-3 bg-gray-950">
              <Text className="text-emerald-400 font-mono text-[10px] leading-4 select-text">
                {agent_trace}
              </Text>
            </ScrollView>
          )}
        </View>
      ) : null}

      {/* Render Providers list if returned by AI matching */}
      {!isUser && providers && providers.length > 0 ? (
        <View className="w-full mt-3 self-stretch">
          <Text className="text-gray-400 font-bold text-xs mb-2 px-1">Available Providers Matching Your Request:</Text>
          {providers.map((provider) => (
            <ProviderCard key={provider.id} provider={provider} />
          ))}
        </View>
      ) : null}
    </View>
  )
}
