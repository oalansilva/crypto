# Snapshot — card #818 `card-818-dsh-grill-spawn-cite` (Assessment B ROUND 2)

- Card: #818 — https://github.com/oalansilva/crypto/issues/818 (OPEN)
- Change: `openspec/changes/card-818-dsh-grill-spawn-cite/`
- Critic: isolated Design Critic B ROUND 2 (static detector; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A)
- UTC: 2026-09-04T20:46:53Z
- Tuple (sessão unbound): hooks `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`. MUST NOT editar `design.md`.
- Board: `oalansilva` Project 1 — **Status=Design** (`PVTI_lAHOAAHtBM4BV8b2zg5Mf0w`). Irmão #817 também **Status=Design**. `UI impact: none` não saltou coluna.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-818-dsh-grill-spawn-cite` (branch `card-818-dsh-grill-spawn-cite`)
- Overlay live: `pin: v1.1.6`; `clients.dsh.auto: false`
- Produto origin tags: `v1.1.6` (latest) … `v1.0.0`. **`v1.1.7` ainda livre** (`gh api repos/oalansilva/covenant-flow/tags`)
- UI impact: **none** (harness/plugin dsh + goldens + pin; nenhuma rota, shell, componente ou copy de produto)
- Prototype: **N/A** confirmed — sem HTML desta change; `frontend/public/prototypes/` sem `card-818-*`; Playwright visual **não** correu (Browser N/A)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Detector = issue vs OpenSpec vs live code vs goldens listados em `design.md`
- `design.md` sha256: `fd87ee73a5aa313c9ac5e694e69b04770b4a01e5889ad60be9a39e19e53cfada` (**2238** palavras) — bate o digest esperado
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + 2 spec deltas: `process-harness`, `covenant-flow`)
- `openspec validate card-818-dsh-grill-spawn-cite --type change --strict`: **valid**
- `openspec instructions apply`: `state: ready`; **30** checkboxes (cópia 1–6 duplicada; 22 textos únicos)
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto; este crítico MUST NOT editar `design.md`)
- Git: change **untracked** (`?? openspec/changes/card-818-dsh-grill-spawn-cite/`); zero diff de produto nesta onda

---

## Brief

No dsh, spawn Design-autor / Apply / review cai em `dsh_grill_spawn` só porque o briefing cita o ritual já fechado. Incidente: `session-679a762b`, #790 turno 2; retry sem a palavra passou. Card #818: distinguir **papel** vs **citação** em `isGrillShapedSpawn` (JS do plugin), sem ensinar `guard.py` `decide()`, sem filho grill no dsh, pin patch sobre live `v1.1.6` **após rebase no tip** (irmão #817 no mesmo nucleus). `UI impact: none`.

Audience: operador do board no cliente dsh. Outcome: T3→T5 não atrasa por citação; filho grill continua impossível. Direction: apertar haystacks JS (description ganha; marcadores pinados no prompt; sem `JSON.stringify` do objecto). Scope: plugin dsh + goldens + canal produto/pin; zero UI Cripto.

---

## Round 2 — recheck P1 close

Pedido desta onda: #817 named; rebase/tip; «listener unchanged» = ordem não bytes; MUST NOT revert `dsh_reasoning_effort_spawn` / `agent/request`; grill first; pin next free after origin. G1 deny; G12 citation allow; no `decide()` matcher; no HTML; no Design Critique; `openspec validate`.

