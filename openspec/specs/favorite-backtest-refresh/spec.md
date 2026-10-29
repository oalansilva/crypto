# favorite-backtest-refresh Specification

## Purpose
TBD - created by archiving change card-219-favorite-backtests-refresh. Update Purpose after archive.
## Requirements
### Requirement: Favorite backtests refresh automatically
The system SHALL refresh due favorited backtests through an internal backend routine without requiring user interaction.

#### Scenario: Daily refresh runs for due favorites
- **WHEN** the backend worker starts the favorite refresh routine
- **THEN** it SHALL select favorites that never completed a refresh or completed before the configured refresh interval
- **AND** it SHALL fetch and refresh the market data required by the favorite timeframe before recalculating the backtest
- **AND** for crypto deep backtests it SHALL prepare the required intraday candles before recalculating the backtest
- **AND** it SHALL rerun each due favorite using the saved symbol, timeframe, strategy, direction, period start, and fixed parameter ranges
- **AND** it SHALL persist refreshed metrics, trades, candles, and indicator context on the favorite

#### Scenario: One favorite refresh fails
- **WHEN** one favorite refresh raises an error
- **THEN** the routine SHALL persist failure status and error for that favorite
- **AND** it SHALL continue processing other due favorites
- **AND** it SHALL preserve the favorite's previous metrics

#### Scenario: Favorite refresh returns stale market data
- **WHEN** a favorite refresh completes its calculation but the newest returned candle is older than the tolerated freshness window for the favorite timeframe
- **THEN** the routine SHALL persist failure status and error for that favorite
- **AND** it SHALL preserve the favorite's previous metrics instead of marking stale results as refreshed

### Requirement: Favorite refresh attempts are auditable
The system SHALL record refresh attempts in both the favorite row and `auto_backtest_runs`.

#### Scenario: Refresh succeeds
- **WHEN** a favorite refresh completes successfully
- **THEN** the favorite SHALL store success status, start timestamp, completion timestamp, and run id
- **AND** `auto_backtest_runs` SHALL store a successful run linked to the favorite

#### Scenario: Refresh fails
- **WHEN** a favorite refresh fails
- **THEN** the favorite SHALL store failed status, start timestamp, completion timestamp, run id, and error message
- **AND** `auto_backtest_runs` SHALL store a failed run linked to the favorite

### Requirement: Refresh routine is internal
The system SHALL run favorite refresh from the backend worker and SHALL NOT expose it as a user-facing OpenClaw workflow.

#### Scenario: Runtime worker is enabled
- **WHEN** `RUN_FAVORITE_BACKTEST_REFRESH` is enabled
- **THEN** the backend worker SHALL start the favorite refresh loop
- **AND** shutdown SHALL stop the loop cleanly

### Requirement: Favorite refresh respects CPU guardrails
The system SHALL throttle the automatic favorite refresh routine so it does not continue starting refresh work while host CPU usage is above the configured ceiling, defaulting to 60 percent.

#### Scenario: CPU is above ceiling before next favorite
- **WHEN** the favorite refresh routine is about to start another due favorite
- **AND** measured CPU usage is above the configured ceiling
- **THEN** it SHALL pause or skip starting that favorite during the current cycle
- **AND** it SHALL record the CPU guard as the reason work was paused or skipped
- **AND** it SHALL keep already refreshed favorites committed

#### Scenario: CPU stays below ceiling
- **WHEN** measured CPU usage is at or below the configured ceiling
- **THEN** the routine SHALL continue processing due favorites up to the configured batch limit

### Requirement: Favorite refresh runs as a daily bounded cycle
The system SHALL run automatic favorite refresh as a bounded background cycle configured to attempt due favorites at least once per day while respecting batch limits and pauses.

#### Scenario: Runtime stack starts
- **WHEN** the standard crypto stack start script runs without explicit overrides
- **THEN** it SHALL enable the runtime worker and favorite refresh routine by default
- **AND** it SHALL keep a daily refresh interval by default
- **AND** it SHALL run the refresh loop more frequently than once per day so bounded batches can cover the due queue
- **AND** it SHALL use a bounded per-cycle favorite limit by default

#### Scenario: More favorites are due than the batch limit
- **WHEN** due favorites exceed the configured per-cycle limit
- **THEN** the routine SHALL process at most the configured number in that cycle
- **AND** it SHALL leave the remaining favorites due for later cycles

### Requirement: Favorite refresh runtime state is observable
The system SHALL expose safe operational state for the automatic favorite refresh routine through backend runtime status.

#### Scenario: Runtime status is requested
- **WHEN** `/api/runtime/status` is requested
- **THEN** the response SHALL include whether favorite refresh is enabled
- **AND** it SHALL include sanitized latest-cycle state including due, success, failed, skipped, CPU threshold, and reason when available

#### Scenario: Refresh cycle completes or pauses
- **WHEN** a favorite refresh cycle completes or stops because of CPU guardrails
- **THEN** the system SHALL update the latest-cycle state before waiting for the next cycle

