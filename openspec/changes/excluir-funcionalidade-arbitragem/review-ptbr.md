# Review PT-BR: Excluir Funcionalidade de Arbitragem

## Resumo

Remover completamente a funcionalidade de arbitragem do sistema (frontend + backend + testes + docs).

## O que será removido

**Frontend:**
- Página `/arbitrage` e rota associada
- Entrada de navegação para Arbitragem
- Atalhos da Home que mencionam arbitragem

**Backend:**
- Endpoint `/api/arbitrage/spreads`
- Monitor de arbitragem em background
- Serviços `arbitrage_monitor.py` e `arbitrage_spread_service.py`
- Configuração relacionada

**Testes e Docs:**
- Testes dedicados (`test_arbitrage_spread_*.py`)
- Referências na QA checklist e docs

## Impacto

- Frontend: `App.tsx`, `AppNav.tsx`, `ArbitragePage.tsx`
- Backend: `api.py`, `main.py`, `config.py`, `arbitrage_monitor.py`, `arbitrage_spread_service.py`
- Nenhuma nova capability criada

## Próximos Passos

1. Alan aprova planning
2. DEV implementa via `/opsx:apply`
3. QA valida
4. Alan homologa
5. Archive via `/opsx:archive`
