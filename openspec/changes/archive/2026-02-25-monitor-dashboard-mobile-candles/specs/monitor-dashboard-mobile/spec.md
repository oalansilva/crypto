## ADDED Requirements

### Requirement: Monitor includes a Dashboard tab (mobile-first)
The system MUST provide a mobile-first **Dashboard** tab inside the existing Monitor screen.

#### Scenario: User opens Monitor
- **WHEN** the user navigates to the Monitor screen
- **THEN** the UI renders tabs including Status and Dashboard

#### Scenario: User opens Dashboard tab
- **WHEN** the user selects the Dashboard tab
- **THEN** the UI renders a dashboard view optimized for mobile screens

#### Scenario: Dashboard list is derived from Favorites
- **WHEN** the dashboard loads
- **THEN** it shows only symbols that exist in the Favorites dataset

### Requirement: Asset type and data source follow existing rules
The system MUST reuse existing asset classification and data source rules where possible.

#### Scenario: Crypto symbols are classified by slash
- **WHEN** a favorite symbol contains `/` (e.g., `BTC/USDT`)
- **THEN** the system treats the symbol as Crypto

#### Scenario: Stock symbols are classified by no slash
- **WHEN** a favorite symbol does not contain `/` (e.g., `NVDA`)
- **THEN** the system treats the symbol as Stocks

### Requirement: Candlestick chart renders for a selected symbol
The system MUST render a candlestick chart for the selected favorite symbol.

#### Scenario: User selects a symbol
- **WHEN** the user taps a symbol card (or selects it)
- **THEN** the UI displays a candlestick chart for that symbol

### Requirement: Timeframe switching for charts
The system MUST allow switching the candlestick chart timeframe for a symbol.

#### Scenario: Switch to 15m
- **WHEN** the user selects timeframe = 15m
- **THEN** the candlestick chart updates to show 15m candles

#### Scenario: Switch to 1h
- **WHEN** the user selects timeframe = 1h
- **THEN** the candlestick chart updates to show 1h candles

#### Scenario: Switch to 4h
- **WHEN** the user selects timeframe = 4h
- **THEN** the candlestick chart updates to show 4h candles

#### Scenario: Switch to 1d
- **WHEN** the user selects timeframe = 1d
- **THEN** the candlestick chart updates to show 1d candles

### Requirement: Dashboard works on mobile without horizontal scrolling
The dashboard MUST avoid horizontal scrolling and provide touch-friendly controls.

#### Scenario: No horizontal scroll on mobile
- **WHEN** the dashboard is rendered on a small viewport
- **THEN** the main content fits the viewport width without requiring horizontal scrolling

#### Scenario: Touch targets are large enough
- **WHEN** controls (symbol selection, timeframe buttons) are rendered on mobile
- **THEN** they provide touch targets of at least 44x44px (or equivalent)
