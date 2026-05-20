import React from 'react'
import { View, TouchableOpacity } from 'react-native'
import { Feather } from '@expo/vector-icons'

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
    <View className="flex-row items-center" style={{ gap: 2 }}>
      {stars.map((star) => {
        const isFilled = star <= rating
        const color = isFilled ? '#fbbf24' : '#4b5563'

        if (interactive && onRatingChange) {
          return (
            <TouchableOpacity
              key={star}
              onPress={() => onRatingChange(star)}
              accessibilityRole="button"
              accessibilityLabel={`${star} star${star > 1 ? 's' : ''}`}
              hitSlop={{ top: 8, bottom: 8, left: 4, right: 4 }}
            >
              <Feather
                name={isFilled ? 'star' : 'star'}
                size={size}
                color={color}
                style={isFilled ? {} : { opacity: 0.4 }}
              />
            </TouchableOpacity>
          )
        }

        return (
          <Feather
            key={star}
            name="star"
            size={size}
            color={color}
            style={isFilled ? {} : { opacity: 0.4 }}
          />
        )
      })}
    </View>
  )
}
