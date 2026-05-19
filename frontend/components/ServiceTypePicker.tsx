// components/ServiceTypePicker.tsx
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Modal, ScrollView } from 'react-native';
import { Feather } from '@expo/vector-icons';

interface ServiceTypePickerProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
}

const SERVICE_TYPES = [
  { value: 'plumber', label: 'Plumber', icon: '🔧' },
  { value: 'electrician', label: 'Electrician', icon: '⚡' },
  { value: 'ac_technician', label: 'AC Technician', icon: '❄️' },
  { value: 'tutor', label: 'Tutor', icon: '📚' },
  { value: 'cleaner', label: 'Cleaner', icon: '🧹' },
  { value: 'carpenter', label: 'Carpenter', icon: '🪚' },
  { value: 'painter', label: 'Painter', icon: '🎨' },
  { value: 'mechanic', label: 'Mechanic', icon: '🔩' },
  { value: 'cook', label: 'Cook', icon: '👨‍🍳' },
  { value: 'security_guard', label: 'Security Guard', icon: '🛡️' },
];

/**
 * Service Type Picker Component
 * Dropdown-style picker for selecting service types
 */
export default function ServiceTypePicker({ value, onChange, placeholder, error }: ServiceTypePickerProps) {
  const [showModal, setShowModal] = useState(false);

  const selectedService = SERVICE_TYPES.find(s => s.value === value);

  const handleSelect = (serviceValue: string) => {
    onChange(serviceValue);
    setShowModal(false);
  };

  return (
    <View>
      <TouchableOpacity
        onPress={() => setShowModal(true)}
        className={`bg-gray-800 rounded-xl p-3 flex-row justify-between items-center ${error ? 'border border-red-500' : ''}`}
      >
        <Text className={selectedService ? 'text-white' : 'text-gray-400'}>
          {selectedService ? `${selectedService.icon} ${selectedService.label}` : (placeholder || 'Select Service Type')}
        </Text>
        <Feather name="chevron-down" size={20} color="#9ca3af" />
      </TouchableOpacity>

      {error && <Text className="text-red-400 text-xs mt-1 ml-2">{error}</Text>}

      {/* Service Type Modal */}
      <Modal
        visible={showModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowModal(false)}
      >
        <TouchableOpacity
          activeOpacity={1}
          onPress={() => setShowModal(false)}
          className="flex-1 bg-black/50 justify-end"
        >
          <View className="bg-gray-900 rounded-t-3xl border-t border-gray-800 max-h-3/4">
            <View className="p-4 border-b border-gray-800">
              <Text className="text-white text-lg font-bold text-center">Select Service Type</Text>
            </View>

            <ScrollView className="p-4">
              {SERVICE_TYPES.map((service) => (
                <TouchableOpacity
                  key={service.value}
                  onPress={() => handleSelect(service.value)}
                  className={`p-4 rounded-xl mb-2 flex-row items-center ${
                    value === service.value ? 'bg-emerald-500' : 'bg-gray-800'
                  }`}
                >
                  <Text className="text-2xl mr-3">{service.icon}</Text>
                  <Text className={`text-base font-bold ${
                    value === service.value ? 'text-white' : 'text-gray-300'
                  }`}>
                    {service.label}
                  </Text>
                  {value === service.value && (
                    <Feather name="check" size={20} color="#fff" style={{ marginLeft: 'auto' }} />
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>

            <TouchableOpacity
              onPress={() => setShowModal(false)}
              className="p-4 border-t border-gray-800"
            >
              <Text className="text-gray-400 text-center font-bold">Cancel</Text>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}
