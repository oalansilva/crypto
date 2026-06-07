## Purpose

Keep the landing lead capture endpoint compatible with production subdomains and local previews.

## MODIFIED Requirements

### Requirement: Landing lead endpoint works on production subdomains
The landing page SHALL post lead capture requests through the relative `/api/leads` path on production domain variants.

#### Scenario: Visitor opens a production subdomain
- **WHEN** a visitor opens the landing page on `criptofarol.com.br` or any hostname ending in `.criptofarol.com.br`
- **THEN** the lead form SHALL use `/api/leads`
- **AND** it SHALL NOT target the development `:5174` lead endpoint

#### Scenario: Developer opens local preview
- **WHEN** a developer opens the landing page outside the `criptofarol.com.br` domain family
- **THEN** the lead form SHALL keep using the same host with port `5174` for the local lead endpoint
