## 1. Lib: grill-shaped spawn helper (JS only)

- [x] 1.1 Em `scripts/process-fsm/dsh_plugin_lib.js`, exportar `isGrillShapedSpawn(tool, args)` : true só se `tool` é exactamente `subagent` ou `subagent_fork` **e** a substring `grill-card` (case-insensitive, `includes` após `toLowerCase()`, **não** regex) aparece em `args.description` ou `args.prompt`
- [x] 1.2 Aceitar `args` objecto (shape live `ToolExecution.arguments`) **e** string JSON (shape do dump `5a6c8c5c`); parse fail → varrer a string crua; nested → `JSON.stringify` do objecto parseado; `run_in_background` irrelevante; `grill_card` / `grill card` **não** match
- [x] 1.3 **Não** editar `guard.py` (fonte MUST NOT conter `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`); não editar `dsh_stubs.py`, `grok_stubs.py`, `process-fsm.yaml`, `AGENTS.md`, `backend/` nem `frontend/src/`; não vendorar `deepseek-harness`

## 2. Plugin Guard: deny grill-shaped antes de runGuard

- [x] 2.1 `.dsh/plugin/process-fsm-guard.js`: no listener `tools/pre-execute` já existente, chamar `isGrillShapedSpawn` **antes** de `isCordisRestricted` / `runGuard`; match → `{ kind: "deny", reason: "process-fsm-guard deny reason=dsh_grill_spawn" }` sem `next()`
- [x] 2.2 Manter ordem #784: listener deny **antes** de `registerProvider`; `typeof ctx.skills?.registerProvider === "function"`; try/catch — throw do provider MUST NOT impedir deny write **nem** deny grill-shaped
- [x] 2.3 `isCordisRestricted` continua só `cordis_*`; write-like fail-closed intacto; `subagent` não-grelha continua `next()` (fail-open); **não** deny `Task` / `spawn_subagent` / OpenCode `task`; **não** alterar `.dsh/cordis.patch.yml`; **não** alterar `.cursor/hooks.json`

## 3. Skills canónicas (dois ramos rotulados)

- [x] 3.1 `.cursor/skills/grill-card/SKILL.md`: o copy **live** usa `**não** chama` e H2 `## Perguntas da rodada (host)`. Depois do Apply, após `_plain` (ver 4.6), frases `não chama a ferramenta do host`, `o pai spawna`, `dump d5`, `quem chama` MUST viver **somente** sob `## Cliente: Cursor e Grok`. `## Precondição` MAY manter Status=`Em Refinamento` + id N; após `_plain` MUST NOT conter `filho`, `spawna`, `relaying`, `dump d5`, `ask_user_question`, `askuserquestion`, `não chama`. O H2 `## Perguntas da rodada` / `## Perguntas da rodada (host)` MUST NOT permanecer secção partilhada de topo (mover nested `###` ou dois ramos). `## Cliente: dsh` após `_plain` MUST conter a substring **contígua** `root chama ask_user_question`; MUST NOT conter `não chama ask_user_question`; MUST NOT conter `não chama a ferramenta do host`; MUST NOT `subagent`/`subagent_fork` (nem `run_in_background: false`); T1 canónico só depois das respostas ou fronteira só-fato. Frontmatter spawn prompt MAY ficar. Como (DoD / `gh issue edit`) MAY ficar partilhado **sem** as frases de spawn/host. MUST NOT deixar `**não** chama` / «quem chama … é o **pai**» em Precondição/Perguntas partilhadas (furo `5a6c8c5c`)
- [x] 3.2 `.cursor/skills/covenant-flow/SKILL.md` secção `## Grill-card`: **uma** linha prefixada `Cliente dsh:` (dsh não spawna filho grill). Preservar “O **pai** spawna” + “todas as options” / “não colapsa”
- [x] 3.3 Não alongar `.dsh/skills/*`; não nomear host tool em `.grok/skills/*`; não mudar `description` YAML de forma a forçar regeneração Grok **ou**, se mudar, regenerar stubs thin sem `AskUserQuestion`/`ask_user_question`

## 4. Goldens pytest `scripts/process-fsm`

