import React from 'react'
import { View, Text, TouchableOpacity } from 'react-native'

interface StarRatingProps {
  rating: number
  maxStars?: number
  size?: number
  onRatingChange?: (rating: number) => void
  interactive?: boolean
}

export default function StarRating({
  rating,
  maxStars = 5,
  size = 20,
  onRatingChange,
  interactive = false,
}: StarRatingProps) {
  const stars = Array.from({ length: maxStars }, (_, i) => i + 1)

  return (
    <View className="flex-row items-center space-x-1">
      {stars.map((star) => {
        const isFilled = star <= rating
        const starChar = isFilled ? '★' : '☆'
        const color = isFilled ? 'text-amber-400' : 'text-gray-600'

        if (interactive && onRatingChange) {
          return (
            <TouchableOpacity
              key={star}
              onPress={() => onRatingChange(star)}
              className="px-1"
            >
              <Text style={{ fontSize: size * 1.5 }} className={`${color} font-bold`}>
                {starChar}
              </Text>
            </TouchableOpacity>
          )
        }

        return (
          <Text
            key={star}
            style={{ fontSize: size }}
            className={`${color} font-bold mr-0.5`}
          >
            {starChar}
          </Text>
        )
      })}
    </View>
  )
}
