# Snapshot — card #786 `card-786-dsh-grill-root` (Assessment B, ROUND 6)

- Card: #786 — https://github.com/oalansilva/crypto/issues/786 (OPEN)
- Change: `card-786-dsh-grill-root`
- Critic: isolated Design Critic B r6 (detector posture; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A; r5 só como contexto de que o pacote já tinha PASS e o autor acrescentou substring **contígua** + RED)
- UTC: 2026-08-29T15:45:00Z
- Tuple: hooks `q=None` `bound_card=⊥` `q_git=develop` (sessão unbound). Write produto deny. Esta onda só `.impeccable/critique/**`.
- Status observado: Project 1 `Status=Design` (`optionId=bd47fbe8`, item `PVTI_lAHOAAHtBM4BV8b2zg4iQpo`)
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-786-dsh-grill-root` (branch `card-786-dsh-grill-root`)
- Overlay live: `pin: v1.1.1`; `clients.dsh.auto: false`
- UI impact: **none** (harness/hooks/docs de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** justificado — sem HTML desta change; Playwright visual **não** correu (Browser N/A)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Sem superfície visual nova ou alterada. Detector Impeccable da pele dsh permanece o de #782/#784; este card não o altera.
- `design.md` sha256: `3cd3bc9a06d067ce25f5f722798789c4e1aff04dbf28e89e7a777c72fffe9ece` (2589 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + três spec deltas: `grill-card`, `process-harness`, `covenant-flow`)
- `openspec validate card-786-dsh-grill-root --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto; este crítico MUST NOT editar `design.md`)

Delta r6 sob teste: N2 / D10 / spec exigem substring **contígua** `root chama ask_user_question` em `_plain(dsh)` **e** três fixtures exactos (`nunca chama` RED, frase partida RED, backticks GREEN). PASS só com zero P0/P1 aberto, incluindo regressão do pacote r5.

---

## Brief

