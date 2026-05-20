import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'
import { Platform } from 'react-native'
import "../global.css";

export default function RootLayout() {
  return (
    <>
      <StatusBar style={Platform.OS === 'web' ? 'dark' : 'light'} />
      <Stack screenOptions={{
        headerStyle: { backgroundColor: '#030712' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
        contentStyle: { 
          backgroundColor: '#030712' 
        },
      }}>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="(auth)/login" options={{ title: 'Login', headerShown: false }} />
        <Stack.Screen name="(auth)/register" options={{ title: 'Register', headerShown: false }} />
        <Stack.Screen name="(user)" options={{ headerShown: false }} />
        <Stack.Screen name="(provider)" options={{ headerShown: false }} />
        <Stack.Screen name="worker/[id]" options={{ title: 'Provider Profile', headerShown: true }} />
        <Stack.Screen name="booking/confirm" options={{ title: 'Confirm Booking', headerShown: true }} />
        <Stack.Screen name="booking/[id]" options={{ title: 'Booking Details', headerShown: true }} />
        <Stack.Screen name="conversation/[id]" options={{ title: 'Chat', headerShown: false }} />
      </Stack>
    </>
  )
}