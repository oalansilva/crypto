# Snapshot — card #729 `card-729-filho-por-atividade` (Assessment B / detector r2)

- Card: #729
- Change: `card-729-filho-por-atividade`
- Critic: isolated Design Critic B r2 (detector; no transcript inherit; no inherit of A/B-r1)
- UTC: 2026-08-25
- UI impact: none (harness/skills/docs; no product surface)
- Prototype: N/A confirmed (no HTML, no `frontend/public/prototypes/` path, Playwright not run)
- Tuple: `.grok/rules/process-fsm-page.md` ausente. Path bind = 729 / `card-729-filho-por-atividade`. Sem product write.
- Surfaces lidas: change `proposal.md` / `design.md` (D1–D14 + Apply contract) / `tasks.md`; spec deltas `llm-flow-emission`, `cursor-harness`, `grill-card`; mains `openspec/specs/{llm-flow-emission,cursor-harness,grill-card}/spec.md`; skills `alan-workflow`, `design-critic`, `grill-card`, `openspec-apply-change`; Grok stub `grill-card`; `docs/backlog-operating-model.md`; `scripts/process-fsm/test_grill_card.py`; `.cursor/process-fsm.yaml` T5/`G_design` (read-only)

Prior P1s treated as closed *if* D12–D14, task 3.2 allow-list, and grill bind Status+id hold across design/tasks/spec deltas. This r2 only reopens a closed item when those surfaces contradict.

---

## Brief

Sucessor do D8 do #673: um chat `#<id>` (Em Refinamento → Done técnico); pai orquestra; filho/onda por atividade; recusa no mesmo chat (não “abra `#id Apply`”); grill bind = Status + id no prompt, não branch `card-<id>-*`; sem evento/hook/`enabled_tools` novo; T1/T7/dual critic intactos; `UI impact: none`.

R2 fecha (intenção): D12 pai só `## Design Critique` + T5 pai; D13 inherit global fica, lista fechada isolada; D14 Apply child sem git/δ; testes em `scripts/process-fsm` sem yaml; grill Status+id.

Audience: operador do harness (Cursor + Grok). Outcome: mesmo transcript por card sem misturar atividades no pai. Direction: runbook/skills/specs, não δ. Scope: três capabilities já existentes.

---

## Critique (detector)

### D12 vs tasks vs spec deltas (writer de `## Design Critique`)

D12 + Apply contract + task 1.2: A/B só `.impeccable/critique/**`; autor escreve o resto; pai **pode** gravar **somente** `## Design Critique`; T5/`submeter_design` só o pai; P0/P1 → re-spawn do autor (pai não polish).

`cursor-harness` cenário **Parent does not author Design** replica a exceção (MAY write só a seção; T5 no pai; re-spawn).

Contradição que sobrevive:

- Corpo SHALL de **Design gate is process-based**: “The parent MUST NOT author `design.md` or prototype files itself” — **sem** a exceção D12.
- `llm-flow-emission` delta: “parent MUST NOT execute … Design authorship” — **sem** exceção de colar bullets.
- `proposal.md` What Changes: “Design gate: sessão pai não escreve `design.md`/protótipo” — **sem** exceção.

Depois do archive o SHALL é a lei. Apply/orquestrador que seguir o corpo (ou o proposal) **não** cola o veredito; A/B não podem; autor não é re-spawnado só para bullets (alternativa rejeitada em D12). T5/`G_design` + emissão obrigatória da seção ficam sem escritor legal. D12 no `design.md` não sobrevive ao apply fatiado nem ao spec archive.

D12/task 1.2 usam permissão (“pode” / except-only / spec MAY), não dever. Mesmo com a exceção no cenário, ninguém **MUST** gravar a seção após A/B sem P0/P1.

### D13 vs tasks vs spec (inherit)

