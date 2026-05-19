// app/booking/confirm.tsx
import React, { useState } from 'react';
import { View, Text, TextInput, Pressable, Alert, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { bookingsAPI } from '../../lib/api';
import DateTimePicker from '../../components/DateTimePicker';
import { validateLocation, validateDateTime } from '../../lib/validation';
import { Feather } from '@expo/vector-icons';

/**
 * Confirmation screen for creating a booking.
 * Params (from route):
 *  - provider_id, provider_name, service_type, rating, rate_per_hour, eta_minutes, estimated_price
 */
export default function BookingConfirm() {
  const router = useRouter();
  const {
    provider_id,
    provider_name,
    service_type,
    rating,
    rate_per_hour,
    eta_minutes,
    estimated_price,
    area,
  } = useLocalSearchParams<{
    provider_id: string;
    provider_name: string;
    service_type: string;
    rating: string;
    rate_per_hour: string;
    eta_minutes: string;
    estimated_price?: string;
    area?: string;
  }>();

  const [location, setLocation] = useState(area || '');
  const [scheduledTime, setScheduledTime] = useState('');
  const [note, setNote] = useState('');
  const [budget, setBudget] = useState(estimated_price || '');
  const [urgency, setUrgency] = useState<'normal' | 'urgent' | 'emergency'>('normal');
  const [loading, setLoading] = useState(false);

  const [locationError, setLocationError] = useState<string | null>(null);
  const [timeError, setTimeError] = useState<string | null>(null);

  const handleBook = async () => {
    // Prevent multiple simultaneous submissions
    if (loading) return;

    // Reset errors
    setLocationError(null);
    setTimeError(null);

    // Validate location
    const locationValidation = validateLocation(location);
    if (!locationValidation.isValid) {
      setLocationError(locationValidation.error || '');
      return;
    }

    // Validate scheduled time
    const timeValidation = validateDateTime(scheduledTime);
    if (!timeValidation.isValid) {
      setTimeError(timeValidation.error || '');
      return;
    }

    setLoading(true);
    try {
      await bookingsAPI.create({
        provider_id,
        service_type,
        location,
        scheduled_at: scheduledTime,
        note: note || undefined,
        booked_via: 'browse',
        budget: budget ? Number(budget) : undefined,
        eta_minutes: eta_minutes ? Number(eta_minutes) : undefined,
        urgency,
      });

      // Navigate to bookings page immediately (auto-refresh)
      router.replace('/(user)/bookings');

      // Show success message after navigation
      setTimeout(() => {
        Alert.alert('✅ Success', 'Booking ho gayi! Provider ko notify kar diya');
      }, 300);
    } catch (e: any) {
      Alert.alert('❌ Error', e.message || 'Kuch masla aa gaya, dobara try karo');
      setLoading(false);
    }
  };

  return (
    <ScrollView className="flex-1 bg-gray-950" contentContainerStyle={{ paddingBottom: 40 }}>
      {/* Header */}
      <View className="bg-gradient-to-r from-gray-900 to-gray-800 px-6 py-6 border-b border-emerald-500/20">
        <TouchableOpacity onPress={() => router.back()} className="mb-4">
          <Feather name="arrow-left" size={24} color="#10b981" />
        </TouchableOpacity>
        <Text className="text-3xl font-bold text-white mb-2">Confirm Booking</Text>
        <Text className="text-gray-400">Review details and confirm</Text>
      </View>

      <View className="px-6 pt-6">
        {/* Provider Summary Card */}
        <View className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-5 mb-6 border border-emerald-500/20 shadow-xl">
          <View className="flex-row items-center mb-4">
            <View className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 items-center justify-center mr-4">
              <Text className="text-white font-bold text-xl">
                {provider_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
              </Text>
            </View>
            <View className="flex-1">
              <Text className="text-white text-xl font-bold mb-1">{provider_name}</Text>
              <Text className="text-emerald-400 text-sm font-semibold">{service_type}</Text>
            </View>
          </View>

          <View className="flex-row flex-wrap gap-3">
            <View className="bg-gray-800/50 px-3 py-2 rounded-lg flex-row items-center">
              <Feather name="star" size={14} color="#fbbf24" />
              <Text className="text-white text-sm font-semibold ml-1.5">{rating}</Text>
            </View>
            <View className="bg-gray-800/50 px-3 py-2 rounded-lg flex-row items-center">
              <Feather name="clock" size={14} color="#10b981" />
              <Text className="text-white text-sm font-semibold ml-1.5">{eta_minutes} min</Text>
            </View>
            <View className="bg-gray-800/50 px-3 py-2 rounded-lg flex-row items-center">
              <Feather name="dollar-sign" size={14} color="#10b981" />
              <Text className="text-white text-sm font-semibold ml-1.5">Rs. {rate_per_hour}/hr</Text>
            </View>
          </View>
        </View>

        {/* Estimated Price */}
        {estimated_price && (
          <View className="bg-gradient-to-r from-emerald-500/10 to-emerald-600/10 rounded-2xl p-5 mb-6 border border-emerald-500/30">
            <Text className="text-gray-400 text-sm mb-2">💰 Estimated Total</Text>
            <Text className="text-white text-4xl font-bold">Rs. {estimated_price}</Text>
            <Text className="text-emerald-400 text-xs mt-2">✨ AI-powered transparent pricing</Text>
          </View>
        )}

        {/* Urgency Selector */}
        <View className="mb-6">
          <Text className="text-white text-base font-semibold mb-3">⚡ Urgency Level</Text>
          <View className="flex-row gap-2">
            {(['normal', 'urgent', 'emergency'] as const).map((level) => (
              <TouchableOpacity
                key={level}
                onPress={() => setUrgency(level)}
                className={`flex-1 py-3 rounded-xl border ${
                  urgency === level
                    ? 'bg-emerald-500/20 border-emerald-500'
                    : 'bg-gray-800 border-gray-700'
                }`}
              >
                <Text className={`text-center font-semibold ${
                  urgency === level ? 'text-emerald-400' : 'text-gray-400'
                }`}>
                  {level === 'normal' ? '🟢 Normal' : level === 'urgent' ? '🟡 Urgent' : '🔴 Emergency'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Input Form */}
        <View className="space-y-5">
          <View>
            <Text className="text-white text-base font-semibold mb-2">📍 Location</Text>
            <TextInput
              placeholder="Enter your address (e.g., F-10 Islamabad)"
              placeholderTextColor="#6b7280"
              className={`bg-gray-800 text-white rounded-xl px-4 py-4 text-base border ${
                locationError ? 'border-red-500' : 'border-gray-700'
              }`}
              value={location}
              onChangeText={(text) => {
                setLocation(text);
                setLocationError(null);
              }}
            />
            {locationError && (
              <Text className="text-red-400 text-sm mt-2 ml-2">⚠️ {locationError}</Text>
            )}
          </View>

          <View>
            <Text className="text-white text-base font-semibold mb-2">📅 Scheduled Time</Text>
            <DateTimePicker
              value={scheduledTime}
              onChange={(value) => {
                setScheduledTime(value);
                setTimeError(null);
              }}
              placeholder="YYYY-MM-DD HH:mm"
              error={timeError || undefined}
            />
          </View>

          <View>
            <Text className="text-white text-base font-semibold mb-2">💬 Additional Notes (Optional)</Text>
            <TextInput
              placeholder="Any special requirements or instructions..."
              placeholderTextColor="#6b7280"
              className="bg-gray-800 text-white rounded-xl px-4 py-4 text-base border border-gray-700"
              value={note}
              onChangeText={setNote}
              multiline
              numberOfLines={3}
              textAlignVertical="top"
            />
          </View>

          <View>
            <Text className="text-white text-base font-semibold mb-2">💵 Your Budget (Optional)</Text>
            <TextInput
              placeholder="Enter your budget in PKR"
              placeholderTextColor="#6b7280"
              className="bg-gray-800 text-white rounded-xl px-4 py-4 text-base border border-gray-700"
              keyboardType="numeric"
              value={budget}
              onChangeText={setBudget}
            />
            <Text className="text-gray-500 text-xs mt-2 ml-2">
              💡 This helps us match you with the right provider
            </Text>
          </View>
        </View>

        {/* Confirm Button */}
        <TouchableOpacity
          onPress={handleBook}
          disabled={loading}
          className={`rounded-2xl py-4 px-6 mt-8 flex-row justify-center items-center shadow-lg ${
            loading ? 'bg-gray-700' : 'bg-gradient-to-r from-emerald-600 to-emerald-500'
          }`}
        >
          {loading ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <>
              <Feather name="check-circle" size={20} color="#fff" />
              <Text className="text-white font-bold text-lg ml-2">Confirm Booking</Text>
            </>
          )}
        </TouchableOpacity>

        <Text className="text-gray-500 text-xs text-center mt-4">
          By confirming, you agree to our terms and conditions
        </Text>
      </View>
    </ScrollView>
  );
}
