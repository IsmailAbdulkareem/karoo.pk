import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Alert } from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { workersAPI, ratingsAPI } from '../../lib/api'
import StarRating from '../../components/StarRating'
import LoadingScreen from '../../components/LoadingScreen'

export default function WorkerProfileScreen() {
  const { id } = useLocalSearchParams()
  const [provider, setProvider] = useState<any>(null)
  const [reviews, setReviews] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      fetchProfile()
    }
  }, [id])

  const fetchProfile = async () => {
    setLoading(true)
    try {
      // 1. Fetch provider details
      const profileRes = await workersAPI.getById(id as string)
      setProvider(profileRes)

      // 2. Fetch provider reviews
      const ratingsRes = await ratingsAPI.providerRatings(id as string)
      setReviews(ratingsRes || [])
    } catch (err) {
      console.error(err)
      Alert.alert('Masla', 'Profile fetch karne mein masla hua.')
    } finally {
      setLoading(false)
    }
  }

  // Get initials for profile picture replacement
  const getInitials = (nameStr: string) => {
    if (!nameStr) return 'P'
    return nameStr
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const formatService = (service: string) => {
    if (!service) return ''
    return service
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (loading) {
    return <LoadingScreen message="Profile load ho rahi hai..." />
  }

  if (!provider) {
    return (
      <View className="flex-1 bg-gray-950 justify-center items-center px-6">
        <Text className="text-white text-lg font-bold mb-4">Profile nahi mil saki</Text>
        <TouchableOpacity
          onPress={() => router.back()}
          className="bg-emerald-505 px-6 py-3 rounded-xl bg-emerald-500"
        >
          <Text className="text-white font-bold">Wapas Jaein</Text>
        </TouchableOpacity>
      </View>
    )
  }

  return (
    <View className="flex-1 bg-gray-950">
      <ScrollView className="flex-1 px-6 pt-6" contentContainerStyle={{ paddingBottom: 100 }}>
        {/* Profile Card Header */}
        <View className="items-center mb-8 bg-gray-900 border border-gray-800 rounded-3xl p-6 relative shadow-lg shadow-black/40">
          {provider.is_available && (
            <View className="absolute top-4 right-4 flex-row items-center bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
              <View className="w-2.5 h-2.5 rounded-full bg-emerald-500 mr-2 animate-pulse" />
              <Text className="text-emerald-400 text-xs font-black uppercase">Available</Text>
            </View>
          )}

          <View className="w-24 h-24 rounded-full bg-emerald-500/15 border-2 border-emerald-500/30 items-center justify-center mb-4">
            <Text className="text-emerald-400 font-extrabold text-3xl">{getInitials(provider.name)}</Text>
          </View>

          <Text className="text-white font-black text-2xl mb-1 text-center">{provider.name}</Text>
          <View className="bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 mb-4">
            <Text className="text-emerald-400 text-sm font-bold">
              {formatService(provider.service_type)}
            </Text>
          </View>

          {/* Core Info Badges */}
          <View className="flex-row justify-around w-full border-t border-gray-800/60 pt-4 mt-2">
            <View className="items-center">
              <Text className="text-gray-500 text-[10px] uppercase font-extrabold tracking-wider mb-1">Rating</Text>
              <View className="flex-row items-center">
                <Text className="text-white font-black text-base mr-1">{provider.rating?.toFixed(1) || '0.0'}</Text>
                <Text className="text-amber-400 text-base">★</Text>
              </View>
            </View>

            <View className="w-[1px] bg-gray-800" />

            <View className="items-center">
              <Text className="text-gray-500 text-[10px] uppercase font-extrabold tracking-wider mb-1">Reviews</Text>
              <Text className="text-white font-black text-base">{provider.total_ratings || reviews.length}</Text>
            </View>

            <View className="w-[1px] bg-gray-800" />

            <View className="items-center">
              <Text className="text-gray-500 text-[10px] uppercase font-extrabold tracking-wider mb-1">Rate / Hour</Text>
                <Text className="text-white font-black text-base">PKR {provider.rate_per_hour || 'N/A'}</Text>
            </View>
          </View>
        </View>

        {/* Bio Section */}
        <View className="bg-gray-900 border border-gray-800 rounded-3xl p-5 mb-6 shadow-md shadow-black/20">
          <Text className="text-white font-extrabold text-base mb-2">Introduction / Tajruba (Bio)</Text>
          <Text className="text-gray-300 text-sm leading-relaxed">
            {provider.bio || 'Is provider ne abhi koi bio likhi nahi hai.'}
          </Text>
        </View>

        {/* Reviews Section */}
        <View>
          <Text className="text-white font-extrabold text-lg mb-4 px-1">Customer Reviews ({reviews.length})</Text>
          {reviews.length === 0 ? (
            <View className="bg-gray-900 border border-gray-800 rounded-2xl p-5 items-center">
              <Text className="text-gray-400 text-sm text-center">Is provider ke paas abhi koi review nahi hai.</Text>
            </View>
          ) : (
            reviews.map((review, index) => (
              <View key={index} className="bg-gray-900 border border-gray-800 rounded-2xl p-4 mb-3">
                <View className="flex-row justify-between items-start mb-2">
                  <StarRating rating={review.stars} size={12} />
                  <Text className="text-gray-500 text-[10px] font-bold">
                    {new Date(review.created_at).toLocaleDateString()}
                  </Text>
                </View>
                {review.review_text ? (
                  <Text className="text-gray-200 text-sm italic mb-2">"{review.review_text}"</Text>
                ) : null}
                {review.tags && review.tags.length > 0 && (
                  <View className="flex-row flex-wrap mt-1">
                    {review.tags.map((tag: string, tagIdx: number) => (
                      <View key={tagIdx} className="bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded mr-1.5 mb-1.5">
                        <Text className="text-emerald-400 text-[10px] font-bold">#{tag}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            ))
          )}
        </View>
      </ScrollView>

      {/* Sticky Bottom booking CTA */}
      <View className="absolute bottom-0 left-0 right-0 p-4 bg-gray-900 border-t border-gray-800 flex-row items-center justify-between pb-6">
        <View className="pr-4">
          <Text className="text-gray-500 text-[10px] uppercase font-bold tracking-wider mb-0.5">Estimated Cost</Text>
          <Text className="text-white font-extrabold text-lg">PKR {provider.rate_per_hour}/hr</Text>
        </View>

        <TouchableOpacity
          onPress={() =>
            router.push({
              pathname: '/booking/confirm',
              params: {
                provider_id: provider.id,
                provider_name: provider.name,
                service_type: provider.service_type,
                rating: provider.rating.toString(),
                rate_per_hour: provider.rate_per_hour.toString(),
                eta_minutes: provider.eta_minutes?.toString() || '',
                area: provider.area || '',
              },
            })
          }
          className="bg-emerald-500 px-8 py-3.5 rounded-xl justify-center items-center shadow-lg shadow-emerald-500/20"
        >
          <Text className="text-white font-bold text-base">Book Karo Now ➔</Text>
        </TouchableOpacity>
      </View>
    </View>
  )
}
