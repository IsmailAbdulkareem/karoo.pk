// lib/validation.ts - Form validation utilities

import { ValidationResult } from './types';

/**
 * Validate Pakistani phone number format
 * Must be 11 digits starting with 03
 */
export function validatePhone(phone: string): ValidationResult {
  const cleaned = phone.replace(/\s|-/g, '');

  if (!cleaned) {
    return { isValid: false, error: 'Phone number zaroori hai' };
  }

  if (!/^\d+$/.test(cleaned)) {
    return { isValid: false, error: 'Sirf numbers allowed hain' };
  }

  if (!cleaned.startsWith('03')) {
    return { isValid: false, error: 'Phone number 03 se shuru hona chahiye' };
  }

  if (cleaned.length !== 11) {
    return { isValid: false, error: 'Phone number 11 digits ka hona chahiye (03001234567)' };
  }

  return { isValid: true };
}

/**
 * Validate password strength
 * Minimum 6 characters
 */
export function validatePassword(password: string): ValidationResult {
  if (!password) {
    return { isValid: false, error: 'Password zaroori hai' };
  }

  if (password.length < 6) {
    return { isValid: false, error: 'Password kam az kam 6 characters ka hona chahiye' };
  }

  return { isValid: true };
}

/**
 * Validate name field
 * Must not be empty and at least 2 characters
 */
export function validateName(name: string): ValidationResult {
  if (!name || !name.trim()) {
    return { isValid: false, error: 'Name zaroori hai' };
  }

  if (name.trim().length < 2) {
    return { isValid: false, error: 'Name kam az kam 2 characters ka hona chahiye' };
  }

  return { isValid: true };
}

/**
 * Validate email format (optional field)
 */
export function validateEmail(email: string): ValidationResult {
  if (!email || !email.trim()) {
    return { isValid: true }; // Email is optional
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Email format galat hai' };
  }

  return { isValid: true };
}

/**
 * Validate service type for providers
 */
export function validateServiceType(serviceType: string): ValidationResult {
  const validTypes = [
    'plumber',
    'electrician',
    'ac_technician',
    'tutor',
    'cleaner',
    'carpenter',
    'painter',
    'mechanic',
    'cook',
    'security_guard'
  ];

  if (!serviceType || !serviceType.trim()) {
    return { isValid: false, error: 'Service type zaroori hai' };
  }

  if (!validTypes.includes(serviceType.toLowerCase())) {
    return { isValid: false, error: 'Invalid service type' };
  }

  return { isValid: true };
}

/**
 * Validate rate per hour (must be positive number)
 */
export function validateRate(rate: string): ValidationResult {
  if (!rate || !rate.trim()) {
    return { isValid: false, error: 'Rate zaroori hai' };
  }

  const numRate = Number(rate);

  if (isNaN(numRate)) {
    return { isValid: false, error: 'Rate number hona chahiye' };
  }

  if (numRate <= 0) {
    return { isValid: false, error: 'Rate 0 se zyada hona chahiye' };
  }

  if (numRate > 100000) {
    return { isValid: false, error: 'Rate bohot zyada hai' };
  }

  return { isValid: true };
}

/**
 * Validate location/area field
 */
export function validateLocation(location: string): ValidationResult {
  if (!location || !location.trim()) {
    return { isValid: false, error: 'Location zaroori hai' };
  }

  if (location.trim().length < 2) {
    return { isValid: false, error: 'Location kam az kam 2 characters ka hona chahiye' };
  }

  return { isValid: true };
}

/**
 * Validate date/time format (YYYY-MM-DD HH:mm)
 */
export function validateDateTime(dateTime: string): ValidationResult {
  if (!dateTime || !dateTime.trim()) {
    return { isValid: false, error: 'Date aur time zaroori hai' };
  }

  // Check format YYYY-MM-DD HH:mm
  const dateTimeRegex = /^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}$/;

  if (!dateTimeRegex.test(dateTime)) {
    return { isValid: false, error: 'Format: YYYY-MM-DD HH:mm (e.g. 2026-05-20 10:00)' };
  }

  // Check if date is valid
  const date = new Date(dateTime);
  if (isNaN(date.getTime())) {
    return { isValid: false, error: 'Invalid date' };
  }

  // Check if date is in the past
  if (date < new Date()) {
    return { isValid: false, error: 'Date past mein nahi ho sakti' };
  }

  return { isValid: true };
}

/**
 * Validate rating stars (1-5)
 */
export function validateStars(stars: number): ValidationResult {
  if (!stars) {
    return { isValid: false, error: 'Rating zaroori hai' };
  }

  if (stars < 1 || stars > 5) {
    return { isValid: false, error: 'Rating 1 se 5 ke beech honi chahiye' };
  }

  return { isValid: true };
}