D13 + task 1.1 + Apply contract + ADDED `Activity children do not inherit parent transcript`: lista fechada (grill / Design-autor / Apply-coluna / QA / A/B / dois reviewers) sem transcript; L17 global `inherit` permanece para o resto. Alinhado. P1 anterior fechado.

### D14 vs tasks vs spec (Apply child sem git/δ)

D14 + task 1.4 + Apply contract: filho Apply não commita, não push, não `process_event`, não spawna reviewers; devolve status; pai git + `pedir_review`.

Spec ADDED só: nested spawn proibido; slice interno; pai não implementa. **Não** há SHALL “Apply child MUST NOT commit/push/`process_event`”. `cursor-harness` main (não modificado) ainda diz: agente que começa implementação SHALL `process_event iniciar_apply` antes de product Write. D14 lista deveres do pai (commit, `pedir_review`, onda, `aceitar_sha`, QA, T14) e omite `iniciar_apply`. Omissão de spec, não inversão de D14 nas tasks.

### Leftover “abra chat novo” / “Um chat por coluna”

**Não** está tasked como comportamento desejado. Tasks 1.1, 1.2, 3.2, 4.3 mandam **substituir/dropar/assertir ausência**. Specs deltas proíbem pedir `#<id> Apply`.

Ainda no contrato **após** 3.1:

- Main `llm-flow-emission` **Purpose** (“um chat por coluna”) **não** entra no delta.
- Headings OpenSpec MODIFIED continuam “One chat per column…”.
- Cenário ainda se chama **New column starts a new chat** com corpo de filho no mesmo `#<id>`.

Live skills/docs ainda D8 (esperado pré-apply): `alan-workflow` `## Um chat por coluna` + “pedir chat novo com o título da coluna”; `design-critic` item 6 + handoff “outro chat `#<id> Apply`”; `docs/backlog-operating-model.md` linha 66. Task 2.1 só troca essa linha de chat; **não** retargeta “Designer/Critic Agent pode mover `Design -> Aprovação de Design`” (contradiz D12 T5 pai-only). `decision-log` #673 histórico (task 2.2 — correto).

### Grill bind Status+id

Spec + task 1.3 + contrato: bind = `Status=Em Refinamento` da issue N + N no prompt; MUST NOT `card-<id>-*`. P1 anterior fechado.

Resíduo: contrato/task 1.3 exigem N igual ao `#<id>` do pai; spec Unbound só “no issue id or Status is not Em Refinamento”. Cenário ainda se chama **Bound card**. `test_grill_card.py` `assert "bound_card" in text` — coberto por task 3.2.

### Gate / FSM / yaml / UI

- `tasks.md` **não** lista `.cursor/process-fsm.yaml`. Specs: sem estado/evento/hook/`enabled_tools`. Task 3.2: testes only, not yaml. Confirmado.
- T1: grill child MUST NOT `priorizar` / item-edit Status (grill spec).
- T7: recusa same-chat; Apply só com `Pronto para Dev`.
- Dual A/B e reviewers: ondas do pai; nested proibido (spec ADDED + D5).
- I1–I9 / T0–T17 alphabet não reabertos.
- Product UI: none. Tasks 4.1 + contrato: zero `frontend/src/` e zero produto `backend/`. Sem path de protótipo nesta change.

### Apply contract vs 3.2 (P1 r1)