| Critério P1 (r1) | Onde no pacote r2 | Resultado |
| --- | --- | --- |
| #817 named | Context (link + `card-817-dsh-reasoning-effort` + Status=Design + mesmos ficheiros); Non-Goals; D4; D5; Apply contract 1/3/5/6; Risks; Open Questions; proposal Impact; spec `covenant-flow` + cenário clobber; spec `process-harness` cenário sibling; tasks header + 2.3/4.1/4.2/5.2/6.2 **da 1.ª cópia** | **CLOSED** |
| rebase/tip | D5; Apply contract passo 1; task 4.1 (1.ª); spec «Pin from v1.1.6 must not clobber sibling #817»; proposal What Changes | **CLOSED** no contrato canónico |
| «listener unchanged» = ordem, não bytes | D4 explícito; task 2.3 (1.ª); spec: «That order is the meaning of «listener unchanged» — the plugin file MUST NOT be required byte-identical to pin `v1.1.6`» | **CLOSED** |
| MUST NOT revert `dsh_reasoning_effort_spawn` / `agent/request` | Non-Goals; D4; Apply contract 3/6; Rollback; tasks header + 2.3/4.2; spec MUST NOT revert | **CLOSED** |
| grill first | D4: `isGrillShapedSpawn` **primeiro** deny de spawn, **antes** de `runGuard`; gate #817 MAY depois do grill e antes de cordis; live plugin já grill → cordis → `runGuard` | **CLOSED** |
| pin next free after origin | D5: `gh api` tags **e** rebase; fallback de número ≠ rebase; se `v1.1.7` livre e tip `v1.1.6` MAY; se #817 ocupou, próximo patch; MUST NOT hardcode `v1.1.7` no vácuo. Origin live: `v1.1.7` livre | **CLOSED** no contrato canónico |
| G1 still deny | D3 tabela G1 permanece; task 1.4; spec cenário description `grill-card 701`; live `test_g1_*` ainda deny | **CLOSED** |
| G12 citation allow | D3 G12 phrase `grill-card fronteira vazia`; task 1.1; spec «Design-author citation…»; G12 **ausente** no pytest live (pré-Apply esperado; TDD 1.1 deve falhar no matcher actual) | **CLOSED** no contrato |
| No `decide()` matcher | D1/D3; task 2.3; spec `shared decide() does not gain`; `guard.py` fonte **sem** `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`; G11 allow; hooks `Task` fora | **CLOSED** |
| No HTML | Prototype N/A; zero `card-818-*` em `frontend/public/prototypes/`; Apply MUST NOT `frontend/src/**` | **CLOSED** |
| No Design Critique | `design.md` sem `## Design Critique` / `Design Agent verdict` | **CLOSED** |
| openspec validate | `--type change --strict` → **valid** | **CLOSED** |
| digest | `fd87ee73a5aa313c9ac5e694e69b04770b4a01e5889ad60be9a39e19e53cfada` | **MATCH** |

Residual desta onda: `tasks.md` tem **duas** secções 1–6. A 1.ª copia o P1-close; a 2.ª (linhas 37–68) é o checklist r1: 4.1 = «se `v1.1.7` livre, usá-la» **sem** rebase; 2.3 **sem** MUST NOT revert / «não bytes»; 6.2 **sem** linhas sibling. OpenSpec conta **30** tasks. Não reabre o P1 no `design.md`/specs (Apply skill também carrega `## Apply contract`), mas é furo de checklist. **P2**.

---

## Probes (live, este worktree, pré-Apply)

Estado pré-Apply **esperado**: o matcher live ainda é o de #786 (`v1.1.6`). G12 ainda não existe no pytest. Isso não é furo do contrato; é o baseline que o Apply deve partir.

### Helper JS — `scripts/process-fsm/dsh_plugin_lib.js`

`isGrillShapedSpawn(tool, args)`:

- tools exactas `subagent` / `subagent_fork` (G5: `Task` / `spawn_subagent` / `task` → false)
- needle `grill-card` via `toLowerCase()` + `String.includes` (não regex)
- `grillHaystacks`: top-level `description`/`prompt` **e** `JSON.stringify(args)` no objecto; string → parse ou crua
- **não** caminha chaves aninhadas excepto via stringify (G10 nested `{ inner: { prompt: "x grill-card y" } }` é true **hoje porque o blob stringify contém a needle**)
- **sem** lista de marcadores de citação (qualquer `grill-card` em haystack → true)

G12 live (sonda, matcher actual): description `design-autor 818` + prompt `grill-card fronteira vazia` → haystack prompt + stringify → **true / deny**. Contrato D1/G12 exige false/allow após Apply. TDD task 1.1: live **deve** falhar G12 antes do patch do helper.

### Plugin — `.dsh/plugin/process-fsm-guard.js`

