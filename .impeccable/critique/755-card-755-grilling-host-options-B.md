# Snapshot — card #755 `card-755-grilling-host-options` (Assessment B)

- Card: #755
- Change: `card-755-grilling-host-options`
- Critic: isolated Design Critic B (no transcript inherit; no Assessment A)
- UTC: 2026-08-27T02:28:10Z
- Tuple: `q=Design` `bound_card=755` `q_git=card-755-grilling-host-options`; `enabled_events`: recriticar, submeter_design, cancelar; write produto deny
- UI impact: none (skills/runbook/specs/pytest de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: N/A confirmed (sem HTML, sem `frontend/public/prototypes/`, Playwright não correu)
- Detector/browser: N/A justificado — sem superfície visual nova ou alterada
- Surfaces lidas (read-only): issue #755 body + comentário canônico; change `proposal.md` / `design.md` / `tasks.md`; spec deltas `grill-card`, `cursor-harness`; mains `openspec/specs/{grill-card,cursor-harness}/spec.md`; skills `.cursor/skills/grill-card/SKILL.md`, `alan-workflow` § Grill-card, `grilling/SKILL.md`, `openspec-apply-change`; stubs `.grok/skills/{grill-card,grilling,alan-workflow}`; `scripts/process-fsm/test_grill_card.py`; `.cursor/process-fsm.yaml` (T1/T5/T7/`enabled_tools`, read-only)

---

## Brief

Kaizen P2 Operacao: o card da ferramenta do host (`AskUserQuestion` Cursor / `ask_user_question` Grok) pode pintar só a recomendada; o operador confirma a seta ou escreve Other. Lei nos dois clientes em `grill-card` (vendor Matt intacto); uma linha de relay no `alan-workflow`; filho isolado devolve N≥2 opções (dump D5); pai mapeia 1:1 e não colapsa; Q aberta sem `options[]` fictícias; fallback Matt só se a ferramenta faltar; comentário canônico idempotente; stubs/gerador #668 e yaml FSM congelados; `UI impact: none`.

Audience: operador do harness (Cursor + Grok). Outcome: Q fechada mostra todas as alternativas reais no card. Direction: skills + spec mínima, não δ. Scope: capabilities já existentes `grill-card` + `cursor-harness`.

---

## Critique (contrato)

### Issue ↔ proposal ↔ design ↔ tasks ↔ specs

Issue #755 (DoD completo, fronteira da história vazia, Q1=B / Q2=A / Q3=A / Q4=B / Q5=A) mapeia 1:1 para o pacote:

| Entra (issue) | Onde no pacote |
| --- | --- |
| Lei em `grill-card`; vendor Matt não reescrito | D1; task 1.1; spec ADDED + cenário Vendor Matt intacto |
| Uma linha Grill-card em `alan-workflow` (pai, todas as options, não colapsa) | D6; task 1.2; spec `cursor-harness` ADDED |
| Q fechada N≥2 reais; recomendada primeiro `(Recommended)`; Other não conta | D2; spec ADDED Closed grill questions; needles 3.1 |
| Q aberta sem `options[]` fictícias | D3; cenário Open question |
| Fallback Matt: escolhas no corpo; `➡️` só recomenda | D4; cenário Markdown fallback |
| Relaying: filho lista N opções; pai chama o host; filho não chama | D5/D6; dump template em design; cenário Child dump |
| Stubs Grok + `grok_stubs.py` intactos; não nomear ferramenta | D7; tasks 1.2/2.1/5.1; cenário Vendor/stubs |
| Needles pytest; sessão real = Homologado, não QA | D9; tasks 3.1–3.2 / 5.2 |
| Comentário canônico idempotente; #755 já tem um prematuro | D8; spec MODIFIED + 3 cenários; task 5.2 |
| Sem FSM/hook/`enabled_tools`; `AGENTS.md` always-on não cresce; UI none | D10; tasks 5.1; cenário No FSM change |

Residuais da história (dump filho→pai; se relay exige `cursor-harness`) estão fechados: D5 template + D6 “não cabe só em `grill-card`”. `## Open Questions` = Nenhuma. `openspec validate … --strict` PASS.

Não-entra (vendor TUI, yaml, #667/#668, dual-write Hermes/`~/.codex`, sessão real como gate) está em Goals/Non-Goals, Apply contract e tasks 5.1. Sem drift.

### Parent relay em dois specs

D6 justifica `cursor-harness` porque quem chama o host é o pai (orquestrador). O mesmo dever também entrou no SHALL MODIFIED de `grill-card` (parent present all alternatives / MUST NOT collapse). Não contradiz; duplica. A linha única do runbook (task 1.2) é o delta de implementação do pai; a lei completa (1:1, ordem, `(Recommended)`, Q aberta, dump D5) mora no skill do filho + spec `grill-card` ADDED. Aceitável pelo teto “uma linha”.

### Apply — o que o card proibiu

Allow-list explícita (design Apply contract + tasks 1.1–1.2 / 2.1 / 3.1 / 5.1):

- Editar: `.cursor/skills/grill-card/SKILL.md`; **uma linha** na § Grill-card de `.cursor/skills/alan-workflow/SKILL.md`; deltas OpenSpec já no change; testes em `scripts/process-fsm/`.
- Zero: `frontend/src/`, produto `backend/`, `.cursor/process-fsm.yaml`, `scripts/process-fsm/grok_stubs.py`, stubs `.grok/skills/*`, `.cursor/skills/grilling/SKILL.md`, `AGENTS.md` always-on.

Needles de 3.1 **protegem** o vendor e os stubs (ainda `❓`/`➡️`; **não** contêm nomes de ferramenta) em vez de os editar. Contrato de testes já está no allow-list (não o furo #729 contract-vs-3.2). Apply fatiado lê `## Apply contract` + tasks + specs; não deve abrir produto.

Risco residual: a “uma linha” em `alan-workflow` é o único write no runbook T1/T7. Se o Apply reflowar o parágrafo Grill-card além dessa linha, pode tocar T1 (“comenta o handoff”). Task 1.2 + contract são suficientemente estreitos; não é P1.

### T1 / T7 / FSM

- T1: spec MODIFIED mantém `MUST NOT process_event priorizar` / `gh project item-edit` Status; comentário continua “à espera de T1 (Alan)”; idempotência não arrasta coluna. `enabled_events[Em Refinamento]=[priorizar, cancelar]`; `transitions.T1.actor=Alan`. Sem task no yaml.
- T7: `tasks.md` “Apply só com `Status=Pronto para Dev`”. Dual A/B não foi cancelado (esta crítica existe). `UI impact: none` no alan-workflow já diz que não pula colunas. Agent não aprova design (`Aprovação de Design` read-only).
- T5/`G_design`: ficheiros OpenSpec presentes; crítica = snapshots em `.impeccable/critique/**`. Este card não reabre o writer de `## Design Critique`.
- `enabled_tools` Design inalterado (`write_openspec`, `write_prototype`, `gist`, `task_critique`). Em Refinamento continua `[issue_edit, comment]`. Sem `enabled_tools` novo para a ferramenta do host (proibido pelo card; a lei é skill, não yaml).
- I1–I9 / alfabeto T0–T17 não reabertos.

Wording “Design-critic / Impeccable N/A” e “Snapshot N/A” = detector visual / protótipo, não skip da onda A/B. T7 permanece.

### Comentário #755

Issue já tem o texto **exato** `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` (owner, 2026-08-27). D8 + task 5.2: Apply/grill **não** postam outro; se o existente é exato, deixar. Spec cenários Canonical already exact / Frontier reopens / text is wrong cobrem o DoD. Sem segundo comentário neste turno (critic só snapshot).

### Dump D5 vs vendor Matt

Filho MUST Read `grilling` (formato `❓`+`➡️`) **e** devolver dump D5 (lista `Opções:` com `(Recommended)` primeiro) **e** NÃO chamar o host. Spec ADDED: MUST NOT return only the `➡️`. Task 1.1 junta os três. O loop (árvore, fronteira, uma rodada) continua o primitivo; o fio para o pai é D5. Coerente se Apply não deixar o “esperar” do skill atual como “chama `ask_user_question`”.

### Stubs Grok

`.grok/skills/grill-card/` e `grilling/` e `alan-workflow/` = MUST Read canônico, não copiam o runbook, **não** nomeiam `AskUserQuestion`/`ask_user_question`. Uma linha no canônico `alan-workflow` chega ao pai Grok sem dual-write. D7 intacto.

---

## Audit

- A11y / responsive / browser / detector: N/A (`UI impact: none`). Prototype N/A confirmed. Playwright não correu.
- Dual critic / T7 / browser-on-UI: não enfraquecidos; browser N/A aqui.
- FSM yaml: não é task; specs proíbem estado/evento/hook/`enabled_tools`. T1 Alan; T7 Alan; T5 parent `submeter_design`.
- Grok stubs: MUST Read; needles 3.1 afirmam ausência dos nomes de ferramenta. `grok_stubs.py` fora do allow-list.
- Package: `proposal.md`, `design.md`, `tasks.md`, deltas `grill-card` + `cursor-harness`. Sem artefato OpenSpec em falta. `validate --strict` PASS.
- Product UI: nenhuma path de protótipo; tasks 5.1 zero `frontend/src/` e zero produto `backend/`.

---

## Trace

1. Issue #755 — host card N≥2 nos dois clientes; lei em `grill-card` + 1 linha pai; vendor/stubs/yaml congelados; UI none; comentário idempotente.
2. proposal What Changes / Capabilities — MODIFY `grill-card` + mínimo `cursor-harness`; sem `process-harness`.
3. design D1–D10 + Apply contract + needles explícitos; Open Questions vazias (D5/D6 fecham residuais).
4. tasks 1.1–1.2 skills; 2.1 spec deltas; 3.1–3.2 pytest; 4.1 validate; 5.1–5.2 UI none + não comentar #755 de novo.
5. spec `grill-card` MODIFIED (relay pai + comentário idempotente) + ADDED host-options/dump/fallback/stubs.
6. spec `cursor-harness` ADDED parent relay; MUST NOT yaml / `AGENTS.md` grow / nome nos stubs.
7. Live skills ainda sem a lei (esperado pré-apply). `test_grill_card.py` ainda só DoD/#667 needles + `bound_card`.
8. Comentário canônico prematuro no issue = texto exato; D8 deixa.

---

## Findings (para emissão curta)

### P0

(nenhum)

### P1

(nenhum)

### P2

- **Fallback Matt está no skill do filho, não no pai.** Task 1.1 + spec `grill-card` cobrem “host tool unavailable → corpo lista escolhas, `➡️` só recomenda”. O filho **não** chama o host (D5/D6). `cursor-harness` ADDED diz que o pai SHALL chamar a ferramenta, sem cláusula de indisponibilidade; a linha 1.2 do `alan-workflow` também não. Disposition: uma cláusula no SHALL `cursor-harness` / na linha do pai — se a ferramenta faltar, pintar o dump D5 em Matt (escolhas no corpo). Hoje os dois clientes têm a ferramenta; residual, não gate.
- **`test_grill_card.py` `assert "bound_card" in text`.** 3.1 estende needles e não manda conservar/reescrever esse assert. Apply de 1.1 que reescrever o skill e apagar a palavra quebra 3.2; Apply que a conservar reancora o token. Disposition: 3.1 MUST manter os `DOD_NEEDLES` atuais (incl. `bound_card` como “id N no prompt, não o git”) ou reescrever o assert para Status+id.

### P3

- Parent-relay duplicado: SHALL MODIFIED `grill-card` **e** ADDED `cursor-harness`. Corpos alinhados; archive leva os dois.
- Template D5 (`Q<n>` / `Opções:`) está no design, não no SHALL (spec só “list N + recommendation, recommended first”). Task 1.1 aponta D5 — Apply lê design.
- Needles não cobrem dump D5, `(Recommended)`, “filho não chama”, idempotência do comentário — o issue já limitou needles a ferramentas / N≥2 / Other / vendor / relay / stubs. Needles não provam TUI (risco assumido em D9).
- `alan-workflow` live “com fronteira vazia, comenta o handoff T1” vs lei idempotente no filho. Task 1.2 = uma linha só (não reescreve essa frase). Filho lê `grill-card`; pai não posta o comentário.
- Wording tasks/design “Impeccable N/A” / “Snapshot N/A” = detector/protótipo, não skip A/B. T7 continua a linkar o markdown desta pasta.
- Vocabulário `ask_user_question.options[]` é atalho; o schema Grok é `questions[].options[]`. Closed Q mutuamente exclusivas não dizem `multi_select=false` nem “uma invocação por rodada” (vendor: whole frontier).
- Headings OpenSpec: requirement `grill-card is the Em Refinamento interview front door` agora também carrega host-options/idempotência no mesmo bloco MODIFIED — identidade longa, corpo vale.

### Disposition

Zero P0/P1. Issue/design/tasks/specs batem; T1/T7/yaml não reabertos; allow-list de Apply não inclui o que o card proibiu. P2 = fallback no caminho do pai e needle `bound_card` no pytest existente. Detector/browser N/A (sem superfície). Prototype N/A confirmed.

### Verdict

**PASS**
