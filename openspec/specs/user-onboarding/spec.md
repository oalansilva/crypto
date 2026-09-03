# user-onboarding Specification

## Purpose
TBD - created by archiving change card-222-onboarding. Update Purpose after archive.
## Requirements
### Requirement: First-use onboarding prompt
The authenticated app SHALL show new users a concise onboarding prompt that explains where to start and how to continue the core beta journey. The prompt (component `OnboardingGuide`) SHALL keep the journey Favoritos → Monitor → carteira opcional, SHALL NOT name comprar / stop / vender, and SHALL NOT claim that the Farol never sends orders nor that the connection is read-only-only.

#### Scenario: New user opens the app
- **Given** utilizador autenticado sem dispensar onboarding (critério 5)
- **WHEN** an authenticated user opens a protected route without dismissing onboarding in the current browser
- **THEN** the app SHALL show a concise first-use guide with the recommended starting path
- **AND** the guide SHALL present Favorites as the first step
- **AND** the guide SHALL provide direct actions to open Help and Favorites

#### Scenario: User dismisses first-use guide
- **Given** utilizador com guia visível (critério 5)
- **WHEN** the user dismisses the first-use guide
- **THEN** the guide SHALL stop appearing in that browser session/storage
- **AND** Help SHALL remain accessible from navigation

#### Scenario: OnboardingGuide does not name Operar and does not lie — check negativo Q7=B
- **Given** `OnboardingGuide` (primeiro uso e embutido em `/help`) em leitura (critério 5)
- **WHEN** a tester reads `OnboardingGuide` (first use and embedded in `/help`)
- **THEN** the journey SHALL remain Favoritos → Selecionar estratégias → Monitor → Carteira Binance opcional (not a prerequisite)
- **AND** the content SHALL NOT name comprar / stop / vender, nem Spot, nem Operar
- **AND** the content SHALL NOT say “nunca envia ordem”, “nunca movimenta dinheiro e nunca envia ordem”, “API apenas para consulta”, “somente leitura” or “só consulta” as absolute product truth
- **AND** the guardrail SHALL remain apoio à decisão without profit promises

### Requirement: Help center explains the recommended beta journey
The app SHALL provide a Help route (`/help`) that explains the recommended order of the main screens in simple Portuguese. The Help content outside the `OnboardingGuide` block (header intro, usage grid, quick actions) SHALL admit comprar / stop / vender Spot **no Farol** (opcional; nunca saque; não é bot) and SHALL correct “saldos read-only” as the only truth.

#### Scenario: User opens Help
- **Given** utilizador autenticado abre `/help` (critério 4)
- **WHEN** an authenticated user opens `/help`
- **THEN** the app SHALL explain the recommended order: Favoritos, selecao de estrategias, Monitor, and optional Binance wallet setup
- **AND** the page SHALL provide direct navigation actions for the core screens
- **AND** wallet setup SHALL NOT be presented as a prerequisite to start

#### Scenario: User reads responsible positioning
- **Given** utilizador lê onboarding ou Help (critério 4)
- **WHEN** the user reads onboarding or Help content
- **THEN** the content SHALL frame Cripto Farol as apoio a decisao
- **AND** the content SHALL NOT promise profit, present signals as guaranteed calls, encourage leverage, or use guru-style claims

#### Scenario: Help outside OnboardingGuide admits Spot and corrects read-only — Q6=A
- **Given** `/help` fora do `OnboardingGuide` em leitura (critério 4)
- **WHEN** a tester reads `/help` outside the `OnboardingGuide` block (help-usage-grid Carteira, header intro, guardrail)
- **THEN** the Carteira section SHALL NOT say “saldos read-only” as the only wallet truth
- **AND** it SHALL explain leitura para Home/Carteira e, com permissão Spot Trade (sem saque) opcional, possibilidade de comprar / stop / vender Spot **no Farol** após confirmação (nunca saque; não é bot 24/7)
- **AND** the intro SHALL reflect the same optional Spot distinction if it mentions carteira
- **AND** the page SHALL NOT claim the Farol never sends orders

#### Scenario: Help/Onboarding boundary is respected
- **Given** `/help` com `OnboardingGuide` embutido (critérios 4 e 5)
- **WHEN** `/help` is rendered with embedded `OnboardingGuide`
- **THEN** the `OnboardingGuide` component SHALL still satisfy the Q7=B negative check (no Operar naming, no lie)
- **AND** the surrounding Help grid/intro SHALL satisfy Q6=A (Spot admission), without contaminating the guide itself

### Requirement: Onboarding remains responsive
The onboarding prompt and Help route SHALL be usable on desktop and mobile without broken text, overlap, or horizontal scrolling.

#### Scenario: Mobile user opens Help
- **WHEN** the Help route is viewed on a mobile viewport
- **THEN** the guide content SHALL reflow into a single-column layout
- **AND** primary actions SHALL remain visible and tappable without horizontal scrolling

### Requirement: No ensaio flag and no issue contamination
The change SHALL NOT introduce flag/toggle/indicador de ensaio nem absorver issues #463/#637/#692, mantendo copy-only e P0 no-go sem irmã (critérios 6 e 7).

#### Scenario: No ensaio flag — critério 6
- **Given** Entra deste card em auditoria (critério 6)
- **WHEN** se procura flag/toggle/indicador Ensaio vs Mercado real, fail-closed, token de ensaio
- **THEN** não há flag, toggle, fail-closed de submit/place/cancel, indicador de modo, nem token de ensaio

#### Scenario: No contamination #463/#637/#692 — critério 7
- **Given** board com #463/#637/#692 como issues próprias (critério 7)
- **WHEN** este card fecha
- **THEN** #463, #637, #692 continuam issues próprias, sem arquivos deles alterados por este card

