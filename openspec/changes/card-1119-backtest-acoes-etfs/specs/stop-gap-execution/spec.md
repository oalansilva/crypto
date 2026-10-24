## ADDED Requirements

### Requirement: Stop exit uses the available price on a gap

For every class (crypto, ação, ETF) and every execution path that uses the shared exit routine (individual backtest, optimization, Combo lote, Descoberta, daily favorite refresh; daily and intrabar modes), a stop check on a candle SHALL work as follows. Long: if the candle opens at or below the stop price, the exit SHALL be at that open; otherwise, if the low reaches the stop, the exit SHALL be at the stop price. Short is the mirror: open at or above the stop exits at the open; otherwise a high that reaches the stop exits at the stop. The exit SHALL then pay the same fee and slippage as any exit. Without a gap the result SHALL be identical to today.

#### Scenario: Long gap

- **WHEN** a long position has stop 95 and the next candle opens at 90
- **THEN** the exit is at 90 with fee and slippage, not at 95
- **AND** the trade is marked as stop with gap, keeping the stop price 95 for reference

#### Scenario: Short gap

- **WHEN** a short position has stop 105 and the next candle opens at 110
- **THEN** the exit is at 110 with fee and slippage, not at 105

#### Scenario: Stop touched without gap

- **WHEN** a long position has stop 95, the candle opens at 97 and the low reaches 94
- **THEN** the exit is at 95, exactly as today

#### Scenario: Resumption after closed market

- **WHEN** an ação is held overnight or over a weekend and the first candle of the next session opens below the stop
- **THEN** the exit is at the open of that first candle

#### Scenario: Gap inside intrabar mode

- **WHEN** the run uses 15m intrabar precision and a 15m candle opens beyond the stop
- **THEN** the exit is at the open of that 15m candle

### Requirement: Gap effect is explained and measurable

The result SHALL count the stop exits with gap and SHALL show, in the trade list, the stop price and the available price for each of them. A regression check SHALL compare crypto before and after on a fixed window and sample: trades without gap SHALL be identical, and every difference SHALL be a trade with gap. The screen SHALL show only the new number, with the gap rule explained; the before/after comparison SHALL live in the demonstration evidence of the card, not in the UI (decision of Alan in Design, 23/10/2026).

#### Scenario: Crypto regression before and after

- **WHEN** BTC/USDT 1d runs on a fixed sample with the old and the new exit routine
- **THEN** the list of trades differs only where a stop candle opened beyond the stop
- **AND** total return, win rate and drawdown differ only by those trades
- **AND** the before/after table is in the demonstration evidence, while the result page shows only the new number

#### Scenario: Existing crypto favorites

- **WHEN** the daily refresh runs for an existing crypto favorite after this change
- **THEN** it uses the new exit routine and the favorite number may get worse where there was a gap
- **AND** the previous number stays in the refresh history
