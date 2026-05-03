# Tasks: Issue #69 — Monitor com estratégias favoritas

- [x] Ajustar `OpportunityService.get_favorites` para não aplicar filtro implícito de tier em `tier=all`/vazio.
- [x] Ajustar `OpportunityService._filter_by_tier` para tratar `all`/vazio como sem filtro de tier.
- [x] Remover deduplicação por símbolo no `MonitorStatusTab` para preservar múltiplos cartões por ativo/estratégia.
- [x] Tornar `OpportunityCard` explícito no nome exibido da estratégia/label.
- [x] Reforçar cobertura de regra `all` inclui `tier=null` em `backend/tests/unit/test_opportunity_service_coverage.py`.
