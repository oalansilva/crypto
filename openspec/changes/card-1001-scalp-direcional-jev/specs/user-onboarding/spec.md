## MODIFIED Requirements

### Requirement: Help center explains the recommended beta journey

The app SHALL provide a Help route (`/help`) that explains the recommended order of the main screens in simple Portuguese. The Help content outside the `OnboardingGuide` block (header intro, usage grid, quick actions) SHALL admit comprar / stop / vender Spot **no Farol** no Operar (opcional; nunca saque; confirmação por clique) and the optional directional BTCUSDT scalp on the Monitor (default off; while on, post-only without per-order confirmation; never saque). It SHALL correct “saldos read-only” as the only truth. It SHALL NOT say «nao e bot» / «não é bot 24/7» as an absolute.

#### Scenario: User opens Help

- **Given** utilizador autenticado abre `/help`
- **WHEN** an authenticated user opens `/help`
- **THEN** the app SHALL explain the recommended order: Favoritos, selecao de estrategias, Monitor, and optional Binance wallet setup
- **AND** the page SHALL provide direct navigation actions for the core screens
- **AND** wallet setup SHALL NOT be presented as a prerequisite to start

#### Scenario: User reads responsible positioning

- **Given** utilizador lê onboarding ou Help
- **WHEN** the user reads onboarding or Help content
- **THEN** the content SHALL frame Cripto Farol as apoio a decisao
- **AND** the content SHALL NOT promise profit, present signals as guaranteed calls, encourage leverage, or use guru-style claims

#### Scenario: Help outside OnboardingGuide admits Spot, Operar confirmation, and optional scalp

- **Given** `/help` fora do `OnboardingGuide` em leitura
- **WHEN** a tester reads `/help` outside the `OnboardingGuide` block (help-usage-grid Carteira, header intro, guardrail)
- **THEN** the Carteira section SHALL NOT say “saldos read-only” as the only wallet truth
- **AND** it SHALL explain leitura para Home/Carteira e, com permissão Spot Trade (sem saque) opcional, possibilidade de comprar / stop / vender Spot **no Farol** após confirmação no Operar (nunca saque)
- **AND** it SHALL admit the optional Monitor scalp (default off; never saque)
- **AND** it SHALL NOT say «nao e bot» or «não é bot 24/7» as an absolute
- **AND** the intro SHALL reflect the same optional Spot distinction if it mentions carteira
- **AND** the page SHALL NOT claim the Farol never sends orders

#### Scenario: Help/Onboarding boundary is respected

- **Given** `/help` com `OnboardingGuide` embutido
- **WHEN** `/help` is rendered with embedded `OnboardingGuide`
- **THEN** the `OnboardingGuide` component SHALL still satisfy the Q7=B negative check (no Operar naming, no lie)
- **AND** the surrounding Help grid/intro SHALL satisfy Spot admission and the optional-scalp admission, without contaminating the guide itself
