# Snapshot — card #809 `card-809-grill-card-operator-ceiling` (Assessment B r2)

- Card: #809 — https://github.com/oalansilva/crypto/issues/809 (OPEN)
- Change: `openspec/changes/card-809-grill-card-operator-ceiling/`
- Critic: isolated Design Critic B r2 (detector; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A)
- UTC: 2026-08-30T01:58:14Z
- Tuple (sessão unbound): hooks `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`.
- Board: `oalansilva` Project 1 — **Status=Design** (`optionId=bd47fbe8`). `UI impact: none` não saltou coluna.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-809-grill-card-operator-ceiling`
- Overlay live: `pin: v1.1.5`
- UI impact: **none** (adapter `grill-card` + uma frase no runbook + goldens pytest; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** confirmed (sem HTML desta change; `frontend/public/prototypes/` sem `card-809-*`; Playwright visual **não** correu)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Detector desta onda = sondas de adapter/vendor/skins/scanner D4 r2 (SHA misto + eventos estreitos + dump pass + stamp Other/silêncio). Impeccable visual / `DESIGN.md` / Playwright = N/A.
- `design.md` sha256: `1b07fe96243df5e2e0eddc11960388206c67fc2c35bd331fe603325b235a3f75` (~1853 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + 2 spec deltas: `grill-card`, `covenant-flow`)
- `openspec validate card-809-grill-card-operator-ceiling --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto; este crítico MUST NOT editar `design.md`)
- Q1=A, Q2=A, Q3=A congeladas no issue (não reabrir).
- P1 r1 re-sondados após patch: scanner SHA/`priorizar`; pass dump `Não priorizar ainda` / `acabada` / `20260830`; Other/silence never Recommended.

---

## Brief

Alan sofre nas Qs de grelha: options só inteligíveis com identificadores do git, e «A» na recomendada ratifica desenho. Card #809: tecto de linguagem no **adapter** `grill-card` (não no vendor Matt) em **todo** Em Refinamento; facto no body / *como* no Design; Other vazio / silêncio / «não percebi» reclassificam e **nunca** aceitam a recomendada; fronteira deste adapter = 6 DoD + zero decisão de operador; comentário canónico inalterado; pin patch esperado `v1.1.6`. `UI impact: none`.

Audience: operador do board (PO) nas Qs fechadas do host; pai Cursor/Grok e root dsh no relay. Outcome: Qs em português de operador; T1 continua só Alan. Direction: tecto no canónico `.cursor/skills/grill-card/SKILL.md` + frase exacta D5 no bloco Grill-card; vendor intocado. Scope: produto + pin; sem `backend/` / `frontend/src/`; sem coluna nova.

---

## Probes (live, este worktree, pré-Apply)

Estado pré-Apply **esperado** (o tecto ainda não existe no produto `v1.1.5`).

### Adapter / vendor / T1

- `.cursor/skills/grill-card/SKILL.md`: **sem** tecto. Passo 1 = «Ler grilling e aplicar o loop». Passos 4/5: fronteira **zerou** + 6 seções → comentário exacto `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` Proibido: `process_event priorizar`, `gh project item-edit` Status, `/opsx:*` (inclui `/opsx:explore`).
- `.cursor/skills/grilling/SKILL.md`: Matt `❓`/`➡️`. Stop = «every branch of the design tree visited». Sem `AskUserQuestion` / `ask_user_question`. Dual definição de fronteira = residual D9/task 1.2 (override no adapter, **sem** editar o vendor).
- `.cursor/process-fsm.yaml` T1: `from=Em Refinamento` `event=priorizar` `actor=Alan` `to=Todo`. Sem task de yaml neste card (task 2.2 MUST NOT).
- `test_grill_card.py`: needles porta / host options / vendor Matt / stubs Grok / pin `v1.1.5`. **Sem** `ceiling_violation`, **sem** `fixtures/grill_ceiling/`. Pin-test `test_dsh_adapter.py` crava `v1.1.5` (task 4.3 sobe a tag deste card).

### Covenant-flow / explore / peles