### Requirement: Refresh of a new post-70/30 favorite uses the complete stored period

Automatic and manual refresh of a favorite **created after this card** following 70/30 SHALL rerun on the complete chosen period persisted on that favorite. For period «todo» the refresh SHALL pull through today. The routine SHALL NOT substitute the Discovery training window for that favorite. Favorites already stored with a training window SHALL keep being refreshed on their stored start/end until someone saves them again.

#### Scenario: New todo favorite refresh extends to now

- **WHEN** the refresh routine (or the operator's revalidate) runs for a new «todo» favorite created after 70/30
- **THEN** the run uses first candle → now
- **AND** the list status/period after refresh still show the complete period, not 17/08/2017 → 24/12/2023

#### Scenario: Legacy training favorite refresh unchanged

- **WHEN** the refresh routine runs for a favorite still stored with 17/08/2017 → 24/12/2023
- **THEN** it SHALL keep that window
- **AND** it SHALL NOT silently expand to all-history in this card

### Requirement: Next favorite refresh uses the slippage table

When a favorite is next refreshed by the existing automatic routine, the recalculation SHALL apply `backtest-slippage-by-timeframe` for that favorite's timeframe. This change SHALL NOT enqueue an immediate full recálculo of all favorites.

#### Scenario: Due 4h favorite refresh uses 0,02% slippage

- **WHEN** a due 4h favorite is refreshed by the normal worker
- **THEN** the backtest applies 0,02% slippage per side and 0,075% fee
- **AND** this card does not start a one-shot refresh of every favorite

#### Scenario: Due 1h favorite refresh uses 0,03% slippage

- **WHEN** a due 1h favorite is refreshed by the normal worker
- **THEN** the backtest applies 0,03% slippage per side

### Requirement: Atualização de ação e ETF pelo calendário
A atualização diária de favorito de ação ou ETF SHALL medir o frescor pelo calendário da classe (`market-session-awareness`), não pelo tempo corrido. O dado está fresco quando o último candle fechado esperado pelo calendário está presente. Fim de semana, feriado e horário fora do pregão MUST NOT gerar "Falha na atualização". Quando nenhum candle fechou desde a última atualização, o ciclo MUST pular a reexecução e manter o status de sucesso. A cripto MUST manter as regras de hoje.

#### Scenario: Refresh de NVDA 1h no domingo
- **WHEN** a atualização roda no domingo para um favorito NVDA 1h, com o último bloco fechado na sexta
- **THEN** o favorito MUST continuar "Backtest atualizado", sem falha

#### Scenario: Atraso real na atualização
- **WHEN** a atualização roda na terça e falta o pregão de segunda de NVDA
- **THEN** o favorito MUST ficar "Falha na atualização", com o motivo do atraso

### Requirement: Intradiário e precisão de ação e ETF na atualização
A atualização de favorito de ação ou ETF da Binance SHALL coletar a série do tempo gráfico e o 5m do intrabar pelo caminho do #1118 (`prepare_equity_history` com intrabar). Ela MUST rodar com precisão diária, marcada em `analysis_execution`, quando não houver 15m que cubra a janela, como no lote. A falta de 15m MUST NOT ser falha.

#### Scenario: NVDA em todo o histórico
- **WHEN** a atualização de NVDA 1d em todo o histórico roda
- **THEN** o favorito MUST ficar atualizado com "Precisão diária · sem 15m de …" no trecho sem 5m

### Requirement: Aguardando dados e período operacional no último pregão
Quando a série tem menos candles fechados do que a análise precisa, a atualização SHALL gravar o status `INSUFFICIENT`, com a contagem disponível e a necessária. Favoritos MUST mostrar "Aguardando dados: N de M candles", em cinza, e não "Falha". No favorito com período operacional "todo o histórico", o fim do período de ação e ETF MUST ser a data do último pregão fechado, não a data de hoje. A busca do primeiro candle MUST usar a fonte do favorito.

#### Scenario: Ticker novo
- **WHEN** um favorito de um ticker com 40 pregões precisa de 200 candles
- **THEN** a atualização MUST gravar `INSUFFICIENT` "40 de 200 candles", sem falha

#### Scenario: Fim do período no sábado
- **WHEN** a atualização de NVDA com período "todo o histórico" roda no sábado, 24 out. 2026
- **THEN** o fim do período MUST ser 23 out. 2026

### Requirement: Status de atualização mostra o último pregão
Para ação e ETF, o status de sucesso em Favoritos SHALL ser "Backtest atualizado: <data e hora> · último pregão <data>".

#### Scenario: Linha de NVDA
- **WHEN** a atualização de NVDA terminou no sábado às 08:12, com o último pregão em 23 out.
- **THEN** a linha MUST mostrar "Backtest atualizado: 24/10, 08:12 · último pregão 23/10"

