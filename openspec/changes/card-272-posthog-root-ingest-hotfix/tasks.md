## 1. Static Landing Analytics

- [x] 1.1 Add sanitized standard `$pageview` capture to the static V4 landing served at the root.
- [x] 1.2 Keep legacy/funnel events and ensure submit events remain PII-free.
- [x] 1.3 Extend runtime PostHog config handling for first-party `/ingest` plus `ui_host`.

## 2. Proxy Routing

- [x] 2.1 Add Caddy first-party PostHog routes for ingest, static SDK assets, and token config assets.
- [x] 2.2 Keep lead/API/frontend routing behavior unchanged.

## 3. Validation

- [x] 3.1 Expand focused Node tests for root/V4 and legacy static landing analytics.
- [x] 3.2 Run OpenSpec validation, focused tests, syntax checks, and frontend build.
- [x] 3.3 Validate served DEV/PROD routes after integration/restart/release as applicable.

Note: use project skills and local rules when touching OpenSpec, frontend tests, runtime routing, and release validation.
