import { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import { storage } from '@/lib/storage';

/**
 * Karoo Landing Page – dark theme, immediate role‑based redirect.
 */
export default function IndexScreen() {
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = await storage.getToken();
      const role = await storage.getRole();
      if (token && role) {
        // redirect based on stored role
        if (role === 'user') router.replace('/(user)/chat');
        else router.replace('/(provider)/dashboard');
      } else {
        setChecking(false);
      }
    };
    checkAuth();
  }, []);

  if (checking) {
    return (
      <View className="flex-1 bg-gray-950 items-center justify-center">
        <ActivityIndicator size="large" color="#10b981" />
      </View>
    );
  }

  return (
    <ScrollView className="flex-1 bg-gray-950 p-4" contentContainerStyle={{ alignItems: 'center' }}>
      {/* Header */}
      <View className="flex-row items-center mb-2">
        <Text className="text-5xl font-bold text-emerald-500">Karoo</Text>
        <Feather name="handshake" size={36} color="#10b981" style={{ marginLeft: 8 }} />
      </View>
      <Text className="text-xl text-white mb-1">Pakistan ka AI Service Platform</Text>
      <Text className="text-lg text-gray-400 mb-6">
        Plumber, electrician, AC — sab milenge AI se
      </Text>

      {/* Feature Cards */}
      <View className="w-full space-y-4 mb-8">
        <View className="bg-gray-900 rounded-2xl p-4">
          <Text className="text-white text-lg font-medium">AI Chat</Text>
          <Text className="text-gray-400 text-sm">Instant AI‑driven service matching</Text>
        </View>
        <View className="bg-gray-900 rounded-2xl p-4">
          <Text className="text-white text-lg font-medium">Browse Workers</Text>
          <Text className="text-gray-400 text-sm">Explore nearby providers</Text>
        </View>
        <View className="bg-gray-900 rounded-2xl p-4">
          <Text className="text-white text-lg font-medium">Rated Providers</Text>
          <Text className="text-gray-400 text-sm">Trusted, verified ratings</Text>
        </View>
      </View>

      {/* Action Buttons */}
      <TouchableOpacity
        className="bg-emerald-500 rounded-xl py-4 px-6 mb-4 w-11/12 items-center"
        onPress={() => router.push('/(auth)/login')}
        accessibilityRole="button"
        accessibilityLabel="Find a service, login"
      >
        <Text className="text-white text-lg font-semibold">Service Dhundho</Text>
      </TouchableOpacity>

      <TouchableOpacity
        className="bg-emerald-500 rounded-xl py-4 px-6 mb-2 w-11/12 items-center"
        onPress={() => router.push('/(auth)/register?role=provider')}
        accessibilityRole="button"
        accessibilityLabel="Register as provider"
      >
        <Text className="text-white text-lg font-semibold">Provider Hoon</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/(auth)/login')}>
        <Text className="text-gray-400 underline">Already registered? Login</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}
