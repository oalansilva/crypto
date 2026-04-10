export const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

/**
 * Build an absolute URL for an API endpoint.
 *
 * NOTE: API_BASE_URL may be relative (e.g. "/api" when using Vite dev server proxy).
 */
export function apiUrl(path: string): URL {
  const base = String(API_BASE_URL || '').trim()
  const p = String(path || '').trim()
  const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base
  const normalizedPath = p.startsWith('/') ? p : `/${p}`
  const endpoint = normalizedPath === normalizedBase || normalizedPath.startsWith(`${normalizedBase}/`)
    ? normalizedPath
    : `${normalizedBase}${normalizedPath}`

  return endpoint.startsWith('http')
    ? new URL(endpoint)
    : new URL(endpoint, window.location.origin)
}

function toWebSocketBase(base: string): string {
  if (base.startsWith('http://') || base.startsWith('https://')) {
    return base.replace(/^http/, 'ws')
  }

  const origin = window.location.origin.replace(/^http/, 'ws')
  const normalizedBase = base.startsWith('/') ? base : `/${base}`
  return `${origin}${normalizedBase}`
}

// WebSocket URL derivado automaticamente do API_BASE_URL.
export const WS_BASE_URL = toWebSocketBase(API_BASE_URL);