- `## Grill-card`: disparo = body sem as 6 seções; relay `todas as options` / `não colapsa`; `Cliente dsh:`. **Não** nomeia o tecto (D5 é o Apply). `/opsx:explore` vive na secção *Card primeiro* («só para furo técnico, nunca para reescrever a história») — **não** é porta de Em Refinamento.
- Peles thin MUST Read do canónico (linhas não-vazias no body): `.grok` 3, `.dsh` 3, `.opencode` 3. Grok grill-card/grilling **sem** host tools. Live já cumpre o teto ≤8; Apply MUST NOT copiar o tecto para os stubs.

### Scanner D4 r2 (sonda das classes pinadas)

Não há helper live. Simulação das classes **estreitas** de Decision 4 r2 (SHA 40 **ou** 7–39 hex **misto** dígito+letra a–f; evento só `process_event`/`iniciar_design`; **não** `\b[0-9a-f]{7,40}\b` largo; **não** substring `priorizar`):

| Texto (Q/option de operador) | Classe que dispara | Resultado r2 |
| --- | --- | --- |
| `Não priorizar ainda` (Recommended) vs Alan arrasta | — (verbo PT fora da classe evento) | **pass** (assert unidade) |
| `A história está acabada` | SHA misto exige dígito; `acabada` só-letras | **pass** (assert unidade) |
| evidência `20260830` | SHA misto exige letra a–f; só-dígitos | **pass** (assert unidade) |
| evidência `2026-08-30` | hífens partem o token | pass |
| `Alan prioriza agora` | — | pass |
| quem sofre / o que passa/falha / o que não entra | `/` sem extensão git | pass |
| `process_event priorizar` | token `process_event` | **violation** (assert unidade) |
| `94f8ed41` | 8 hex misto | **violation** (assert unidade) |
| `WatchlistRow` / `` `WatchlistRow` `` | sem path / sem `_`/`()`/`.` no backtick | **pass (falso negativo)** |
| `frontend/src/pages/Monitor.tsx` vs `WatchlistRow` | path `/.+\.tsx` | violation (o fail_monitor vive disto) |
| `` `v1.1.5` `` | backtick + `.` | violation (tag = identificador; OK) |
| `` `grill-card` `` | hífen, sem `_`/`()`/`.` | pass |
| `` `enabled_tools` `` / `` `classify_qa_gate` `` | backtick + `_` | violation |
| `classify_qa_gate` sem backtick | — | **pass (FN)** |
| `iniciar_design` | token evento | violation |
| `iniciar o Design` | — | pass |
| `` `priorizar` `` | verbo PT, sem `process_event` | pass (FN aceite do aperto) |

`pass_operator.md` MUST **conter** `Não priorizar ainda` / `acabada` / `20260830` e o scanner MUST devolvê-las false — esconder as palavras no dump **não** basta (D4). Fixture `grill_ceiling/` ainda **ausente** (pré-Apply).

### Superfície visual

Nenhuma rota/HTML. Prototype N/A. Zero diff exigido em `frontend/src/` / `backend/`.

---

## Hunt (furos pedidos) — contrato vs live (r2)

