# Tasks: Sinais de Trading BUY/SELL/HOLD

**Card:** #53  
**change_id:** `sinais-de-trading-buy-sell-hold`  
**Estágio:** DESIGN → DEV

---

## 1. Backend — API de Sinais

- [x] **1.1** Criar schema `Signal` no Pydantic (SignalType, ConfidenceGauge, SignalResponse)
- [x] **1.2** Criar endpoint `GET /signals` com params: type, confidence_min, asset, risk_profile, limit
- [x] **1.3** Criar endpoint `GET /signals/{id}` retornando sinal individual
- [x] **1.4** Criar endpoint `GET /signals/latest` retornando últimos 5 sinais (confidence ≥70%)
- [x] **1.5** Implementar cache in-memory (dict c/ TTL 5 min) para resultados de Binance
- [x] **1.6** Integrar chamada Binance API (OHLCV) com error handling e rate limit backoff
- [x] **1.7** Integrar chamada ao modelo LSTM+RandomForest (mock/Card #55) para gerar sinais
- [x] **1.8** Adicionar header `X-Disclaimer: Isenção de responsabilidade: este não é advice financeiro.` em todas as respostas de sinais
- [x] **1.9** Documentar rotas no Swagger/OpenAPI (FastAPI auto)

---

## 2. Frontend — SignalCard Component

- [x] **2.1** Criar componente `SignalCard` com props: type, asset, confidence, target_price, stop_loss, indicators, created_at
- [x] **2.2** Implementar badge colorido por tipo (BUY=verde, SELL=vermelho, HOLD=cinza)
- [x] **2.3** Criar componente `ConfidenceGauge` (barra 0–100%, threshold 70%, cor dinâmica)
- [x] **2.4** Adicionar estados: default, hover, loading (skeleton), error
- [x] **2.5** Implementar responsividade (3 cols desktop, 2 tablet, 1 mobile)

---

## 3. Frontend — Lista e Filtros

- [x] **3.1** Criar página `/signals` (ou seção em dashboard)
- [x] **3.2** Implementar `RiskProfileSelector` (3 toggles: Conservative/Moderate/Aggressive) com persistência em localStorage
- [x] **3.3** Implementar `FilterBar`: dropdown tipo, dropdown ativo, slider/input confidence mínima
- [x] **3.4** Implementar debounce de 300ms nos filtros antes de disparar busca
- [x] **3.5** Criar estado de loading (skeleton cards) e estado vazio ("Nenhum sinal encontrado")
- [x] **3.6** Adicionar botão "Limpar filtros"
- [x] **3.7** Implementar paginação ou "Ver mais sinais" (load more)

---

## 4. Frontend — Disclaimer

- [x] **4.1** Criar componente `DisclaimerBanner` com texto: "Isenção de responsabilidade: este não é advice financeiro."
- [x] **4.2** Posicionar banner fixo no rodapé da seção de sinais
- [x] **4.3** Ícone ⚠️ visível junto ao texto

---

## 5. Integração e UX

- [x] **5.1** Conectar `GET /signals` ao frontend (React Query ou fetch)
- [x] **5.2** Passar risk_profile do localStorage em todas as requisições
- [x] **5.3** Tratar erro de API com toast + retry button
- [x] **5.4** Exibir badge "Dados desatualizados" se cache >5min
- [ ] **5.5** Verificar responsividade em mobile (teste manual)

---

## 6. Testes

- [ ] **6.1** Testar endpoint `GET /signals` com todos os combos de filtros (Postman/curl)
- [x] **6.2** Testar threshold 70% (sinal com 69% não deve aparecer)
- [ ] **6.3** Snapshot tests dos componentes SignalCard (BUY/SELL/HOLD)
- [ ] **6.4** Testar empty state e error state
- [ ] **6.5** Testar responsividade (resize browser)

---

## 7. Documentação

- [x] **7.1** Adicionar README ou note referenciando Card #55 para implementação completa dos indicadores
- [x] **7.2** Documentar contratos de API (schemas Pydantic + request/response examples)

---

## 8. Expansão para Todos os Pares USDT

- [x] **8.1** Adicionar função `_fetch_all_usdt_pairs_from_binance()` usando `GET /api/v3/exchangeInfo`
- [x] **8.2** Filtrar pares: status=TRADING, quoteAsset=USDT, isSpotTradingAllowed=true
- [x] **8.3** Implementar cache de 5 minutos para lista de pares USDT (`_USDT_PAIRS_CACHE`)
- [x] **8.4** Substituir `DEFAULT_ASSETS` fixo por fetch dinâmico em `_normalize_assets()`
- [x] **8.5** Atualizar `build_signal_feed()` para gerar sinais para todos os pares USDT
- [x] **8.6** Adicionar semáforo `MAX_CONCURRENT_KLINES=20` para limitar requests concorrentes
- [x] **8.7** Atualizar `available_assets` no response para conter todos os pares USDT
- [x] **8.8** Atualizar `get_latest_high_confidence_signals()` para usar todos os pares
- [x] **8.9** Atualizar `get_signal_detail()` com limite maior para busca
- [x] **8.10** Adicionar error handling em `build_signal_feed()` para ignorar pares com dados inválidos

---

## Dependências

- Card #55 (indicadores RSI/MACD/Bollinger Bands) — implementação completa do modelo
- Frontend existente em :5173
- Backend existente em :8003

---

## Critérios de Done

- [x] GET /signals retorna dados corretos com filtros
- [x] SignalCard renderiza todos os campos
- [x] Confidence gauge marca threshold 70%
- [x] Filtros funcionam com debounce
- [x] Disclaimer visível na página
- [ ] Todos os testes passando
- [ ] Responsividade verificada
