// lib/types.ts - TypeScript interfaces for Karoo app

// ============================================
// USER & AUTH TYPES
// ============================================

export interface User {
  id: string;
  name: string;
  phone: string;
  email?: string;
  role: 'user' | 'provider';
  city?: string;
  reliability_score?: number;
  total_ratings?: number;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: 'user' | 'provider';
  user_id: string;
}

// ============================================
// PROVIDER TYPES
// ============================================

export interface Provider {
  id: string;
  user_id: string;
  name: string;
  service_type: string;
  area: string;
  lat?: number;
  lng?: number;
  rating: number;
  total_ratings: number;
  rate_per_hour?: number;
  is_available: boolean;
  is_online?: boolean;
  bio?: string;
  eta_minutes?: number;
  match_score?: number;
  on_time_score?: number;
  review_recency?: number;
  avatar_url?: string;
}

// ============================================
// BOOKING TYPES
// ============================================

export type BookingStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled';

export interface Booking {
  id: string;
  user_id: string;
  provider_id: string;
  service_type: string;
  location: string;
  scheduled_at: string;
  status: BookingStatus;
  note?: string;
  booked_via: 'chat' | 'browse' | 'request';
  budget?: number;
  agreed_rate?: number;
  user_lat?: number;
  user_lng?: number;
  eta_minutes?: number;
  created_at: string;
  updated_at: string;
  // Joined fields
  provider_name?: string;
  user_name?: string;
}

export interface BookingCreatePayload {
  provider_id: string;
  service_type: string;
  location: string;
  scheduled_at: string;
  note?: string;
  booked_via: 'chat' | 'browse' | 'request';
  budget?: number;
  agreed_rate?: number;
  user_lat?: number;
  user_lng?: number;
  eta_minutes?: number;
}

// ============================================
// CHAT TYPES
// ============================================

export interface ChatMessage {
  id: string;
  user_id: string;
  role: 'user' | 'bot';
  content: string;
  created_at: string;
  parsed_intent?: ParsedIntent;
  agent_trace?: string;
}

export interface ParsedIntent {
  service_type?: string;
  location?: string;
  time?: string;
  confidence: number;
  location_lat?: number;
  location_lng?: number;
}

export interface ChatResponse {
  reply: string;
  intent?: ParsedIntent;
  providers: Provider[];
  needs_clarification: boolean;
  agent_trace: string;
}

// ============================================
// NOTIFICATION TYPES
// ============================================

export type NotificationType =
  | 'booking_created'
  | 'booking_accepted'
  | 'booking_rejected'
  | 'booking_cancelled'
  | 'booking_completed'
  | 'service_request'
  | 'request_accepted';

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  body: string;
  type: NotificationType;
  ref_id?: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  unread_count: number;
}

// ============================================
// RATING TYPES
// ============================================

export interface Rating {
  id: string;
  booking_id: string;
  rater_id: string;
  ratee_id: string;
  rater_role: 'user' | 'provider';
  stars: number;
  review_text?: string;
  tags: string[];
  created_at: string;
}

export interface RatingCreatePayload {
  booking_id: string;
  ratee_id: string;
  stars: number;
  review_text?: string;
  tags?: string[];
}

// ============================================
// CONVERSATION & MESSAGING TYPES
// ============================================

export interface Conversation {
  id: string;
  booking_id: string;
  user_id: string;
  provider_id: string;
  last_message?: string;
  last_message_at?: string;
  user_unread_count: number;
  provider_unread_count: number;
  created_at: string;
  updated_at: string;
  // Joined fields
  other_party_name?: string;
  other_party_avatar?: string;
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender_role: 'user' | 'provider';
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface SendMessagePayload {
  message: string;
}

export interface CreateConversationPayload {
  booking_id: string;
}

// ============================================
// SERVICE REQUEST TYPES
// ============================================

export interface ServiceRequest {
  id: string;
  user_id: string;
  service_type: string;
  location: string;
  scheduled_at?: string;
  budget?: number;
  description?: string;
  status: 'open' | 'taken' | 'cancelled';
  created_at: string;
  // Joined fields
  user_name?: string;
  user_phone?: string;
}

export interface ServiceRequestCreatePayload {
  service_type: string;
  location: string;
  scheduled_at?: string;
  budget?: number;
  description?: string;
}

// ============================================
// CONVERSATION TYPES
// ============================================

export interface Conversation {
  id: string;
  booking_id: string;
  user_id: string;
  provider_id: string;
  last_message?: string;
  last_message_at?: string;
  user_unread_count: number;
  provider_unread_count: number;
  created_at: string;
  updated_at: string;
  other_party_name?: string;
  other_party_avatar?: string;
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender_role: 'user' | 'provider';
  message: string;
  is_read: boolean;
  created_at: string;
}

// ============================================
// EARNINGS TYPES
// ============================================

export interface EarningsBreakdown {
  booking_id: string;
  service_type: string;
  location: string;
  customer_name: string;
  scheduled_at: string;
  agreed_rate?: number;
  budget?: number;
  earned: number;
}

export interface EarningsResponse {
  provider_id: string;
  total_completed_jobs: number;
  total_earned_pkr: number;
  rate_per_hour: number;
  message: string;
  earnings_breakdown: EarningsBreakdown[];
}

// ============================================
// FORM VALIDATION TYPES
// ============================================

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

// ============================================
// API ERROR TYPES
// ============================================

export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}
