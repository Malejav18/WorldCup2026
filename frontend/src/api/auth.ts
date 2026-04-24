import { api, tokenStore } from "./client";
import type { TokenResponse, UserPublic } from "../types";

export const authApi = {
  register: async (email: string, password: string, displayName: string): Promise<UserPublic> => {
    const { data } = await api.post<UserPublic>("/auth/register", {
      email,
      password,
      display_name: displayName,
    });
    return data;
  },

  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
    tokenStore.set(data.access_token, data.refresh_token);
    return data;
  },

  logout: async (): Promise<void> => {
    const refresh = tokenStore.getRefresh();
    if (refresh) {
      try {
        await api.post("/auth/logout", { refresh_token: refresh });
      } catch {
        // best-effort
      }
    }
    tokenStore.clear();
  },

  validate: async (): Promise<{ user_id: string; role: string; email: string | null }> => {
    const token = tokenStore.getAccess();
    if (!token) throw new Error("No access token");
    const { data } = await api.post("/auth/validate", { access_token: token });
    return data;
  },
};
