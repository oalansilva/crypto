import posthog from 'posthog-js'
import type { CaptureResult } from 'posthog-js'
import type { AttributionPayload } from './attribution'

type AnalyticsProperties = Record<string, string | number | boolean | null | undefined>

type RuntimePostHogConfig = {
  key?: string
  host?: string
}

const DEFAULT_POSTHOG_HOST = 'https://us.i.posthog.com'
const SAFE_ATTRIBUTION_KEYS: Array<keyof AttributionPayload> = [
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_content',
  'utm_term',
  'landing_path',
  'first_seen_at',
]
const DENIED_AUTOMATIC_PROPERTIES = [
  '$current_url',
  '$initial_current_url',
  '$referrer',
  '$initial_referrer',
  '$referring_domain',
  '$initial_referring_domain',
  '$search_engine',
  '$search_keyword',
  '$initial_search_engine',
  '$initial_search_keyword',
]

let analyticsEnabled = false
let analyticsInitialized = false

function runtimeConfig(): RuntimePostHogConfig {
  return {
    key: import.meta.env.VITE_POSTHOG_KEY,
    host: import.meta.env.VITE_POSTHOG_HOST,
  }
}

function compactProperties(properties: AnalyticsProperties): AnalyticsProperties {
  return Object.fromEntries(
    Object.entries(properties).filter(([, value]) => value !== undefined && value !== null && value !== ''),
  )
}

function stripUrlAutomaticProperties(captureResult: CaptureResult | null): CaptureResult | null {
  if (!captureResult?.properties) return captureResult

  const properties = { ...captureResult.properties }
  for (const property of DENIED_AUTOMATIC_PROPERTIES) {
    delete properties[property]
  }

  return {
    ...captureResult,
    properties,
  }
}

export function safeAttributionProperties(attribution?: AttributionPayload | null): AnalyticsProperties {
  if (!attribution) return {}

  const properties: AnalyticsProperties = {}
  for (const key of SAFE_ATTRIBUTION_KEYS) {
    const value = attribution[key]
    if (value) properties[key] = value
  }
  if (attribution.referrer) {
    try {
      properties.referrer_domain = new URL(attribution.referrer).hostname
    } catch {
      properties.referrer_domain = attribution.referrer.split('/')[0]
    }
  }
  return properties
}

export function initAnalytics(attribution?: AttributionPayload | null): boolean {
  if (analyticsInitialized) return analyticsEnabled

  analyticsInitialized = true
  const { key, host } = runtimeConfig()
  if (!key) return false

  posthog.init(key, {
    api_host: host || DEFAULT_POSTHOG_HOST,
    capture_pageview: false,
    autocapture: false,
    before_send: stripUrlAutomaticProperties,
    persistence: 'localStorage',
    loaded: () => {
      analyticsEnabled = true
      captureAnalyticsEvent('app_initialized', safeAttributionProperties(attribution))
    },
  })

  analyticsEnabled = true
  return true
}

export function captureAnalyticsEvent(eventName: string, properties: AnalyticsProperties = {}): void {
  if (!analyticsEnabled) return

  try {
    posthog.capture(eventName, compactProperties(properties))
  } catch {
    // Analytics must never break the product flow.
  }
}

export function captureInitialPageview(attribution?: AttributionPayload | null): void {
  if (typeof window === 'undefined') return

  captureAnalyticsEvent('pageview', {
    path: window.location.pathname,
    ...safeAttributionProperties(attribution),
  })
}
