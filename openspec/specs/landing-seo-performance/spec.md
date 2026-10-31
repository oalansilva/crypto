# landing-seo-performance Specification

## Purpose
TBD - created by archiving change card-1160-landing-auditoria. Update Purpose after archive.
## Requirements
### Requirement: Real robots.txt, sitemap and icons
The landing domain SHALL serve a real `robots.txt` (text/plain) that points to the sitemap and keeps `/api/` and `/prototypes/` out of indexing, a real `sitemap.xml` (XML) listing `/`, `/privacidade` and `/termos`, a `favicon.ico` and an `apple-touch-icon.png`.

#### Scenario: Crawler requests robots and sitemap
- **WHEN** a client requests `https://criptofarol.com.br/robots.txt` and `/sitemap.xml`
- **THEN** each SHALL return status 200 with `text/plain` and an XML content type respectively
- **AND** neither SHALL return the SPA HTML

#### Scenario: Browser requests the icons
- **WHEN** a client requests `/favicon.ico` and `/apple-touch-icon.png`
- **THEN** each SHALL return status 200 with an image

### Requirement: Share preview and search metadata
The landing SHALL declare a title that says what the product does, a meta description with correct Portuguese accents, `canonical` to `https://criptofarol.com.br/`, Open Graph (`og:title`, `og:description`, `og:image` 1200×630, `og:url`, `og:type`, `og:locale`) and Twitter Card `summary_large_image`, and JSON-LD with `Organization` and `FAQPage` matching the visible FAQ. `/privacidade` and `/termos` SHALL declare their own title, description and canonical.

#### Scenario: Link pasted in WhatsApp
- **WHEN** the landing URL is pasted in WhatsApp or X
- **THEN** the preview SHALL show the 1200×630 image, the title and the description

#### Scenario: FAQ structured data
- **WHEN** the FAQ text changes
- **THEN** the `FAQPage` JSON-LD SHALL carry the same questions and answers as the visible FAQ

### Requirement: www redirects to the apex domain
`www.criptofarol.com.br` SHALL answer every path with a permanent redirect (301 or 308) to the same path on `https://criptofarol.com.br`.

#### Scenario: Visitor opens the www host
- **WHEN** a client requests `https://www.criptofarol.com.br/privacidade`
- **THEN** the response SHALL be a 301 or 308 to `https://criptofarol.com.br/privacidade`

### Requirement: Landing performance budget
The landing SHALL serve the hero as responsive WebP or AVIF with `srcset`, weighing at most 200 KB on a 390px phone; SHALL load at most 2 font families, served from the landing's own asset path (no third-party font host); SHALL serve its CSS, scripts and images from a landing-owned path outside `/prototypes/` with a long `Cache-Control` (at least 30 days) and a version in the URL so a new deploy is picked up; and SHALL reach Lighthouse mobile Performance ≥ 90 and SEO ≥ 95.

#### Scenario: Phone loads the landing
- **WHEN** Lighthouse mobile runs against `https://criptofarol.com.br/`
- **THEN** Performance SHALL be at least 90 and SEO at least 95
- **AND** the hero image transferred SHALL be at most 200 KB

#### Scenario: Asset paths and caching
- **WHEN** the landing HTML is inspected
- **THEN** no asset URL SHALL contain `/prototypes/` or `cripto-farol-landing/`
- **AND** static assets SHALL respond with a `Cache-Control` max-age of at least 30 days
- **AND** the HTML itself SHALL NOT be cached for long

#### Scenario: Fonts
- **WHEN** the landing loads its fonts
- **THEN** it SHALL request at most 2 font families
- **AND** every font file SHALL come from the landing's own `/lp/` path, with no request to `fonts.googleapis.com` or `fonts.gstatic.com`

### Requirement: Security headers on the landing domain
Responses from `criptofarol.com.br` SHALL carry `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, a `Referrer-Policy` and `Content-Security-Policy` with `frame-ancestors 'none'` (or `X-Frame-Options: DENY`), without breaking the landing, the PostHog first-party path, the lead form or the app.

#### Scenario: Header check
- **WHEN** a client requests `https://criptofarol.com.br/`
- **THEN** the response SHALL include HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy` and a `frame-ancestors` restriction
- **AND** the landing form, PostHog `/ingest` and `/login` SHALL keep working

