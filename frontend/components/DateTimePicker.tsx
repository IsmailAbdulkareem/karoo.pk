// components/DateTimePicker.tsx
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Modal, Platform } from 'react-native';
import { Feather } from '@expo/vector-icons';

interface DateTimePickerProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
}

/**
 * Custom DateTime picker component
 * Format: YYYY-MM-DD HH:mm
 *
 * For now uses text input with format helper.
 * Can be upgraded to use native date picker later.
 */
export default function DateTimePicker({ value, onChange, placeholder, error }: DateTimePickerProps) {
  const [showHelper, setShowHelper] = useState(false);

  const formatDateTime = (input: string): string => {
    // Remove non-numeric characters except space and dash
    let cleaned = input.replace(/[^\d\s:-]/g, '');

    // Auto-format as user types
    if (cleaned.length >= 4 && cleaned[4] !== '-') {
      cleaned = cleaned.slice(0, 4) + '-' + cleaned.slice(4);
    }
    if (cleaned.length >= 7 && cleaned[7] !== '-') {
      cleaned = cleaned.slice(0, 7) + '-' + cleaned.slice(7);
    }
    if (cleaned.length >= 10 && cleaned[10] !== ' ') {
      cleaned = cleaned.slice(0, 10) + ' ' + cleaned.slice(10);
    }
    if (cleaned.length >= 13 && cleaned[13] !== ':') {
      cleaned = cleaned.slice(0, 13) + ':' + cleaned.slice(13);
    }

    return cleaned.slice(0, 16); // Max length YYYY-MM-DD HH:mm
  };

  const handleChange = (text: string) => {
    const formatted = formatDateTime(text);
    onChange(formatted);
  };

  const setToday = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    onChange(`${year}-${month}-${day} ${hours}:${minutes}`);
    setShowHelper(false);
  };

  const setTomorrow = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const year = tomorrow.getFullYear();
    const month = String(tomorrow.getMonth() + 1).padStart(2, '0');
    const day = String(tomorrow.getDate()).padStart(2, '0');
    onChange(`${year}-${month}-${day} 10:00`);
    setShowHelper(false);
  };

  return (
    <View>
      <View className="flex-row items-center">
        <TextInput
          placeholder={placeholder || "YYYY-MM-DD HH:mm"}
          placeholderTextColor="#9ca3af"
          className={`flex-1 bg-gray-800 rounded-xl p-3 text-white ${error ? 'border border-red-500' : ''}`}
          value={value}
          onChangeText={handleChange}
          keyboardType="numbers-and-punctuation"
        />
        <TouchableOpacity
          onPress={() => setShowHelper(true)}
          className="ml-2 p-3 bg-gray-800 rounded-xl"
        >
          <Feather name="calendar" size={20} color="#10b981" />
        </TouchableOpacity>
      </View>

      {error && <Text className="text-red-400 text-xs mt-1 ml-2">{error}</Text>}

      {/* Helper Modal */}
      <Modal
        visible={showHelper}
        transparent
        animationType="fade"
        onRequestClose={() => setShowHelper(false)}
      >
        <TouchableOpacity
          activeOpacity={1}
          onPress={() => setShowHelper(false)}
          className="flex-1 bg-black/50 justify-center items-center"
        >
          <View className="bg-gray-900 rounded-2xl p-6 w-4/5 border border-gray-800">
            <Text className="text-white text-lg font-bold mb-4">Quick Select</Text>

            <TouchableOpacity
              onPress={setToday}
              className="bg-emerald-500 rounded-xl py-3 mb-3"
            >
              <Text className="text-white text-center font-bold">Aaj (Today)</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={setTomorrow}
              className="bg-emerald-500 rounded-xl py-3 mb-3"
            >
              <Text className="text-white text-center font-bold">Kal (Tomorrow)</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => setShowHelper(false)}
              className="bg-gray-800 rounded-xl py-3"
            >
              <Text className="text-gray-300 text-center font-bold">Cancel</Text>
            </TouchableOpacity>

            <View className="mt-4 bg-gray-800 rounded-xl p-3">
              <Text className="text-gray-400 text-xs text-center">
                Format: YYYY-MM-DD HH:mm{'\n'}
                Example: 2026-05-20 10:00
              </Text>
            </View>
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}
