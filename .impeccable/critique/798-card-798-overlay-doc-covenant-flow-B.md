# Snapshot — card #798 `card-798-overlay-doc-covenant-flow` (Assessment B)

- Card: #798 — https://github.com/oalansilva/crypto/issues/798
- Change: `openspec/changes/card-798-overlay-doc-covenant-flow/`
- Critic: isolated Design Critic B (detector; no transcript inherit; no Assessment A)
- UTC: 2026-08-29T20:27:00Z
- Tuple (sessão unbound): hooks `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`.
- Board: `oalansilva` Project 1 item `PVTI_lAHOAAHtBM4BV8b2zg4jwOE` — **Status=Design** (não Todo; `UI impact: none` não saltou coluna).
- UI impact: **none** (Markdown de carga no consumidor; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: N/A confirmed (sem HTML desta change; `frontend/public/prototypes/` sem `card-798-*`; Playwright visual **não** correu)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Sem superfície visual nova ou alterada. Impeccable visual / `DESIGN.md` / Playwright desta coluna = N/A.
- Helper live: `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh` existe, executável, 7892 bytes (Gist OpenSpec; não envia `.impeccable/critique/`).
- Pasta `.cursor/skills/alan-workflow*`: **ausente**. Pin overlay `v1.1.4`. `overlay_doc: docs/crypto-overlay.md`.
- `design.md` sha256: `efa41abe91802cd1cc270567f72b892ab4f828e82692e0e4dc0e6f5463348899` (~1020 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + spec delta `consumer-load-docs`)
- `openspec validate card-798-overlay-doc-covenant-flow --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto).
- Browser gate: **N/A (no UI)**.

---

## Brief

Agente cooperativo (dsh e qualquer cliente que `Read` docs vivos) segue o path concreto `alan-workflow` e toma `FsError` / `FS_NOT_FOUND`, com o runbook certo já no git pinado. Card #798: retarget dos **quatro** docs vivos de carga do consumidor `oalansilva/crypto` para `covenant-flow` / `covenant-flow-environments`; helper no path pinado; zero token `alan-workflow` nos 4; zero notas formerly/avoid **nesses** 4. AND «formerly» das specs main de #773 **permanece**. `UI impact: none`. Q1=B, Q2=A, Q3=A, Q4=A congeladas.

Audience: operador do harness no Cripto (dsh / Cursor / qualquer cliente que carregue overlay/`rules.md`). Outcome: o path que o agente lê existe. Direction: Markdown humano (`overlay_doc` ≠ yaml). Scope: só os 4 ficheiros; sem produto `covenant-flow`, sem pin bump, sem peles, sem UI.

---

## Probes (live, este worktree, pré-Apply)

### Hits `rg -n 'alan-workflow'` (T0 do issue = live)

| Ficheiro | Hits live | Issue T0 |
| --- | ---: | ---: |
| `docs/crypto-overlay.md` | 19 | 19 |
| `rules.md` | 8 | 8 |
| `docs/backlog-operating-model.md` | 1 | 1 |
| `docs/analytics/funil-social-site-leads-plan.md` | 1 | 1 |
| `AGENTS.md` | 0 | 0 |

`.covenant-flow/overlay.yaml` e `.cursor/rules/harness.mdc`: zero token.

### Origens live vs D5

Presentes no overlay/`rules.md`: `.cursor/skills/alan-workflow/`, `.cursor/skills/alan-workflow` (sem slash), `.cursor/skills/alan-workflow-ambientes/`, `alan-workflow-ambientes`, helper `.../alan-workflow/scripts/publish-openspec-card-artifacts.sh`, verbos `seguir`/`siga`/`carregue`/`use`/`aplique`/`execute`/`seguem`, `inventario/classificacao de \`alan-workflow\``, `skill \`alan-workflow\``, `em \`alan-workflow\``, `seguir alan-workflow` (sem backticks). Banner: `Use \`alan-workflow\` + \`alan-workflow-ambientes\``. Visual QA backlog: `AGENTS.md` / `alan-workflow`.

### Specs main «formerly» (#773)

`openspec/specs/covenant-flow/spec.md:98` — `covenant-flow` (formerly `alan-workflow`), `covenant-flow-environments` (formerly `alan-workflow-ambientes`). Histórico (`docs/release-*`, `docs/decision-log.md`, palestra, archive) conserva o token **de propósito** (Non-Goal).

### Superfície visual

Nenhuma rota/HTML/protótipo. Banner Hermes = blockquote Markdown de plano analítico (instrução de agente), não ecrã CriptoFarol. Visual QA nos docs = processo Playwright, não clone de UI. Classificado `UI impact: none`.

---

## Hunt (furos pedidos) — contrato vs live

| Furo | Contrato | Live | Disposition |
| --- | --- | --- | --- |
| 4 ficheiros do issue nos 3 artefatos | Entra: overlay_doc, `rules.md`, `backlog-operating-model.md`, banner `funil-social-site-leads-plan.md` | proposal Impact + capability; design Q1/Apply 1–4; spec SHALL + cenário Apply; tasks 1 / 2 / 3.1 / 3.2 / 4.1 | **CLOSED** |
| Helper path existe | D5 row helper; spec overlay AND; task 1.2 | `.cursor/skills/covenant-flow/scripts/publish-openspec-card-artifacts.sh` no worktree (bash, Gist-only OpenSpec) | **CLOSED** |
| Q4 zero token nos 4 vs «formerly» main | Q4=A; D4/D7; Non-Goal specs main; spec MUST NOT rewrite AND «formerly»; task 4.3 zero diff `openspec/specs/**` | Token nos 4 = 19+8+1+1; formerly **só** em specs main/arquivo; Goals não pedem apagar main | **CLOSED** |
| Non-Goals contradizem Goals | Goals = retarget 4 + helper + rg vazio + banner nomes; Non-Goals = não recriar alias, não apagar banner, não reescrever formerly main, não absorver #780 | Complementares: «zero formerly **nos 4**» ≠ «apagar formerly **nas specs main**»; «retarget banner» ≠ «apagar banner» | **CLOSED** |
| `UI impact: none` bypass de coluna | Anti-bypass skill; Prototype N/A; T7/Aprovação de Design permanecem | Status **Design**; sem HTML; `## Design Critique` ausente (autor); T5 é do pai após PASS | **CLOSED** |
| Superfície visual não classificada | design `## UI impact` none + `## Prototype` N/A justificado | Sem `frontend/public/prototypes/card-798-*`; funil/Visual QA são docs, classificados none | **CLOSED** |
| D5 vs tasks vs spec vs issue | D5 tabela 6 origens; spec verbos issue; tasks 1.1 issue + 2.1 live `execute`/`seguem`; 4.1 = Q4 | Ver P2/P3: destinos e verbos extra | ver Findings |

---

## Critique (contrato vs live)

Issue #798 sintetizado (Q1–Q4 no body). Pacote OpenSpec ADDED `consumer-load-docs` (não MODIFIED `covenant-flow` main).

| Entra | Onde |
| --- | --- |
| 4 docs vivos; Q1=B | proposal; D1; spec req 1; tasks 1–3 |
| Q2=A toda instrução de carga (path **e** verbo) | D2; spec SHALL verbs; tasks 1.1 / 2.1 |
| Helper path pinado | D5 última row; spec overlay AND; task 1.2 |
| Q4=A zero token / zero formerly **nos 4**; formerly main fica | D4/D7; spec MUST NOT + AND #773; tasks 1.3 / 2.2 / 4.1 / 4.3 |
| Banner retarget; DEV/PROD intacto | D6; spec req 2; task 3.2 |
| Visual QA backlog | Apply 3; spec cenário; task 3.1 |
| Só consumidor; sem card produto; sem yaml/AGENTS/harness/peles/HTML | D3/D8; Non-Goals; spec req 3; tasks 4.2–4.4 |
| Sem reabrir #773/#554/#786/#784; sem absorver #780 | Non-Goals; spec SHALL NOT reopen (780 só design/proposal) |

`## Open Questions` = nenhuma. Prototype N/A justificado. Sem HTML. Sem rewrite `DESIGN.md`. Sem `## Design Critique` pré-preenchido. T7 humana permanece.

Aceite observável pós-Apply: `rg` vazio nos 4 (4.1); pasta ausente (4.2); banner nomes + aviso DEV/PROD (3.2 + spec ANDs); Visual QA nomeia `covenant-flow` (3.1); spec overlay THEN pinam runbook / environments / helper; zero diff árvores Non-Goal (4.3).

---

## Findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- **D5 row 2 é prefixo de `alan-workflow-ambientes`.** `.cursor/skills/alan-workflow` (sem slash) ⊂ `.cursor/skills/alan-workflow-ambientes/`. Substituição mecânica na ordem da tabela pode emitir `covenant-flow-ambientes` (sinónimo **não** na coluna Destino). MUST NOT inventar sinónimos já proíbe o nome errado; spec overlay AND e task 3.2 pinam `covenant-flow-environments`. Task **4.1 só observa ausência da origem**, não presença dos destinos no overlay_doc. Disposition: Apply MUST substituir `*-ambientes` / path ambientes **antes** do token curto; evidência de overlay_doc = spec THEN (três paths) + 1.1/1.2, não só `rg` vazio.

### P3

- Spec SHALL de verbos = issue (`siga`/`seguir`/`carregue`/`use`/`aplique`); live `rules.md` tem também `execute` / `seguem` / `em \`alan-workflow\``; overlay tem listas parentéticas e `skill \`alan-workflow\`` sem verbo Q2. Tasks 1.1/2.1 são Q2-shaped; **4.1/Q4** é o sweep. Apply MUST não parar em 1.1/2.1 se 4.1 falhar.
- Spec req 3 omite «não absorver #780» (está em Non-Goals/proposal) e omite `frontend/public/prototypes/` (Apply MUST NOT + task 4.3 cobrem).
- Task 4.4 escreve `openspec validate --change …`; CLI live recusa `--change`. Canónico desta sonda: `openspec validate card-798-overlay-doc-covenant-flow --type change --strict` (valid).
- Issue aceite ainda diz «Sem `process_event` de Status neste card» (grelha T0). Não está no Apply contract. T5 = pai após PASS; não é bypass nem bloqueio de coluna.
- Título do Project 1 ≠ título da issue (cinzentos no issue, ausentes no título do board). #780 Em Refinamento; Non-Goal não absorver.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no UI).**
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM: sem task de estado/evento/`enabled_tools`. Status já Design; T7 Alan; T5 parent. `UI impact: none` não pulou Design nem Aprovação de Design.
- Product UI Cripto: zero `frontend/src/` / `backend/` / HTML no Apply contract.
- Pin `v1.1.4` inalterado; `overlay.yaml` sem token; helper e skill environments existem no git pinado.
- Q4 vs main: formerly de #773 intacto; Goals não o apagam.

---

## Trace

1. Live: 19+8+1+1 hits nos 4; helper covenant-flow no disco; pasta alan-workflow ausente; formerly só em specs main/arquivo.
2. Issue #798 DoD = 4 ficheiros, Q2 path+verbo, helper, rg vazio, banner DEV/PROD, Visual QA backlog, Q4 zero notas nos 4, não reescrever formerly main.
3. Design D1–D8 + Apply contract 1–4 pinam o DoD; D5 é a tabela de alvos; D4/D7 separam Q4 dos 4 vs AND main.
4. Spec ADDED `consumer-load-docs` cobre overlay / rules / Visual QA / rg / banner / out-of-scope; `openspec validate --strict` verde.
5. Tasks 1.1–1.3 / 2.1–2.2 / 3.1–3.2 / 4.1–4.4 são o ouro que o Apply falha se deixar token, apagar banner, editar yaml/AGENTS/specs main, recriar pasta, ou gerar HTML.

---

## Disposition

Zero P0/P1 abertos. Os seis furos pedidos estão fechados no contrato (4 ficheiros nos 3 artefatos, helper no worktree, Q4 ≠ apagar formerly main, Non-Goals alinhados aos Goals, `UI impact: none` com Status=Design e Prototype N/A, zero superfície visual por classificar). Residual P2 (ordem D5 prefixo `*-ambientes` vs evidência 4.1 só-origem) não colapsa o DoD se Apply seguir D5 destinos + spec overlay AND. Dual-write formerly nos 4, apagar banner, editar specs main, UI/HTML, e bypass de coluna estão fechados no texto. Detector/browser visual **N/A (no UI)**. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido.

Pai: com A também PASS e zero P0/P1, colar `## Design Critique` e `process_event submeter_design`. Sem polish neste transcript. MUST NOT editar `design.md` daqui. MUST NOT `process_event` neste filho.

### Verdict

**PASS**
