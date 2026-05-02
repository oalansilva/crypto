## ADDED Requirements

### Requirement: System layout follows DESIGN.md visual tokens
The frontend UI SHALL apply a consistent system layout inspired by `DESIGN.md` across authenticated app screens, including near-black canvas surfaces, dark elevated cards, Binance-yellow primary actions, compact radii, flat hairline separation, trading green/red semantics, and a sans-serif plus financial-number typography stack.

#### Scenario: Authenticated user opens an app page
- **WHEN** an authenticated user opens any primary app route
- **THEN** the page SHALL render inside the standardized shell with the shared background, navigation, text tokens, and surface tokens

#### Scenario: Shared surfaces render consistently
- **WHEN** a page uses shared cards, muted panels, forms, tables, or buttons
- **THEN** those elements SHALL inherit the standardized token colors, radius scale, and shadow treatment

### Requirement: Trading workflow density is preserved
The frontend UI SHALL adapt `DESIGN.md` for a crypto/trading workspace without replacing workflow screens with marketing-style hero sections or decorative filler.

#### Scenario: User opens Monitor or Wallet
- **WHEN** the user opens Monitor or Wallet
- **THEN** the first viewport SHALL prioritize actionable trading data, controls, and status over explanatory or decorative content

### Requirement: Existing navigation and authorization behavior is preserved
The system layout update SHALL NOT change route behavior, admin-only menu visibility, account menu behavior, or mobile navigation accessibility.

#### Scenario: Common user opens navigation
- **WHEN** a non-admin authenticated user views the app navigation
- **THEN** admin-only entries SHALL remain hidden

#### Scenario: Mobile user opens navigation
- **WHEN** a user opens the app on a mobile viewport
- **THEN** the main menu SHALL remain reachable and usable without horizontal scrolling
