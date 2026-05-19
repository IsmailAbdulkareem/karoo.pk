import React from 'react'
import { View, Text, TouchableOpacity } from 'react-native'

interface EmptyStateProps {
  emoji: string
  title: string
  subtitle: string
  buttonText?: string
  onPress?: () => void
}

export default function EmptyState({ emoji, title, subtitle, buttonText, onPress }: EmptyStateProps) {
  return (
    <View className="flex-1 bg-transparent justify-center items-center py-12 px-6">
      <Text className="text-6xl mb-4">{emoji}</Text>
      <Text className="text-white font-bold text-xl text-center mb-2">{title}</Text>
      <Text className="text-gray-400 text-sm text-center max-w-[280px] mb-6">{subtitle}</Text>
      {buttonText && onPress ? (
        <TouchableOpacity
          onPress={onPress}
          className="bg-emerald-500 px-6 py-3 rounded-xl items-center shadow-lg shadow-emerald-500/20"
        >
          <Text className="text-white font-bold text-base">{buttonText}</Text>
        </TouchableOpacity>
      ) : null}
    </View>
  )
}
