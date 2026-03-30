import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, AuthState } from '../types'

interface AuthActions {
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  updateAccessToken: (token: string) => void;
}

const getMinRoleLevel = (user: User | null): number => {
  if (!user || !user.roles.length) return 99;
  return Math.min(...user.roles.map(r => r.level));
}

const getScopes = (user: User | null): string[] => {
  if (!user) return [];
  const scopeSet = new Set<string>();
  user.roles.forEach(role => {
    role.scopes.forEach(scope => {
      scopeSet.add(`${scope.resource}:${scope.action}`);
    });
  });
  return Array.from(scopeSet);
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      minRoleLevel: 99,
      deptId: null,
      scopes: [],
      isAuthenticated: false,

      setAuth: (user, accessToken, refreshToken) => {
        const minRoleLevel = getMinRoleLevel(user);
        const scopes = getScopes(user);
        set({
          user,
          accessToken,
          refreshToken,
          minRoleLevel,
          deptId: user.department_id,
          scopes,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          minRoleLevel: 99,
          deptId: null,
          scopes: [],
          isAuthenticated: false,
        });
      },

      updateAccessToken: (token) => {
        set({ accessToken: token });
      }
    }),
    {
      name: 'rbac-auth-storage',
    }
  )
)