Listener `tools/pre-execute` (live `v1.1.6`; **sem** `agent/request` / `dsh_reasoning_effort_spawn` neste tip — isso é o delta #817, ainda não pinado):

1. `isGrillShapedSpawn` → `{ kind: "deny", reason: "process-fsm-guard deny reason=dsh_grill_spawn" }` **sem** `next()`
2. `isCordisRestricted`
3. `runGuard` + `denyFromDecision`
4. `next()`

Confirmado: `index(isGrillShapedSpawn) < index(isCordisRestricted) <` implícito `runGuard`; `ctx.on("tools/pre-execute")` **antes** de `registerProvider`. Grill deny **antes** de `runGuard` / `decide()`. `inject = ["systemPrompt", "skills"]`.

### `guard.py` / Cursor hooks — N3 / G11 intactos

- Fonte de `scripts/process-fsm/guard.py`: **não** contém `grill-card`, `dsh_grill_spawn`, `isGrillShapedSpawn`
- G11 live: `decide({tool: "Task", args: {prompt: "grill-card 701"}})` → `permission: allow` (teste existente)
- `.cursor/hooks.json` `preToolUse` matcher ainda `Write|StrReplace|Delete|EditNotebook` — `Task` fora

Contrato #818: Apply MUST NOT ensinar `decide()`. Tasks 2.3 / spec cenário `shared decide() does not gain the spawn rule` / G11. **Hunt «teaching decide()»: não está no pacote.**

### Goldens — `scripts/process-fsm/test_dsh_grill_spawn.py`

Presentes (G1–G11): G1 description `grill-card 701` deny + ordem plugin; G2 `Please run Grill-Card` deny; G4 Design-autor **sem** needle allow; G5 três tools host `nextCalled === true`; G6 JSON string description deny; G10 unitário JS nested stringify true + negativos `grill_card` / `grill card`; G11 `decide()` allow + fonte Python sem needle.

**Ausentes (pré-Apply):** G12 / G12b / G12c / G12d. Tasks 1.1–1.3 exigem-nos via `apply` + `tools/pre-execute` (G12d também afirma G10 nested permanece true).

### Pin live

- Overlay Cripto: `pin: v1.1.6`
- `test_dsh_adapter.py` `test_pin_copies_dsh_without_injecting_clients_dsh` crava `"v1.1.6"`
- `test_grill_card.py` needle `overlay["pin"] == "v1.1.6"`
- Tasks 3.2 / 4.1 / 5.1 (1.ª cópia): subir para a tag **deste** card após rebase; não hardcode `v1.1.7` no vácuo

### Superfície visual

Nenhuma rota/HTML desta change. Prototype N/A. Zero task `backend/` / `frontend/src/`. `UI impact: none` **não** está mal classificado.

---

## Hunt (furos pedidos) — contrato vs live vs issue

| Furo | Contrato 818 r2 | Live / irmão / issue | Disposition |
| --- | --- | --- | --- |
| G12 markers vs prompt do incidente | Lista pinada D1; G12 MUST `grill-card fronteira vazia`; critério 1 do issue = essa frase | Incidente coberto. Briefing típico Design-autor também usa `Do NOT re-interview` / `Do NOT invoke grill-card` / `Closed grill facts` / `grilled DoD` — cobertos. **Não** cobertos: `Do NOT spawn grill-card`, `não spawna filho grill`, `skill grill-card` sozinho, `não reentrevista` (sem -ar), backticks a partirem o marcador contíguo. Risks r2 nomeiam isto como P2 aceite | **P2** accepted-residual |
| `JSON.stringify` vs G10 nested prompt | D2: MUST NOT stringify o objecto; recursar só chaves `description`/`prompt`; `{ inner: { prompt: "x grill-card y" } }` permanece deny; G12d `inner.fact` allow | Live G10 nested é true **via stringify**, não via walk. D2 + task 1.3/2.1 substituem stringify por recursão no **mesmo** patch | **CLOSED** no contrato |
| pin `v1.1.7` vs live `v1.1.6` + irmão #817 | D4/D5 + Apply contract + spec clobber: nomeia #817; rebase/tip; listener = ordem não bytes; MUST NOT revert gate/`agent/request`; grill first; pin-tests = tag deste card após rebase | Live pin `v1.1.6`. Origin `v1.1.7` livre. #817 Status=Design, mesmos ficheiros. Pacote canónico fecha o P1 r1 | **P1 CLOSED** |
| `tasks.md` 2.ª cópia r1 | 1.ª cópia alinha D4/D5; 2.ª (ids OpenSpec 16–30) 4.1 sem rebase; 2.3 sem revert #817 | Apply vê 30 tasks. Skill Apply também lê `## Apply contract` (rebase). Não anula D5 | **P2** (checklist; não reabre P1 do design) |
| teaching `decide()` | Proibido: D1/D3/D4, proposal, task 2.3, spec G11/N3 | `guard.py` sem needle; G11 allow; hooks `Task` fora; G12 via `apply`+pre-execute, não Python | **CLOSED** |
| permitir filho grill no dsh | Non-goal; G1/G2/G6 permanecem deny; root grelha | G1 description `grill-card 701` sempre deny mesmo com marcador (description ganha). G2 sem marcador permanece deny. Stuffed: description `refine 701` + «Please run Grill-Card» + `fronteira vazia` → allow deste deny (Risks) | **P2** stuffed (nomeado; não reabre #786) |
| UI mal classificada | `UI impact: none`; Prototype N/A; live_route N/A | Zero HTML `card-818-*`; zero `frontend/src/` / `backend/` no Apply contract; Playwright N/A correcto | **CLOSED** |
| Design Critique pré-preenchido | Filho autor não escreve; crítico não edita `design.md` | Ausente | **CLOSED** |

---

## Rubrica (UI none)

- **Escopo:** issue critérios 1–5 sintetizados (citação Design-autor allow; G1 deny; Apply/review citação allow; G5 tools fora; Python sem matcher). Pin incluído neste card (grelha pediu canal como #786). Irmão #817 nomeado. Não reentrevista. Não reabre #786/#790.
- **Regressão de produto:** G1/G2/G6/G10 papel pinados a permanecer; G5/G11/N3 fecham Task-deny no OpenCode; listener grill antes de `runGuard`; MUST NOT clobber sanitizer #817.
- **Riscos operacionais:** stuffed citation + `refine 701`; FN papel noutro campo; lista de marcadores fechada; checklist duplicado em `tasks.md` (P2).
- **Superfície visual:** nenhuma por classificar. Prototype N/A.

---

## Critique (contrato vs live)

Issue #818 DoD grelhado (fronteira vazia) sintetizado em proposal/design/tasks/specs. `openspec validate --strict` verde. Prototype N/A justificado. Sem HTML. Sem rewrite `DESIGN.md`. Sem `## Design Critique` pré-preenchido. Matcher live ainda `v1.1.6` (pré-Apply). Papel vs citação está decidido (*como* = D1–D2) e G12 usa a frase do critério 1.

O pacote **não** ensina `decide()`, **não** autoriza filho grill como goal, **não** classifica UI como affected. G10 nested vs remoção de stringify está coerente **se** a recursão de `description`/`prompt` chegar no mesmo patch (tasks 1.3 + 2.1).

P1 r1 (corrida de pin com #817 / «listener inalterado» como bytes) está **fechado** em D4/D5 + Apply contract + specs. Residual r2: 2.ª cópia de `tasks.md` ainda ensina o 4.1 fraco — P2, não P1.

---

## Findings

### P0

*(nenhum aberto)*

### P1

*(nenhum aberto — P1 r1 CLOSED)*

- ~~Corrida de pin `v1.1.7` com #817 no mesmo nucleus, sem merge.~~ **CLOSED** nesta revisão: Context nomeia [#817](https://github.com/oalansilva/crypto/issues/817); D4 «listener inalterado» = ordem grill-antes-de-`runGuard` + reason, **não** bytes `v1.1.6`; D5 + Apply contract exigem `gh api` tags **e** rebase no tip (incl. #817); MUST NOT reverter `dsh_reasoning_effort_spawn` / `agent/request`; grill permanece primeiro; pin-tests = tag **deste** card após rebase, não `v1.1.7` no vácuo; fallback de número ≠ rebase.

### P2

- **`tasks.md` duplicado (cópia r1 após a r2).** OpenSpec lista 30 checkboxes. A 2.ª 4.1 («se `v1.1.7` livre, usá-la») omite rebase; a 2.ª 2.3 omite MUST NOT revert / «não bytes». Disposition: **aberto, não bloqueante** — Apply MUST seguir D5 / 1.ª 4.1 / spec clobber, não a 2.ª cópia. Autor SHOULD apagar linhas 37–68. `## Apply contract` no `design.md` continua a carregar rebase mesmo na task fraca.

- **Lista de marcadores incompleta vs briefings reais (não vs o incidente).** Incidente #790 / critério 1 / G12 usam `grill-card fronteira vazia` — coberto. Frases canónicas de spawn Design-autor/Apply que citam `grill-card` **sem** um dos 9 marcadores ainda deny: `Do NOT spawn grill-card`, `dsh não spawna filho grill`, «skill grill-card», `não reentrevista` (skill covenant-flow, sem infinitivo), `` não invocar `grill-card` `` (backtick parte `não invocar grill-card`). Risks já nomeiam. Disposition: **accepted-residual** — não alargar a lista neste card (D1). Apply MUST NOT alargar marcadores.

- **Stuffed bypass ≠ autorizar filho grill.** Description `refine 701` + prompt «Please run Grill-Card» + `fronteira vazia` passa **este** deny. G1 (`grill-card 701` na description) continua deny mesmo com marcador. Non-goal «permitir filho grill» mantém-se para o caminho G1. Disposition: **accepted-residual** (Risks). Não reabre #786.

- **G10 nested depende hoje de stringify.** Remover stringify **sem** o walk recursivo de `prompt` aninhado parte G10. Contrato já exige os dois no mesmo TDD (1.3 + 2.1). Disposition: residual de Apply, não de recorte — o pacote está pinado; não é P1 do *como*.

### P3

- Issue body ainda diz «#786 open; change ainda não arquivada». Disco deste worktree: `openspec/changes/archive/2026-09-03-card-786-dsh-grill-root/`. Design.md já corrigiu o facto live. Drift do issue, não do OpenSpec.
- Spec cenário «nested citation…» mistura G12d e G10 nested no mesmo WHEN/THEN; tasks 1.3 separam os payloads. Apply MUST ter dois asserts, não um WHEN ambíguo.
- `não reentrevista` vs marcador `não reentrevistar`; marcadores sem variante com backticks. Já coberto no P2 da lista; não alargar.
- Pin-tests ainda `v1.1.6` até Apply (esperado). Homólogo ao residual de #809/#786.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no UI).**
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM: sem task de estado/evento/`enabled_tools`. Status já Design; T7 Alan; T5 parent. `UI impact: none` não pulou Design nem Aprovação de Design.
- Product UI Cripto: zero `frontend/src/` / `backend/` / HTML no Apply contract.
- `guard.py` sem matcher grill: confirmado.
- Plugin: `isGrillShapedSpawn` antes de `runGuard`: confirmado. Sem `agent/request` neste tip `v1.1.6` (esperado).
- `openspec validate --strict`: valid.
- `design.md` digest/palavras: `fd87ee73a5aa313c9ac5e694e69b04770b4a01e5889ad60be9a39e19e53cfada` / 2238.
- Sem `## Design Critique` no design.md.
- Sem HTML proto desta change.

---

## Trace

1. Live `v1.1.6`: stringify haystack; substring `grill-card` = papel; G1–G11; G12 ausente; `guard.py` limpo; plugin grill→cordis→runGuard; sem `agent/request`.
2. Issue #818 DoD = papel vs citação; Design-autor com `grill-card fronteira vazia` passa este deny; G1 permanece; Python sem matcher; canal+pin; não entra filho grill / Cursor-Grok / reabrir #786/#790.
3. Design D1–D6 r2: description ganha; marcadores pinados; sem stringify; G12 via `apply`; listener = ordem não bytes; pin = tag deste card após rebase no tip #817; MUST NOT revert sibling.
4. Specs MODIFIED `process-harness` + ADDED `covenant-flow` pin (cenário clobber #817). Tasks TDD G12* antes do helper **e** cópia r1 residual. Validate strict verde. Digest esperado MATCH.
5. P1 r1 fechado no contrato. Residual r2 = checklist duplicado (P2).

---

## Disposition

| ID | Severidade | Estado | Notas |
| --- | --- | --- | --- |
| pin `v1.1.7` × #817 / «listener inalterado» | P1 r1 | **CLOSED** | #817 named; rebase/tip; ordem≠bytes; MUST NOT revert gate/`agent/request`; grill first; pin = tag após origin |
| `tasks.md` 2.ª cópia r1 (4.1 sem rebase) | P2 | **ABERTO** | 30 checkboxes; não reabre P1 (Apply contract + specs); SHOULD apagar linhas 37–68 |
| marcadores incompletos vs spawn «Do NOT spawn grill-card» / backticks | P2 | accepted-residual | incidente G12 coberto; D1 não alarga |
| stuffed `refine 701` + marcador | P2 | accepted-residual | G1 description ainda deny |
| stringify vs G10 nested | P2/closed contrato | Apply mesmo patch | 1.3 + 2.1 pinam recursão + G10 true + G12d allow |
| teaching `decide()` | — | **CLOSED** | fonte + G11 + G12 via plugin |
| filho grill como goal | — | **CLOSED** | Non-goal + G1/G2 |
| UI misclassified | — | **CLOSED** | none correcto; sem HTML |
| Design Critique pré-preenchido | — | **CLOSED** | ausente |
| issue #786 archive drift | P3 | accepted | design.md já tem o facto de disco |
| pin-tests live `v1.1.6` | P3 | esperado pré-Apply | task 3.2 |

Zero P0/P1 aberto. Finding determinístico classificado. Detector/browser visual **N/A (no UI)**. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido. Digest esperado MATCH. `openspec validate --strict` valid.

MUST NOT editar `design.md` daqui. MUST NOT `process_event` neste filho.

### Verdict

**PASS**
