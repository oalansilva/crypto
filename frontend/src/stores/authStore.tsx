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
}

const AuthContext = createContext<AuthContextValue | null>(null)

const ACCESS_TOKEN_KEY = 'auth_access_token'
const REFRESH_TOKEN_KEY = 'auth_refresh_token'
const USER_KEY = 'auth_user'

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
    const stored = loadFromStorage()
    return {
      ...stored,
      isLoading: !!stored.accessToken,
    }
  })

  // Validate existing token on mount
  useEffect(() => {
    const stored = loadFromStorage()
    if (!stored.accessToken) {
      setState({ user: null, accessToken: null, refreshToken: null, isLoading: false })
      return
    }

    axios
      .get<AuthUser>(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${stored.accessToken}` },
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
        localStorage.removeItem(ACCESS_TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
        setState({ user: null, accessToken: null, refreshToken: null, isLoading: false })
      })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const res = await axios.post<{ accessToken: string; refreshToken: string } & AuthUser>(
      `${API_BASE}/auth/login`,
      { email, password }
    )
    const { accessToken, refreshToken, id, email: uEmail, name, isAdmin } = res.data
    const user: AuthUser = { id, email: uEmail, name, isAdmin }

    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    localStorage.setItem(USER_KEY, JSON.stringify(user))

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
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    queryClient.clear() // Clear React Query cache on logout
    setState({ user: null, accessToken: null, refreshToken: null, isLoading: false })
  }, [])

  const getAccessToken = useCallback(() => state.accessToken, [state.accessToken])

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, getAccessToken }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
