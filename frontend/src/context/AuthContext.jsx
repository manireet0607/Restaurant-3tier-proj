import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, setUnauthorizedHandler, tokenStore } from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!tokenStore.get());

  const logout = useCallback(() => { tokenStore.clear(); setUser(null); }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    if (!tokenStore.get()) return;
    api.me().then(setUser).catch(logout).finally(() => setLoading(false));
  }, [logout]);

  const finish = (res) => { tokenStore.set(res.access_token); setUser(res.user); return res.user; };
  const value = useMemo(() => ({
    user, loading, logout,
    login: async (email, password) => finish(await api.login({ email, password })),
    register: async (data) => finish(await api.register(data)),
  }), [user, loading, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
