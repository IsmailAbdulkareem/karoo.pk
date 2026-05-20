import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import { auth } from '@/lib/auth';
import { validatePhone, validatePassword } from '@/lib/validation';

export default function LoginScreen() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const handleLogin = async () => {
    setError(null);
    setPhoneError(null);
    setPasswordError(null);

    const phoneValidation = validatePhone(phone);
    if (!phoneValidation.isValid) {
      setPhoneError(phoneValidation.error || '');
      return;
    }

    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
      setPasswordError(passwordValidation.error || '');
      return;
    }

    setLoading(true);
    try {
      await auth.login(phone, password);
    } catch (e: any) {
      setError(e.message || 'Login mein masla aa gaya. Dobara try karein.');
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
          className={`bg-gray-800 rounded-xl p-4 text-white ${phoneError ? 'border border-red-500' : ''}`}
          placeholderTextColor="#9ca3af"
          value={phone}
          onChangeText={(text) => {
            setPhone(text);
            setPhoneError(null);
          }}
          accessibilityLabel="Phone number"
        />
        {phoneError && <Text className="text-red-400 text-xs mt-1 ml-2">{phoneError}</Text>}
      </View>

      <View className="mb-6">
        <View className="relative">
          <TextInput
            placeholder="Password"
            secureTextEntry={!showPassword}
            className={`bg-gray-800 rounded-xl p-4 text-white pr-12 ${passwordError ? 'border border-red-500' : ''}`}
            placeholderTextColor="#9ca3af"
            value={password}
            onChangeText={(text) => {
              setPassword(text);
              setPasswordError(null);
            }}
            accessibilityLabel="Password"
          />
          <TouchableOpacity
            onPress={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-0 bottom-0 justify-center"
            accessibilityLabel={showPassword ? 'Hide password' : 'Show password'}
          >
            <Feather name={showPassword ? 'eye-off' : 'eye'} size={20} color="#9ca3af" />
          </TouchableOpacity>
        </View>
        {passwordError && <Text className="text-red-400 text-xs mt-1 ml-2">{passwordError}</Text>}
      </View>

      <TouchableOpacity
        className={`rounded-xl py-4 items-center mb-4 ${loading ? 'bg-emerald-500/50' : 'bg-emerald-500'}`}
        onPress={handleLogin}
        disabled={loading}
        accessibilityRole="button"
        accessibilityLabel="Login"
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text className="text-white text-lg font-semibold">Login Karo</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/(auth)/register')} accessibilityRole="button" accessibilityLabel="Register">
        <Text className="text-gray-400 text-center underline">Account nahi? Register karo</Text>
      </TouchableOpacity>
    </View>
  );
}
