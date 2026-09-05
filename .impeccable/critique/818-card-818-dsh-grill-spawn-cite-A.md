# Snapshot — Assessment A · ronda 2 · card #818 `card-818-dsh-grill-spawn-cite`

- Card: #818 — kaizen: `dsh_grill_spawn` não deve deny spawn de Design/Apply só por citar `grill-card`
- Change: `card-818-dsh-grill-spawn-cite`
- Critic: Assessment A ronda 2 (isolado; inherit de modelo; sem transcript do pai; sem partilha com B; sem nested agent)
- Modelo: inherit
- UTC: 2026-09-04T20:47:00Z
- Tuple (este isolado): hook `bound_card=⊥` `q_git=develop` `q=None`. Prompt: worktree `card-818-dsh-grill-spawn-cite`; Write produto deny. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit/push. Não editar `design.md` / proposal / tasks / specs / HTML / `backend/` / `frontend/src/`.
- Board: Project 1 — **Status=Design** (`optionId=bd47fbe8`; item `PVTI_lAHOAAHtBM4BV8b2zg5Mf0w`). Issue OPEN. Labels `priority:P0` `front:operacao` `type:operacao` `kaizen`. `UI impact: none` não saltou coluna.
- Digest `design.md` **medido**: sha256 `fd87ee73a5aa313c9ac5e694e69b04770b4a01e5889ad60be9a39e19e53cfada` · **2238** palavras (`wc -w` = `str.split`) · 15882 bytes · 144 linhas. **Coincide com o digest reclamado.**
- `openspec validate card-818-dsh-grill-spawn-cite --type change --strict`: **valid**
- `## Design Critique` / `Design Agent verdict` em `design.md`: **ausentes** (filho autor correto)
- UI impact: **none** (harness/plugin dsh + goldens + pin; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: **N/A** — `UI impact: none`; zero HTML `frontend/public/prototypes/*818*`; sem rewrite de `DESIGN.md`; sem pipeline Impeccable visual; Playwright desta coluna = N/A. Snapshot visual N/A no `design.md` (T7 visual). Este ficheiro é o snapshot git-tracked da crítica de processo.
- Overlay live: `pin: v1.1.6`; `clients.dsh.auto: false`. Origin `oalansilva/covenant-flow` tags até `v1.1.6` (`v1.1.7` **livre** neste instante).
- Matcher live (pré-Apply, esperado): `scripts/process-fsm/dsh_plugin_lib.js` `isGrillShapedSpawn` — tools exactas `subagent` / `subagent_fork`; needle `grill-card` via `toLowerCase()` + `includes` (não regex) em `description`/`prompt` **e** `JSON.stringify(args)` L93–96; parse de `arguments` string; parse fail → string crua; reason `dsh_grill_spawn`; `next()` não corre no deny. Listener `.dsh/plugin/process-fsm-guard.js` **antes** de `isCordisRestricted` / `runGuard` (live `v1.1.6`: grill → cordis → `runGuard`). `guard.py` fonte **sem** `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`. G12 **ausente** em `test_dsh_grill_spawn.py` (G1–G11 só).
- P1 r1 (onda B, no prompt desta ronda): D4 «listener unchanged» lido como byte-identical `v1.1.6` clobber de #817 `agent/request` e `dsh_reasoning_effort_spawn`. Autor r2: nomeia #817; Apply rebase no tip; listener inalterado = grill deny primeiro antes de `runGuard`, não bytes; manter listeners do sibling; pin-tests após rebase.
- Method: issue #818 (REST); comentário T1 canónico exacto (`issuecomment-5519683554`); `proposal.md` / `design.md` D1–D6 + Apply contract / Risks; `tasks.md` 1–6 (cópia r2 + leftover r1); deltas `process-harness` + `covenant-flow`; live `isGrillShapedSpawn` + G1–G11; pin-tests `v1.1.6`; sibling Design `#817` no mesmo board. Adversário = Apply TDD que verdeia **os asserts listados** (G12 allow / G1 deny no mesmo ficheiro; N3 Python sem matcher; spec «não reverter #817»), não a prosa «MUST distinguish».

---

## Brief (só neste snapshot)

Incidente `session-679a762b` (#790 turno 2): o primeiro spawn do Design-autor caiu em `dsh_grill_spawn` porque o prompt citava `grill-card fronteira vazia` (ritual já fechado), não porque o filho ia grelhar. Retry sem a palavra passou — o modelo não pode aprender a omitir o ritual nem a grelhar no filho (proibido no dsh). Outcome: T3→T5 não atrasa por citação; papel grill continua deny. Direction: apertar **só** `isGrillShapedSpawn` (dois haystacks + marcadores pinados; description ganha; nested só chaves `description`/`prompt`; MUST NOT `JSON.stringify` o objecto). Scope: plugin dsh + goldens + pin patch `v1.1.7` (ou próximo livre **após rebase** no tip, irmão #817). Fora: filho grill no dsh; Cursor/Grok; `decide()`; #786/#790 reabertos; reverter #817; pin a partir de `v1.1.6` que clobber o sibling; produto UI; ensinar a omitir a palavra.

Audience: operador do board no cliente dsh. Personas visuais Impeccable: **N/A** (sem ecrã). Personas de processo: (1) pai Design-autor que cita o DoD; (2) pai que tenta spawnar filho `grill-card N`; (3) Apply/reviewer que cita `grill-card dod` / `closed grill`.

---

## 1. Escopo vs issue grelhado #818

Body live: seis seções DoD; **Fronteira: vazia**; comentário canónico `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` Design **não** reentrevista. Residual da grelha (*como* apertar o match) está fechado em D1–D6, não reaberto como Q. Open Questions: P1 (#817 pin race) fechado em D4/D5 + Apply contract.

| Aceite / Entra | Design r2 | Tasks / spec |
| --- | --- | --- |
| Papel vs citação no deny dsh | D1: description com `grill-card` → deny; prompt com needle **e** marcador pinado → não este deny; prompt com needle sem marcador → deny | tasks 2.1–2.2; spec `dsh Guard denies grill-shaped subagent spawn` |
| Design-autor + `grill-card fronteira vazia` passa **este** deny (`next()` corre) | G12; critério 1 literal | task 1.1; spec scenario Design-author citation |
| Apply / reviewer citam DoD grelhado | G12b/c (`grill-card dod` / `dod grelhado` / `closed grill` + `grill-card`) | task 1.2; spec isolated Apply/reviewer |
| Papel grill continua deny; #786 não reabre | G1/G2/G6/G10 intactos; Non-Goals; spec MUST NOT reopen #786 | tasks 1.4, 2.3, 5.2 |
| Guard Python sem matcher | D3/D4; G11/N3 | task 2.3, 3.2 |
| Cursor `Task` / Grok `spawn_subagent` / OpenCode `task` fora | G5 intacto; D4 | spec Cursor-shaped scenario |
| Canal produto + pin Cripto (como #786) **sem clobber #817** | D5: rebase no tip/tag existente; tag = a deste card; pin-tests sobem para **essa** tag, não `v1.1.7` no vácuo; nunca major | tasks 4–5 (cópia r2); spec `Citation-vs-role grill deny ships as product patch pin` + scenario clobber |
| Listener «inalterado» = ordem + reason, **não** bytes | D4: grill **primeiro** deny de spawn, antes de `runGuard`, reason `dsh_grill_spawn`, sem `next()`; MUST NOT byte-identical `v1.1.6`; MUST NOT reverter `dsh_reasoning_effort_spawn` / `agent/request` | task 2.3 r2; spec scenario `grill spawn deny stays first and does not revert sibling #817` |
| Nested stringify = FP de citação noutro campo | D2: walk só `description`/`prompt`; G12d allow em `inner.fact`; G10 nested `inner.prompt` permanece true | task 1.3 |
| FN `refine 701` sem needle **não** é deste card | Non-Goals + Risks | — |

Não entra (e não foi alargado): filho grill no dsh; mudar Cursor/Grok; reabrir Design #790; matcher em `decide()`; deny global de spawn; `backend/` / `frontend/src/`; pin major; regex; UI/HTML/`DESIGN.md`/Playwright desta coluna; reverter #817.

Facto actualizado vs body da grelha (não é reentrevista): grelha disse «#786 ainda open; change ainda não arquivada». Disco deste worktree: `openspec/changes/archive/2026-09-03-card-786-dsh-grill-root/` existe. Board: #786 **Pronto** (issue GitHub ainda `state=open` — fecho de issue ≠ recorte deste card). #790 **Pronto**. #817 **Status=Design** (item `PVTI_lAHOAAHtBM4BV8b2zg5MgL8`).

---

## 2. Superfície visual

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, copy, tokens | **none** — Apply MUST NOT |
| `backend/` de app | **none** — Apply MUST NOT |
| Protótipo HTML / Playwright / `DESIGN.md` / Impeccable visual | **N/A** justificado |
| Card GUI dsh (`:3080`, `ask_user_question`) | **vendor** — não prototipar; este card não toca a grelha no root |
| Texto de skills Cursor/Grok grill / comentário T1 | **intocado** (processo; não UI produto) |
| Reason `dsh_grill_spawn` no plugin | processo (string de deny, não ecrã Cripto) |

`live_route: N/A harness-only`. Clone gate isento. `UI impact: none` + Prototype N/A com justificativa não vazia.

---

## 3. Regressão de produto / ops (#786 / #790 / #817 / Cursor-Grok / Python / pin)

| Contrato vivo | Este design r2 |
| --- | --- |
| **#786** root dsh grelha; MUST NOT spawnar filho grill; fail-closed de **papel**; matcher fora de `decide()`; G1–G11 via `apply`+pre-execute; G5 tools Cursor/Grok/OpenCode `next()`; FN `refine 701` aceite | Não reabre. G1/G2/G6/G10 de papel permanecem deny. G5/G11/N3 intactos. Stub dsh `grill-card` medido: 3 linhas não-vazias no body (≤8). |
| **#790** Design-autor já entregou após retry | Non-Goal: não reabrir o Design do #790. Este card só desbloqueia o briefing que cita o ritual. |
| **#809** pin `v1.1.6` tecto | Overlay live `v1.1.6`; este card bump patch **após rebase**, não reescreve tecto. |
| **#817** `sanitizeReasoningEffort` / `agent/request` (após `await next()`) / `agent/request-error` / gate `dsh_reasoning_effort_spawn` **depois** do grill e **antes** de cordis; mesmos ficheiros `dsh_plugin_lib.js` + `.dsh/plugin/process-fsm-guard.js`; hoped tag `v1.1.7` | Nomeado no Context, Non-Goals, D4, D5, Apply contract, Risks, Migration, spec process-harness scenario sibling, spec covenant-flow clobber. Funções **disjuntas** (haystacks vs sanitizer). Apply #818 MUST rebase no tip; MUST NOT pin a partir de `v1.1.6` depois do sibling; MUST NOT reverter listeners. Rollback = `v1.1.6` **só** se o sibling ainda não estiver pinado; senão a tag do sibling. |
| Cursor `preToolUse` | Live `.cursor/hooks.json` matcher `Write\|StrReplace\|Delete\|EditNotebook` — spec exige que continue assim. |
| OpenCode `runGuard` em todo `tool.execute.before` | Matcher MUST NOT ir para Python (senão Task com `grill-card` no prompt passa a deny). G11 `decide()` allow permanece. |
| `clients.dsh.auto: false`; `SCHEMA_MAJOR` 1; sem linha `AGENTS.md`; sem vendor `deepseek-harness`; sem `process-fsm.yaml` | Spec covenant-flow + D5. |
| Rollback | pin Cripto `v1.1.6` **condicionado** ao sibling; sem migration; sem rebuild frontend. |

Plugin omitido / `--patch` ausente → spawn allow (#782): residual aceite, não deste card.

G1 live (fonte do plugin) assert `isGrillShapedSpawn` **antes** de `isCordisRestricted` e `runGuard` — **sobrevive** ao insert #817 entre grill e cordis; não exige bytes de `v1.1.6`.

---

## 4. Matcher vs goldens G1 / G2 / G6 / G10 / G12 (simulado neste isolado)

Algoritmo D1–D2 (pós-Apply; live ainda é stringify — G12 **RED** no matcher actual, como o TDD exige):

1. Tools exactas `subagent` / `subagent_fork` (senão false).
2. Recolher strings `description` e `prompt` em qualquer profundidade; `arguments` string → `JSON.parse` ou crua como prompt; **proibido** `JSON.stringify` do objecto.
3. Se alguma `description` contém `grill-card` → **true** (deny). Citação no prompt **não** salva.
4. Senão, se nenhum prompt contém `grill-card` → **false**.
5. Senão, se o prompt com needle contém **algum** marcador pinado → **false** (citação). Senão → **true** (papel via prompt).

Marcadores pinados (minúsculas; `includes`; Apply MUST NOT alargar): `fronteira vazia`, `do not re-interview`, `não reentrevistar`, `do not invoke grill-card`, `não invocar grill-card`, `closed grill`, `grill-card dod`, `dod grelhado`, `grilled dod`.

| Golden | Payload | Live hoje (stringify) | D1–D2 | Contrato |
| --- | --- | --- | --- | --- |
| **G1** | description `grill-card 701` | deny | deny | permanece |
| **G2** | description `refine 701`, prompt `Please run Grill-Card on the issue` (sem marcador) | deny | deny | permanece |
| **G6** | `arguments` JSON string `{"description":"grill-card 701"}` | deny | deny (parse → description) | permanece |
| **G10 nested** | `inner.prompt` `x grill-card y` | true (stringify **e** walk de `prompt`) | true | permanece |
| **G10 neg** | `grill_card` / `grill card` | false | false | permanece |
| **G10 parseFail** | raw `please run grill-card 701` | true | true (crua = prompt, sem marcador) | permanece |
| **G12** | description `design-autor 818`, prompt contém `grill-card fronteira vazia` | **deny (FP do incidente)** | **allow** (`next()` true; reason ≠ `dsh_grill_spawn`) | **novo; TDD RED no live** |
| **G12b** | description `apply 818`, prompt `grill-card dod` / `grill-card`+`dod grelhado` | deny | allow | novo |
| **G12c** | description `diff-reviewer 818`, `closed grill` + `grill-card` | deny | allow | novo |
| **G12d** | `inner.fact` com `grill-card`, sem needle em description/prompt | **deny (stringify)** | **allow** | fecha o alargamento #786 |
| G4/G5/G11 | Design-autor sem needle; Task/spawn_subagent/task; `decide()` allow | allow / não este deny | intacto | — |

G2 `Please run Grill-Card` → `toLowerCase` inclui `grill-card`, sem marcador → deny. O incidente (`grill-card fronteira vazia`) casa o marcador `fronteira vazia` **e** a needle; description G12 MUST NOT conter `grill-card` (task 1.1). Description ganha: `grill-card 701` + prompt com `fronteira vazia` continua G1 deny.

**FP (falso positivo) pós-patch:** spawn Design/Apply/review com needle só no prompt **e** marcador pinado deixa de ser este deny — é o aceite. FP residual: description contém `grill-card` por acidente → ainda deny. Critério 1 exige description **não** papel; G4/G12 usam `design-autor N`. Não é P0.

**FN (falso negativo) pós-patch:**

- Description `refine 701` sem needle `grill-card` (Q6 #786) — **fora deste card**.
- Papel só noutro campo (`inner.task`, `inner.fact`) — G12d **quer** este FN; stringify para o tapar reintroduz o incidente.
- Prompt papel **e** marcador stuffed (`Please run Grill-Card` + `fronteira vazia`) com description sem needle → allow deste deny. Aceite em Risks: description `grill-card 701` (padrão real do spawn grill-card) ainda deny.
- «grelha a história» sem substring `grill-card` — mesma classe FN #786.

Walk D2 vs live `grillHaystacks`: live empurra description, prompt **e** `JSON.stringify(args)` (L93–96). D2 remove o stringify; recursa objectos/arrays só para achar chaves `description`/`prompt`. Cyclic → WeakSet/try-catch, não throw. G10 nested continua true porque `inner.prompt` é chave `prompt`.

---

## 5. P1 r1 fechado — pin / listener / sibling #817

Sonda r2 (o que o autor reclamou vs disco):

| Reclamado | Disco r2 | Fecha P1? |
| --- | --- | --- |
| Nomeia #817 | Context L5: issue + change `card-817-dsh-reasoning-effort` + Status=Design + ficheiros + ordem grill → `dsh_reasoning_effort_spawn` → cordis → `runGuard` + `agent/request` / `agent/request-error`. Non-Goals: reverter #817 / pin `v1.1.6` que clobber. Spec covenant-flow L4. Board live: #817 Design. | **sim** |
| Apply rebase no tip | D5 + Apply contract passo 1 **antes** do helper; task 4.1 r2; spec «Apply SHALL `gh api` tags **and** rebase»; scenario `Pin from v1.1.6 must not clobber sibling #817`. Fallback de **número** ≠ rebase. | **sim** |
| Listener inalterado = ordem, não bytes | D4: primeiro deny de spawn, antes de `runGuard`, reason exacta, sem `next()`; **não** exige `.dsh/plugin/process-fsm-guard.js` byte-identical a `v1.1.6`. Task 2.3 r2 idêntico. Spec: «That order is the meaning of «listener unchanged» — the plugin file MUST NOT be required byte-identical to pin `v1.1.6`». | **sim** |
| Manter listeners do sibling | D4 / Apply contract passo 3 / task 2.3 r2 / task 6.2 r2 / spec scenario sibling THEN gate e `agent/request` remain. Gate #817 MAY depois do grill, antes de cordis — casa com #817 task 2.4 `(1) isGrillShapedSpawn (2) dsh_reasoning_effort_spawn (3) isCordisRestricted (4) runGuard`. Funções disjuntas vs `sanitizeReasoningEffort`. | **sim** |
| Pin-tests após rebase | D5 + task 3.2 r2: sobem `v1.1.6` → **esta** tag depois do rebase; MUST NOT hardcode `v1.1.7` no vácuo. Spec THEN overlay `pin:` = tag deste card after rebase. Live pin-tests ainda `v1.1.6` (pré-Apply esperado). | **sim** |

Sibling #817 (lido só como contrato vizinho, não como crítica B): D8/#817 já trata a colisão com #818 como residual nomeado e também manda rebase para **não** reverter haystacks deste card. Os dois Designs agora exigem tip-first. `v1.1.7` livre agora; não é THEN exclusivo.

**Porque não reabre P1:** o clobber exigia um freeze byte-a-byte do plugin `v1.1.6`. Esse freeze **já não é** o THEN. Spec + D4/D5 + Apply contract + tasks r2 (2.3 / 3.2 / 4.1 / 4.2 / 5.2 / 6.2) + preamble `Não reverter #817` fecham o caminho. G1 asserts de ordem (grill < cordis < `runGuard`) continuam verdes com o insert #817 — não são prova de bytes. Rollback deixou de ser reset cego a `v1.1.6`.

---

## 6. Apply contract testável

Ordem TDD explícita e adversária (r2):

1. `gh api` tags **e** rebase o checkout do produto na tag/tip que já existir (incl. #817). MUST NOT partir de `v1.1.6` a ignorar o sibling.
2. Acrescentar G12/G12b/G12c/G12d em `test_dsh_grill_spawn.py` **antes** de mudar o helper — live **deve falhar G12** (medido: stringify trata o prompt do incidente como papel; zero `test_g12*`).
3. Reescrever haystacks em `dsh_plugin_lib.js` (D1–D2). `guard.py` **não** se edita. Plugin: grill **primeiro**, reason, sem `next()` — **não** byte-identical a `v1.1.6`. MUST NOT reverter `dsh_reasoning_effort_spawn` / `agent/request`.
4. `pytest scripts/process-fsm/test_dsh_grill_spawn.py`: G1–G11 verdes; G12 allow; N3 fonte `guard.py` sem as três needles. Pacote `scripts/process-fsm` sem GitHub verde. Pin-tests sobem `v1.1.6` → tag deste card **após rebase**.
5. Commit + tag patch no produto = **esta** tag após o rebase (MAY `v1.1.7` se livre e tip ainda `v1.1.6`; senão próximo patch). `install.sh --pin` continua a copiar nucleus/adapters.
6. `implantar --pin` no Cripto; overlay `pin:` = essa tag; `clients.dsh.auto: false`; zero diff `backend/` / `frontend/src/`; MUST NOT clobber #817.

G12 MUST `import { apply }` + `tools/pre-execute` (mesmo caminho G1–G9), não unitário Python em `decide()`. G10 continua unitário JS. Asserts pinados: `nextCalled === true` e reason **não** contém `dsh_grill_spawn` no allow; G1 `nextCalled === false` + `dsh_grill_spawn`.

Furo fraco (P3, não bloqueia): task 1.2 escreve prompt `` `dod grelhado` `` sem exigir co-ocorrência de `grill-card`. Sem a needle, o live **já** permite (passo 4 do algoritmo). Apply MUST escrever `grill-card` **e** `dod grelhado` no mesmo prompt para o golden ir RED no matcher actual. G12 (frase exacta do incidente) e G12c (`closed grill` + `grill-card`) são RED no live.

---

## Critique (heurísticas de processo; Nielsen visual N/A)

Sem ecrã de produto. Heurísticas mapeadas ao deny/spawn:

1. **Visibilidade do estado do sistema** — o pai vê `dsh_grill_spawn` só quando o trabalho é grelhar, não quando cita o DoD. G12 torna o incidente visível como regressão testável. #817 permanece visível como deny *outro* (`dsh_reasoning_effort_spawn`) se o tip o tiver.
2. **Correspondência com o mundo** — vocabulário grelhado (papel ≠ citação) está no algoritmo, não numa allow-list de identity (`design-autor` / `apply`) rejeitada em D1.
3. **Controlo / liberdade** — spawn Design/Apply/review deixa de ser um beco que ensina a omitir `grill-card`. Filho grill continua sem controlo no dsh (G1).
4. **Consistência** — Cursor/Grok/OpenCode Task fora deste deny (G5); Python sem matcher (G11/N3). Quatro clientes não ganham a mesma regra por acidente. Irmão #817 no mesmo nucleus não é apagado por «listener unchanged».
5. **Prevenção de erro** — description ganha; lista de marcadores **fechada**; rebase obrigatório **antes** do helper (D5) previne clobber do sanitizer.
6. **Reconhecimento** — G12 usa a frase literal do incidente (`grill-card fronteira vazia`).
7. **Flexibilidade** — PT/EN na lista (`fronteira vazia` / `do not re-interview` / `não reentrevistar` / `dod grelhado` / `grilled dod`). Tag MAY `v1.1.7` ou próximo patch.
8. **Design minimalista** — um helper, zero UI, zero `AGENTS.md`, zero T1 novo.
9. **Recuperação de erro** — outro deny do Guard ainda pode aplicar depois de `next()` neste matcher (critério 1). Rollback = pin da tag anterior que ainda contenha o sibling.
10. **Ajuda** — D6: o ritual **continua citado** nas skills; a «solução» não é omitir.

Carga cognitiva do Apply: tabela G1–G12 + lista de 9 marcadores + ordem TDD + rebase #817. Suficiente para não improvisar regex/`decide()`/freeze de bytes.

---

## Audit (técnico; a11y/perf visual N/A)

- **a11y / contraste / teclado / viewports:** N/A — sem superfície visual.
- **Console / rede / HTML:** N/A.
- **Helper live L77–108:** `JSON.stringify(args)` ainda presente — **pré-Apply esperado**, não defeito do design.
- **Listener live L20–29:** `isGrillShapedSpawn` antes de cordis/`runGuard`; reason exacta `process-fsm-guard deny reason=dsh_grill_spawn`; `next()` não chamado no deny. Zero `agent/request` neste pin `v1.1.6` (pré-#817; esperado).
- **`guard.py`:** grep das três needles = 0.
- **Cyclic:** D2 manda WeakSet/try-catch; live já ignora stringify cíclico.
- **`run_in_background`:** G3 permanece deny (G1 + flag false); spec inalterada.
- **Skins grill-card:** dsh stub 3 linhas não-vazias no body; spec MUST stay ≤8; este card não as edita.
- **OpenSpec:** change valid `--strict`. Capabilities: modified `process-harness` + `covenant-flow`; none new — alinhado ao proposal.
- **`tasks.md`:** 30 checkboxes; **duas** cópias de `## 1.`–`## 6.` (15+15). Cópia r2 (L1–34) fecha P1. Cópia r1 leftover (L37–68): 2.3 «permanece … antes de `runGuard`» **sem** «não bytes»; 4.1 só bump de número **sem** rebase; 5.2/6.2 sem «não clobber #817». Preamble L1 ainda diz `Não reverter #817`. Spec SHALL prevalece sobre o leftover. Não é P1 (o leftover não **exige** restaurar bytes `v1.1.6`; D4/D5/spec/tasks r2 fecham o clobber). É P2 de higiene Apply.

---

## Trace

| Passo | Evidência |
| --- | --- |
| Issue #818 | REST `GET /repos/oalansilva/crypto/issues/818`; board `gh project item-list` → Status=Design |
| Comentário T1 | `issuecomment-5519683554` texto canónico exacto |
| Artefactos | `proposal.md` `design.md` `tasks.md` `specs/process-harness/spec.md` `specs/covenant-flow/spec.md` `.openspec.yaml` |
| Digest | `sha256sum` + `wc -w` = reclamado `fd87ee73…` / 2238 |
| Matcher / testes | `dsh_plugin_lib.js` L75–108; `test_dsh_grill_spawn.py` G1–G11 (zero G12); plugin L17–29 |
| Pin | overlay `v1.1.6`; `gh api repos/oalansilva/covenant-flow/tags` até `v1.1.6`; pin-tests L524/L539 e `test_grill_card.py` L256 |
| Sibling | `#817` Design `PVTI_lAHOAAHtBM4BV8b2zg5MgL8`; design #817 D8/task 2.4 ordem grill → effort → cordis → `runGuard` + `agent/request` |
| Archive #786 | `openspec/changes/archive/2026-09-03-card-786-dsh-grill-root/` |
| Validate | `openspec validate … --strict` valid |
| UI | zero prototype 818; `live_route: N/A` |
| Design Critique no design.md | ausente |
| P1 r1 | fechado em D4/D5 + spec sibling/clobber + tasks r2 2.3/3.2/4.1/6.2 |

Detector visual / browser / Playwright: **N/A** justificado (Assessment B desta onda não precisa de URL viva de produto; este A não spawna B).

---

## Achados

- P0: (nenhum aberto).
- P1: (nenhum aberto). P1 r1 (listener «unchanged» = bytes `v1.1.6` clobber #817 `agent/request` / `dsh_reasoning_effort_spawn`) **fechado** em D4 (ordem+reason, não bytes) + D5 (rebase no tip; pin-tests para **esta** tag; fallback de número ≠ rebase) + Apply contract passos 1/3/5/6 + Non-Goals + spec process-harness scenario sibling + spec covenant-flow clobber + tasks r2 2.3/3.2/4.1/4.2/5.2/6.2. Sonda: #817 nomeado; tip origin ainda `v1.1.6`; funções disjuntas; G1 ordem sobrevive ao insert do sibling.
- P2: `tasks.md` dual-write — cópia r1 leftover (L37–68) omite rebase / «não bytes» / keep-sibling. Spec + D4/D5 + cópia r2 + preamble prevalecem; leftover não exige freeze. Disposition: **accepted-residual** (higiene Apply; não reabre P1).
- P2: stuffed citation — prompt papel (`Please run Grill-Card`) + marcador pinado e description sem `grill-card` passa este deny. Disposition: **accepted-residual** (Risks; G1 description papel continua deny).
- P2: FN papel noutro campo / `refine 701` sem needle. Disposition: **accepted-residual** (fora do card; stringify reintroduz o incidente).
- P2: lista de marcadores incompleta — briefing que só diz «skill grill-card» sem marcador ainda deny. Disposition: **accepted-residual** (G12b/c + `fronteira vazia` cobrem o aceite; Apply MUST NOT alargar).
- P2: plugin omitido / `--patch` ausente → spawn allow (#782). Disposition: **accepted-residual** (não deste card).
- P3: task 1.2 `dod grelhado` isolado pode verdear no live (sem needle `grill-card`). Disposition: **accepted-residual** — G12/G12c já são RED no live; Apply deve co-ocorrer a needle no golden b.
- P3: `description`/`prompt` como array de strings não entra no haystack (D2 só empilha se string). Envelope dsh real usa strings. Disposition: **accepted-residual**.
- P3: vários prompts (citação top-level + `inner.prompt` papel) — concat vs per-string não está pinado; goldens não misturam. Envelope real tem um prompt. Disposition: **accepted-residual**.
- Dual-write T0–T17 / matcher em `decide()` / deny Cursor `Task` / deny global subagent / Auto dsh / produto UI / superfície visual sem classificar / Design Critique pré-PASS no `design.md` / vendor harness / reabrir #786/#790 / ensinar omitir a palavra / freeze byte-identical do plugin `v1.1.6`: **false**.

---

## Disposition

Zero P0/P1 abertos. P1 r1 fechado: «listener inalterado» = grill primeiro antes de `runGuard` + reason, **não** bytes; Apply rebase no tip; pin-tests após rebase; listeners #817 mantidos. Recorte = issue grelhado; *como* D1–D6 fecha o residual da grelha sem reabrir #786 nem reverter #817. G12 é o aceite do incidente e falha no matcher live (TDD). Prototype N/A justificado; UI classificada. Residuais (tasks leftover, stuffed, FN #786, lista fechada) = P2/P3 aceites no design.

Pai: pode `submeter_design` se B também PASS. Sem polish neste transcript. MUST NOT editar `design.md` daqui. MUST NOT `process_event`.

---

## Verdict

**PASS** (zero P0/P1; P1 r1 fechado; Prototype N/A justificado; UI impact none classificado; crítica isolada Assessment A ronda 2; snapshot não vazio; digest `design.md` confirmado `fd87ee73…` / 2238)

## Snapshot

`.impeccable/critique/818-card-818-dsh-grill-spawn-cite-A.md`
