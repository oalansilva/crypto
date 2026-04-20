# Proposal: Onchain + Fundamentals + Git Analysis Signal Engine

## 1. User Story

**As a** trader,  
**I want** a signal system that combines onchain technical analysis, fundamental data (git activity), and repository health metrics,  
**so I can** receive informed BUY/SELL/HOLD recommendations with clear confidence scoring.

---

## 2. Value Proposition

- Adds a new signal input dimension (onchain + fundamentals) to the existing signals system
- Differentiates the platform from competitors by incorporating transparent, data-driven fundamental signals
- Composable with existing RSI/MACD/Bollinger combo logic

---

## 3. Scope In

- Onchain data ingestion: wallet flows, TVL changes, active addresses, exchange inflows/outflows
- Fundamental data: GitHub activity (commits, stars, PRs, issues), developer engagement metrics
- Signal composition engine: combine onchain + fundamental + existing price indicators into unified BUY/SELL/HOLD
- Confidence scoring (0–100%)
- Backend API endpoint to serve the new signal type
- Frontend: SignalCard displaying onchain + fundamental signal with confidence gauge
- Historical signal storage for backtesting

---

## 4. Scope Out

- Sentiment analysis from news/social media (future card)
- Multi-chain deep dive (focus on top-5 chains for MVP)
- Real-time websocket streaming (batch polling is fine for MVP)
- Portfolio optimizer integration

---

## 5. Risks & Dependencies

| Risk | Likelihood | Impact | Mitigation |
|------|-------------|--------|------------|
| Onchain API rate limits | Medium | Medium | Cache aggressively (5-min TTL); fallback to stale data |
| GitHub API rate limits | Medium | Low | Use unauthenticated endpoints + token rotation |
| Signal accuracy validation | High | High | Require backtesting evidence before surfacing to users |
| Integration with existing combo system | Medium | Medium | Phase 1: standalone signal; Phase 2: integrate into combo |

---

## 6. Dependencies

- Existing signals infrastructure (`/signals` API, SignalCard component)
- CoinGecko or similar price data (already in use)
- GitHub API (public, no auth required for basic endpoints)
- Onchain data provider (to be selected: options: DeFiLlama, Dune, or direct node RPC)

---

## 7. 5W2H

| | |
|---|---|
| **What** | Signal engine combining onchain metrics (TVL, active addresses, flows) + fundamental metrics (GitHub activity) into BUY/SELL/HOLD signals with confidence score |
| **Why** | Differentiate platform with data-driven fundamental signals; close feature gap vs competitors |
| **Who** | Traders using the platform for DeFi/altcoin signals |
| **When** | MVP in one sprint; backtesting validation in follow-up |
| **Where** | Backend `/signals/onchain` endpoint; Frontend SignalCard; Historical DB table |
| **How** | Aggregate onchain APIs + GitHub API → scoring algorithm → signal output |
| **How Much** | ~5 onchain metrics + 4 git metrics = 9 input variables; simple weighted sum or logistic regression for MVP |

---

## 8. ICE Score (estimate)

| Dimension | Score | Notes |
|---|---|---|
| **Impact** | 8 | Core differentiator for traders |
| **Confidence** | 5 | Unproven signal quality; needs backtesting |
| **Ease** | 4 | Multiple API integrations; data pipeline complexity |
| **ICE** | **160** | High priority candidate |

---

## 9. Open Questions

1. Which onchain data provider to use? (DeFiLlama vs Dune vs custom RPC)
2. What is the baseline scoring model? (weighted sum, ML, rule-based?)
3. What is the minimum backtesting evidence before going live?
4. Does Alan want this integrated INTO existing signals page or as a separate tab?
5. Which chains/tokens to prioritize for MVP?
