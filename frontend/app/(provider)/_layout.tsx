import { Tabs, useRouter } from 'expo-router'
import React, { useEffect, useState } from 'react'
import { View, ActivityIndicator } from 'react-native'
import { Feather } from '@expo/vector-icons'
import { storage } from '../../lib/storage'

export default function ProviderLayout() {
  const router = useRouter()
  const [authorized, setAuthorized] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkRole = async () => {
      try {
        const token = await storage.getToken()
        const role = await storage.getRole()
        if (!token) {
          router.replace('/(auth)/login')
        } else if (role !== 'provider') {
          // If not a provider, redirect to user chat
          router.replace('/(user)/chat')
        } else {
          setAuthorized(true)
        }
      } catch (err) {
        console.error('Provider layout auth check error:', err)
        router.replace('/(auth)/login')
      } finally {
        setLoading(false)
      }
    }
    checkRole()
  }, [])

  if (loading) {
    return (
      <View className="flex-1 bg-gray-950 justify-center items-center">
        <ActivityIndicator size="large" color="#10b981" />
      </View>
    )
  }

  if (!authorized) return null

  return (
    <Tabs
      screenOptions={{
        headerStyle: {
          backgroundColor: '#111827',
          borderBottomWidth: 1,
          borderBottomColor: '#1f2937',
        },
        headerTintColor: '#ffffff',
        headerTitleStyle: {
          fontWeight: '900',
          fontSize: 18,
        },
        tabBarStyle: {
          backgroundColor: '#111827',
          borderTopWidth: 1,
          borderTopColor: '#1f2937',
          paddingBottom: 8,
          paddingTop: 8,
          height: 64,
        },
        tabBarActiveTintColor: '#10b981',
        tabBarInactiveTintColor: '#9ca3af',
        tabBarLabelStyle: {
          fontSize: 10,
          fontWeight: 'bold',
        },
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color }) => <Feather name="grid" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="requests"
        options={{
          title: 'Marketplace',
          tabBarIcon: ({ color }) => <Feather name="shopping-bag" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="bookings"
        options={{
          title: 'Bookings',
          tabBarIcon: ({ color }) => <Feather name="calendar" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="earnings"
        options={{
          title: 'Earnings',
          tabBarIcon: ({ color }) => <Feather name="trending-up" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="chat"
        options={{
          title: 'Partner AI',
          tabBarIcon: ({ color }) => <Feather name="message-square" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="notifications"
        options={{
          title: 'Alerts',
          tabBarIcon: ({ color }) => <Feather name="bell" size={22} color={color} />,
          headerShown: false,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color }) => <Feather name="user" size={22} color={color} />,
        }}
      />
    </Tabs>
  )
}
