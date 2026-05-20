import React from 'react'
import { View, Text, TouchableOpacity } from 'react-native'
import { Feather } from '@expo/vector-icons'

interface EmptyStateProps {
  icon: keyof typeof Feather.glyphMap
  title: string
  subtitle: string
  buttonText?: string
  onPress?: () => void
}

export default function EmptyState({ icon, title, subtitle, buttonText, onPress }: EmptyStateProps) {
  return (
    <View className="flex-1 bg-transparent justify-center items-center py-12 px-6">
      <Feather name={icon} size={48} color="#10b981" style={{ marginBottom: 16 }} />
      <Text className="text-white font-bold text-xl text-center mb-2">{title}</Text>
      <Text className="text-gray-400 text-sm text-center max-w-[280px] mb-6">{subtitle}</Text>
      {buttonText && onPress ? (
        <TouchableOpacity
          onPress={onPress}
          accessibilityRole="button"
          accessibilityLabel={buttonText}
          className="bg-emerald-500 px-6 py-4 rounded-xl items-center shadow-lg shadow-emerald-500/20"
        >
          <Text className="text-white font-bold text-base">{buttonText}</Text>
        </TouchableOpacity>
      ) : null}
    </View>
  )
}
