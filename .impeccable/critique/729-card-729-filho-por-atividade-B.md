# Snapshot — card #729 `card-729-filho-por-atividade` (Assessment B / detector)

- Card: #729
- Change: `card-729-filho-por-atividade`
- Critic: isolated Design Critic B (detector; no transcript inherit)
- UTC: 2026-08-25T12:00:00Z
- UI impact: none (harness/skills/docs; no product surface)
- Prototype: N/A confirmed (no HTML, no `frontend/public/prototypes/` path, Playwright not run)
- Surfaces lidas: issue #729 body; change `proposal.md` / `design.md` / `tasks.md`; specs `llm-flow-emission`, `cursor-harness`, `grill-card` (change vs main); skills `alan-workflow`, `design-critic`, `grill-card`, `openspec-apply-change`; Grok stubs; `docs/backlog-operating-model.md`; `docs/decision-log.md` #673; `scripts/process-fsm` Guard/paging/test_grill_card; `.cursor/process-fsm.yaml` (read-only)

---

## Brief

Sucessor do D8 do #673: um chat `#<id>` (Em Refinamento → Done técnico); pai orquestra; filho/onda por atividade; recusa no mesmo chat (não “abra `#id Apply`”); grill bind = Status + id no prompt, não branch `card-<id>-*`; sem evento/hook/`enabled_tools` novo; T1/T7/dual critic intactos; `UI impact: none`.

Audience: operador do harness (Cursor + Grok). Outcome: mesmo transcript por card sem misturar atividades no pai. Direction: runbook/skills/specs, não δ. Scope: três capabilities já existentes.

---

## Critique (detector)

### Leftover “abra `#id Apply`” / “Um chat por coluna”

Main specs still instruct the D8 freeze:

- `openspec/specs/llm-flow-emission/spec.md` Requirement **One chat per column without a new FSM gate**: separate chat per column; tell operator to open `#<id> <coluna>`.
- `openspec/specs/cursor-harness/spec.md` Requirement **One chat per column on both clients**: ask for a new chat titled `#<id> Apply`.
- Purpose line of main `llm-flow-emission`: “um chat por coluna”.
- Skills/docs still live: `alan-workflow` `## Um chat por coluna` (“pedir chat novo”); `design-critic` item 6 + handoff “outro chat `#<id> Apply`”; `docs/backlog-operating-model.md` gate-de-design line.

The change **does MODIFY** those two requirements (same headings, new bodies: one chat per card, same-chat refusal, no new FSM gate). Tasks 1.1, 1.2, 2.1, 3.2 cover skills/docs/tests. `docs/decision-log.md` #673 keeps the old phrase as history (task 2.2 — correct).

Gap: main **Purpose** of `llm-flow-emission` is not in the delta; after archive the requirement body says “one chat per card” while Purpose still says “um chat por coluna”.

Change spec leftover names (OpenSpec MODIFIED identity): headings stay “One chat per column…”; scenario still titled **New column starts a new chat** while the body spawns a child in the same `#<id>` chat. Body is the contract; title is residue.

### Grill bind vs branch

Main `grill-card` requires `bound_card` + session on the issue; skill precond: “sessão bound a `card-<id>-*`”. Change MODIFIES to Status=Em Refinamento + issue id in spawn prompt; scenario **Grill does not require a card branch**. Task 1.3 matches issue #729. `test_grill_card.py` still asserts `"bound_card" in text` — Apply must not keep the old bind to satisfy that needle.

Guard: `gh issue edit` has no product path → early allow; Status `item-edit` still denied. Grill-on-develop is not a product-write bypass. Paging on `develop` stays unbound (`bound_card=⊥`) because yaml is frozen — Moore page will not inject the Em Refinamento grill stub. Residual, not a Guard hole.

### Gate / FSM

- `tasks.md` does **not** list `.cursor/process-fsm.yaml` as an edit. Specs say yaml unchanged (no state/event/hook/`enabled_tools`).
- T1: grill child MUST NOT `priorizar` / item-edit Status.
- T7: Apply child only if `Status=Pronto para Dev`; same-chat refusal otherwise.
- Dual A/B and dual reviewers: parent waves; nested spawn forbidden.
- I1–I9 / T0–T17 alphabet not reopened.
- No `frontend/src/` or product `backend/` in tasks except 4.1 “do not edit”.

### Missing writer after A/B

