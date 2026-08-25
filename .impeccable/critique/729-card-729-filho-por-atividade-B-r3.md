# Snapshot — card #729 `card-729-filho-por-atividade` (Assessment B / detector r3)

- Card: #729
- Change: `card-729-filho-por-atividade`
- Critic: isolated Design Critic B r3 (detector; no transcript inherit; no inherit of A/B-r1/r2)
- UTC: 2026-08-25
- UI impact: none (harness/skills/docs; no product surface)
- Prototype: N/A confirmed (no HTML, no `frontend/public/prototypes/` path, Playwright not run)
- Tuple: `.grok/rules/process-fsm-page.md` ausente. Path bind = 729 / `card-729-filho-por-atividade`. Sem product write.
- Surfaces lidas: change `proposal.md` / `design.md` (D1–D14 + Apply contract) / `tasks.md`; spec deltas `llm-flow-emission`, `cursor-harness`, `grill-card`; mains `openspec/specs/{llm-flow-emission,cursor-harness,grill-card}/spec.md`; skills `alan-workflow`, `design-critic`, `grill-card`, `openspec-apply-change`; Grok stub `grill-card`; `docs/backlog-operating-model.md`; `scripts/process-fsm/test_grill_card.py`; `.cursor/process-fsm.yaml` T5/`G_design` (read-only)

Prior P1 treated as closed *if* Design-gate SHALL, `llm-flow-emission`, and `proposal.md` What Changes carry the D12 exception (parent MUST write only `## Design Critique` after A/B with zero P0/P1; re-spawn author on P0/P1; T5 parent). This r3 only reopens a closed item when those surfaces contradict. Parent patch list also checked: Apply child MUST NOT `process_event`/git/reviewers (scenario); grill Unbound N mismatch; task 2.1 T5 parent; task 3.1 Purpose line.

---

## Brief

Sucessor do D8 do #673: um chat `#<id>` (Em Refinamento → Done técnico); pai orquestra; filho/onda por atividade; recusa no mesmo chat (não “abra `#id Apply`”); grill bind = Status + id no prompt, não branch `card-<id>-*`; sem evento/hook/`enabled_tools` novo; T1/T7/dual critic intactos; `UI impact: none`.

R3 fecha (intenção): P1 r2 D12 no corpo SHALL `cursor-harness` + exceção `llm-flow-emission` + proposal What Changes; grill Unbound com N mismatch; Apply child sem git/δ no cenário; 2.1 T5 pai; 3.1 Purpose.

Audience: operador do harness (Cursor + Grok). Outcome: mesmo transcript por card sem misturar atividades no pai. Direction: runbook/skills/docs, não δ. Scope: três capabilities já existentes.

---

## Critique (detector)

### D12 vs SHALL / proposal / `llm-flow-emission` (P1 r2)

Fechado no corpo, não só no cenário:

- `cursor-harness` **Design gate is process-based** SHALL: parent MUST NOT author OpenSpec/proposal/specs/tasks, prototype, or `design.md` **except** after A/B return with zero open P0/P1 the parent **MUST** write only `## Design Critique` (bullets, disposition, verdict, snapshot path). Open P0/P1 SHALL re-spawn the Design-author child with those findings; parent MUST NOT polish. `process_event submeter_design` SHALL stay on the parent.
- `llm-flow-emission` one-chat requirement: parent MUST NOT execute Design authorship **except** writing only `## Design Critique` after A/B as specified in `cursor-harness`.
- `proposal.md` What Changes: exceção explícita — depois de A/B com zero P0/P1 o pai grava **somente** `## Design Critique`.
- Task 1.2 + Apply contract: mesma exceção; T5 parent-only; P0/P1 → re-spawn author.

Archive segue o SHALL: o escritor legal da seção existe. Critics continuam só `.impeccable/critique/**`. Autor não é re-spawnado só para bullets (alternativa D12 rejeitada). T5/`G_design` (ficheiros OpenSpec presentes; crítica = dever do Agent) tem quem cole o veredito.

Resíduo (não P1): cenário **Parent does not author Design** ainda MAY (teto do patch: só aquela seção); D12 design.md “pode”; task 1.2 except-only. O dever está no corpo SHALL (MUST). proposal Capabilities ainda resume “sessão pai não escreve `design.md`/protótipo” — What Changes e o spec já têm a exceção.

