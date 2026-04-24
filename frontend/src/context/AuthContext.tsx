import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { authApi } from "../api/auth";
import { tokenStore } from "../api/client";
import { usersApi } from "../api/users";
import type { UserProfileSelf } from "../types";

interface AuthState {
  user: UserProfileSelf | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfileSelf | null>(null);
  const [loading, setLoading] = useState(true);

  const loadProfile = useCallback(async () => {
    const token = tokenStore.getAccess();
    if (!token) {
      setUser(null);
      return;
    }
    try {
      const profile = await usersApi.me();
      setUser(profile);
    } catch {
      // 404 (perfil no creado aun por el evento) o 401: ambos dejan user=null.
      setUser(null);
    }
  }, []);

  useEffect(() => {
    (async () => {
      await loadProfile();
      setLoading(false);
    })();
  }, [loadProfile]);

  useEffect(() => {
    const handler = () => setUser(null);
    window.addEventListener("auth:logout", handler);
    return () => window.removeEventListener("auth:logout", handler);
  }, []);

  const login = async (email: string, password: string) => {
    await authApi.login(email, password);
    await loadProfile();
  };

  const register = async (email: string, password: string, displayName: string) => {
    await authApi.register(email, password, displayName);
    // Tras registrar, login para obtener tokens. El perfil se crea por evento
    // en user-service: puede tardar unos segundos en aparecer. loadProfile es
    // tolerante: si 404 aun, user queda null y el flujo igual navega al login.
    await authApi.login(email, password);
    await loadProfile();
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  const value = useMemo<AuthState>(
    () => ({ user, loading, login, register, logout, refreshProfile: loadProfile }),
    [user, loading, loadProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
