// lib/api.ts – Axios instance and API helper groups
import axios, { AxiosResponse } from 'axios';
import { storage } from './storage';

// Base URL for Karoo backend - reads from environment variable
const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Create Axios instance
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// Request interceptor to attach JWT token
api.interceptors.request.use(async (config) => {
  const token = await storage.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear storage on auth failure
      await storage.clearAll();
    }
    return Promise.reject(error);
  },
);

// Helper function to wrap API calls with error handling
async function safeCall<T> (promise: Promise<AxiosResponse<T>>) {
  try {
    const result = await promise;
    return result.data;
  } catch (err) {
    const message = axios.isAxiosError(err) && err.response?.data?.detail || 'Kuch masla aa gaya, dobara try karo.';
    throw new Error(message);
  }
}

// Auth API group
export const authAPI = {
  register: (data: any) => safeCall(api.post('/auth/register', data)),
  login: (data: any) => safeCall(api.post('/auth/login', data)),
  me: () => safeCall(api.get('/auth/me')),
};

// Chat API group
export const chatAPI = {
  send: (message: string, user_lat?: number, user_lng?: number) =>
    safeCall(api.post('/api/chat', { message, user_lat, user_lng })),
  history: () => safeCall(api.get('/api/chat/history')),
  clearHistory: () => safeCall(api.delete('/api/chat/history')),
  providerChat: (message: string) =>
    safeCall(api.post('/api/chat/provider', { message })),
};

// Workers API group
export const workersAPI = {
  list: (params?: any) => safeCall(api.get('/api/workers', { params })),
  getById: (id: string) => safeCall(api.get(`/api/workers/${id}`)),
  updateProfile: (data: any) => safeCall(api.put('/api/workers/profile', data)),
  updateAvailability: (is_online: boolean, is_available: boolean) =>
    safeCall(api.put(`/api/workers/availability?is_online=${is_online}&is_available=${is_available}`)),
};

// Bookings API group
export const bookingsAPI = {
  create: (data: any) => safeCall(api.post('/api/bookings', data)),
  myBookings: () => safeCall(api.get('/api/bookings/my')),
  accept: (id: string) => safeCall(api.put(`/api/bookings/${id}/accept`)),
  reject: (id: string) => safeCall(api.put(`/api/bookings/${id}/reject`)),
  cancel: (id: string) => safeCall(api.put(`/api/bookings/${id}/cancel`)),
  complete: (id: string) => safeCall(api.put(`/api/bookings/${id}/complete`)),
  earnings: () => safeCall(api.get('/api/bookings/earnings')),
};

// Requests API group
export const requestsAPI = {
  create: (data: any) => safeCall(api.post('/api/requests', data)),
  open: (params?: any) => safeCall(api.get('/api/requests/open', { params })),
  accept: (id: string) => safeCall(api.put(`/api/requests/${id}/accept`)),
  my: () => safeCall(api.get('/api/requests/my')),
};

// Notifications API group
export const notificationsAPI = {
  list: () => safeCall(api.get('/api/notifications')),
  markRead: (id: string) => safeCall(api.put(`/api/notifications/${id}/read`)),
  markAllRead: () => safeCall(api.put('/api/notifications/read-all')),
};

// Ratings API group
export const ratingsAPI = {
  submit: (data: any) => safeCall(api.post('/api/ratings', data)),
  providerRatings: (id: string) => safeCall(api.get(`/api/ratings/provider/${id}`)),
  userRatings: (id: string) => safeCall(api.get(`/api/ratings/user/${id}`)),
  pending: () => safeCall(api.get('/api/ratings/pending')),
};

// Conversations API group
export const conversationsAPI = {
  list: () => safeCall(api.get('/api/conversations')),
  messages: (id: string) => safeCall(api.get(`/api/conversations/${id}/messages`)),
  send: (id: string, message: string) =>
    safeCall(api.post(`/api/conversations/${id}/messages`, { message })),
};

export default api;
