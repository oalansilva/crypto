# Relatório do Design-autor em rework — #1015 · card-1015-jev-log-diagnostico

Filho **Design-autor em rework** (spawn isolado, cliente dsh; único rework, teto 1+1+1). Worktree `crypto-worktrees/card-1015-jev-log-diagnostico`, branch `card-1015-jev-log-diagnostico`. Escrita só em `openspec/changes/card-1015-jev-log-diagnostico/**` e neste relatório. Sem `process_event`, issue, board, Gist, comentário, commit/push, filhos; `backend/**` e `frontend/src/**` intocados (só leitura para conferir a evidência do P2).

## Veredito do crítico tratado

PASS, P0=0 · P1=0 · P2=1 · P3=5. Aplicada a correção mínima do **único P2 [contrato-visivel]**; os 5 P3 ficam registados como aceitos (detalhe de Apply), não resolvidos.

## P2 — correção aplicada (opção escolhida)

Estreitar o requisito/cenários a gates com `skip_reason` não nulo **e** declarar explicitamente os fechos não-gate fora do ficheiro. Confirmei a evidência no código (read-only): `scalp_service.py` `sent = False` + `rest_open` (l.836-837), guarda de envio com `live_send` (l.838-845), `BinanceOrderError` → `result = None` (l.887-890), `skipped=None if sent else intent.skip_reason` (l.942-947); `scalp_engine.py` l.382 `send=True, skip_reason=None`.

1. `specs/scalp-jev-diagnostic-log/spec.md`
   - Requisito «A cycle that sends no order logs its skip_reason» → «A cycle refused by a gate logs its skip_reason», com a definição «ends without an order and its `skip_reason` is non-null» e a frase de fronteira (rejeição do broker / `send=True` sem `live_send` / `rest_open` ficam no aviso existente `scalp post failed …`, fora do ficheiro).
   - Cenário «Every orderless cycle leaves its gate» → «Every gate-refused cycle leaves its gate», `WHEN` com `skip_reason` não nulo.
2. `design.md`
   - Decisão 5: acrescentada a frase «**Fronteira do log de recusa:** …» com os três fechos não-gate.
   - Apply contract: «Registo de recusa em todo ciclo recusado por um gate (com `skip_reason` não nulo) …» + fronteira no aviso existente.

Restantes requisitos/cenários da spec, decisões 1-4/6-7, riscos, tokens do gate, bloco D4, `proposal.md` e `tasks.md` intactos (diff mínimo).

## P3 aceitos — registados em `design.md`

Nova secção `## P3 (detalhe de Apply — aceitos, resolvidos no Apply)`, uma linha por item: `floor` não é token real; recusa cobre ciclos de saída (`exit_resting`/`stuck`/`hold_position`); predicado de `has_position`/`has_balance` fixado no Apply; `_redact` por lista de envs sensíveis e nunca logar headers; restantes já aceites na lista P3 do Apply contract.

## Validação

`/usr/bin/openspec validate card-1015-jev-log-diagnostico --type change --strict` → `Change 'card-1015-jev-log-diagnostico' is valid` (exit 0).

## Ficheiros alterados

- `openspec/changes/card-1015-jev-log-diagnostico/design.md`
- `openspec/changes/card-1015-jev-log-diagnostico/specs/scalp-jev-diagnostic-log/spec.md`

Este relatório não submete Design, Gist nem T5; a submissão fica com o pai.
