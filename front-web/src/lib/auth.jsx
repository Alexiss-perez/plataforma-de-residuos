import { createContext, useContext, useEffect, useState } from "react";
import api from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("ecomatch_token");
    const stored = localStorage.getItem("ecomatch_user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
    // Si hay token, validar contra el backend
    if (token) {
      api.get("/auth/me")
        .then(({ data }) => {
          setUser(data);
          localStorage.setItem("ecomatch_user", JSON.stringify(data));
        })
        .catch(() => {
          localStorage.removeItem("ecomatch_token");
          localStorage.removeItem("ecomatch_user");
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = (userData, token) => {
    localStorage.setItem("ecomatch_token", token);
    localStorage.setItem("ecomatch_user", JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("ecomatch_token");
    localStorage.removeItem("ecomatch_user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