Fechado: contrato agora “skills/docs/specs/**testes** listados nas tasks”; “Zero `.cursor/process-fsm.yaml`”; 3.2 allow-list de testes, não yaml.

---

## Audit

- A11y/responsive/browser: N/A (`UI impact: none`). Prototype N/A confirmed.
- Dual critic / T7 / browser-on-UI: não enfraquecidos; browser N/A aqui.
- FSM yaml: não é task; specs proíbem evento novo.
- Grok stubs: MUST Read canônico; dual-write fora. Stub `grill-card` description ainda “Use when bound_card is set”.
- Package: `proposal.md`, `design.md`, `tasks.md`, specs das três capabilities. Sem artefato OpenSpec em falta.
- D13/D14/3.2/grill-bind: alinhados design↔tasks; D14 incompleto no spec delta; D12 contradito no SHALL/proposal.

---

## Trace

1. Issue #729 — chat por card, filho por atividade, grill sem branch, recusa no mesmo chat, yaml inalterado, UI none.
2. proposal — still “pai não escreve design.md/protótipo” (sem D12).
3. design D12–D14 + Apply contract — writer, inherit lista fechada, Apply sem git/δ, testes ≠ yaml.
4. tasks 1.1–1.4 / 2.1–2.2 / 3.1–3.3 / 4.1–4.3 — D12–D14 e 3.2 allow-list; 2.1 só a linha chat-por-coluna.
5. cursor-harness SHALL MUST NOT author vs cenário MAY `## Design Critique`.
6. llm-flow-emission MUST NOT Design authorship; Purpose main “um chat por coluna” fora do delta.
7. grill-card delta Status+id; Unbound sem match `#<id>` do pai.
8. Live D8 skills/docs (pré-apply); `test_grill_card.py` needle `bound_card`.

---

## Findings (para emissão curta)

### P0

(nenhum)

### P1

- **D12 não está no SHALL / proposal / `llm-flow-emission`.** Design D12 + task 1.2 + cenário `cursor-harness` nomeiam o pai para **só** `## Design Critique`. O corpo da requirement “Design gate is process-based” ainda `MUST NOT author design.md`; o delta `llm-flow-emission` proíbe “Design authorship”; `proposal.md` diz que o pai não escreve `design.md`/protótipo. Archive segue o SHALL → ninguém cola bullets (critics e autor estão proibidos de o fazer). Disposition: gravar a exceção no **corpo** das duas requirements e no proposal (“except `## Design Critique` after A/B”); parent **MUST** colar bullets+disposition+verdict+path quando A/B devolver zero P0/P1 (MAY só descreve o teto do patch, não a obrigação).

### P2

- **D14 ausente do spec delta.** Tasks/contrato proíbem commit/push/`process_event` no filho Apply; ADDED `cursor-harness` só veta nested reviewers + slice. Main “Agent SHALL `iniciar_apply` before product Write” não foi retargetado ao pai. Disposition: SHALL no ADDED + nomear `iniciar_apply` como dever do pai antes do spawn.
- **Purpose `llm-flow-emission` (“um chat por coluna”) fora do delta.** 3.1 aplica o requirement novo e deixa o Purpose mentir. Disposition: uma linha no Purpose (ou task 3.1).
- **Grill N ≠ `#<id>` do pai** só no contrato/task 1.3; spec Unbound não tem mismatch. Disposition: AND no cenário Unbound.
- **Task 2.1 estreita.** Troca “um chat por coluna”; backlog continua “Designer/Critic Agent pode mover `Design → Aprovação de Design`” contra D12 T5 pai-only.

### P3

- Headings MODIFIED “One chat per column…”; cenário `New column starts a new chat` (corpo já é filho no mesmo chat); grill cenário `Bound card`.
- Task 3.2 grepa `abra \`#id Apply\`` / `Um chat por coluna`; `design-critic` hoje diz “outro chat `#<id> Apply`” — needle fraca se 1.2 for incompleto.
- `test_grill_card.py` `assert "bound_card" in text` (já na 3.2).
- Stub Grok `grill-card` description ainda `bound_card is set` (dual-write fora).

### Disposition

P1 bloqueia PASS: D12 nas tasks não vence o SHALL/proposal na lei arquivada. P2 = D14 spec gap, Purpose leftover, grill mismatch, backlog T5. “Abra chat novo” está tasked como **remoção**, não como comportamento. `process-fsm.yaml` continua fora das tasks. Sem superfície de produto. Prototype N/A confirmed.

### Verdict

**BLOCKED**