- [x] 4.1 G1–G3: `import { apply } from` `.dsh/plugin/process-fsm-guard.js` + `tools/pre-execute` deny `subagent` description `grill-card 701`, `subagent_fork` needle só em `prompt` mixed-case, e G1 com `run_in_background: false`; `nextCalled === false`; reason contém `dsh_grill_spawn`. MUST NOT satisfazer G1–G9 com unitário Python/`decide()`
- [x] 4.2 G4/G5: mesmo `apply`+pre-execute; `subagent` sem needle chama `next()`; `Task`, `spawn_subagent` **e** OpenCode `task` com `prompt` contendo `grill-card` → `nextCalled === true` (prova que `decide()` não ganhou match prompt-wide)
- [x] 4.3 G6/G10/G11: `apply` + `arguments` string JSON deny; unitário JS `isGrillShapedSpawn` objecto/string/nested (não substitui G1–G9); Python `decide({tool: "Task", args: {prompt: "grill-card 701"}})` sem path → `permission: allow`
- [x] 4.4 G7–G9: `apply` write deny ilegal + `cordis_define` + `registerProvider` throw ainda deny write **e** grill-shaped; D13/D16/D20/#784 passam
- [x] 4.5 N1: `test_grill_card.py` #755 verdes (`HOST_TOOLS`, `DOD_NEEDLES`, Grok stubs, vendor Matt)
- [x] 4.6 N2/N3: em `test_grill_card.py` definir `_plain(text)`: lowercase; colapsar whitespace; strip ênfase `*` / `**` / `_word_`; strip backticks; MUST NOT apagar `_` em `ask_user_question`. Incluir **exactamente** estes asserts:

```
assert "não chama a ferramenta do host" in _plain("**não** chama a ferramenta do host")
assert _plain("ask_user_question") == "ask_user_question"
assert "o pai spawna" in _plain("O **pai** spawna")
assert "root chama ask_user_question" not in _plain("O runtime root nunca chama ask_user_question.")
assert "root chama ask_user_question" not in _plain("O runtime root não chama. chama ask_user_question.")
assert "root chama ask_user_question" in _plain("O runtime root chama `ask_user_question`.")
```

  (no-op `_plain = lower+whitespace` falha o primeiro.) `full, cursor, dsh = map(_plain, (text, _heading_section(text, "## Cliente: Cursor e Grok"), _heading_section(text, "## Cliente: dsh")))`. Para cada frase `não chama a ferramenta do host`, `o pai spawna`, `dump d5`, `quem chama`: `full.count(frase) == cursor.count(frase)` e `cursor.count(frase) >= 1`. `dsh` contém a substring **contígua** `root chama ask_user_question`; `dsh` **não** contém `não chama ask_user_question` nem `não chama a ferramenta do host`. Se `## Precondição` existir, `_plain` dessa secção **não** contém `filho`, `spawna`, `relaying`, `dump d5`, `ask_user_question`, `askuserquestion`, `não chama`. Qualquer H2 `^## [^#]` cujo `_plain` contém `perguntas da rodada` (com ou sem `(host)`) MUST ter offset dentro do span Cursor ou dsh — senão fail. Covenant-flow Grill-card `Cliente dsh:`; fonte de `guard.py` **sem** `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`; `dsh_stubs.py` / `grok_stubs.py` / `process-fsm.yaml` inalterados; `AGENTS.md` ≤40 sem `ask_user_question`; stub `.dsh/skills/grill-card` ≤8 + MUST Read; pin-test (quando `install.sh` existe) espera `v1.1.3`; `pytest scripts/process-fsm` sem GitHub

## 5. Produto covenant-flow (tag v1.1.3)

- [x] 5.1 Commit no repo `oalansilva/covenant-flow` (plugin + lib + skills canónicas + goldens) e tag **`v1.1.3`** (não major; não vendorar DeepSeek). `v1.1.2` no origin já aponta o README PT-BR; não mover tag publicada.
- [x] 5.2 `install.sh --pin` continua a copiar `.dsh/` sempre; `CLIENT_KEYS` três; `SCHEMA_MAJOR` 1; skill `implantar` / README não reivindicam Auto dsh

## 6. Pin Cripto

- [x] 6.1 `implantar --pin v1.1.3` no Cripto; overlay `pin: v1.1.3`; `clients.dsh.auto: false` permanece
- [x] 6.2 Não ligar porta 3080 em `environments.dev.services`; não systemd; não reabrir #608/#720/#773/#782/#784/#755; não re-grelhar #701; não dual-write T0–T17

## 7. Verificação

- [x] 7.1 `openspec validate` da change verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [x] 7.2 Stubs `.dsh/skills/` ≤8 linhas; `.dsh/` sem T0–T17; `AGENTS.md` ≤40; sem Auto dsh; `.cursor/hooks.json` matcher Write inalterado

## 8. Homologação humana (não bloqueia apply/T14; bloqueia Auto)

- [ ] 8.1 Dump autenticado da GUI dsh web `http://127.0.0.1:3080` de **um turno** «refine/grelha o card N» (N em Em Refinamento, fronteira com decisão, plugin pinado, cwd = canonical DEV, preset `standard`): `tool/call` `ask_user_question` no **root** **antes** de comentário canónico T1 novo; **sem** `subagent`/`subagent_fork` grill-shaped. Fixture `5a6c8c5c` = só regressão negativa. Homologação ≠ `./restart`; 3080 ≠ systemd
