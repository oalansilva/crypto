## ADDED Requirements

### Requirement: Backtest direction (long or short)
The system SHALL support a backtest direction parameter allowing the user to run simulations in **long** (default, unchanged behavior) or **short** mode. In short mode, the same template entry/exit logic applies: signal 1 SHALL be interpreted as **open short**, signal -1 as **close short**. PnL, stop loss and take profit SHALL be calculated correctly for short positions (stop above entry price, take profit below entry, PnL when price falls).

#### Scenario: Run backtest in short mode with multi_ma_crossover
- **GIVEN** the user is on the Configure Backtest screen
- **AND** the user has selected template `multi_ma_crossover` and symbol BTC/USDT
- **AND** the user selects direction **short**
- **WHEN** the user runs the backtest
- **THEN** the system MUST interpret entry signals (signal 1) as open short and exit signals (signal -1) as close short
- **AND** MUST compute PnL for short (profit when exit price < entry price)
- **AND** MUST apply stop loss above entry price and take profit below entry price for short positions
- **AND** MUST return trades with `type: 'short'` and metrics consistent with short simulation

#### Scenario: Long mode remains default and unchanged
- **GIVEN** the user runs a backtest without specifying direction or with direction **long**
- **WHEN** the backtest executes
- **THEN** the system MUST behave exactly as today: signal 1 = open long, signal -1 = close long
- **AND** MUST compute PnL, stop loss and take profit as for long positions
- **AND** MUST return trades with `type: 'long'`
- **AND** no existing long-only code paths SHALL be altered for long mode

#### Scenario: Deep backtest (15m) respects direction
- **GIVEN** the user runs a backtest with direction **short** and Deep Backtest enabled
- **WHEN** the system simulates execution using 15m candles
- **THEN** stop loss for short MUST be checked when price reaches stop level **above** entry (e.g. high of candle)
- **AND** take profit for short MUST be checked when price reaches target **below** entry (e.g. low of candle)
- **AND** intraday exit logic MUST follow the same priority as long mode (stop loss before signal exit)
