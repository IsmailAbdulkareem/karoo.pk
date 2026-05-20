// components/BookingCard.tsx
import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Feather } from '@expo/vector-icons';

export interface BookingCardProps {
  booking: any;
  onPress?: () => void; // Add this
}

export function BookingCard({ booking, onPress }: BookingCardProps) {
  const getStatusColor = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'pending') return 'bg-yellow-500/20 border-yellow-500';
    if (s === 'confirmed') return 'bg-blue-500/20 border-blue-500';
    if (s === 'completed') return 'bg-green-500/20 border-green-500';
    if (s === 'cancelled') return 'bg-red-500/20 border-red-500';
    return 'bg-gray-500/20 border-gray-500';
  };

  const getStatusIcon = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'pending') return 'clock';
    if (s === 'confirmed') return 'check-circle';
    if (s === 'completed') return 'check';
    if (s === 'cancelled') return 'x-circle';
    return 'info';
  };

  const getStatusTextColor = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'pending') return 'text-yellow-500';
    if (s === 'confirmed') return 'text-blue-500';
    if (s === 'completed') return 'text-green-500';
    if (s === 'cancelled') return 'text-red-500';
    return 'text-gray-500';
  };

  const Wrapper = onPress ? TouchableOpacity : View;

  return (
    <Wrapper
      onPress={onPress}
      className="bg-gray-900 rounded-xl p-4 mb-3 border border-gray-800"
      activeOpacity={onPress ? 0.7 : 1}
    >
      {/* Service Name */}
      <View className="flex-row items-center justify-between mb-3">
        <Text className="text-white text-lg font-bold flex-1">
          {booking.service?.name || 'Service'}
        </Text>
        <View className={`px-3 py-1 rounded-full border ${getStatusColor(booking.status)}`}>
          <View className="flex-row items-center">
            <Feather 
              name={getStatusIcon(booking.status) as any} 
              size={12} 
              color={getStatusTextColor(booking.status).includes('yellow') ? '#eab308' :
                     getStatusTextColor(booking.status).includes('blue') ? '#3b82f6' :
                     getStatusTextColor(booking.status).includes('green') ? '#10b981' :
                     getStatusTextColor(booking.status).includes('red') ? '#ef4444' : '#6b7280'} 
            />
            <Text className={`ml-1 text-xs font-bold ${getStatusTextColor(booking.status)}`}>
              {booking.status || 'Unknown'}
            </Text>
          </View>
        </View>
      </View>

      {/* Provider Info */}
      {booking.provider && (
        <View className="flex-row items-center mb-2">
          <Feather name="user" size={14} color="#9ca3af" />
          <Text className="text-gray-400 ml-2 text-sm">
            {booking.provider.name || 'Provider'}
          </Text>
        </View>
      )}

      {/* Date & Time */}
      {booking.scheduled_at && (
        <View className="flex-row items-center mb-2">
          <Feather name="calendar" size={14} color="#9ca3af" />
          <Text className="text-gray-400 ml-2 text-sm">
            {new Date(booking.scheduled_at).toLocaleDateString('en-US', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Text>
        </View>
      )}

      {/* Location */}
      {booking.address && (
        <View className="flex-row items-start mb-2">
          <Feather name="map-pin" size={14} color="#9ca3af" />
          <Text className="text-gray-400 ml-2 text-sm flex-1" numberOfLines={1}>
            {booking.address}
          </Text>
        </View>
      )}

      {/* Price */}
      {booking.total_amount && (
        <View className="flex-row items-center justify-between mt-3 pt-3 border-t border-gray-800">
          <Text className="text-gray-400 text-sm">Total Amount</Text>
          <Text className="text-emerald-500 text-lg font-bold">
            PKR {booking.total_amount}
          </Text>
        </View>
      )}

      {/* Tap indicator if onPress exists */}
      {onPress && (
        <View className="flex-row items-center justify-center mt-2">
          <Text className="text-gray-500 text-xs">Tap for details</Text>
          <Feather name="chevron-right" size={12} color="#6b7280" />
        </View>
      )}
    </Wrapper>
  );
}