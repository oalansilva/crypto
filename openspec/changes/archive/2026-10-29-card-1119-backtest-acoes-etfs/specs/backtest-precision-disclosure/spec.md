## ADDED Requirements

### Requirement: Effective precision is never silent

Every individual backtest result, for every class, SHALL carry the requested precision and the effective precision. When intrabar precision is requested and the 15m intraday covers the whole window, the run SHALL use 15m intrabar precision. When the intraday is missing or does not cover the window, the whole run SHALL use the precision of the timeframe candle (daily precision on 1d) and the result SHALL say that the intraday was missing and in which stretch (dates). The title and the fact of the precision SHALL name the timeframe ("Precisão diária" only on 1d; "Precisão do candle de 4h" on 4h, and so on). An error reading the intraday SHALL be reported the same way, with the reason. When Alan turns intrabar off, the result SHALL say daily precision was chosen, without a warning. The precision of the result SHALL never fall without being shown.

#### Scenario: NVDA all history, intraday only since May 2026

- **WHEN** NVDA runs on 1d over all history with intrabar on and the 5m exists only since 19 May 2026
- **THEN** the run uses daily precision
- **AND** the result says "Precisão diária: o intradiário de 15m faltou de 11 nov. 2014 a 18 mai. 2026; o stop foi simulado no candle diário em toda a janela"

#### Scenario: SPY window covered by intraday

- **WHEN** SPY runs on 1h from 1 Aug to 22 Oct 2026 and the 15m covers the window
- **THEN** the result says "Precisão intrabar 15m"

#### Scenario: Crypto fallback becomes visible

- **WHEN** a crypto pair runs with intrabar on and its 15m does not cover the window
- **THEN** the result shows the precision of the timeframe candle and the missing stretch, instead of only a log line

#### Scenario: Crypto 4h fallback names the 4h candle

- **WHEN** BTC/USDT runs on 4h with intrabar on and its 15m does not cover the window
- **THEN** the result says "Precisão do candle de 4h" and the fact says "Candle de 4h", never "diária"

### Requirement: Conventions and limitations are listed in the result

The result page and the Otimização result SHALL list, for the execution shown: session and calendar, gap rule, costs, annualization, fraction (ação/ETF), short (when short) and the adjusted-price note (ação and ETF). The list SHALL be readable without hover. On desktop and tablet (768 px and wider) everything SHALL be open. On a phone (below 768 px) the block SHALL start collapsed: title, provenance, precision, the partial-coverage warning (when there is one) and a line of warnings of the execution SHALL stay visible, and the facts and conventions SHALL open with one tap on a button that announces its state (`aria-expanded`), keeps focus and has a target of at least 44 px (decision of Alan in Design, 23/10/2026).

#### Scenario: Conventions for an ação on desktop

- **WHEN** the NVDA result opens at 1440 px
- **THEN** session, gap, costs, annualization, fraction and adjusted prices are visible as text, with no toggle

#### Scenario: Conventions for an ação on a phone

- **WHEN** the NVDA result opens at 390 px
- **THEN** the precision and the line "Avisos: 1 saída com gap · taxa assumida · posição com fração" are visible and the facts are collapsed
- **AND** one tap on "Fatos e convenções desta execução" shows session, gap, costs, annualization, fraction and adjusted prices as text, without horizontal scroll

#### Scenario: Adjusted prices on an ETF

- **WHEN** the SPY result opens
- **THEN** the conventions include "Preços ajustados"
