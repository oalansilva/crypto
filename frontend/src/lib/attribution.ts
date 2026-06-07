export type AttributionPayload = {
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  utm_content?: string
  utm_term?: string
  referrer?: string
  landing_path?: string
  first_seen_at?: string
}

const STORAGE_KEY = 'criptofarol_attribution'
const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'] as const

function safeReferrer(value?: string): string | undefined {
  if (!value) return undefined
  try {
    const url = new URL(value)
    return `${url.origin}${url.pathname}`.slice(0, 500)
  } catch {
    return value.split('?')[0].split('#')[0].slice(0, 500) || undefined
  }
}

function safeLandingPath(url: URL): string {
  const params = new URLSearchParams()
  for (const key of UTM_KEYS) {
    const value = url.searchParams.get(key)
    if (value) params.set(key, value)
  }
  const query = params.toString()
  return `${url.pathname}${query ? `?${query}` : ''}`.slice(0, 500)
}

function readStoredAttribution(): AttributionPayload | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as AttributionPayload
  } catch {
    return null
  }
}

export function getStoredAttribution(): AttributionPayload | null {
  if (typeof window === 'undefined') return null
  return readStoredAttribution()
}

export function captureAttributionFromUrl(now = new Date()): AttributionPayload | null {
  if (typeof window === 'undefined') return null

  const url = new URL(window.location.href)
  const params = url.searchParams
  const utms: AttributionPayload = {}

  for (const key of UTM_KEYS) {
    const value = params.get(key)
    if (value) {
      utms[key] = value.slice(0, 200)
    }
  }

  const existing = readStoredAttribution()
  if (existing) return existing

  const hasUtm = Object.keys(utms).length > 0
  const referrer = safeReferrer(document.referrer)

  if (!hasUtm && !referrer) return null

  const attribution: AttributionPayload = {
    ...utms,
    referrer,
    landing_path: safeLandingPath(url),
    first_seen_at: now.toISOString(),
  }

  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(attribution))
  } catch {
    return attribution
  }

  return attribution
}