| Furo | Contrato r2 | Live / artefacto | Disposition |
| --- | --- | --- | --- |
| Q1=A vs tasks | mesmo tecto em **todo** Em Refinamento (produto + harness); git id → body/Design | issue Entra; design D1; spec product+harness; task **1.1**; golden Monitor + 3 harness | **CLOSED** |
| Q2=A vs tasks | Other vazio / silêncio / «não percebi» reclassificam; **nunca** aceite da recomendada; Other #755 automático ≠ option; golden MUST NOT «não percebi» como *label* Recommended | D2 + D5 exacta + task **1.3** + spec 3 cenários stamp + fixtures `fail_stamp_other_empty` / `_silence` / `_nao_percebi`; task 4.1/4.2 needles Other/silêncio | **CLOSED** (era P1 r1) |
| Q3=A vs tasks | texto canónico exacto; só o *quando*; T1 Alan | task **1.2**; spec comentário pinado; adapter já tem a linha | **CLOSED** |
| vendor vs adapter | tecto no adapter; vendor Matt intocado; fronteira adapter ≠ árvore Matt | vendor: árvore inteira; adapter passo 1 aplica o loop; D9 + task 1.2 alinham passos 4/5; spec «MUST NOT keep asking design-tree»; task 1.4 vendor intocado; delta **ADDED** (não MODIFY o SHALL vivo «apply the vendored grilling primitive») | **P2** (override tem de ganhar; não P0/P1) |
| explore-as-door | porta = `grill-card`; `/opsx:explore` não substitui | adapter Proibido `/opsx:*`; covenant-flow explore ≠ reescrever história; spec cenário Explore; task **6.2** | **CLOSED** |
| skins bloat | stubs MUST Read; body ≤8; MUST NOT copiar tecto | live 3/3/3 linhas; D7 / task 3.1 / spec; pytest hoje só crava ≤8 no stub **dsh** | **CLOSED** no contrato; residual P3 |
| golden falha Qs boas de operador | aceite 6 + D4 r2: SHA misto; eventos só `process_event`/`iniciar_design`; `pass_operator` **inclui** as três frases; asserts unidade | sonda: as três frases **pass**; `process_event priorizar` / `94f8ed41` **violation**; spec cenário «Operator-only dump with priorizar acabada and compact date passes» | **CLOSED** (era P1 r1) |
| silent-Other=A | Não entra + Vocabulário `_Avoid: Other = A` + D2 + D5 + 1.3 + 3 dumps stamp; never Recommended | D5 nomeia Other vazio, silêncio e as frases; golden proíbe «não percebi» como label Recommended; Other do host fora de `options[]` | **CLOSED** (era P1 r1) |
| T1 ainda Alan | não mexer T1/colunas; comentário espera Alan; agente não `priorizar` | yaml T1 actor Alan; adapter proíbe o evento; spec «T1 remains Alan-only»; D8; tasks 1.2 / 2.2 | **CLOSED** |

---

## Critique (contrato vs live)

Issue #809 sintetizado (Q1–Q3 no body, congeladas). Pacote OpenSpec ADDED `grill-card` + `covenant-flow`. Prototype N/A justificado. Sem HTML. Sem rewrite `DESIGN.md`. Sem `## Design Critique` pré-preenchido. T7 humana permanece.

Patches r2 fecham os dois P1 da r1 no **contrato**: matcher D4 já não inverte o aceite 6; D5 / task 1.3 / spec / três fail-stamp alinham Other/silêncio/«não percebi» a never-Recommended. Q1/Q3/T1/explore/skins/vendor-intocado continuam pinados. Residuais = fronteira vendor vs adapter, schema dos dumps stamp, FNs do scanner estreito.

---

## Findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- **Fronteira vendor vs adapter.** Vendor intacto continua a definir sessão vazia = árvore Matt inteira; o SHALL vivo da spec main ainda diz «apply the vendored grilling primitive». D9/task 1.2 são o override (passos 4/5 + MUST NOT continuar Qs de desenho). Delta é ADDED, não MODIFY desse SHALL. Disposition: Apply MUST tornar o stop do adapter explícito e vencedor no canónico; MUST NOT editar `grilling/SKILL.md`.

- **Schema dos dumps stamp.** Task 4.2 exige que os três `fail_stamp_*` reprovem **além** do scanner de identificadores. O contrato não pina campos (ex. `other: empty` + `recorded: recommended`). Disposition: Apply MUST ter um checker de stamp distinto de `ceiling_violation`; MUST NOT falhar os ficheiros só pelo prefixo do nome; MUST NOT pôr «não percebi» como label `(Recommended)` (task 4.1).

- **Silêncio: D2 «reclassificam» vs spec «SHALL remain open».** Ambos proíbem gravar a recomendada. Disposition: Apply MUST NOT stamp A no silêncio; deixar a Q aberta **ou** reclassificar cumpre o DoD; MUST NOT tratar silêncio como aceite.

- **Fail dumps 795/799/801 vs scanner estreito.** Path class exige `/`+extensão; token de código exige backtick com `_`/`()`/`.`; função `classify_qa_gate` sem backtick **passa**. Disposition: as reconstruções MUST incluir um token scanner-positivo (path com `/`, backtick+`_()/`, SHA misto, ou `process_event`) para o golden de identificador disparar de verdade.

### P3

