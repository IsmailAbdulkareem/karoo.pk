// components/BookingCard.tsx
import React from 'react';
import { View, Text, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { bookingsAPI } from '../lib/api';

/**
 * Props for a single booking item.
 */
export interface Booking {
  id: string;
  provider_id: string;
  provider_name: string;
  service_type: string;
  location: string;
  scheduled_time: string; // ISO string or display format
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  rating?: number;
}

interface BookingCardProps {
  booking: Booking;
  onRefresh?: () => void; // optional callback after actions
}

/**
 * Urdu‑friendly status badge colour mapping.
 */
const statusMap: Record<Booking['status'], { label: string; bg: string }> = {
  pending: { label: 'پینڈنگ', bg: 'bg-yellow-400' },
  confirmed: { label: 'مقرر', bg: 'bg-green-500' },
  completed: { label: 'مکمل', bg: 'bg-blue-500' },
  cancelled: { label: 'منسوخ', bg: 'bg-red-500' },
};

export const BookingCard: React.FC<BookingCardProps> = ({ booking, onRefresh }) => {
  const router = useRouter();

  const handleCancel = async () => {
    try {
      // call backend cancel endpoint (assuming /bookings/:id/cancel)
      await bookingsAPI.cancel(booking.id);
      Alert.alert('✅', 'Booking منسوخ کر دی گئی');
      onRefresh?.();
    } catch (e: any) {
      Alert.alert('❌', e.message || 'کچھ مسلئا آ گیا');
    }
  };

  const handleDetails = () => {
    // Navigate to a detail screen – for now just alert placeholder
    Alert.alert('تفصیلات', `Booking ID: ${booking.id}`);
  };

  const handleRate = () => {
    // Navigate to rating screen for provider
    router.push({ pathname: '/rating/provider', params: { provider_id: booking.provider_id } });
  };

  const { label, bg } = statusMap[booking.status];

  return (
    <View className="p-4 mb-3 bg-gray-800 rounded-xl shadow-md">
      <View className="flex-row justify-between items-center mb-2">
        <Text className="text-lg font-medium text-white">{booking.provider_name}</Text>
        <View className={`px-2 py-1 rounded ${bg}`}>
          <Text className="text-xs font-semibold text-white">{label}</Text>
        </View>
      </View>
      <Text className="text-sm text-gray-300">{booking.service_type}</Text>
      <Text className="text-sm text-gray-300">📍 {booking.location}</Text>
      <Text className="text-sm text-gray-300">🗓️ {booking.scheduled_time}</Text>

      {/* Action buttons based on status */}
      {booking.status === 'pending' && (
        <Pressable
          onPress={handleCancel}
          className="mt-2 border border-red-500 rounded px-3 py-1 self-start"
        >
          <Text className="text-red-500 font-medium">منسوخ کریں</Text>
        </Pressable>
      )}
      {booking.status === 'confirmed' && (
        <Pressable onPress={handleDetails} className="mt-2 bg-blue-600 rounded px-3 py-1 self-start">
          <Text className="text-white font-medium">تفصیلات</Text>
        </Pressable>
      )}
      {booking.status === 'completed' && !booking.rating && (
        <Pressable onPress={handleRate} className="mt-2 bg-yellow-500 rounded px-3 py-1 self-start">
          <Text className="text-white font-medium">ریٹ کریں ⭐</Text>
        </Pressable>
      )}
    </View>
  );
};