`cursor-harness` Design gate: Design-author child writes OpenSpec/prototype; parent MUST NOT author `design.md`; critics MAY write only `.impeccable/critique/**`. Nobody is allowed to paste P0–P3 + verdict into `design.md` `## Design Critique` after the wave. Task 1.2 repeats “parent does not write `design.md`”. Table says “1 filho autor” (not a second spawn to stamp the verdict). T5/`G_design` still needs that section. Hole in the new contract.

### Apply contract vs task 3.2

`design.md` Apply contract: “Editar só skills/docs/specs listados nas tasks.” Task 3.2 requires asserts in `scripts/process-fsm` tests (or skill string tests) and `pytest scripts/process-fsm -q`. Sliced apply reads the contract first; tests under `scripts/process-fsm/` are not in that allow-list (yaml must stay out; tests need an explicit allow).

### Product UI

None. No prototype files. No Playwright. Isolated critic scope = process/gates/leftover wording only.

---

## Audit

- A11y/responsive/browser: N/A (`UI impact: none`). Prototype N/A confirmed.
- Dual critic / T7 / browser-on-UI: not weakened; browser N/A here.
- FSM yaml: not a task; specs forbid new event.
- Grok stubs: MUST Read canonical; no dual-write. Grill stub **description** still says `bound_card is set` (frontmatter only).
- Package files present: `proposal.md`, `design.md`, `tasks.md`, specs for `llm-flow-emission` / `cursor-harness` / `grill-card`. No missing OpenSpec artifact.

---

## Trace

1. Issue #729 — chat por card, filho por atividade, grill sem branch, recusa no mesmo chat, yaml inalterado, UI none.
2. proposal/design/tasks — same map; tasks 1.1–1.4 skills, 2.1–2.2 docs, 3.1–3.3 specs/tests, 4.1 no product UI.
3. Change specs MODIFY the two “One chat per column” requirements and grill-card bind; ADD activity-child isolation.
4. Main specs/skills/docs still carry D8 freeze (expected pre-apply).
5. Guard `if not path: allow` — `gh issue edit` on develop OK; unbound paging residual.
6. Apply contract vs 3.2; Design Critique writer vs parent MUST NOT author `design.md`.

---

## Findings (para emissão curta)

### P0

(nenhum)

### P1

- **Writer do `## Design Critique`:** depois da onda A/B, critics não tocam `design.md` e o pai “MUST NOT author `design.md`”; o contrato não nomeia quem grava bullets/verdict no artefato (T5). Disposition: permitir o pai gravar **só** a seção curta de crítica/verdict após A/B, ou um re-spawn explícito do filho autor só para isso.
- **Apply contract vs 3.2:** contract limita edits a skills/docs/specs; task 3.2 exige testes em `scripts/process-fsm` (não o yaml). Disposition: alargar o contract para ficheiros de teste de skill/string em `scripts/process-fsm/` e continuar a proibir `process-fsm.yaml`.

### P2

- Purpose de `openspec/specs/llm-flow-emission/spec.md` (“um chat por coluna”) não entra no delta; após archive o requirement já é chat-por-card e o Purpose mente. Disposition: uma linha no Purpose (ou task 3.1) no mesmo apply.
- Grill em `develop`: spec/skill libertam o bind; sessionStart unbound page não injeta `grill-card` (yaml frozen). Residual operacional, não deny de `gh issue edit`. Disposition: skill do pai deve spawnar mesmo com `bound_card=⊥` se Status+`#<id>` no prompt.

### P3

- Headings OpenSpec MODIFIED permanecem “One chat per column…”; cenário `New column starts a new chat` no change spec tem corpo de filho no mesmo chat. Identidade OpenSpec; corpo vale.
- Task 3.2 só grepa `abra \`#id Apply\`` / `Um chat por coluna`; `alan-workflow` hoje diz “pedir chat novo com o título da coluna” — needle fraca se 1.1 for incompleto.
- `test_grill_card.py` `assert "bound_card" in text` pode reancorar o bind antigo.
- Stub Grok `grill-card` description ainda pede `bound_card`; body MUST Read o canônico (dual-write fora).

### Disposition

P1 bloqueia PASS até o design nomear o escritor da crítica e o allow-list de testes. P2/P3 = leftovers/resíduos de apply. Sem superfície de produto. Prototype N/A confirmed.

### Verdict

**BLOCKED**
