## Why

Na Descoberta de estratégias swing, cancelar uma varredura pode travar em
`cancelling` para sempre: `DiscoveryService.command(cancel)` só marca
`cancelling` + `cancellation_requested`, sem reconciliar nem agendar
finalização. Com o outbox já em `acked` e 0 combinações `running`, nada mais
chama `reconcile_sweep` — único caminho `cancelling -> cancelled`. Caso real
PROD: sweep `#564f92f1` (694 combinações) travou em `cancelling` com 690
`pending` / 4 `succeeded` / 0 `running`. Enquanto não há estado terminal, o
rascunho segue congelado (Q2) e o operador fica sem saída.

## What Changes

- O comando `cancel` finaliza sozinho: reconcilia na hora, sob o lock já
  adquirido — pendentes viram `skipped` de imediato; com 0 `running`, promove
  `cancelling -> cancelled` no mesmo commit.
- Com avaliações em voo (`running > 0`), o sweep permanece `cancelling` (Q1:
  as em curso terminam sozinhas) e o comando agenda um wake-up finalizador no
  outbox; a última conclusão (`reconcile_sweep` com `pending == 0` e
  `running == 0`) promove a `cancelled` sem ação do operador.
- O reparo periódico (`dispatch_outbox` / `_repair_incomplete_sweeps`) cobre sweeps `cancelling` travados (ex.: outbox já `acked`), de modo que o
  caso PROD se cura no próximo dispatch após o deploy, sem backfill.
- Sem mudança visual: correção server-side; polling e botão de cancelar já
  tratam estados terminais.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `discovery-sweep`: o requisito de cancelamento exige
  auto-finalização — fechar na hora quando não há `running` em voo, aguardar
  as em curso terminarem e concluir via wake-up finalizador, e curar via
  reparo os `cancelling` órfãos de outbox `acked`.

## Impact

- Backend: `backend/app/services/discovery_service.py` (`command`,
  novo `ensure_cancel_wakeup`, `_repair_incomplete_sweeps`; `dispatch_outbox`
  publica o finalizador sem filtro novo) e verificação sem mudança do
  orquestrador (`backend/app/tasks/discovery_tasks.py`,
  `backend/app/tasks/discovery_celery_tasks.py`). Mecanismo exato no Design.
- Spec canónica `openspec/specs/discovery-sweep/spec.md` (delta deste change).
- Testes: `backend/tests/integration/test_discovery_service.py` (regressão do
  caso PROD + finalizador + idempotência).
- Fora: frontend (`DiscoveryPage`, polling, botão cancelar); reprocessar as
  690 combinações ignoradas; regra de rascunho congelado (Q2); pause/resume.
