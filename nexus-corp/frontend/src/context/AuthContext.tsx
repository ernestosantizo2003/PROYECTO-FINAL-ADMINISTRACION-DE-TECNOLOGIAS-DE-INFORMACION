import React, { createContext, useState, useEffect, useCallback } from 'react';
import { AuthUser } from '../types';
import { authService } from '../services/auth.service';

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  hasRole: (roles: string[]) => boolean;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('nexus_token'));
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
    setToken(null);
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem('nexus_token');
    if (storedToken) {
      authService
        .getMe()
        .then((userData) => {
          setUser(userData);
          setToken(storedToken);
        })
        .catch(() => {
          logout();
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, [logout]);

  const login = async (username: string, password: string): Promise<void> => {
    const response = await authService.login(username, password);
    localStorage.setItem('nexus_token', response.access_token);
    localStorage.setItem('nexus_user', JSON.stringify(response.user));
    setToken(response.access_token);
    setUser(response.user);
  };

  const hasRole = useCallback(
    (roles: string[]): boolean => {
      if (!user) return false;
      return roles.includes(user.role);
    },
    [user]
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!user && !!token,
        hasRole,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
