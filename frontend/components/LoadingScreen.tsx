import React from 'react'
import { View, Text, ActivityIndicator } from 'react-native'

interface LoadingScreenProps {
  message?: string
}

export default function LoadingScreen({ message = 'Jaari hai...' }: LoadingScreenProps) {
  return (
    <View className="flex-1 bg-gray-950 justify-center items-center px-6">
      <ActivityIndicator size="large" color="#10b981" />
      <Text className="text-gray-400 font-medium text-base mt-4 text-center">
        {message}
      </Text>
    </View>
  )
}
