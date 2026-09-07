# Design

UI impact: none
live_route: N/A card de processo sem tela
surface: new

Sem superfície de produto: card de processo/harness (δ, overlay, skill). Não há rota, shell, copy nem HTML de produto — nunca emprestar `/combo/discovery` nem landing.

Prototype: N/A — sem tela de produto, sem clone de catálogo, sem HTML.
Impeccable: N/A — sem superfície visual para crítica Impeccable.

## Context

Issue [#859](https://github.com/oalansilva/crypto/issues/859). Grelha fechada (q1–q4=A): só o furo em Done; destino Em desenvolvimento; motivo visível obrigatório; Homologado já promovido fora. Hoje `enabled_events[Done] = [homologar, cancelar]`; T15 = Alan `homologar` → Homologado. Overlay: depois de Done não regressa a Em desenvolvimento em homologação, archive, commit, PR ou merge.

## Goals / Non-Goals

**Goals:** aresta humana `nao_homologar` em Done → Em desenvolvimento, só Alan, só com motivo visível no card; Agent rejeita; overlay fura só neste gesto.

**Non-Goals:** Aprovação de Design, priorizar, desfazer Homologado, produto #852, frontend/backend de produto, Agent a arrastar Status.

## Decisions

1. **Nome do evento = `nao_homologar`.** Par de `homologar`. Evita ler-se como desfazer Homologado (`devolver_homologacao`). Recorte intacto.
2. **T18.** `Done --nao_homologar, Alan, guard motivo_visivel--> Em desenvolvimento`, actions `[set_status]`. `enabled_events[Done] = [homologar, nao_homologar, cancelar]`. T15 inalterado. Sem exclusive_group (eventos distintos, como T6/T7).
3. **Guarda observável.** `motivo_visivel` é True só se o issue tiver comentário com o marcador `Não homologar:` e texto não vazio a seguir. Chat sozinho, comentário vazio ou só de Agent → `reject`, q permanece Done. Apply mapeia o predicado em `EvalContext` / `NAMED_GUARDS` (P3 de Apply).
4. **Actor.** Alan no yaml; `HUMAN_EVENTS` inclui `nao_homologar`; `process_event()` rejeita sempre (mover não corre). Alan comenta o motivo e arrasta Done → Em desenvolvimento. I2: T1, T7, T15, T18 Alan-only. T16 continua Agent.
5. **Overlay.** A regra de não-regressão passa a exceptuar **somente** T18 humano com motivo. Archive, commit, PR, merge, closeout e Agent continuam sem Done→Em desenvolvimento. Destino QA/Design continua ilegal neste gesto.
6. **Correção no mesmo card.** Após T18, q=Em desenvolvimento. Reabrir ou criar `card-<id>-*` a partir do `develop` actual (squash T14 já está lá). Write só com I1 (não develop/main). Não chamar `iniciar_apply` (T8 é de Pronto para Dev). Segue `pedir_review` → … → T14 → Done; o par homologar / não homologar reaparece. I4/T17 intactos se o digest mudar.
7. **Homologado.** Sem aresta inversa. `enabled_tools[Done]` permanece `[]`.

## Apply contract

Apply muda: `.cursor/process-fsm.yaml` (Σ, T18, enabled_events, stub Done, I2); `scripts/process-fsm/fsm.py` + `process_event.py` (`LEGAL_SIGMA`, `EXPECTED_MATRIX`, `ALAN_GATES`, `NAMED_GUARDS`, `HUMAN_EVENTS`, testes); skill `covenant-flow` (gates humanos) e `github-project-board`; `AGENTS.md` (Alan-only inclui T18); parágrafo de não-regressão em `docs/crypto-overlay.md`.

MUST NOT: `backend/`, `frontend/src/`, HTML de protótipo, `DESIGN.md`, `CONTEXT.md`, `docs/adr/`, dual-write de lei em `.dsh/` / `.grok/`.

## Risks / Trade-offs

- [Alan arrasta sem comentário] → δ: recusa não conta; Agent não escreve produto e não faz item-edit; pede motivo ou restaurar Done.
- [Correção em develop] → I1/I6 continuam a deny Write.
- [Closeout/archive a copiar o furo] → overlay e testes: só T18 humano; Agent/PR/merge rejeitam.

## Open Questions

Nenhuma de operador. Marcador `Não homologar:` é *como* deste Design.

## Design Critique

- P0 — nenhum. Recorte q1–q4=A intacto; sem tela; Agent fora do gate. Disposition: aceitar.
- P1 — nenhum. Disposition: aceitar.
- P2 — nenhum. Disposition: aceitar.
- P3 — `motivo_visivel` → EvalContext/NAMED_GUARDS; overlay exceptuar T18 nas duas frases de não-regressão; runbook pós-T18 (reabrir `card-<id>-*` a partir de develop, não T8); restore Done se arraste sem comentário; slug ≠ evento (não inventar inversa em Homologado). Disposition: aceito, detalhe de Apply.
- Tokens do autor: `UI impact: none` / `live_route: N/A card de processo sem tela` / `surface: new` em linhas próprias; Prototype N/A justificado; sem rota de catálogo emprestada.
- Snapshot: `.impeccable/critique/859-card-859-devolver-homologacao-2026-09-07T19-22Z.md`
- Prototype: N/A
- Spawns: 2 (1 autor + 1 crítico isolado; 0 rework)
- Design Agent verdict: **PASS**
