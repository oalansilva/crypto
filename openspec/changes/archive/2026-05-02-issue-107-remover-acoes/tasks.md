## 1. Frontend

- [x] 1.1 Remove US Stocks market selection and stock data-source payload from Combo Configure.
- [x] 1.2 Filter Favorites to crypto pairs only and remove the Asset Type dropdown.
- [x] 1.3 Filter Monitor status/dashboard data to crypto pairs only and remove stocks UI affordances.

## 2. Backend

- [x] 2.1 Make `/api/markets/us/nasdaq100` unavailable for the crypto-only MVP.
- [x] 2.2 Make `/api/market/candles` reject non-crypto symbols for the crypto-only MVP.

## 3. Validation

- [x] 3.1 Update affected frontend/backend tests for crypto-only behavior.
- [x] 3.2 Run targeted checks plus proportional build/test validation.

Nota: usar skills locais aplicáveis, especialmente `$crypto-frontend`, `$openspec-apply-change` e `$openspec-verify-change`.

## Evidência

- `$openspec-new-change`: `openspec new change "issue-107-remover-acoes"` e `openspec status --change "issue-107-remover-acoes"`.
- `$openspec-ff-change`: `openspec instructions proposal/design/specs/tasks --change "issue-107-remover-acoes"`; artifacts criados.
- `$openspec-apply-change`: implementação concluída em frontend Combo/Favorites/Monitor e backend market/combo/opportunities/admin backfill.
- `$openspec-verify-change`: `openspec status --change "issue-107-remover-acoes" --json` retornou `isComplete=true`.
- Validações: backend targeted `29 passed`; `node --test frontend/tests/combo-market-selector.test.mjs` passou; `npm --prefix frontend run build` passou; Playwright targeted `4 passed`; `git diff --check` passou; `./restart` passou.
