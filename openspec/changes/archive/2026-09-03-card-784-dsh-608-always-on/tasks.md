## 1. Lib: stub reader + skill provider

- [x] 1.1 Em `scripts/process-fsm/dsh_plugin_lib.js`, exportar `readAgentsStub()` que lê `join(REPO_ROOT, "AGENTS.md")` em UTF-8 e devolve `""` se o ficheiro faltar ou a leitura falhar (fail-open; sem throw)
- [x] 1.2 Exportar `createRepoDshSkillProvider(root)` com `name: "covenant-flow-process"`; `list(options)` e `get(candidate, options)` **async/thenable** (MUST NOT devolver array síncrono); `list` ignora `options.cwd`; um nível `join(root, ".dsh/skills")/<name>/SKILL.md`; dir ausente → `[]`; frontmatter inválido = skip (parse `---`/`dsh_stubs.py`, MUST NOT `import 'yaml'` nem `@deepseek-ai/dsh-skill-filesystem`); cada candidate `provider: "covenant-flow-process"` + kebab `name` + `description` não-vazia + `source: "custom"` + `rank: 300` + `invocation` booleanos + `locator`/`path`; `get(candidate, options)` relê locator e devolve `content` string (não `get(name)`)
- [x] 1.3 Não editar `backend/` nem `frontend/src/` de produto; não vendorar `deepseek-harness`

## 2. Plugin Guard: secção agents + registerProvider

- [x] 2.1 `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt", "skills"]`; manter `tools/pre-execute` fail-closed e `covenant-flow:moore` order 50
- [x] 2.2 Registar `covenant-flow:agents` order 40, `text` função = `readAgentsStub()`; MUST NOT interpolar T0–T17 no JS; MUST NOT `complete: true`
- [x] 2.3 `tools/pre-execute` + secções **antes** de `ctx.skills.registerProvider((control) => createRepoDshSkillProvider(REPO_ROOT))`; só se `typeof ctx.skills?.registerProvider === "function"`; try/catch — throw do provider MUST NOT impedir deny; `_mock_ctx_prelude` MUST incluir `skills.registerProvider` que chama a factory
- [x] 2.4 Não alterar `.dsh/cordis.patch.yml` (sem skill paths, sem `customSkillDirs`); não tocar host row `skill-filesystem`; não desligar native loader; não segundo plugin

## 3. Boot: canonical_paths.dev inválido

- [x] 3.1 `dsh_boot.sh`: se `canonical_paths.dev` não-vazio e **não** é diretório → exit ≠0 e stderr nomeia o path
- [x] 3.2 Chave vazia/ausente → `LAUNCH_DIR=REPO_ROOT`; diretório existente → `LAUNCH_DIR=DEV_ROOT` (preservar #782); boot MUST NOT setar workspace GUI da sessão
- [x] 3.3 Canal continua `dsh web --patch` com `name` absoluto; `dsh plugin add` não é pin

## 4. Goldens pytest `scripts/process-fsm`

- [x] 4.1 A1: `apply` regista secções agents 40 + moore 50 **localizadas por `name`/`order`** (MUST NOT `sections[0]===moore`); actualizar `test_plugin_deny_on_illegal_product_write_without_throw`; `inject` contém `systemPrompt` e `skills`
- [x] 4.2 A2/A3: `text()` do stub contém wording always-on do ficheiro e não T0/`release-guard pre`; ficheiro ausente → `""`
- [x] 4.3 A4/A5: fake `waitWithAbort`+`validateCandidate` (cópia das regras live, sem importar `dsh-skill`) com `signal` não abortado; `list` thenable; cada candidate `provider === "covenant-flow-process"`; `get(candidate, options)` thenable com `content` string MUST Read canónico; stubs ≤8 linhas; lookup cwd = homedir
- [x] 4.4 A6: `cordis.patch.yml` sem `.dsh/skills` / `customSkillDirs`
- [x] 4.5 A7/A8/A9: boot exit ≠0 no DEV não-dir (stderr com path); vazio → launch `REPO_ROOT` (`dsh` fake no PATH); diretório válido ainda preferido
- [x] 4.6 A10: o provider que `apply()` registou sobrevive a fake `waitWithAbort(list, signal)` + `validateCandidate` e lista `covenant-flow`; D13/D16/D20 #782 passam; pin-test `v1.1.1`; `pytest scripts/process-fsm` sem GitHub

## 5. Produto covenant-flow (tag v1.1.1)

- [x] 5.1 Commit no repo `oalansilva/covenant-flow` (plugin + lib + boot + goldens) e tag **`v1.1.1`** (não major; não vendorar DeepSeek)
- [x] 5.2 `install.sh --pin` continua a copiar `.dsh/` sempre; `CLIENT_KEYS` três; `SCHEMA_MAJOR` 1; skill `implantar` / README não reivindicam Auto dsh

## 6. Pin Cripto

- [x] 6.1 `implantar --pin v1.1.1` no Cripto; overlay `pin: v1.1.1`; `clients.dsh.auto: false` permanece
- [x] 6.2 Não ligar porta 3080 em `environments.dev.services`; não systemd; não implantar Clara/Hermes; não reabrir #608/#720/#773/#782

## 7. Verificação

- [x] 7.1 `openspec validate` da change verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [x] 7.2 Stubs `.dsh/skills/` ≤8 linhas; `.dsh/` sem T0–T17; `AGENTS.md` ≤40; sem Auto dsh

## 8. Homologação humana (não bloqueia apply; bloqueia Auto)

- [ ] 8.1 Replay sessão `306d48f7-d893-471e-ba4c-8fe7a5153fda`: cwd ≠ repo, preset `standard`, plugin `--patch`; first-request dump contém stub `AGENTS.md` **e** `<available_skills>` com `covenant-flow`; Guard deny continua; tool `skill` extra (não DoD)
