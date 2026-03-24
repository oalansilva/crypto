## Why

A funcionalidade de arbitragem deixou de fazer parte do foco atual do produto, mas ainda aparece na navegação, mantém uma página dedicada, expõe uma API própria e inicializa um monitor em background. Isso aumenta ruído operacional, custo de manutenção e risco de regressões em uma superfície que não queremos mais oferecer.

## What Changes

- Remover a rota e a página de arbitragem do frontend, incluindo entradas de navegação e títulos associados.
- Remover o endpoint `/api/arbitrage/spreads` e o monitor de arbitragem em background do backend.
- Remover serviços, configuração e testes dedicados à arbitragem, além de referências operacionais e checklists que ainda tratam a funcionalidade como ativa.
- Atualizar as specs vivas para refletir a aposentadoria da capability de spread detection e a remoção do atalho “Arbitrage” da Home.

## Capabilities

### New Capabilities
- Nenhuma.

### Modified Capabilities
- `cex-cex-spread-detection`: aposentar a capability de detecção de spreads entre exchanges e formalizar que a aplicação não expõe mais superfícies de arbitragem.
- `home`: remover “Arbitrage” da lista de atalhos suportados pela Home.

## Impact

- Frontend: `frontend/src/App.tsx`, `frontend/src/components/AppNav.tsx`, `frontend/src/pages/ArbitragePage.tsx` e qualquer cópia que ainda cite `/arbitrage`.
- Backend: `backend/app/api.py`, `backend/app/main.py`, `backend/app/config.py`, `backend/app/services/arbitrage_monitor.py` e `backend/app/services/arbitrage_spread_service.py`.
- Testes e docs: `tests/test_arbitrage_spread_service.py`, `tests/test_arbitrage_spreads_api.py`, `docs/qa-ui-checklist.md` e referências OpenSpec relacionadas.
