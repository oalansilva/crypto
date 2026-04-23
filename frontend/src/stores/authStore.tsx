import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import axios from 'axios'
import { queryClient } from '../lib/queryClient'

const API_BASE = '/api'

export interface AuthUser {
  id: string
  email: string
  name: string
  isAdmin: boolean
}

interface AuthState {
  user: AuthUser | null
  accessToken: string | null
  refreshToken: string | null
  isLoading: boolean
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  getAccessToken: () => string | null
  updateUser: (patch: Partial<AuthUser>) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

const ACCESS_TOKEN_KEY = 'auth_access_token'
const REFRESH_TOKEN_KEY = 'auth_refresh_token'
const USER_KEY = 'auth_user'
const E2E_AUTH_BYPASS = import.meta.env.VITE_E2E_AUTH_BYPASS === '1'
const E2E_AUTH_FALLBACK_USER: AuthUser = {
  id: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  isAdmin: false,
}

const E2E_AUTH_FALLBACK_TOKENS = {
  accessToken: 'test-access-token',
  refreshToken: 'test-refresh-token',
}

function getE2EAuthState() {
  const { accessToken: currentAccessToken, refreshToken: currentRefreshToken, user: currentUser } = loadFromStorage()
  return {
    accessToken: currentAccessToken || E2E_AUTH_FALLBACK_TOKENS.accessToken,
    refreshToken: currentRefreshToken || E2E_AUTH_FALLBACK_TOKENS.refreshToken,
    user: currentUser || E2E_AUTH_FALLBACK_USER,
  }
}

function persistAuthState(accessToken: string | null, refreshToken: string | null, user: AuthUser | null) {
  if (user && accessToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    }
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    return
  }

  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

function loadFromStorage() {
  try {
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    const userStr = localStorage.getItem(USER_KEY)
    const parsedUser = userStr ? (JSON.parse(userStr) as Partial<AuthUser>) : null
    const user = parsedUser
      ? {
          id: String(parsedUser.id || ''),
          email: String(parsedUser.email || ''),
          name: String(parsedUser.name || ''),
          isAdmin: Boolean(parsedUser.isAdmin),
        } satisfies AuthUser
      : null
    return { accessToken, refreshToken, user }
  } catch {
    return { accessToken: null, refreshToken: null, user: null }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const stored = E2E_AUTH_BYPASS ? getE2EAuthState() : loadFromStorage()
    return {
      ...stored,
      isLoading: E2E_AUTH_BYPASS ? false : !!stored.accessToken,
    }
  })

  // Validate existing token on mount
  useEffect(() => {
    if (E2E_AUTH_BYPASS) {
      const { accessToken, refreshToken, user } = getE2EAuthState()
      persistAuthState(accessToken, refreshToken, user)
      setState({ user, accessToken, refreshToken, isLoading: false })
      return
    }

    const stored = loadFromStorage()
    if (!stored.accessToken) {
      setState({ user: null, accessToken: null, refreshToken: null, isLoading: false })
      return
    }

    const controller = new AbortController()
    const timeoutId = window.setTimeout(() => {
      controller.abort()
    }, 8000)

    axios
      .get<AuthUser>(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${stored.accessToken}` },
        signal: controller.signal,
      })
      .then((res) => {
        setState({
          user: res.data,
          accessToken: stored.accessToken,
          refreshToken: stored.refreshToken,
          isLoading: false,
        })
      })
      .catch(() => {
        // Token invalid - clear storage
        persistAuthState(null, null, null)
        setState({ user: null, accessToken: null, refreshToken: null, isLoading: false })
      })
      .finally(() => {
        window.clearTimeout(timeoutId)
        setState((prev) => ({ ...prev, isLoading: false }))
      })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const res = await axios.post<{ accessToken: string; refreshToken: string } & AuthUser>(
      `${API_BASE}/auth/login`,
      { email, password }
    )
    const { accessToken, refreshToken, id, email: uEmail, name, isAdmin } = res.data
    const user: AuthUser = { id, email: uEmail, name, isAdmin }

    persistAuthState(accessToken, refreshToken, user)
    setState({ user, accessToken, refreshToken, isLoading: false })
  }, [])

  const register = useCallback(async (name: string, email: string, password: string) => {
    const res = await axios.post<AuthUser>(`${API_BASE}/auth/register`, {
      name,
      email,
      password,
    })
    // Auto-login after register
    await login(email, password)
  }, [login])

  const logout = useCallback(() => {
    persistAuthState(null, null, null)
    queryClient.clear() // Clear React Query cache on logout
    setState({ user: null, accessToken: null, refreshToken: null, isLoading: false })
  }, [])

  const getAccessToken = useCallback(() => state.accessToken, [state.accessToken])
  const updateUser = useCallback((patch: Partial<AuthUser>) => {
    setState((current) => {
      if (!current.user) return current

      const user = { ...current.user, ...patch }
      persistAuthState(current.accessToken, current.refreshToken, user)
      return { ...current, user }
    })
  }, [])

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, getAccessToken, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
