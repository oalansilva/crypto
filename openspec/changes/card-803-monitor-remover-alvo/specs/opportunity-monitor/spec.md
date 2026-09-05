# Delta — opportunity-monitor — remover alvo derivado (card #803)

## MODIFIED Requirements

### Requirement: Monitor card shows explicit risk for HOLD

The system SHALL display, for every HOLD opportunity visible in the Monitor board, the hierarchical risk block directly on the card without requiring opening the chart: current state (Compra/Venda via `resolveOpportunitySignal`), distância relevante, stop, entrada and preço atual when the payload provides reliable top-level `opportunity.*` values (`is_holding=true` + `stop_price`/`entry_price`/`distance_to_stop_pct`), formatted in USD and % with 2 casas reusing `toDisplayValue`/`priceString` of `OpportunityCard.tsx`. Visible HOLD order SHALL be `distância até saída` → `distância até stop` → `stop` → `entrada` → `preço atual`. The card and the chart modal risk panel SHALL use the same recorte and order for the same payload. The UI SHALL NOT display label or value `alvo` / `Alvo`, SHALL NOT derive a take-profit-like price (`last_price * (1 ± dist/100)` or equivalent), and SHALL NOT keep a hidden, tooltip, or renamed equivalent. The card SHALL also display the scenario sentence "se o preço cruzar X, a leitura de posição deixa de valer" only when a proven invalidation exists (`stop_price` or `signal_history` invalidation).

#### Scenario: HOLD with reliable stop shows risk without opening chart
- **WHEN** payload has `is_holding=true` and `stop_price`/`entry_price` and `distance_to_stop_pct`
- **THEN** the card shows `distância até saída`, `distância até stop`, `stop`, `entrada` and `preço atual` in that order, formatted in USD/`%` with 2 casas, without opening the chart
- **AND** the card SHALL NOT show rótulo or valor `alvo`

#### Scenario: Chart modal matches HOLD card without alvo
- **WHEN** the trader opens the Monitor chart modal for the same HOLD payload
- **THEN** the modal risk block uses the same order and recorte as the card
- **AND** SHALL NOT show `alvo` / `Alvo` or a derived alvo price

#### Scenario: Scenario sentence uses proven stop
- **WHEN** HOLD payload contains `signal_history[].explanation.summary` and `stop_price`
- **THEN** the frase "se cruzar X" uses the stop/invalidation from the payload.

#### Scenario: Tester can point to risk without operator
- **WHEN** tester walks only the card (roteiro #75 "contexto/histórico → risco")
- **THEN** he can point where it hurts if the reading fails without operator explanation.

### Requirement: Unavailable data is explicit on the card

When a risk field has no reliable data (null/undefined/stale), the card SHALL display exactly `indisponível — dado não confiável` for that field. The UI SHALL never hide the field silently nor invent a placeholder or reuse a number from another timeframe. HOLD SHALL NOT add an `alvo` line when data is stale (no "alvo indisponível").

#### Scenario: Missing or stale risk field shows indisponível
- **WHEN** card renders with null/undefined/stale risk data
- **THEN** the field shows `indisponível — dado não confiável` — not omitted nor invented.

#### Scenario: No cross-timeframe backfill
- **WHEN** required field is absent for the strategy timeframe
- **THEN** the UI does not backfill with a value from another timeframe.

#### Scenario: Stale HOLD has no alvo line
- **WHEN** HOLD card or modal renders with null/undefined/stale risk data
- **THEN** affected fields show `indisponível — dado não confiável`
- **AND** there is no `alvo` line, including no "alvo indisponível"

### Requirement: EXIT hides operable Entry/Stop and shows residual risk

When `resolveOpportunitySignal` resolves to EXIT, the Monitor card SHALL NOT show Entry/Stop as operable values. It SHALL show `posição encerrada segundo a estratégia — sem risco residual mapeado` when `signal_history` is empty, or the residual risk when history exists. Chart modal coherence SHALL match the card for the same payload. EXIT SHALL NOT show `alvo`.

#### Scenario: EXIT with empty signal history hides Entry/Stop
- **WHEN** card renders in EXIT and `signal_history` is empty
- **THEN** Entry/Stop do not appear as operable and the message `posição encerrada segundo a estratégia — sem risco residual mapeado` is explicit.

#### Scenario: EXIT with residual risk shows it
- **WHEN** EXIT has `signal_history` with residual risk
- **THEN** the card shows that residual risk instead of the empty-state message and does not treat old Entry/Stop as actionable.

#### Scenario: EXIT does not show alvo
- **WHEN** card or modal renders in EXIT
- **THEN** `alvo` does not appear
- **AND** `preço atual` and the bloco `Risco residual` remain
