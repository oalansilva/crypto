/**
 * Fetch wrapper that automatically includes JWT authentication.
 */
export function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = localStorage.getItem('auth_access_token')
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return fetch(url, { ...options, headers })
}
