// Cliente axios compartido por toda la app.
// - Inyecta el Authorization: Bearer <access_token> en cada request.
// - En 401, intenta refrescar el token una vez; si falla, limpia tokens y
//   dispara "auth:logout" que el AuthContext escucha para redirigir a /login.
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const ACCESS_TOKEN_KEY = "wc2026.access_token";
const REFRESH_TOKEN_KEY = "wc2026.refresh_token";

export const tokenStore = {
  getAccess: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  set: (access: string, refresh: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Control de refresh para no disparar en paralelo.
let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = tokenStore.getRefresh();
  if (!refresh) return null;
  try {
    const response = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refresh });
    const { access_token, refresh_token: newRefresh } = response.data;
    tokenStore.set(access_token, newRefresh);
    return access_token;
  } catch {
    return null;
  }
}

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const url = original?.url ?? "";

    // Evitamos el loop: /auth/refresh no reintenta.
    if (error.response?.status === 401 && !original._retry && !url.includes("/auth/refresh")) {
      original._retry = true;
      if (!refreshing) refreshing = refreshAccessToken();
      const newToken = await refreshing;
      refreshing = null;
      if (newToken) {
        original.headers = original.headers ?? {};
        (original.headers as Record<string, string>).Authorization = `Bearer ${newToken}`;
        return api.request(original);
      }
      // Refresh fallo: limpiar y avisar al AuthContext.
      tokenStore.clear();
      window.dispatchEvent(new Event("auth:logout"));
    }
    return Promise.reject(error);
  },
);
