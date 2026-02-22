export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8003/api";

/**
 * Build an absolute URL for an API endpoint.
 *
 * NOTE: API_BASE_URL may be relative (e.g. "/api" when using Vite dev server proxy).
 */
export function apiUrl(path: string): URL {
  const base = String(API_BASE_URL || '').trim()
  const p = String(path || '').trim()
  const endpoint = p.startsWith('/') ? `${base}${p}` : `${base}/${p}`

  return endpoint.startsWith('http')
    ? new URL(endpoint)
    : new URL(endpoint, window.location.origin)
}

// WebSocket URL derivado automaticamente do API_BASE_URL
// Converte http(s)://host:port/api para ws(s)://host:port/api
export const WS_BASE_URL = API_BASE_URL.replace(/^http/, "ws");
