import { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import apiClient from '../api/axios';
import { jwtDecode } from 'jwt-decode';

interface AuthContextType {
  isAuthenticated: boolean;
  user: { [key: string]: any } | null;
  loading: boolean;
  login: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  markOnboardingComplete: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<{ [key: string]: any } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        try {
          const decoded: { exp: number, user_id: string } = jwtDecode(accessToken);
          if (decoded.exp > Date.now() / 1000) {
            setUser(decoded);
            try {
              const response = await apiClient.get('/auth/business/');
              setUser({ ...decoded, business: response.data });
            } catch {
              // Keep the decoded session when business data is unavailable.
            }
          } else {
            setUser(null);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
        } catch (_e: unknown) {
          setUser(null);
        }
      }
      setLoading(false);
    };
    initializeAuth();
  }, []);

  const login = (accessToken: string, refreshToken: string) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    const decoded: { [key: string]: any } = jwtDecode(accessToken);
    setUser(decoded);
  };

  const logout = () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      apiClient.post('/auth/logout/', { refresh_token: refreshToken });
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const markOnboardingComplete = () => {
    setUser((current) => current ? {
      ...current,
      has_completed_onboarding: true,
      business: { ...current.business, has_completed_onboarding: true },
    } : current);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated: !!user, user, loading, login, logout, markOnboardingComplete }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};