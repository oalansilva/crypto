## Why

O custo de LLM no fluxo Design/Apply/Review é dominado por **output** (prosa Impeccable no chat e no `design.md` que o apply relê) e por **cache × turnos** em chat longo. Quem paga é o operador do harness (Alan), nos dois clientes. Precisamos avaliar com a rubrica Impeccable completa e publicar só o veredito, sem afrouxar T7, browser gate, dual critic em UI nem dual reviewer.

Issue: [#673](https://github.com/oalansilva/crypto/issues/673).

## What Changes

- **Os dois harnesses.** Lei canônica em `.cursor/skills/`, `.agents/skills/design-critic`, skill Impeccable, `rules.md`, overlay Impeccable e spec `impeccable-design-gate`. Adapter Grok continua MUST Read o canônico — sem fork. Stubs Grok de `design-critic` e Impeccable se faltarem.
- **Avaliação intacta** (UI affected): pipeline `context → shape → prototype → critique → audit → polish → browser`; A e B isolados no mesmo modelo, **sem inherit de transcript**; A usa a rubrica; B = detector + browser real. PASS exige zero P0/P1, browser verde e snapshot não vazio.
- **Teto de forma na emissão da crítica:** chat e as seções Impeccable/Design Critique de `design.md` levam só bullets P0–P3, disposition e verdict. Achados extras = mais bullets. Proibido tabela Nielsen, ensaio de personas ou Brief/Critique/Audit/Trace integrais no chat ou no `design.md`. O arquivo ainda guarda seções curtas que o apply relê (problema, decisões, Apply contract, URL/digest).
- Snapshot completo em `.impeccable/critique/` (**git-tracked**) e **link** no comentário/Gist do card. Alan abre no T7. Apply e Code Review **não lêem** o snapshot. Gist OpenSpec **não** envia a pasta.
- Protótipo por clone+delta. Design/critics usam URL + screenshot + digest — **não** despejam HTML no chat/`design.md`. Apply continua lendo o arquivo do protótipo (#530). Polish = patch no arquivo.
- Reviewers **sem inherit de transcript** de Design/Apply; mesmo modelo; prompt autocontido. Dois papéis (#569) permanecem. Saída: findings ou `No findings.` Bugbot continua opcional.
- Um chat por coluna (Design ≠ Apply ≠ Review ≠ Release); título `#id coluna`. Agente recusa misturar colunas no mesmo transcript. Sem gate novo na FSM. Sem hook.
- `UI impact: none` neste card e em cards futuros sem superfície: Impeccable/`DESIGN.md`/Playwright = N/A justificado; Design + T7 continuam.
- Folha de tokens para o agente. `DESIGN.md` humano e o YAML visual permanecem intactos.
- OpenSpec/apply: contexto da task + spec fatiada + seções curtas de `design.md`. Não o pacote inteiro nem o dump Impeccable.
- Medição por proxy no comentário de handoff: palavras de `design.md`, bytes HTML gerado vs copiado, número de spawns. Sem dashboard. Sem parser de usage.

## Capabilities

### New Capabilities

- `llm-flow-emission`: contrato transversal de **emissão** (chat/`design.md`/handoff) vs **avaliação**. Snapshot, um chat por coluna, contexto fatiado no apply, folha de tokens, proxies de custo. Não enfraquece gates.

### Modified Capabilities

- `impeccable-design-gate`: avaliação (rubrica, dual critic, detector, browser, zero P0/P1) permanece; emissão publicada deixa de ser o relatório integral; snapshot obrigatório e não vazio no PASS de UI affected; critics herdam **modelo**, não transcript.
- `cursor-harness`: runbook recusa misturar colunas no mesmo chat; apply não lê o pacote OpenSpec inteiro nem o snapshot Impeccable; Design gate allowlist `.impeccable/critique/**`; os dois clientes.
- `process-harness`: stubs Grok de `design-critic` e Impeccable apontam para `.agents/skills/` (MUST Read); gerador/CI cobre esses extras; sem dual-write da lei.
- `cursor-code-review`: reviewers com prompt autocontido, sem transcript de Design/Apply; saída findings ou `No findings.`; dois papéis intactos.
- `prototype-as-ui-spec`: apply continua lendo o HTML do disco; Design/critics não despejam HTML no contexto publicado; polish é patch.

## Impact

- Skills/lei: `.agents/skills/design-critic`, overlay Impeccable em `docs/crypto-overlay.md` (só o bloco Impeccable), `rules.md`, `.cursor/skills/alan-workflow`, `.cursor/skills/openspec-apply-change`, prompts `.cursor/agents/*-reviewer.md`, `scripts/process-fsm/grok_stubs.py`, publish-openspec helper, folha de tokens em `.agents/skills/impeccable/references/`.
- Specs acima. Sem `backend/` de produto, sem `frontend/src/`. Sem mudança de T0–T17, I1–I9 ou `process_event`.
- Não reabre #530, #569, #613, #667, #668. Não encolhe tools bundled do Grok TUI. Não instrumenta medidor de $ real.
- `UI impact: none`. Prototype N/A. Impeccable N/A neste card (o card muda o harness, não uma tela de produto).
