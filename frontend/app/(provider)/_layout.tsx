import { Tabs, useRouter } from 'expo-router'
import React, { useEffect, useState } from 'react'
import { Text, View, ActivityIndicator } from 'react-native'
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
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>📊</Text>,
        }}
      />
      <Tabs.Screen
        name="requests"
        options={{
          title: 'Marketplace',
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>📋</Text>,
        }}
      />
      <Tabs.Screen
        name="bookings"
        options={{
          title: 'Bookings',
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>📅</Text>,
        }}
      />
      <Tabs.Screen
        name="earnings"
        options={{
          title: 'Earnings',
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>💰</Text>,
        }}
      />
      <Tabs.Screen
        name="chat"
        options={{
          title: 'Partner AI',
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>🤖</Text>,
        }}
      />
      <Tabs.Screen
        name="notifications"
        options={{
          title: 'Alerts',
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 18 }}>🔔</Text>,
          headerShown: false,
        }}
      />
    </Tabs>
  )
}
