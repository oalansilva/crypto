# Delta — opportunity-monitor — risco explícito (card #792)

## ADDED Requirements

### Requirement: Monitor card shows explicit risk for HOLD

The system SHALL display, for every HOLD opportunity visible in the Monitor board, the hierarchical risk block directly on the card without requiring opening the chart: current state (Compra/Venda via `resolveOpportunitySignal`), distância relevante, stop and alvo when the payload provides reliable top-level `opportunity.*` values (`is_holding=true` + `stop_price`/`entry_price`/`distance_to_stop_pct`), formatted in USD and % with 2 casas reusing `toDisplayValue`/`priceString` of `OpportunityCard.tsx`. The card SHALL also display the scenario sentence "se o preço cruzar X, a leitura de posição deixa de valer" only when a proven invalidation exists (`stop_price` or `signal_history` invalidation).

#### Scenario: HOLD with reliable stop/alvo shows risk without opening chart
- **WHEN** payload has `is_holding=true` and `stop_price`/`entry_price` and `distance_to_stop_pct`
- **THEN** the card shows distância + stop + alvo formatted in USD/`%` with 2 casas without opening the chart.

#### Scenario: Scenario sentence uses proven stop
- **WHEN** HOLD payload contains `signal_history[].explanation.summary` and `stop_price`
- **THEN** the frase "se cruzar X" uses the stop/invalidation from the payload.

#### Scenario: Tester can point to risk without operator
- **WHEN** tester walks only the card (roteiro #75 "contexto/histórico → risco")
- **THEN** he can point where it hurts if the reading fails without operator explanation.

### Requirement: Unavailable data is explicit on the card

When a risk field has no reliable data (null/undefined/stale), the card SHALL display exactly `indisponível — dado não confiável` for that field. The UI SHALL never hide the field silently nor invent a placeholder or reuse a number from another timeframe.

#### Scenario: Missing or stale risk field shows indisponível
- **WHEN** card renders with null/undefined/stale risk data
- **THEN** the field shows `indisponível — dado não confiável` — not omitted nor invented.

#### Scenario: No cross-timeframe backfill
- **WHEN** required field is absent for the strategy timeframe
- **THEN** the UI does not backfill with a value from another timeframe.

### Requirement: EXIT hides operable Entry/Stop and shows residual risk

When `resolveOpportunitySignal` resolves to EXIT, the Monitor card SHALL NOT show Entry/Stop as operable values. It SHALL show `posição encerrada segundo a estratégia — sem risco residual mapeado` when `signal_history` is empty, or the residual risk when history exists. Chart modal coherence SHALL match the card for the same payload.

#### Scenario: EXIT with empty signal history hides Entry/Stop
- **WHEN** card renders in EXIT and `signal_history` is empty
- **THEN** Entry/Stop do not appear as operable and the message `posição encerrada segundo a estratégia — sem risco residual mapeado` is explicit.

#### Scenario: EXIT with residual risk shows it
- **WHEN** EXIT has `signal_history` with residual risk
- **THEN** the card shows that residual risk instead of the empty-state message and does not treat old Entry/Stop as actionable.

### Requirement: Protected strategy risk stays public-safe

When `is_strategy_protected=true`, the card SHALL NOT expose `parameters` nor `indicator_values` secrets for any viewer except admin or explicit transparency. Risk display SHALL use only top-level public derived fields (`stop_price`/`entry_price`/`distance_to_stop_pct`). Common user and admin views both respect this rule.

#### Scenario: Protected strategy does not leak secrets in risk block
- **WHEN** `is_strategy_protected=true` and a common user views HOLD
- **THEN** risk shows only top-level `stop_price`/`entry_price` — not `parameters`/`indicator_values`.

### Requirement: Badge uses Compra/Venda via resolveOpportunitySignal

The badge text on the Monitor card SHALL be `Compra`/`Venda` derived from `resolveOpportunitySignal` (hold→Compra, exit→Venda, short direction inverts per existing visual mapping), consistent between card and chart modal.

#### Scenario: Badge text matches resolved signal
- **WHEN** card renders any opportunity
- **THEN** badge shows `Compra` for hold and `Venda` for exit via `resolveOpportunitySignal`.
