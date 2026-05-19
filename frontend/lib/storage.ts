// frontend/lib/storage.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

const PREFIX = 'karoo:';

/**
 * Helper for storing simple key/value pairs in AsyncStorage.
 * All keys are prefixed to avoid collision with other apps.
 */
export const storage = {
  // ── Token ─────────────────────────────────────────────────────
  async setToken(token: string) {
    await AsyncStorage.setItem(`${PREFIX}token`, token);
  },
  async getToken(): Promise<string | null> {
    return AsyncStorage.getItem(`${PREFIX}token`);
  },
  async clearToken() {
    await AsyncStorage.removeItem(`${PREFIX}token`);
  },

  // ── User ─────────────────────────────────────────────────────
  async setUser(user: string) {
    await AsyncStorage.setItem(`${PREFIX}user`, user);
  },
  async getUser(): Promise<string | null> {
    return AsyncStorage.getItem(`${PREFIX}user`);
  },
  async clearUser() {
    await AsyncStorage.removeItem(`${PREFIX}user`);
  },

  // ── Role ("user" | "provider") ────────────────────────────────
  async setRole(role: string) {
    await AsyncStorage.setItem(`${PREFIX}role`, role);
  },
  async getRole(): Promise<string | null> {
    return AsyncStorage.getItem(`${PREFIX}role`);
  },
  async clearRole() {
    await AsyncStorage.removeItem(`${PREFIX}role`);
  },

  // ── Convenience ─────────────────────────────────────────────
  async clearAll() {
    await Promise.all([
      this.clearToken(),
      this.clearUser(),
      this.clearRole(),
    ]);
  },
};
