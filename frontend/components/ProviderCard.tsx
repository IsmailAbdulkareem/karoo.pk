import React, { useState } from 'react'
import { View, Text, TouchableOpacity, Modal } from 'react-native'
import { router } from 'expo-router'
import StarRating from './StarRating'
import { Feather } from '@expo/vector-icons'

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
  estimated_price?: number
  price_breakdown?: string
}

interface ProviderCardProps {
  provider: ProviderProps
  hideActions?: boolean
  match_score?: number
}

export default function ProviderCard({ provider, hideActions = false, match_score }: ProviderCardProps) {
  const [showPriceModal, setShowPriceModal] = useState(false)

  const getInitials = (fullName: string) => {
    return fullName
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  // Format service type nicely
  const formatService = (service: string) => {
    return service
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <>
      <View className="bg-gradient-to-br from-gray-900 to-gray-800 border border-emerald-500/20 rounded-2xl p-4 mb-3 shadow-xl">
        {/* Availability badge */}
        {provider.is_available && (
          <View className="absolute top-3 right-3 flex-row items-center bg-emerald-500/20 px-2.5 py-1 rounded-full border border-emerald-500/30">
            <View className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
            <Text className="text-emerald-400 text-xs font-bold">Available</Text>
          </View>
        )}

        {/* Profile section */}
        <View className="flex-row items-center mb-3 pr-20">
          <View className="w-14 h-14 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 items-center justify-center mr-3 shadow-lg">
            <Text className="text-white font-bold text-lg">{getInitials(provider.name)}</Text>
          </View>
          <View className="flex-1">
            <Text className="text-white font-bold text-lg mb-1">{provider.name}</Text>
            <View className="self-start bg-emerald-500/15 px-2.5 py-1 rounded-lg border border-emerald-500/30">
              <Text className="text-emerald-400 text-xs font-semibold">
                {formatService(provider.service_type)}
              </Text>
            </View>
          </View>
        </View>

        {/* Match Score with gradient bar */}
        {match_score !== undefined && (
          <View className="mb-3 bg-gray-800/50 p-3 rounded-xl border border-emerald-500/10">
            <View className="flex-row justify-between items-center mb-2">
              <View className="flex-row items-center">
                <Feather name="target" size={12} color="#9ca3af" style={{ marginRight: 4 }} />
                <Text className="text-gray-400 text-xs font-semibold">AI Match Score</Text>
              </View>
              <Text className="text-emerald-400 text-sm font-bold">{Math.round(match_score * 100)}%</Text>
            </View>
            <View className="w-full bg-gray-700 h-2.5 rounded-full overflow-hidden">
              <View
                style={{ width: `${match_score * 100}%` }}
                className="bg-gradient-to-r from-emerald-500 to-emerald-400 h-full rounded-full shadow-lg shadow-emerald-500/50"
              />
            </View>
          </View>
        )}

        {/* Price section - Prominent display */}
        {provider.estimated_price && (
          <View className="mb-3 bg-gradient-to-r from-emerald-500/10 to-emerald-600/10 p-3 rounded-xl border border-emerald-500/30">
            <View className="flex-row justify-between items-center">
              <View>
                <View className="flex-row items-center mb-1">
                  <Feather name="dollar-sign" size={12} color="#9ca3af" style={{ marginRight: 4 }} />
                  <Text className="text-gray-400 text-xs font-semibold">Estimated Price</Text>
                </View>
                <Text className="text-white text-2xl font-bold">Rs. {provider.estimated_price}</Text>
              </View>
              {provider.price_breakdown && (
                <TouchableOpacity
                  onPress={() => setShowPriceModal(true)}
                  accessibilityRole="button"
                  accessibilityLabel="View price breakdown"
                  className="bg-emerald-500/20 px-3 py-2 rounded-lg border border-emerald-500/30"
                >
                  <Text className="text-emerald-400 text-xs font-semibold">View Breakdown</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        )}

        {/* Info grid */}
        <View className="bg-gray-800/30 rounded-xl p-3 border border-gray-700/50 flex-row flex-wrap justify-between mb-3">
          <View className="w-[48%] mb-2">
            <View className="flex-row items-center mb-1">
              <Feather name="star" size={10} color="#6b7280" style={{ marginRight: 3 }} />
              <Text className="text-gray-500 text-[10px] uppercase font-bold tracking-wider">Rating</Text>
            </View>
            <View className="flex-row items-center">
              <StarRating rating={provider.rating ?? 0} size={14} />
              <Text className="text-white text-sm font-bold ml-2">{provider.rating?.toFixed(1) ?? '0.0'}</Text>
            </View>
          </View>

          <View className="w-[48%] mb-2">
            <View className="flex-row items-center mb-1">
              <Feather name="dollar-sign" size={10} color="#6b7280" style={{ marginRight: 3 }} />
              <Text className="text-gray-500 text-[10px] uppercase font-bold tracking-wider">Rate</Text>
            </View>
            <Text className="text-white text-sm font-bold">Rs. {provider.rate_per_hour ?? 'N/A'}/hr</Text>
          </View>

          {provider.area && (
            <View className="w-[48%]">
              <View className="flex-row items-center mb-1">
                <Feather name="map-pin" size={10} color="#6b7280" style={{ marginRight: 3 }} />
                <Text className="text-gray-500 text-[10px] uppercase font-bold tracking-wider">Area</Text>
              </View>
              <Text className="text-white text-sm font-bold" numberOfLines={1}>{provider.area}</Text>
            </View>
          )}

          {provider.eta_minutes !== undefined && (
            <View className="w-[48%]">
              <View className="flex-row items-center mb-1">
                <Feather name="clock" size={10} color="#6b7280" style={{ marginRight: 3 }} />
                <Text className="text-gray-500 text-[10px] uppercase font-bold tracking-wider">ETA</Text>
              </View>
              <Text className="text-emerald-400 text-sm font-bold">{provider.eta_minutes} min</Text>
            </View>
          )}
        </View>

        {/* Action buttons */}
        {!hideActions && (
          <View className="flex-row gap-2">
            <TouchableOpacity
              onPress={() => router.push(`/worker/${provider.id}`)}
              accessibilityRole="button"
              accessibilityLabel={`View ${provider.name} profile`}
              className="flex-1 border border-gray-600 py-4 rounded-xl items-center bg-gray-800/50"
            >
              <Text className="text-gray-300 font-semibold text-sm">View Profile</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => {
                if (!provider.id) return
                router.push({
                  pathname: '/booking/confirm',
                  params: {
                    provider_id: provider.id,
                    provider_name: provider.name,
                    service_type: provider.service_type,
                    rating: provider.rating?.toString() ?? '0',
                    rate_per_hour: provider.rate_per_hour?.toString() ?? '0',
                    eta_minutes: provider.eta_minutes?.toString() ?? '',
                    area: provider.area ?? '',
                    estimated_price: provider.estimated_price?.toString() ?? '',
                  },
                })
              }}
              accessibilityRole="button"
              accessibilityLabel={`Book ${provider.name} now`}
              className="flex-1 bg-gradient-to-r from-emerald-600 to-emerald-500 py-4 rounded-xl items-center shadow-lg shadow-emerald-500/30"
            >
              <Text className="text-white font-bold text-sm">Book Now</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* Price Breakdown Modal */}
      {provider.price_breakdown && (
        <Modal
          visible={showPriceModal}
          transparent
          animationType="fade"
          onRequestClose={() => setShowPriceModal(false)}
        >
          <TouchableOpacity
            activeOpacity={1}
            onPress={() => setShowPriceModal(false)}
            className="flex-1 bg-black/70 justify-center items-center px-6"
          >
            <TouchableOpacity activeOpacity={1} className="bg-gray-900 rounded-2xl p-6 w-full max-w-md border border-emerald-500/30">
              <View className="flex-row justify-between items-center mb-4">
                <View className="flex-row items-center">
                  <Feather name="dollar-sign" size={20} color="#10b981" style={{ marginRight: 6 }} />
                  <Text className="text-white text-xl font-bold">Price Breakdown</Text>
                </View>
                <TouchableOpacity onPress={() => setShowPriceModal(false)}>
                  <Feather name="x" size={24} color="#10b981" />
                </TouchableOpacity>
              </View>

              <View className="bg-gray-800 rounded-xl p-4 mb-4">
                <Text className="text-gray-300 text-sm leading-6 whitespace-pre-line">
                  {provider.price_breakdown}
                </Text>
              </View>

              <View className="bg-emerald-500/10 rounded-xl p-3 border border-emerald-500/30">
                <Text className="text-emerald-400 text-xs text-center">
                  Transparent pricing powered by AI
                </Text>
              </View>
            </TouchableOpacity>
          </TouchableOpacity>
        </Modal>
      )}
    </>
  )
}