- `WatchlistRow` / `` `WatchlistRow` `` / `` `grill-card` `` / `` `priorizar` `` sem path/`process_event` fogem ao scanner (falso negativo). Residual já nomeado em Risks (golden **ambos**; fail_monitor precisa do path).
- `cafe2026` (hex misto 8) seria violation — residual de SHA apertado; Qs de operador típicas não usam esse token.
- SHA 7–39 na tabela D4 não escreve `\b` (o de 40 hex escreve). Unit asserts não pinam boundary. Apply SHOULD usar word-boundary como o 40-hex.
- Pytest ≤8 linhas hoje só no stub dsh; spec SHALL nas três peles. Task 3.1 cobre; 4.2 MAY assert grok/opencode. Live já 3/3/3.
- «Entra do card grelhado = comportamento observável» está no spec e no issue; task 1.1 não o repete. Needle no canónico no Apply.
- Tag `v1.1.6` ocupada → D6 bump patch; não bloqueia Design.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no UI).**
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM: sem task de estado/evento/`enabled_tools`. Status já Design; T7 Alan; T5 parent. `UI impact: none` não pulou Design nem Aprovação de Design. Yaml T1 intacto (actor Alan).
- Product UI Cripto: zero `frontend/src/` / `backend/` / HTML no Apply contract.
- Q1=A: tecto em todo Em Refinamento — fechado em 1.1 / spec.
- Q2=A: Other/silêncio/«não percebi» never Recommended — fechado em D2/D5/1.3/spec stamp + pass dump.
- Q3=A: texto canónico + *quando* — fechado em 1.2; T1 não muda de dono.
- #667 / #755 / #786 / bodies #795/#799/#801: Non-Goals; task 6.2 MUST NOT reescrever / reabrir.
- P1 r1 (scanner largo; silent-Other=A): **fechados** no pacote r2. Sonda das classes D4 r2 confirma os cinco asserts de unidade.

---

## Trace

1. Live: adapter sem tecto; vendor = árvore inteira; T1 Alan; peles thin; explore não é porta; golden de tecto inexistente (pré-Apply).
2. Issue #809 DoD = tecto operator em todo card; não percebi reclassifica; Other/silêncio ≠ A; comentário pinado; T1 Alan; explore não porta.
3. Design D1–D9 r2 + D5 exacta (Other/silêncio) + D4 scanner estreito + pass dump com as três frases + 3 fail-stamp; Q1–Q3 congeladas; Open Questions vazias (P1 r1 declarados fechados — esta onda verificou).
4. Specs cobrem tecto, reclassify Other/silêncio/frases, fronteira, golden (asserts unidade + pass dump + stamp), disparo, peles, frase D5, pin patch. `openspec validate --strict` verde.
5. Tasks 1.1–1.4 / 2.1–2.2 / 3.1 / 4.1–4.3 / 5–7. Furos r1 P1 fechados; residual P2 = vendor stop / schema stamp / fail dumps com token positivo.

---

## Disposition

| ID | Severidade | Estado | Notas |
| --- | --- | --- | --- |
| scanner `priorizar` + hash `acabada`/`20260830` vs Qs boas | P1 r1 | **CLOSED** | SHA misto + eventos estreitos; pass dump contém as frases; asserts unidade verdes na sonda |
| silent-Other=A (D5 / 1.3 / cenário golden) | P1 r1 | **CLOSED** | D5+1.3+spec+3 fail-stamp; never Recommended; Other ∉ `options[]` |
| vendor fronteira vs adapter stop | P2 | residual | D9/1.2 têm de ganhar ao passo 1; MUST NOT editar vendor |
| schema dumps stamp | P2 | residual | checker ≠ scanner; sem label «não percebi» Recommended |
| silêncio remain-open vs reclassify | P2 | residual | ambos = não stamp A |
| fail dumps harness sem token scanner-positivo | P2 | residual | path `/` ou backtick+`_()/` ou SHA misto ou `process_event` |
| Q1 / Q3 / T1 / explore / skins | — | **CLOSED** | |
| `WatchlistRow` sem path; ≤8 só dsh pytest | P3 | accepted-residual | |

Zero P0/P1 abertos. Não há finding determinístico sem classificação. Detector/browser visual **N/A (no UI)**. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido.

Pai: com A também PASS e zero P0/P1, colar `## Design Critique` e `process_event submeter_design`. Sem polish neste transcript. MUST NOT editar `design.md` daqui. MUST NOT `process_event` neste filho.

### Verdict

**PASS**