### D13 inherit

D13 + task 1.1 + Apply contract + ADDED `Activity children do not inherit parent transcript`: lista fechada (grill / Design-autor / Apply-coluna / QA / A/B / dois reviewers) sem transcript; L17 global `inherit` de modelo permanece. Alinhado. Não reabrir.

### D14 Apply child sem git/δ

Task 1.4 + Apply contract + ADDED cenário **Apply column child slices internally**: Apply child MUST NOT `process_event`, commit, push, or spawn reviewers; returns status so the parent can git + `pedir_review`. Nested spawn continua no corpo ADDED.

Corpo ADDED ainda não SHALL `MUST NOT process_event`/git (só o cenário). Main `cursor-harness` **Legal apply uses process_event** (não modificado) ainda: Agent SHALL `iniciar_apply` before product Write. D14 lista deveres do pai (commit, `pedir_review`, onda, `aceitar_sha`, QA, T14) e omite `iniciar_apply`. Não é inversão: pai continua dono de `process_event` (proposal What Changes). Omissão de nome, não proibição. P2.

### Grill bind Status+id + N mismatch

Spec SHALL: Status=Em Refinamento + issue id no spawn prompt; MUST NOT `card-<id>-*`. Cenário **Unbound or wrong column** agora: no issue id, Status ≠ Em Refinamento, **or N does not match the parent chat `#<id>`**. Task 1.3 + contrato alinhados. P2 r2 fechado.

Resíduo: contrato/task 1.3 exigem N igual ao `#<id>` do pai; Bound scenario não AND o match (Unbound cobre). `test_grill_card.py` `assert "bound_card" in text` — 3.2 só atualiza *se* o teste tratar `bound_card` como branch (não trata). Cenário ainda se chama **Bound card**.

### Leftover “abra chat novo” / “Um chat por coluna”

**Não** está tasked como comportamento desejado. Tasks 1.1, 1.2, 3.1, 3.2, 4.3 mandam **substituir/dropar/assertir ausência**. Specs deltas proíbem pedir `#<id> Apply`.

Task 3.1 agora inclui Purpose de `llm-flow-emission` (chat por card + filhos, not “um chat por coluna”). Main Purpose ainda mente — esperado pré-apply.

Task 2.1 agora: chat `#id` + filhos; **T5 remains parent `process_event submeter_design` (not the Design-author child)**. Live `backlog-operating-model` “Designer/Critic Agent pode mover `Design -> Aprovação de Design`” — esperado pré-apply.

Headings OpenSpec MODIFIED continuam “One chat per column…”; cenário **New column starts a new chat** com corpo de filho no mesmo `#<id>`. Identidade OpenSpec; corpo vale.

Live skills/docs ainda D8 (esperado pré-apply): `alan-workflow` `## Um chat por coluna`; `design-critic` item 6 + handoff “outro chat `#<id> Apply`”; backlog linha 66.

### Gate / FSM / yaml / UI

- `tasks.md` **não** lista `.cursor/process-fsm.yaml`. Specs: sem estado/evento/hook/`enabled_tools`. Task 3.2: testes only, not yaml. Confirmado.
- T1: grill child MUST NOT `priorizar` / item-edit Status (grill spec).
- T7: recusa same-chat; Apply só com `Pronto para Dev`.
- Dual A/B e reviewers: ondas do pai; nested proibido (spec ADDED + D5).
- I1–I9 / T0–T17 alphabet não reabertos.
- Product UI: none. Tasks 4.1 + contrato: zero `frontend/src/` e zero produto `backend/`. Sem path de protótipo nesta change. Package = `proposal.md` / `design.md` / `tasks.md` / três spec deltas. Sem HTML.

### Apply contract vs 3.2

