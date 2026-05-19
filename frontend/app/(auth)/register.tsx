import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, ScrollView, Alert } from 'react-native';
import { router } from 'expo-router';
import { auth } from '@/lib/auth';
import { validatePhone, validatePassword, validateName, validateEmail, validateServiceType, validateRate, validateLocation } from '@/lib/validation';

import ServiceTypePicker from '@/components/ServiceTypePicker';

/**
 * Register screen – supports both User and Provider roles with validation.
 * Provider‑only fields appear when the Provider toggle is active.
 */
export default function RegisterScreen() {
  const [role, setRole] = useState<'user' | 'provider'>('user');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [city, setCity] = useState('');
  const [email, setEmail] = useState('');
  // Provider‑only fields
  const [serviceType, setServiceType] = useState('');
  const [area, setArea] = useState('');
  const [ratePerHour, setRatePerHour] = useState('');
  const [bio, setBio] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Field-specific errors
  const [nameError, setNameError] = useState<string | null>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [serviceTypeError, setServiceTypeError] = useState<string | null>(null);
  const [areaError, setAreaError] = useState<string | null>(null);
  const [rateError, setRateError] = useState<string | null>(null);

  const handleRegister = async () => {
    // Reset all errors
    setError(null);
    setNameError(null);
    setPhoneError(null);
    setPasswordError(null);
    setEmailError(null);
    setServiceTypeError(null);
    setAreaError(null);
    setRateError(null);

    // Validate common fields
    const nameValidation = validateName(name);
    if (!nameValidation.isValid) {
      setNameError(nameValidation.error || '');
      return;
    }

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

    const emailValidation = validateEmail(email);
    if (!emailValidation.isValid) {
      setEmailError(emailValidation.error || '');
      return;
    }

    // Validate provider-specific fields
    if (role === 'provider') {
      const serviceValidation = validateServiceType(serviceType);
      if (!serviceValidation.isValid) {
        setServiceTypeError(serviceValidation.error || '');
        return;
      }

      const areaValidation = validateLocation(area);
      if (!areaValidation.isValid) {
        setAreaError(areaValidation.error || '');
        return;
      }

      const rateValidation = validateRate(ratePerHour);
      if (!rateValidation.isValid) {
        setRateError(rateValidation.error || '');
        return;
      }
    }

    setLoading(true);
    try {
      const payload: any = {
        name,
        phone,
        password,
        email: email || undefined,
        city: city || undefined,
        role,
      };
      if (role === 'provider') {
        payload.service_type = serviceType;
        payload.area = area;
        payload.rate_per_hour = Number(ratePerHour);
        payload.bio = bio || undefined;
      }
      await auth.register(payload);
      // auth.register redirects based on role
    } catch (e: any) {
      const errorMsg = e.message || 'Registration mein masla aa gaya. Dobara try karein.';
      setError(errorMsg);
      Alert.alert('Registration Failed', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView className="flex-1 bg-gray-950 p-4" contentContainerStyle={{ alignItems: 'center' }}>
      <Text className="text-3xl font-bold text-emerald-500 mb-6">Account Banao</Text>

      {error && (
        <View className="bg-red-500/10 border border-red-500 rounded-xl p-3 mb-4 w-full">
          <Text className="text-red-400 text-center">{error}</Text>
        </View>
      )}

      {/* Role selector */}
      <View className="flex-row mb-4 space-x-4">
        <TouchableOpacity
          className={`px-4 py-2 rounded-xl ${role === 'user' ? 'bg-emerald-500' : 'bg-gray-800'} `}
          onPress={() => setRole('user')}
        >
          <Text className="text-white">👤 User</Text>
        </TouchableOpacity>
        <TouchableOpacity
          className={`px-4 py-2 rounded-xl ${role === 'provider' ? 'bg-emerald-500' : 'bg-gray-800'} `}
          onPress={() => setRole('provider')}
        >
          <Text className="text-white">🔧 Provider</Text>
        </TouchableOpacity>
      </View>

      {/* Common fields */}
      <View className="mb-4">
        <TextInput
          placeholder="Name"
          placeholderTextColor="#9ca3af"
          className={`bg-gray-800 rounded-xl p-3 text-white ${nameError ? 'border border-red-500' : ''}`}
          value={name}
          onChangeText={(text) => {
            setName(text);
            setNameError(null);
          }}
        />
        {nameError && <Text className="text-red-400 text-xs mt-1 ml-2">{nameError}</Text>}
      </View>

      <View className="mb-4">
        <TextInput
          placeholder="Phone (e.g. 03001234567)"
          keyboardType="phone-pad"
          placeholderTextColor="#9ca3af"
          className={`bg-gray-800 rounded-xl p-3 text-white ${phoneError ? 'border border-red-500' : ''}`}
          value={phone}
          onChangeText={(text) => {
            setPhone(text);
            setPhoneError(null);
          }}
        />
        {phoneError && <Text className="text-red-400 text-xs mt-1 ml-2">{phoneError}</Text>}
      </View>

      <View className="mb-4">
        <TextInput
          placeholder="Password (min 6 characters)"
          secureTextEntry
          placeholderTextColor="#9ca3af"
          className={`bg-gray-800 rounded-xl p-3 text-white ${passwordError ? 'border border-red-500' : ''}`}
          value={password}
          onChangeText={(text) => {
            setPassword(text);
            setPasswordError(null);
          }}
        />
        {passwordError && <Text className="text-red-400 text-xs mt-1 ml-2">{passwordError}</Text>}
      </View>

      <View className="mb-4">
        <TextInput
          placeholder="Email (optional)"
          keyboardType="email-address"
          placeholderTextColor="#9ca3af"
          className={`bg-gray-800 rounded-xl p-3 text-white ${emailError ? 'border border-red-500' : ''}`}
          value={email}
          onChangeText={(text) => {
            setEmail(text);
            setEmailError(null);
          }}
        />
        {emailError && <Text className="text-red-400 text-xs mt-1 ml-2">{emailError}</Text>}
      </View>

      <View className="mb-4">
        <TextInput
          placeholder="City (optional)"
          placeholderTextColor="#9ca3af"
          className="bg-gray-800 rounded-xl p-3 text-white"
          value={city}
          onChangeText={setCity}
        />
      </View>

      {/* Provider‑only fields */}
      {role === 'provider' && (
        <View className="w-full">
          <View className="mb-4">
            <ServiceTypePicker
              value={serviceType}
              onChange={(value) => {
                setServiceType(value);
                setServiceTypeError(null);
              }}
              placeholder="Select Service Type"
              error={serviceTypeError || undefined}
            />
          </View>

          <View className="mb-4">
            <TextInput
              placeholder="Area / neighbourhood"
              placeholderTextColor="#9ca3af"
              className={`bg-gray-800 rounded-xl p-3 text-white ${areaError ? 'border border-red-500' : ''}`}
              value={area}
              onChangeText={(text) => {
                setArea(text);
                setAreaError(null);
              }}
            />
            {areaError && <Text className="text-red-400 text-xs mt-1 ml-2">{areaError}</Text>}
          </View>

          <View className="mb-4">
            <TextInput
              placeholder="Rate per hour (PKR)"
              keyboardType="numeric"
              placeholderTextColor="#9ca3af"
              className={`bg-gray-800 rounded-xl p-3 text-white ${rateError ? 'border border-red-500' : ''}`}
              value={ratePerHour}
              onChangeText={(text) => {
                setRatePerHour(text);
                setRateError(null);
              }}
            />
            {rateError && <Text className="text-red-400 text-xs mt-1 ml-2">{rateError}</Text>}
          </View>

          <View className="mb-4">
            <TextInput
              placeholder="Short bio (optional)"
              placeholderTextColor="#9ca3af"
              className="bg-gray-800 rounded-xl p-3 text-white h-24"
              multiline
              value={bio}
              onChangeText={setBio}
            />
          </View>
        </View>
      )}

      <TouchableOpacity
        className="bg-emerald-500 rounded-xl py-3 px-6 w-full items-center mb-4"
        onPress={handleRegister}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text className="text-white text-lg font-semibold">Account Banao</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity onPress={() => router.push('/(auth)/login')}>
        <Text className="text-gray-400 underline">Already have an account? Login</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}
