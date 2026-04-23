## 1. OpenSpec Alignment

- [ ] 1.1 Validar que `proposal.md`, `design.md`, `tasks.md` e specs abaixo estão consistentes.
- [ ] 1.2 Executar `openspec validate 2026-04-22-backfill-historico-ativos --type change`.
- [ ] 1.3 Corrigir inconsistências de validação (se houver) antes de implementação.

## 2. Backend: Job de backfill

- [ ] 2.1 Criar serviço `OhlcvBackfillService` com parâmetros:
  - `symbol`, `timeframes`, `history_window_years=2`, `page_size`, `max_requests_per_minute`.
- [ ] 2.2 Implementar paginação temporal por lotes (cursor/cutoff) e checkpoint persistido por job.
- [ ] 2.3 Aplicar política de throttle e retries (`429`/`5xx` + backoff + jitter).
- [ ] 2.4 Garantir idempotência por chave única e estado de reexecução (skip duplicates / safe reruns).
- [ ] 2.5 Implementar comandos de start manual, cancel e schedule para backfill de novo ativo.

## 3. Backend: Estado e APIs de progresso

- [ ] 3.1 Criar modelo/armazenamento de `backfill_job` (status, progresso, métricas, erros).
- [ ] 3.2 Expor endpoints administrativos:
  - `POST /api/admin/backfill/jobs` (criar manual)
  - `GET /api/admin/backfill/jobs`
  - `GET /api/admin/backfill/jobs/{job_id}`
  - `POST /api/admin/backfill/jobs/{job_id}/cancel` (ou equivalente)
- [ ] 3.3 Expor endpoint/scheduler para disparo diário de ativos sem histórico ou incompleto.
- [ ] 3.4 Criar trilha de logs resumida de execução por job (sem saturar disco).

## 4. Frontend: Admin progress

- [ ] 4.1 Adicionar/atualizar painel admin para listar jobs de backfill ativos/concluídos.
- [ ] 4.2 Exibir progresso por ativo: `status`, `timeframes`, `processed`, `estimated_total`, `percent`, `ETA`, `last_error`, `attempts`.
- [ ] 4.3 Permitir ação manual de start/cancel/retry na UI admin.
- [ ] 4.4 Poll ou SSE leve para atualização em tempo real.

## 5. Validação

- [ ] 5.1 Validar job de backfill manual com 1 ativo e múltiplos timeframes (smoke).
- [ ] 5.2 Validar throttle simulando limite de provider (sem bloqueio/erro fatal).
- [ ] 5.3 Validar rerun idempotente após falha parcial (o mesmo job finaliza sem duplicidade).
- [ ] 5.4 Validar progress no admin até `completed/failed/partial_complete`.
- [ ] 5.5 Atualizar docs de operação conforme necessário.

> Nota: usar project skills de `.codex/skills` quando aplicável (ex.: arquitetura, testes, depuração, review).
