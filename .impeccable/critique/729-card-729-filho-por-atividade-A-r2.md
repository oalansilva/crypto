# Snapshot — card #729 `card-729-filho-por-atividade` — Assessment A r2

- Card: #729
- Change: `card-729-filho-por-atividade`
- Critic: Assessment A recritique (isolated Design critic; no parent transcript inherit)
- UTC: 2026-08-25
- UI impact: none (justificado: harness/skills/docs; nenhuma rota, shell, componente ou copy de produto; Prototype N/A; Playwright N/A)
- Prototype: N/A confirmed (sem HTML, sem `frontend/public/prototypes/`)
- Tuple: `.grok/rules/process-fsm-page.md` ausente. Path bind = 729 / `card-729-filho-por-atividade`. Sem product write.
- Surfaces lidas (r2): `openspec/changes/card-729-filho-por-atividade/{proposal,design,tasks}.md`; change specs `cursor-harness` / `grill-card` / `llm-flow-emission`; main `openspec/specs/{cursor-harness,grill-card,llm-flow-emission}/spec.md`; tasks 1.1–1.4 / 3.2 vs skills atuais `alan-workflow`, `design-critic`, `grill-card`, `openspec-apply-change`; `scripts/process-fsm/test_grill_card.py`; `.cursor/process-fsm.yaml` T8–T11 (read-only); stubs Grok `grill-card`; `docs/backlog-operating-model.md` gate-de-design.

---

## Brief

Recritique isolada após o autor fechar os P1 de A/B em D12–D14 + tasks 1.1–1.4 / 3.2 + cenário `cursor-harness` «Parent does not author Design». Sucessor do D8 do #673: um chat `#<id>` (Em Refinamento → Done técnico); pai orquestra; filhos/ondas isolados; recusa no mesmo chat; grill bind = Status da issue N + N no prompt igual ao `#<id>` do pai (não branch); sem evento FSM; `UI impact: none`.

Audience: operador do harness (Cursor + Grok). Outcome: confirmar se ainda há P0/P1 no contrato de Apply. Direction: runbook/skills/specs, não δ.

---

## Critique

### P1 anteriores — fechados

- **D12 / task 1.2 / cenário Parent does not author Design:** escritor de `## Design Critique` = pai, **somente** essa seção, depois de A/B; `process_event submeter_design` (T5) só o pai; P0/P1 → re-spawn do autor (pai não polish); A/B só `.impeccable/critique/**`; autor não spawna A/B.
- **D13 / task 1.1 / requirement Activity children do not inherit parent transcript:** inherit global de Task/modelo permanece; lista fechada (grill, Design-autor, Apply-coluna, QA, A/B, dois reviewers) MUST spawn isolado (prompt autocontido, sem transcript).
- **D14 / task 1.4:** filho Apply não `process_event`, não commit/push, não spawna reviewers; devolve status ao pai para git + `pedir_review`.
- **Grill bind / task 1.3:** Status da issue N = Em Refinamento + N no prompt igual ao `#<id>` do pai; recusa se faltar, divergir ou Status ≠ Em Refinamento; não exigir `card-<id>-*`.
- **Task 3.2 / Apply contract:** testes só em `scripts/process-fsm` (não o yaml); needles de “abra chat novo” / “Um chat por coluna”; `grill-card` sem bind de branch; `test_grill_card.py` se ainda tratar `bound_card` como branch.

Não reabrir esses P1. O que resta é deriva spec/task, Purpose legado, e o needle `bound_card` do teste atual.

### Escopo vs issue

Proposal/design/tasks ainda cobrem o Entra (um `#<id>`, pai magro, mapa de spawns, grill em `develop`, Apply um filho-coluna, inherit global intacto, Homologado/Release fora). Non-Goals intactos. Sem superfície visual sem classificação. Prototype N/A coerente.

### Gates (T1 / T7 / dual / FSM)

- T1: filho grill MUST NOT `priorizar` / item-edit Status (spec `grill-card`).
- T7: recusa no mesmo chat; Apply só com `Pronto para Dev`; Alan-only não vira evento Agent.
- Dual A/B e dual reviewers: ondas do pai; nested proibido na spec ADDED.
- YAML: tasks não editam `.cursor/process-fsm.yaml`; specs proíbem estado/evento/hook/`enabled_tools`.
- T14: QA = filho checks; `integrar_develop` no pai.
- Browser/snapshot UI-affected: este card é none; o runbook alvo não apaga o gate quando UI affected.

Intenção de gate intacta. Sem P0.

### Residuais (não P1)

**SHALL vs exceção D12.** O requirement `Design gate is process-based` ainda diz «The parent MUST NOT author `design.md` or prototype files itself». A exceção («MAY write only `## Design Critique`») está no cenário, em D12 e na task 1.2. Apply de 1.2 é inequívoco; o body do SHALL após archive fica contraditório. Editorial.

**Grill spec vs task 1.3.** Task recusa N ≠ `#<id>` do pai. Spec `Unbound or wrong column` só cobre id ausente ou Status ≠ Em Refinamento. Apply de 1.3 grava no skill; o capability arquivado fica curto.

