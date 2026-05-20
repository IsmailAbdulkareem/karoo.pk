import { storage } from '@/lib/storage';
import { authAPI } from '@/lib/api';
import { router } from 'expo-router';

export const auth = {
  /**
   * Login with phone and password, store token and role.
   * Redirect based on role.
   */
  login: async (phone: string, password: string) => {
    try {
      const res = await authAPI.login({ phone, password });
      const { access_token, role } = res;
      await storage.setToken(access_token);
      await storage.setRole(role);
      // Optionally fetch user profile and save
      const user = await authAPI.me();
      await storage.setUser(JSON.stringify(user));
      // Redirect
      if (role === 'user') router.replace('/(user)/chat');
      else if (role === 'provider') router.replace('/(provider)/dashboard');
    } catch (e: any) {
      // Propagate to UI
      throw new Error(e?.response?.data?.detail || 'Kuch masla aa gaya. Dobara try karo.');
    }
  },

  /** Register a new user or provider and store token/role */
  register: async (data: any) => {
    try {
      const res = await authAPI.register(data);
      const { access_token, role } = res;
      await storage.setToken(access_token);
      await storage.setRole(role);
      const user = await authAPI.me();
      await storage.setUser(JSON.stringify(user));
      if (role === 'user') router.replace('/(user)/chat');
      else router.replace('/(provider)/dashboard');
    } catch (e: any) {
      throw new Error(e?.response?.data?.detail || 'Kuch masla aa gaya. Dobara try karo.');
    }
  },

  /** Logout - clear stored data only, caller handles navigation */
  logout: async () => {
    try {
      await storage.clearAll();
    } catch (err) {
      console.error('Logout clearAll error:', err);
    }
  },

  /** Simple logged‑in check */
  isLoggedIn: async () => {
    const token = await storage.getToken();
    const role = await storage.getRole();
    return !!token && !!role;
  },
};
