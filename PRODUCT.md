# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary users are a small, manually authorized group of crypto investors in the closed beta. They use the Monitor to follow swing-trading strategies and understand opportunity and risk before making their own decisions.

## Product Purpose

Cripto Farol helps people see context, status, and risk more clearly before deciding in crypto. The Monitor is the main beta surface. Early success means that three to five real beta testers can complete the core flow, use it repeatedly enough to provide meaningful feedback, and identify practical value without mistaking the product for a promise of profit.

## Positioning

Cripto Farol is an educational decision-support product, not financial advice and not a guaranteed signal service. Its useful mechanism is a readable combination of monitored strategies, market context, backtest-informed data, and explicit risk information.

## Operating Context

- The product is in a controlled closed beta.
- Access is manual; public signup is disabled.
- The frontend is the entry point on the current VPS, while the backend remains restricted.
- The core evaluation flow is login -> Monitor -> opportunity card -> chart -> context/history -> risk.
- Feedback is collected through a private beta Telegram group with human oversight.
- Product execution is tracked in the GitHub Project `MVP Cripto - Beta Fechado`; product definitions are documented in `docs/`.

## Capabilities and Constraints

- Controlled login and access for beta users.
- Monitor as the primary screen, with validated or backtest-informed favorite strategies.
- Visible opportunity states such as `Compra` and `Venda`; intermediate states may remain internal logic.
- Entry distance, target, stop, or exit information when reliable data exists.
- Detailed asset and strategy charts, with `4h` and `1d` as the main swing-trading timeframes.
- A visible disclaimer that the product is educational decision support, not financial advice.
- The MVP does not include automated payments, an open public app, automated community, email marketing, or claims of signal accuracy.

## Brand Commitments

- The product name is **Cripto Farol** and the primary domain is `criptofarol.com.br`.
- The verbal promise is **Enxergue melhor antes de decidir em cripto.**
- The brand should communicate clarity, criterio, and vigilancia tranquila.
- The tone is clean, technical, sober, and free of guru, casino, luxury-finance, or hype aesthetics.
- Existing brand assets live under `frontend/public/brand/`; the product identity reference is `docs/brand-system.md`.
- `DESIGN.md` remains the canonical visual authority for the current interface. This product record does not replace, rewrite, or duplicate its visual tokens; any conflict must be resolved by an explicit design decision.

## Evidence on Hand

- Product scope and beta criteria: `docs/mvp-scope.md`.
- Product status and operating context: `docs/project-hub.md`.
- Brand commitments and assets: `docs/brand-system.md`, `frontend/public/brand/cripto-farol-mark.svg`, and `frontend/public/brand/cripto-farol-wordmark.svg`.
- The repository contains versioned HTML prototypes under `frontend/public/prototypes/`.
- No testimonials, public customer benchmarks, pricing evidence, or profit-performance claims are approved for design work.

## Product Principles

1. Clarity comes before a decision.
2. Context and risk are more useful than urgency or certainty.
3. Trust comes from criteria and evidence, not hype.
4. The beta stays small and observable until real usage validates expansion.

## Accessibility & Inclusion

No product-specific accommodation or user research requirement is currently documented. New or changed surfaces must still satisfy the repository's accessibility review, keyboard/focus, semantic-state, contrast, responsive, and real-browser validation gates.
