# Tasks: Template de Sinais para Backtesting no Combo

**Card:** #65  
**change_id:** `criar-template-signals-combo-backtest`  
**Estágio:** DESIGN → DEV

---

## 1. Backend — Template e Schema

- [ ] **1.1** Criar entrada "rsi_macd_bollinger_signals" na tabela `combo_templates` (ou via seed)
- [ ] **1.2** Criar schema `SignalsBacktestRequest` em `app/schemas/combo_params.py` ou novo arquivo `app/schemas/signals_backtest.py`
- [ ] **1.3** Criar schema `SignalsBacktestResponse` com `SignalsBacktestMetrics` aninhado
- [ ] **1.4** Criar schema `Trade` com campos: entry_time, entry_price, exit_time, exit_price, exit_reason, profit_pct, profit_usd, signal_confidence, indicators

---

## 2. Backend — Serviço de Backtest

- [ ] **2.1** Criar `app/services/signals_backtest_service.py`
- [ ] **2.2** Implementar função `run_signals_backtest()`:
  - Fetch candles históricos via Binance API (mesmo padrão de `get_klines`)
  - Iterar sobre candles (exceto últimos N para lookahead prevention)
  - Chamar `_build_signal(asset, risk_profile, candles[:i])` para cada ponto
  - Se sinal = BUY, registrar entrada e simular exit por target/stop
- [ ] **2.3** Implementar `_simulate_trade_entry()` — registra entrada com price/time/confidence
- [ ] **2.4** Implementar `_simulate_trade_exit()` — detecta quando price atinge target ou stop
- [ ] **2.5** Implementar `_calculate_metrics()` — win_rate, total_profit, max_drawdown, avg_duration
- [ ] **2.6** Adicionar lock de sincronização para cache de klines (mesmo padrão existente)

---

## 3. Backend — Endpoint

- [ ] **3.1** Criar endpoint `POST /api/combos/signals-backtest` em `combo_routes.py`
- [ ] **3.2** Validar inputs: symbol (string), days (1-730), risk_profile (enum), initial_capital (>0)
- [ ] **3.3** Chamar `run_signals_backtest()` e retornar `SignalsBacktestResponse`
- [ ] **3.4** Error handling: simbolo inválido, API Binance fora, etc.
- [ ] **3.5** Adicionar header `X-Disclaimer: Isenção de responsabilidade: este não é advice financeiro.`

---

## 4. Backend — Integração Combo Existing

- [ ] **4.1** Garantir que o template "rsi_macd_bollinger_signals" aparece em `GET /api/combos/templates`
- [ ] **4.2** O template deve ser selecionável via `/combo/select` existente
- [ ] **4.3** Vincular o template ao novo endpoint ou fazer o backtest service ser chamado pelo fluxo existente

---

## 5. Frontend — Integração Configure

- [ ] **5.1** Na página `/combo/configure`, quando o template for "rsi_macd_bollinger_signals", exibir campos extras:
  - `asset` (input text, default: BTCUSDT)
  - `days` (input number, default: 365, range: 1-730)
  - `risk_profile` (select: conservative/moderate/aggressive)
  - `initial_capital` (input number, default: 100)
- [ ] **5.2** Persistir escolha de `risk_profile` em localStorage (reaproveitar padrão do Card #53)
- [ ] **5.3** Validar inputs antes de disparar backtest

---

## 6. Frontend — Integração Results

- [ ] **6.1** A página `/combo/results` já existe e suporta métricas/trades. Verificar compatibilidade com `SignalsBacktestResponse`
- [ ] **6.2** Se necessário, adaptar `ComboResultsPage` para renderizar trades de sinais (memo: mesma estrutura `trades` array)
- [ ] **6.3** Garantir que gráfico de candlestick exibe marcas de entry/exit dos trades
- [ ] **6.4** Exibir métricas principais em destaque: win_rate, total_profit_pct, max_drawdown

---

## 7. Testes

- [ ] **7.1** Testar endpoint `POST /api/combos/signals-backtest` com BTCUSDT, 365 dias, moderate (Postman/curl)
- [ ] **7.2** Verificar que trades com RSI > 38 (sell zone) não geram entradas
- [ ] **7.3** Verificar que stop_loss é respeitado (preço mínimo do candle seguinte)
- [ ] **7.4** Verificar que target_price é respeitado (primeiro candle que atinge)
- [ ] **7.5** Testar com diferentes risk_profile (conservative deve ter menos trades)
- [ ] **7.6** Snapshot test da página de results com dados de backtest

---

## 8. Documentação

- [ ] **8.1** Documentar o novo endpoint no Swagger/OpenAPI
- [ ] **8.2** Adicionar exemplo de request/response no docstring do endpoint
- [ ] **8.3** Atualizar README ou SPEC.md se existir

---

## Checklist de Ready-to-Dev

- [x] `_build_signal` em `binance_service.py` está pronto e testado (Card #53)
- [x] Sistema Combo com select/configure/results existe e funciona
- [x] Schema de backtest já definido em `combo_params.py`
- [x] UI de Results já suporta array de trades
- [x] RiskProfile enum já existe com 3 opções

---

## Prioridade de Execução

1. **Primero:** Backend (1.1 → 2.1 → 3.1) — criar template e endpoint
2. **Segundo:** Frontend (5.1) — adaptar configure para novos parâmetros
3. **Terceiro:** Testes (7.1) — validar que endpoint funciona
4. **Quarto:** Results (6.1-6.4) — garantir visualização correta

---

## Notas Técnicas

- **Lookahead bias:** Sempre chamar `_build_signal` com candles ANTES do candle atual (excluir candles futuros)
- **Stop/Target simulation:** Usar close do candle atual como entry. Para exit, verificar High/Low dos candles seguintes (não apenas close)
- **Gaps:**忽略 gaps (finais de semana para Forex) — não deve afectar lógica
- **Capital:** Cada trade usa 100% do capital disponível (simplificação — sem position sizing)
