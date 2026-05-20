// app/(user)/bookings.tsx – User bookings screen with tabs and pull‑to‑refresh
import React, { useCallback, useState } from 'react';
import { FlatList, RefreshControl, Text, View, Alert, TouchableOpacity } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { bookingsAPI } from '../../lib/api';
import { BookingCard } from '../../components/BookingCard';
import { Feather } from '@expo/vector-icons';


// Tab identifiers
type Tab = 'active' | 'completed' | 'cancelled';

export default function UserBookingsScreen() {
  const router = useRouter();
  const [bookings, setBookings] = useState<any[]>([]);
  const [selectedTab, setSelectedTab] = useState<Tab>('active');
  const [refreshing, setRefreshing] = useState(false);

  const loadBookings = useCallback(async () => {
    try {
      const data = await bookingsAPI.myBookings();
      setBookings(data || []);
    } catch (err: any) {
      Alert.alert('Error', err.message || 'Kuch masla aa gaya, dobara try karo');
    }
  }, []);

  // Auto-refresh when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      loadBookings();
    }, [loadBookings])
  );

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadBookings();
    setRefreshing(false);
  }, [loadBookings]);

  // Filter bookings based on selected tab
  const filtered = bookings.filter((b) => {
    const status = b.status?.toLowerCase();
    if (selectedTab === 'active') return status === 'pending' || status === 'confirmed';
    if (selectedTab === 'completed') return status === 'completed';
    if (selectedTab === 'cancelled') return status === 'cancelled';
    return false;
  });

  const renderItem = ({ item }: { item: any }) => (
    <BookingCard 
      booking={item} 
      onPress={() => router.push(`/booking/${item.id}`)} 
    />
  );

  const getTabIcon = (tab: Tab) => {
    if (tab === 'active') return 'clock';
    if (tab === 'completed') return 'check-circle';
    return 'x-circle';
  };

  const getTabCount = (tab: Tab) => {
    return bookings.filter((b) => {
      const status = b.status?.toLowerCase();
      if (tab === 'active') return status === 'pending' || status === 'confirmed';
      if (tab === 'completed') return status === 'completed';
      if (tab === 'cancelled') return status === 'cancelled';
      return false;
    }).length;
  };

  return (
    <View className="flex-1 bg-gray-950">
      {/* Header */}
      <View className="bg-gray-900 px-6 py-6 border-b border-emerald-500/20">
        <Text className="text-3xl font-bold text-white mb-2">My Bookings</Text>
        <Text className="text-gray-400">Track your service requests</Text>
      </View>

      <View className="px-4 pt-4">
        {/* Tab Bar */}
        <View className="flex-row bg-gray-800 rounded-xl p-1 mb-4 border border-gray-700">
          {(['active', 'completed', 'cancelled'] as Tab[]).map((tab) => {
            const isActive = selectedTab === tab;
            const count = getTabCount(tab);

            return (
              <TouchableOpacity
                key={tab}
                onPress={() => setSelectedTab(tab)}
                className={`flex-1 py-3 rounded-lg flex-row items-center justify-center ${
                  isActive ? 'bg-emerald-600' : 'bg-transparent'
                }`}
              >
                <Feather
                  name={getTabIcon(tab) as any}
                  size={16}
                  color={isActive ? '#fff' : '#9ca3af'}
                />
                <Text className={`ml-2 font-bold text-sm ${isActive ? 'text-white' : 'text-gray-400'}`}>
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </Text>
                {count > 0 && (
                  <View className={`ml-1.5 px-2 py-0.5 rounded-full ${
                    isActive ? 'bg-white/20' : 'bg-gray-700'
                  }`}>
                    <Text className={`text-xs font-bold ${isActive ? 'text-white' : 'text-gray-400'}`}>
                      {count}
                    </Text>
                  </View>
                )}
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id?.toString() ?? Math.random().toString()}
        renderItem={renderItem}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#10b981"
            colors={['#10b981']}
          />
        }
        ListEmptyComponent={
          <View className="items-center justify-center mt-20 px-6">
            <View className="w-20 h-20 rounded-full bg-gray-800 items-center justify-center mb-4">
              <Feather name="inbox" size={40} color="#6b7280" />
            </View>
            <Text className="text-white text-xl font-bold mb-2">No Bookings Yet</Text>
            <Text className="text-gray-400 text-center text-sm">
              {selectedTab === 'active' && 'Koi active bookings nahi hain'}
              {selectedTab === 'completed' && 'Koi completed bookings nahi hain'}
              {selectedTab === 'cancelled' && 'Koi cancelled bookings nahi hain'}
            </Text>
          </View>
        }
        contentContainerStyle={{ paddingBottom: 80, paddingHorizontal: 16 }}
      />
    </View>
  );
}