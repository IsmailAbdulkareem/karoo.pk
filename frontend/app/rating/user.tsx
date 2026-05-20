import React, { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { ratingsAPI } from '../../lib/api'
import StarRating from '../../components/StarRating'
import { Feather } from '@expo/vector-icons'

const CUSTOMER_REVIEW_TAGS = [
  'responsive',
  'clear_requirements',
  'on_time_payment',
  'good_communication',
  'respectful',
]

export default function RateCustomerScreen() {
  const params = useLocalSearchParams()
  const { booking_id, user_id, user_name } = params

  const [stars, setStars] = useState(5)
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [reviewText, setReviewText] = useState('')
  const [loading, setLoading] = useState(false)

  const toggleTag = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter((t) => t !== tag))
    } else {
      setSelectedTags([...selectedTags, tag])
    }
  }

  const handleSubmitRating = async () => {
    setLoading(true)
    try {
      const payload = {
        booking_id,
        ratee_id: user_id,
        stars,
        review_text: reviewText.trim() || undefined,
        tags: selectedTags,
      }

      await ratingsAPI.submit(payload)
      Alert.alert('✅ Shukriya Partner!', 'Aapki rating submit ho chuki hai.', [
        { text: 'Okay', onPress: () => router.replace('/(provider)/bookings') },
      ])
    } catch (err: any) {
      console.error(err)
      const errorMsg = err.response?.data?.detail || 'Rating submit karne mein masla hua.'
      Alert.alert('Masla', errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <ScrollView className="flex-1 bg-gray-950 px-6 py-10" contentContainerStyle={{ justifyContent: 'center' }}>
      <View className="bg-gray-900 border border-gray-800 rounded-3xl p-6 shadow-xl shadow-black/40">
        <View className="items-center mb-6">
          <Feather name="star" size={40} color="#fbbf24" style={{ marginBottom: 12 }} />
          <Text className="text-white font-extrabold text-xl text-center">Rate Customer Partner</Text>
          <Text className="text-emerald-400 font-extrabold text-base text-center mt-1 pr-2 pl-2">
            {user_name || 'Customer Partner'}
          </Text>
        </View>

        {/* Interactive Star Selector */}
        <View className="items-center bg-gray-850 py-5 rounded-2xl border border-gray-800 mb-6">
          <Text className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-2">Apni Stars Select Karein</Text>
          <StarRating
            rating={stars}
            interactive
            size={24}
            onRatingChange={setStars}
          />
          <Text className="text-white font-extrabold text-lg mt-2">
            {stars === 5 ? 'Excellent!' : stars === 4 ? 'Very Good!' : stars === 3 ? 'Good' : stars === 2 ? 'Fair' : 'Poor'}
          </Text>
        </View>

        {/* Tag chips select */}
        <Text className="text-gray-300 font-medium mb-3 text-sm">Select Tag Badges</Text>
        <View className="flex-row flex-wrap mb-5">
          {CUSTOMER_REVIEW_TAGS.map((tag) => {
            const isSelected = selectedTags.includes(tag)
            return (
              <TouchableOpacity
                key={tag}
                onPress={() => toggleTag(tag)}
                className={`px-3 py-2 rounded-lg border mr-2 mb-2 ${
                  isSelected ? 'bg-emerald-500/10 border-emerald-500 text-emerald-400' : 'bg-gray-850 border-gray-800 text-gray-400'
                }`}
              >
                <Text className={`text-xs font-bold capitalize ${isSelected ? 'text-emerald-400' : 'text-gray-400'}`}>
                  {tag.replace('_', ' ')}
                </Text>
              </TouchableOpacity>
            )
          })}
        </View>

        {/* Text Input */}
        <View className="mb-6">
          <Text className="text-gray-300 font-medium mb-2 text-sm">Apna review likhein (Optional)</Text>
          <TextInput
            value={reviewText}
            onChangeText={setReviewText}
            maxLength={200}
            multiline
            numberOfLines={3}
            placeholder="Customer ke baare mein apna tajurba share karein..."
            placeholderTextColor="#6b7280"
            className="bg-gray-800 text-white rounded-xl px-4 py-3 border border-gray-700 focus:border-emerald-500 text-base text-left"
          />
          <Text className="text-gray-500 text-right text-xs mt-1 font-bold">{reviewText.length}/200</Text>
        </View>

        {/* Actions Button */}
        <View className="space-y-3">
          <TouchableOpacity
            onPress={handleSubmitRating}
            disabled={loading}
            accessibilityRole="button"
            accessibilityLabel="Submit your rating"
            className="bg-emerald-500 py-4 rounded-xl items-center shadow-lg shadow-emerald-500/20 mb-3"
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text className="text-white font-bold text-lg">Rating Submit Karein</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => router.replace('/(provider)/bookings')}
            accessibilityRole="button"
            accessibilityLabel="Skip rating and go back to bookings"
            className="border border-gray-800 py-4 rounded-xl bg-transparent items-center"
          >
            <Text className="text-gray-400 font-bold text-base">Baad mein Rate Karo</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  )
}
