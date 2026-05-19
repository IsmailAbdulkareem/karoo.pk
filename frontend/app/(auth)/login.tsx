import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { router } from 'expo-router';
import { auth } from '@/lib/auth';
import { validatePhone, validatePassword } from '@/lib/validation';

/**
 * Login screen – Urdu‑friendly UI with validation.
 */
export default function LoginScreen() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const handleLogin = async () => {
    // Reset errors
    setError(null);
    setPhoneError(null);
    setPasswordError(null);

    // Validate phone
    const phoneValidation = validatePhone(phone);
    if (!phoneValidation.isValid) {
      setPhoneError(phoneValidation.error || '');
      return;
    }

    // Validate password
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
      setPasswordError(passwordValidation.error || '');
      return;
    }

    setLoading(true);
    try {
      await auth.login(phone, password);
      // auth.login already redirects based on role
    } catch (e: any) {
      const errorMsg = e.message || 'Login mein masla aa gaya. Dobara try karein.';
      setError(errorMsg);
      Alert.alert('Login Failed', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="flex-1 bg-gray-950 p-4 justify-center">
      <Text className="text-3xl font-bold text-emerald-500 mb-6 text-center">Login Karo</Text>

      {error && <Text className="text-red-400 mb-2 text-center">{error}</Text>}

      <View className="mb-4">
        <TextInput
          placeholder="Phone (e.g. 03001234567)"
          keyboardType="phone-pad"
          className={`bg-gray-800 rounded-xl p-3 text-white ${phoneError ? 'border border-red-500' : ''}`}
          placeholderTextColor="#9ca3af"
          value={phone}
          onChangeText={(text) => {
            setPhone(text);
            setPhoneError(null);
          }}
        />
        {phoneError && <Text className="text-red-400 text-xs mt-1 ml-2">{phoneError}</Text>}
      </View>

      <View className="mb-6">
        <TextInput
          placeholder="Password"
          secureTextEntry
          className={`bg-gray-800 rounded-xl p-3 text-white ${passwordError ? 'border border-red-500' : ''}`}
          placeholderTextColor="#9ca3af"
          value={password}
          onChangeText={(text) => {
            setPassword(text);
            setPasswordError(null);
          }}
        />
        {passwordError && <Text className="text-red-400 text-xs mt-1 ml-2">{passwordError}</Text>}
      </View>

      <TouchableOpacity
        className="bg-emerald-500 rounded-xl py-3 items-center mb-4"
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text className="text-white text-lg font-semibold">Login Karo</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/(auth)/register')}>
        <Text className="text-gray-400 text-center underline">Account nahi? Register karo</Text>
      </TouchableOpacity>
    </View>
  );
}
