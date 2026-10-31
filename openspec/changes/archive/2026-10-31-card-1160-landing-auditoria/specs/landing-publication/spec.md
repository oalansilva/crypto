## ADDED Requirements

### Requirement: Production landing lives in its own repository
The production landing (HTML, CSS, scripts, images, legal pages, `robots.txt`, `sitemap.xml`, icons) SHALL live in the repository `oalansilva/cripto-farol-landing`, branch `main`. The `crypto` repository SHALL keep only prototypes under `frontend/public/prototypes/` and SHALL NOT be the source of the published landing. Lead submission SHALL keep going to the `crypto` backend (`/api/leads`).

#### Scenario: Source of the published landing
- **WHEN** someone looks for the files served at `https://criptofarol.com.br/`
- **THEN** they SHALL come from a checkout of `oalansilva/cripto-farol-landing`
- **AND** `frontend/public/prototypes/` in `crypto` SHALL NOT contain `cripto-farol-landing-v4/` or landing assets used in production

#### Scenario: Lead endpoint stays in crypto
- **WHEN** the landing posts a lead
- **THEN** the request SHALL go to the relative `/api/leads` path, served by the `crypto` backend

### Requirement: Landing deploy and rollback are independent from the crypto release
Publishing the landing SHALL be a deploy of a commit of `oalansilva/cripto-farol-landing` `main` into the PROD landing checkout, without a `crypto` release. Each deploy SHALL record the published commit, and rollback SHALL republish the previous commit. The deploy SHALL write the runtime PostHog configuration outside git.

#### Scenario: Landing-only change
- **WHEN** only landing copy changes
- **THEN** it SHALL be published by the landing deploy alone, without a `crypto` release or restart

#### Scenario: Rollback
- **WHEN** a landing deploy breaks the page
- **THEN** republishing the previous recorded commit SHALL restore the previous page

#### Scenario: Rollback target exists from the first deploy
- **WHEN** the landing repository receives this change
- **THEN** its first commit on the new structure SHALL be the live v4 page without this card's changes, with production asset paths
- **AND** publishing that commit SHALL restore the page as it was before this card, against either the old or the new lead backend

### Requirement: DEV shows the landing under test before production
DEV SHALL serve a checkout of the landing branch under test on its own host, with the same root paths as production (`/`, `/privacidade`, `/termos`, `/robots.txt`, `/sitemap.xml`, icons, landing assets) and with `/api/leads` going to the DEV backend, so QA and homologation see the new landing before PROD. The DEV landing SHALL NOT be indexed.

#### Scenario: QA opens the DEV landing
- **WHEN** QA opens the DEV landing host
- **THEN** it SHALL see the landing from the branch under test, with working legal pages and form against the DEV backend
- **AND** the responses SHALL carry `X-Robots-Tag: noindex`

### Requirement: Old landing asset paths keep working during the cut
After the cut, requests to the old asset paths (`/cripto-farol-landing/assets/*`, `/prototypes/cripto-farol-landing-v4/assets/*`) SHALL be permanently redirected to the new landing asset path for at least one release, and `/prototypes/cripto-farol-landing-v4/` SHALL keep redirecting to `/`.

#### Scenario: Old share preview image
- **WHEN** a client requests `/cripto-farol-landing/assets/hero/cripto-farol-hero.png` after the cut
- **THEN** the response SHALL be a permanent redirect to the landing's own hero asset

### Requirement: The production cut keeps every lead and can be reversed phase by phase
The move of the production landing to its own repository SHALL happen in ordered phases, each verified before the next and each with its own rollback, so that no lead submission is rejected or loses fields during the cut. The page served at any moment SHALL only post to a lead path that understands its payload. The `crypto` removals (v4 page, old landing assets, the Node lead service, the seat counter endpoint) SHALL only be deployed after the new landing is live and verified.

#### Scenario: Visitor submits the form during the cut
- **WHEN** a visitor submits the landing form at any phase of the cut
- **THEN** the lead SHALL be stored with every field the form sent
- **AND** the visitor SHALL NOT see a failure caused by the cut

#### Scenario: Verification posts run against the new backend
- **WHEN** the operator posts a test lead to verify the cut
- **THEN** the post SHALL run only after the new lead backend is deployed
- **AND** it SHALL confirm the lead is stored and Alan is notified

#### Scenario: A phase fails
- **WHEN** a phase of the cut fails its verification
- **THEN** that phase's documented rollback SHALL restore the previous working state without reverting earlier phases