Pele dsh already-on em `v1.1.1` (#784). Sessão `5a6c8c5c`: root leu o canónico, chamou `subagent` `grill-card 701`, **0×** `ask_user_question` (filho `DELEGATED_CALLER`). Este card: grelha no **runtime root** + deny grill-shaped no plugin (`isGrillShapedSpawn` **antes** de `runGuard`); texto canónico com dois ramos rotulados; pin `v1.1.2`. Sem Auto dsh, sem dual-write T0–T17, sem yaml FSM, sem 3080 systemd, sem produto UI.

Audience: operador dsh no consumidor pinado. Outcome: um turno «refine/grelha N» pergunta na GUI **antes** do T1 canónico, sem spawn grill-shaped. Direction: skill rotulada + Guard JS fail-closed + goldens G1–G11/N1–N3 via `apply` do plugin (não `decide()`). Scope: produto `v1.1.2` + pin Cripto; não reabrir #608/#720/#773/#782/#784/#755.

---

## Probes (live, este worktree, pré-Apply)

### Plugin / lib — **ainda v1.1.1; esperado em Design**

- `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt", "skills"]`; listener `tools/pre-execute` faz `isCordisRestricted` → `runGuard` → `denyFromDecision` → `next()`. **Zero** `subagent` / `isGrillShapedSpawn` / `dsh_grill_spawn` no ficheiro.
- `scripts/process-fsm/dsh_plugin_lib.js`: `WRITEISH` = `write`/`edit`/`bash` + `str_replace_editor` mutante. `subagent` **não** é write-like → hoje spawn grill-shaped cai em `next()` (furo `5a6c8c5c`; G1–G3 fecham-no no Apply).
- `guard.py` `decide()`: payload sem path e `tool=Task` continua `_allow()` (G11 já é verdade live; N3 proíbe ensinar o matcher aqui). Fonte **sem** `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`.
- `.cursor/hooks.json` `preToolUse` matcher ainda `Write|StrReplace|Delete|EditNotebook` — `Task` fora. G5 (`Task` / `spawn_subagent` / OpenCode `task` + `nextCalled === true` via `apply`) impede atalho Python que partiria OpenCode.

Goldens #784 no disco: `test_plugin_deny_on_illegal_product_write_without_throw` / D13 / D20 / `registerProvider` throw. G7–G9 MUST reusar este padrão. Pin-test `test_pin_copies_dsh_without_injecting_clients_dsh` ainda crava `v1.1.1`; Apply sobe a `v1.1.2` (P1 do card, não furo live).

### Skill canónica live — furo `5a6c8c5c` ainda no texto (Apply move)

`.cursor/skills/grill-card/SKILL.md`:

- `## Precondição` contém `Este filho escreve o body de N e **não** chama a ferramenta do host` e `O **pai** spawna` / `relaying`.
- H2 `## Perguntas da rodada (host)` é **irmão** de Precondição (não nested sob cliente).
- **Não** existem `## Cliente: Cursor e Grok` nem `## Cliente: dsh`.

N2 r6, corrido contra este ficheiro, **falha** (headings ausentes + Precondição com `filho`/`não chama`). Isso é o estado pré-Apply, não um buraco do contrato.

`.cursor/skills/covenant-flow/SKILL.md` `## Grill-card`: ainda «O **pai** spawna» + `todas as options` / `não colapsa`; **sem** linha `Cliente dsh:` (task 3.2).

Stub `.dsh/skills/grill-card/SKILL.md`: thin MUST Read canónico (corpo ≤8). `dsh_stubs.py` intocado. `AGENTS.md`: 19 linhas não-vazias; sem `ask_user_question`.

`_heading_section` live em `test_grill_card.py` corta no próximo `\n## ` (H3 `###` fica dentro do H2). `_plain` **ainda não existe** — D10/4.6 congelam a função + seis asserts exactos.

### Simulador N2 r6 (skill text × `_plain` + `_heading_section` live)

`_plain` = lowercase; strip backticks / `*` / `**`; `_word_` só em ênfase (não come `ask_user_question`); colapsar whitespace. N2 como tasks 4.6: `full.count == cursor.count >= 1` nas quatro frases; `dsh` **contém** a substring contígua `root chama ask_user_question`; `dsh` **não** contém `não chama ask_user_question` nem `não chama a ferramenta do host`; Precondição sem a lista banida; H2 `perguntas da rodada` só dentro dos spans cliente.

| Cópia `## Cliente: dsh` | Contígua `root chama ask_user_question` | Tokens separados (`root` ∧ `chama ask_user_question`) | N2 r6 |
| --- | --- | --- | --- |
| `O runtime root chama \`ask_user_question\`.` | sim (GREEN ticks) | sim | **PASS** |
| `O runtime root nunca chama ask_user_question.` | **não** (RED) | **sim** (GREEN-em-falso r5) | **FAIL** missing contiguous |
| `O runtime root não chama. chama ask_user_question.` | **não** (RED split) | sim no 2.º fragmento | **FAIL** missing contiguous |
| positiva **e** `nunca chama` na mesma secção | sim | sim | PASS (contradição; P2) |

Fixtures D10 isolados: os dois RED passam; GREEN com strip de backticks passa. Um `_plain = lower+whitespace` no-op **ainda** falha o primeiro assert (`**não**`).

Conclusão do delta r6: o predicado de ficheiro é o **mesmo** `in` contíguo dos RED. Copy só-`nunca` / só-partida **não** verdeia N2. Tokens `root` + `chama ask_user_question` separados (buraco r5) deixam de ser suficientes.

Contrato G1–G11 / N1 / N3 / Precondição `filho` / H2 offset / `Cliente dsh:` / plugin-via-`apply` **não** foi enfraquecido neste round.

### Dual-write / Auto / UI

`UI impact: none` correcto. Zero diff exigido em `frontend/src/` / `backend/`. Sem HTML. Homologação = dump autenticado `:3080` (Q2); não bloqueia T14; bloqueia Auto dsh.

---

## Rubrica (UI none)

- **Escopo:** Q1–Q6 fechadas no issue (todas A); Design não as reabre. Pin patch `v1.1.2`, não major. Matcher só JS do plugin, não `decide()`, não Cursor `Task`.
- **Regressão de produto:** G5+G11+N3 fecham Task-deny no OpenCode. N1 (#755) + vendor Matt + `grok_stubs.py` intocado. Write deny #784 (G7–G9) reusa `apply`+pre-execute.
- **Riscos operacionais:** needle `includes('grill-card')` FP/FN aceite; dump 8.1 é o DoD humano do ask; modelo que ignora o rótulo `## Cliente: dsh` ainda pode 0× ask — Guard não intercepta `gh` comment.
- **Superfície visual:** nenhuma por classificar. Prototype N/A.

---

## P0

*(nenhum aberto)*

- ~~Tokens `root` + `chama ask_user_question` separados verdeiam `root nunca chama ask_user_question`~~ — **fechado r6.** N2 exige substring contígua; RED `nunca` e RED split estão em design D10, tasks 4.6 e spec grill-card (asserts exactos). Simulador: `nunca-only` e `split-only` **FAIL**; happy com backticks **PASS**.

## P1

*(nenhum aberto)*

- `_plain` no-op `lower+whitespace` ainda falha o primeiro fixture (`**não** chama`).
- Precondição após `_plain` ainda MUST NOT `filho` / `spawna` / `relaying` / `dump d5` / `ask_user_question` / `askuserquestion` / `não chama`.
- G1–G9 ainda MUST `import { apply }` + `tools/pre-execute` (não unitário `decide()`).
- G5 ainda inclui OpenCode `task` + `nextCalled === true`.

## P2

- Sinónimos fora do needle (`não pergunta`, `nao` sem acento). Copy dsh com frase positiva **e** `nunca chama` na mesma secção ainda PASS (contradição). Disposition: **accepted-residual** — dump 8.1 + Open Questions.
- Modelo ignora o ramo `## Cliente: dsh` e segue o copy Cursor (`filho` / spawn / D5). Guard Cursor não deny `Task`. Plugin só pega spawn grill-shaped. Disposition: **accepted-residual** (skill + dump).
- Homologação 8.1 não bloqueia T14; pin-test live ainda `v1.1.1` até Apply. Disposition: **accepted** (Q2 / P1 do card).
- Needle `grill-card` (FP se `subagent` legítimo citar a skill; FN `grill_card` / description `refine 701`). Disposition: **accepted** (Q6 fail-closed / residual nomeado).
- `covenant-flow` Grill-card permanece com «O **pai** spawna» unlabeled; mitigação = uma linha `Cliente dsh:`. Disposition: **accepted** (Q4).
- N2 não crava N≥2 / «antes do T1» **dentro** do ramo dsh (ficam em 3.1 + cenário spec + HOST_TOOLS no ficheiro inteiro + dump 8.1). Disposition: **accepted-residual**.

## P3

- `_plain` que faz `replace("*","")` altera o leftover `card-<id>-*` no texto normalizado; o teste #755 lê o ficheiro **cru**.
- G10 JS é MAY (não substitui G1–G9).
- Lookup-table `_plain` que só transforma as seis strings-fixture passa D10 e falha o count no ficheiro com copy `**não**` / `**pai**` — Apply test-driven acaba no strip geral.

---

## Disposition

| ID | Severidade | Estado | Notas |
| --- | --- | --- | --- |
| tokens separados GREEN-em-falso | P0 | **closed r6** | contiguous `in _plain(dsh)` + RED `nunca` / split |
| `_plain` no-op / Precondição `filho` / G1–G9 via `apply` / G5 `task` | P1 | **closed** (ainda no contrato; sem regressão) | |
| sinónimos / rótulo ignorado / dump 8.1 / needle FP-FN | P2 | **accepted-residual** | |
| leftover `*` / G10 MAY | P3 | **accepted** | |

Não há finding determinístico sem classificação.

---

## Verdict

**PASS** — zero P0/P1 aberto. Delta r6 (substring contígua `root chama ask_user_question` + RED `nunca chama` / frase partida + GREEN backticks) fecha o GREEN-em-falso de tokens separados sem regressão de G1–G11, N1/N3, Precondição, H2 Perguntas, nem do deny via `apply` do plugin.

- UI impact: none
- Prototype: N/A (sem superfície Cripto)
- Browser gate: N/A justificado
- Snapshot: `.impeccable/critique/786-card-786-dsh-grill-root-B.md`
- Próximo (pai, não este crítico): sintetizar A/B em `## Design Critique`; se ambos PASS → `process_event submeter_design`. T7 é Alan.