Continua fechado: contrato “skills/docs/specs/**testes** listados nas tasks”; “Zero `.cursor/process-fsm.yaml`”; 3.2 allow-list de testes, não yaml.

---

## Audit

- A11y/responsive/browser: N/A (`UI impact: none`). Prototype N/A confirmed.
- Dual critic / T7 / browser-on-UI: não enfraquecidos; browser N/A aqui.
- FSM yaml: não é task; specs proíbem evento novo. `G_design` = ficheiros OpenSpec presentes (não parse da seção crítica).
- Grok stubs: MUST Read canônico; dual-write fora. Stub `grill-card` description ainda “Use when bound_card is set”.
- Package: `proposal.md`, `design.md`, `tasks.md`, specs das três capabilities. Sem artefato OpenSpec em falta.
- P1 r2 D12: fechado no SHALL/proposal What Changes/`llm-flow-emission`. Grill N mismatch, 2.1 T5, 3.1 Purpose, Apply child git no cenário: alinhados design↔tasks↔spec. D14 `iniciar_apply` no pai continua omitido.

---

## Trace

1. Issue #729 — chat por card, filho por atividade, grill sem branch, recusa no mesmo chat, yaml inalterado, UI none.
2. proposal What Changes — exceção D12 (pai só `## Design Critique` após A/B zero P0/P1); Capabilities cursor-harness ainda sem a frase.
3. design D12–D14 + Apply contract — writer, inherit lista fechada, Apply sem git/δ, testes ≠ yaml.
4. tasks 1.1–1.4 / 2.1–2.2 / 3.1–3.3 / 4.1–4.3 — D12–D14; 2.1 T5 pai; 3.1 Purpose; 3.2 allow-list.
5. cursor-harness SHALL MUST NOT author **except MUST** `## Design Critique`; cenário MAY = teto; T5 pai; re-spawn.
6. llm-flow-emission except Design authorship = só essa seção (as specified in cursor-harness).
7. grill-card Unbound: id ausente **or** Status ≠ Em Refinamento **or** N ≠ `#<id>` do pai.
8. ADDED Apply child MUST NOT `process_event`/commit/push/reviewers (cenário); main `iniciar_apply` não retargetado.
9. Live D8 skills/docs (pré-apply); `test_grill_card.py` needle `bound_card`.

---

## Findings (para emissão curta)

### P0

(nenhum)

### P1

(nenhum)

### P2

- **`iniciar_apply` não é dever nomeado do pai.** Filho Apply MUST NOT `process_event` (cenário ADDED + task 1.4). Main “Agent SHALL `iniciar_apply` before product Write” não foi retargetado. D14 lista commit / `pedir_review` / `aceitar_sha` / T14 e omite `iniciar_apply`. Disposition: uma linha no ADDED/D14/task 1.4 — pai chama `iniciar_apply` antes do spawn.
- **`test_grill_card.py` vs 3.2.** Continua `assert "bound_card" in text` sem tratar `bound_card` como branch. 3.2 só atualiza *se* o teste tratar como branch. Apply de 1.3 que apagar a palavra quebra pytest; Apply que conservar o needle reancora o bind. Disposition: 3.2 MUST reescrever o assert para Status de N + id no prompt.
- **Grill em `develop` (paging).** yaml frozen ⇒ page unbound não injeta `grill-card`. Spec já manda spawnar com Status+N mesmo em `q_git=develop`. Residual operacional, não deny de `gh issue edit`.

### P3

- Headings MODIFIED “One chat per column…”; cenário `New column starts a new chat` (corpo já é filho no mesmo chat); grill cenário `Bound card`.
- proposal Capabilities ainda “Design gate: sessão pai não escreve `design.md`/protótipo” (What Changes já tem a exceção).
- D12 design.md “pode” / task 1.2 except-only / cenário MAY vs SHALL MUST (teto vs dever — dever está no corpo).
- ADDED body não repete MUST NOT `process_event`/git (só o cenário).
- Purpose main `llm-flow-emission` “um chat por coluna” (task 3.1, pré-apply).
- backlog “Designer/Critic Agent pode mover `Design → Aprovação de Design`” (task 2.1, pré-apply).
- Stub Grok `grill-card` description ainda `bound_card is set` (dual-write fora).
- Live skills/docs D8 (esperado pré-apply).

### Disposition

P1 r2 fechado: D12 no SHALL `cursor-harness` (MUST write só `## Design Critique` após A/B zero P0/P1; re-spawn; T5 pai), `llm-flow-emission` (exceção só essa seção), proposal What Changes (mesma exceção). Grill Unbound inclui N mismatch. Apply child MUST NOT `process_event`/git/reviewers no cenário. 2.1 T5 pai; 3.1 Purpose. Sem P0/P1 novo. P2 = `iniciar_apply` não nomeado, needle do teste, paging. Prototype N/A confirmed.

### Verdict

**PASS**
