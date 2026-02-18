## Context

We need a lightweight capability to detect USDT/USDC price deviations across centralized exchanges (Binance, OKX, Bybit) without executing trades. The system already uses CCXT for exchange data.

## Goals / Non-Goals

**Goals:**
- Fetch top-of-book prices for USDT/USDC from multiple CEXs.
- Compute cross-exchange spreads using best-ask (buy) and best-bid (sell).
- Expose a backend API for clients to query spreads with optional threshold filtering.

**Non-Goals:**
- Order execution, transfers, or balance rebalancing.
- Automated trade routing or risk management.
- Persistent storage of historical spreads (optional future enhancement).

## Decisions

- **Price source:** Use CCXT WebSocket order-book streams for USDT/USDC to get real-time best ask/bid updates.
  - *Alternative:* REST `fetch_order_book`; rejected due to slower refresh and potential lag.
- **API shape:** Provide a single endpoint (e.g., `GET /api/arbitrage/spreads`) returning computed opportunities with buy/sell venues, prices, spread %, and timestamp.
  - *Alternative:* Multiple endpoints per exchange; rejected for simplicity and reduced round trips.
- **Computation:** Compute all pairwise spreads across configured exchanges and return only best buy/sell combinations per opportunity.
  - *Alternative:* Only compare a fixed buy/sell pair; rejected for flexibility.

## Risks / Trade-offs

- **Rate limits** → Mitigation: add exchange list as input and keep request frequency controlled by clients.
- **Inconsistent snapshots** (prices fetched at slightly different times) → Mitigation: include per-exchange timestamps and return as-is for visibility.
- **Network latency** → Mitigation: parallelize CCXT calls and set timeouts.
