## Context

Production traffic from social links enters `https://criptofarol.com.br/`, which Caddy serves from the static V4 landing directory. The previous PostHog work loaded the SDK and emitted custom funnel events, but Activity Explore checks were centered on the root URL and PostHog's standard web analytics surfaces expect `$pageview` events.

The static landings also currently point directly at `https://us.i.posthog.com` and `https://us-assets.i.posthog.com`, which can be blocked by browser extensions. PostHog recommends a reverse proxy in production when ad blocking prevents events from appearing.

## Goals / Non-Goals

**Goals:**

- Emit a standard `$pageview` for the root/static landing with sanitized URL context.
- Keep `landing_pageview` and lead funnel events for existing funnel analysis.
- Preserve the no-PII contract for analytics payloads.
- Allow runtime config to point PostHog SDK traffic to a first-party `/ingest` path.
- Add Caddy routes for `/ingest` without changing the lead API or app routes.

**Non-Goals:**

- Do not enable automatic autocapture for arbitrary clicks or inputs.
- Do not expose PostHog personal API keys or server-side secrets.
- Do not change visual landing copy/layout or lead capture UX.
- Do not publish directly to `main` without the normal release flow.

## Decisions

1. **Manual `$pageview` instead of PostHog automatic pageview**
   - Decision: keep `capture_pageview: false` and manually emit `$pageview`.
   - Rationale: manual capture lets us sanitize `$current_url` and `$pathname`, preserve UTM attribution as allowlisted properties, and avoid automatic querystring/referrer leakage.
   - Alternative considered: enable `capture_pageview: true`. Rejected because the automatic event can include URL/referrer properties before project-specific sanitization is obvious to reviewers.

2. **Configurable first-party ingest**
   - Decision: `posthog-config.js` supports `host: "/ingest"` and `ui_host: "https://us.posthog.com"`, while local fallback remains `https://us.i.posthog.com`.
   - Rationale: the same static code can run with direct PostHog in DEV or first-party proxy in production by changing only runtime config.
   - Alternative considered: hardcode `/ingest` in the landing script. Rejected because the legacy prototype paths and local previews still benefit from runtime selection.

3. **Caddy path proxy with explicit upstream hosts**
   - Decision: route `/ingest/static/*` and `/ingest/array/*` to `https://us-assets.i.posthog.com`, and route remaining `/ingest/*` to `https://us.i.posthog.com`.
   - Rationale: the SDK loads both ingest endpoints and asset/config files; both must be first-party paths to reduce blocking.

4. **Tests exercise extracted inline scripts**
   - Decision: extend the existing Node VM tests to run both static landing scripts with runtime config variations.
   - Rationale: the landings are static HTML, so focused VM tests catch event names, PII leaks, no-op behavior, and config-derived asset URLs without a browser dependency.

## Risks / Trade-offs

- **Risk:** Caddy path rewrites for PostHog assets are wrong and SDK assets return 404.
  - **Mitigation:** validate `/ingest/static/array.js` and `/ingest/array/<project-token>/config.js` return 200 after reload.
- **Risk:** `$pageview` appears but includes querystring or referrer path.
  - **Mitigation:** tests assert sanitized `$current_url`, `$pathname`, `landing_path`, and `referrer_domain` only.
- **Risk:** Existing Activity Explore filters still hide events.
  - **Mitigation:** validate network POST to `/ingest/e/` and provide event names to search directly: `$pageview`, `landing_pageview`, and funnel events.
