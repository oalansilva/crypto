## Why

The published landing at `https://criptofarol.com.br/` loads PostHog, but validation showed Alan was checking Activity Explore for the root URL and the current implementation only emits custom funnel events. We need the root landing to emit a standard sanitized `$pageview` and support first-party ingest so PostHog activity is visible and less likely to be blocked.

## What Changes

- Emit a standard `$pageview` event from the static landing root while keeping the existing `landing_pageview` funnel event.
- Sanitize URL/referrer properties so pageview analytics does not include querystrings, tokens, free-text form data, or PII.
- Extend runtime PostHog config to support first-party `/ingest` routing with the correct PostHog UI host.
- Add Caddy routing for first-party PostHog ingest/assets under the Cripto Farol domain.
- Add focused Node tests for root/V4 and legacy static landing analytics behavior.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `product-analytics`: Root/static landing analytics must include a standard sanitized `$pageview` event and support first-party PostHog proxy routing.

## Impact

- Static landing files under `frontend/public/prototypes/cripto-farol-landing-v4/` and `frontend/public/prototypes/cripto-farol-landing/`.
- Runtime PostHog config files under `frontend/public/` and prototype folders.
- Frontend analytics tests under `frontend/tests/`.
- Caddy production/dev routing in `/etc/caddy/Caddyfile` and the versioned operational evidence for this card.