**Apply git na spec.** Task 1.4 e D14 proíbem `process_event`/commit/push no filho Apply. `cursor-harness` ADDED só nomeia nested reviewers. Mesmo padrão: skill fecha, spec não.

**Purpose `llm-flow-emission`.** Main Purpose ainda «um chat por coluna». O delta MODIFIED o requirement, não o Purpose. Após archive o corpo é chat-por-card e o Purpose mente.

**`test_grill_card.py`.** `assert "bound_card" in text` não afirma «bound_card = branch». Task 3.2 só manda atualizar o teste *se* ele tratar `bound_card` como branch. Apply de 1.3 que apagar a palavra deixa pytest vermelho; Apply que conservar o needle para passar o teste reancora o bind velho.

**Grill em `develop`.** `resolve.py` em `develop` é `bound_card=⊥`; yaml frozen ⇒ page unbound não injeta `grill-card`. Spec/task já mandam spawnar com Status+N mesmo em `q_git=develop`. Residual operacional, não furo de Guard (`gh issue edit` sem path de produto).

**L17.** Task 1.1 mantém inherit global e exige isolado na lista fechada. A linha atual «salvo pedido explícito no chat» é qualificativo velho; o runbook da lista é o pedido explícito.

### UI / produto

Nenhuma. Task 4.1 proíbe `frontend/src/` e produto `backend/`. Prototype N/A justificado. Crítica isolada = processo/gates/leftover de wording.

---

## Audit

- A11y / responsive / browser: N/A (`UI impact: none`). Prototype N/A confirmed.
- T1/T7/T15/T16 / dual / yaml: intenção intacta; sem aresta nova.
- Isolamento: D13 + spec ADDED nomeiam a lista; task 1.1 aponta «closed list» (membros no design/spec).
- Grill em `develop`: coerente com T1 Alan-only e `enabled_tools` Em Refinamento `[issue_edit, comment]`.
- Grok: dual-write `.grok/skills/` continua Não entra; stub `MUST Read` o canônico; description do stub ainda cita `bound_card` (P3).
- Snapshot deste r2: git-tracked; Apply/Review não leem.

---

## Trace

1. P1 A/B: writer de `## Design Critique`; inherit L17; Apply contract vs testes; grill bind.
2. design.md D12–D14 + Apply contract — fecham writer, isolados, git/δ no pai.
3. tasks 1.1–1.4 / 3.2 — discriminador de papel, lista isolada, bind Status+N, filho Apply sem git/event/reviewers, testes em `scripts/process-fsm`.
4. change spec `cursor-harness` cenário Parent does not author Design + ADDED Activity children.
5. change spec `grill-card` bind sem branch; Unbound sem mismatch de N.
6. `test_grill_card.py` needle `bound_card`.
7. main `llm-flow-emission` Purpose «um chat por coluna».
8. Skills atuais ainda D8 (esperado pré-apply).

---

## Findings (para emissão curta)

### P0

(nenhum)

### P1

(nenhum)

### P2

- **SHALL vs exceção D12.** `cursor-harness` Design gate ainda «parent MUST NOT author `design.md`»; a permissão de gravar só `## Design Critique` vive no cenário / D12 / task 1.2. Disposition: meter a exceção na frase do requirement.
- **Purpose `llm-flow-emission`.** Continua «um chat por coluna»; fora do delta. Disposition: uma linha no Purpose (task 3.1).
- **`test_grill_card.py` vs 3.2.** O teste exige a string `bound_card`; 3.2 só atualiza se o teste tratar `bound_card` como branch. Disposition: 3.2 MUST reescrever o assert para o bind novo (Status de N + id; não `card-*`).
- **grill-card spec sem mismatch.** Task 1.3 recusa N ≠ `#<id>` do pai; Unbound na spec não. Disposition: AND no cenário Unbound.
- **Grill em `develop` (paging).** SessionStart unbound não injeta `grill-card` (yaml frozen). Disposition: skill do pai spawnar com Status+`#<id>` mesmo com `bound_card=⊥` (já no Entra; residual).

### P3

- Headings OpenSpec MODIFIED «One chat per column…»; cenário `New column starts a new chat` com corpo de filho no mesmo `#<id>`.
- Spec `cursor-harness` ADDED não repete «Apply child MUST NOT `process_event`/git» (task 1.4 / D14 já).
- Task 1.2 / spec de re-spawn omitem «com os achados no prompt»; D12 tem. Isolamento já exige prompt autocontido.
- Task 1.1 diz «closed list» sem enumerar; D13/spec enumeram.
- Stub Grok `grill-card` description ainda pede `bound_card`; body MUST Read o canônico (dual-write fora).
- L17 «salvo pedido explícito no chat» vs lista isolada no runbook.
- D2 «pai não escreve OpenSpec» vs D12 seção curta de crítica.

### Disposition

P1 de A/B fechados em D12–D14 + tasks 1.1–1.4 / 3.2 + cenário `cursor-harness`. Sem P0 de gate. P2 = leftover de archive/Apply (SHALL, Purpose, needle do teste, mismatch na spec, paging). P3 = identidade OpenSpec e resíduos aceitos. Prototype N/A. UI none.

### Verdict

**PASS**
