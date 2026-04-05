# Tasks — #66 Onchain + Fundamentals Signal Engine

## Reconciled Status

- Approval gate is considered satisfied for the current MVP scope
- Backend implementation may start immediately
- Frontend implementation must follow `design.md`, but missing prototype is no longer treated as a blocker to phases 1 and 2

## Phase 1: Data Pipeline (DEV)

- [x] **1.1** Selecionar e integrar provedor onchain (DeFiLlama). Implementar fetching de TVL, endereços ativos, fluxos de exchange para top-5 chains (ETH, SOL, ARB, BASE, MATIC). Cache de 5 min em memória.
- [x] **1.2** Integrar GitHub API pública: coletar commit frequency, star count, PR count, issue count para repositórios de cada token/chain.
- [x] **1.3** Criar tabela `onchain_signals` no banco via SQLAlchemy model + `Base.metadata.create_all()`.
- [x] **1.4** Implementar polling/scheduling: worker `onchain_polling_worker.py` coleta a cada 15 min, persiste para DB.

## Phase 2: Signal Composition Engine (DEV)

- [x] **2.1** Definir modelo de scoring: soma ponderada normalizada com pesos documentados no código (`onchain_service.py`).
- [x] **2.2** Implementar endpoint `GET /api/signals/onchain?token=X&chain=Y`: retorna `{ signal: BUY|SELL|HOLD, confidence: 0-100, breakdown: {...}, timestamp, metrics: {...} }`.
- [x] **2.3** Signal independence: standalone, não depende de Card #53 (archived). Combinação futura fica como extensão.

## Phase 3: Frontend SignalCard (DEV + DESIGN)

- [ ] **3.1** DESIGN: seguir a direção mínima registrada em `design.md` para o SignalCard onchain. Refinamentos visuais adicionais são opcionais para o MVP.
- [ ] **3.2** Implementar `OnchainSignalCard.tsx`: exibe token, chain, BUY/SELL/HOLD badge, confidence gauge (0-100%), breakdown tooltip (quais métricas pesaram).
- [ ] **3.3** Criar página/tab `/signals/onchain` com lista de sinais e filtros (chain, token, confidence threshold).
- [ ] **3.4** Responsive layout: funcional em desktop e mobile.

## Phase 4: Historical Storage + Backtesting (DEV)

- [x] **4.1** Armazenar todos os sinais gerados em `onchain_signals_history` table (model `OnchainSignalHistory`).
- [x] **4.2** Implementar endpoint de performance: `GET /api/signals/onchain/performance` — hit rate, avg confidence, expired rate, by signal type.
- [ ] **4.3** Criar dashboard simples de backtesting: comparar sinais gerados vs preço real após 1h, 4h, 24h.

## Phase 5: QA + Homologation (QA + Alan)

- [ ] **5.1** QA valida: dados onchain são atualizados corretamente após polling cycle.
- [ ] **5.2** QA valida: SignalCard exibe todos os campos corretamente com dados mockados.
- [ ] **5.3** QA valida: filtros na página `/signals/onchain` funcionam (chain, token, confidence).
- [ ] **5.4** QA valida: confidence gauge é visualmente compreensível (threshold: >70% = green, 40-70% = yellow, <40% = red).
- [ ] **5.5** Alan homologa: sinal faz sentido intuitively? Confiança está calibrada adequadamente?

---

## Definition of Done

- Todos os tasks checkados
- Backtesting mostra >55% hit rate OU carta justificada para threshold menor
- Alan homologou
- Card movido para Archived
