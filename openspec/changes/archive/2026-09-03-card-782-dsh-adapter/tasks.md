## 1. Núcleo: quarto dialeto

- [x] 1.1 Extender goldens em `scripts/process-fsm/` para o dialeto nativo dsh `{ tool, args }` (`file_path` / `command`); tools `write`/`edit`/`bash`; mutate `str_replace_editor` (`create`/`str_replace`/`insert`) classifica via **`extract_paths(args.path)`** (D10/D10b deny `write_produto`; D10c Design+`card-*` allow); MUST NOT promover `args.command` a shell `_command()`; MUST NOT despejar a tool inteira em `WRITE_TOOLS`; `view` (D11) não é `write_produto`; `decide()` trata path `product_globs` como `write_produto`. Editor no preset **sdk-minimal** (web-app default desliga)
- [x] 1.2 `write`/`edit` com `file_path` vazio e `str_replace_editor` mutante com `path` vazio MUST deny empty_path **e** `extract_paths()==[]` (D12; não early-return allow; não colapsar com G4/G5); mensagem empty_path MUST NOT citar só “OpenCode”; tool desconhecida permanece allow (#611)
- [x] 1.3 Golden D9: Cursor `Write` + Grok `write` + OpenCode `edit`/`filePath` + dsh `write`/`file_path` no mesmo path/yaml → o mesmo deny
- [x] 1.4 Não editar `backend/` nem `frontend/src/` de produto

## 2. Pele dsh Guard + paging + boot

- [x] 2.1 Criar `scripts/process-fsm/dsh_plugin_lib.js` (irmão de `opencode_plugin_lib.js`, **não** copy do mapper): `runGuard` / `runPage` / `mapAfterPayload` próprio que lê **`file_path` primeiro** (depois `path`); MUST NOT reexportar o mapper OpenCode; write-like sem JSON → fail-closed
- [x] 2.2 Criar `.dsh/plugin/process-fsm-guard.js` (`apply(ctx)`, `inject` tools+systemPrompt): `tools/pre-execute` serializa `{ tool: exec.name, args: exec.arguments }`, chama o mesmo `guard.py`/`decide()`, devolve `{ kind: 'deny', reason }` no deny **sem** `next()` e **sem** throw; allow chama `next()`; restrict `cordis_define`/`cordis_run`/`cordis_stop`/`cordis_undefine`
- [x] 2.3 Paging: no plugin Guard, `ctx.systemPrompt.section` nome `covenant-flow:moore` com `text` função = `page().additional_context` (≤20 linhas, sem release playbook); sem arquivo gitignored + MUST Read; sem `agent/session-start` como único caminho
- [x] 2.4 Versionar `.dsh/cordis.patch.yml` com ids de insert; helper `scripts/process-fsm/dsh_boot.sh` (ou equivalente) materializa `--patch` com `name` **absoluto** dos dois `.js` e lança `dsh web` a partir do canonical DEV; `dsh plugin add` **não** é o canal de pin
- [x] 2.5 Não criar Claude `hooks.json` como Guard; não vendorar `deepseek-ai/deepseek-harness`

## 3. Stubs e always-on

- [x] 3.1 Criar `scripts/process-fsm/dsh_stubs.py` (espelho `opencode_stubs.py`): stubs `.dsh/skills/<name>/SKILL.md` só para skills em `.cursor/skills/`; corpo ≤8 linhas, MUST Read canónico; não duplicar Impeccable/`design-critic`/`playwright-cli` já em `.agents/skills/`
- [x] 3.2 `render_agents()`: nomear Cursor, Grok Build, OpenCode **e** dsh; Cursor Auto; Grok, OpenCode e dsh cooperativos até ensaio; ≤40 linhas não-vazias; sem Auto dsh/OpenCode/Grok; sem T0–T17; quatro nomes **mesmo** se overlay omitir `clients.dsh`
- [x] 3.3 `CLIENT_KEYS` permanece três; `SCHEMA_MAJOR` permanece 1; `empty_template` / `--init` **não** emite `clients.dsh`; `--pin` **não** injeta a chave; D19 omit ainda valida; D19b overlay **com** extra `clients.dsh.auto: false` ainda valida; Apply MUST NOT passar a rejeitar chaves `clients.*` desconhecidas

## 4. Detector Impeccable no quarto cliente

- [x] 4.1 `.dsh/plugin/impeccable-hook.js`: `tools/post-execute` + `agent/turn-stopping` → o mesmo `hook.mjs`; D16: `dsh_plugin_lib.mapAfterPayload` lê `arguments.file_path` (sem `filePath`) e `path` → stdin `file_path`; turn-stopping → `hook_event_name=Stop`; catch-all; **nunca** `{ kind: 'block' }`; **nunca** `steer`; MUST NOT copiar o mapper OpenCode
- [x] 4.2 Cursor/Grok/OpenCode detector permanece; não segundo detector; não lock machine

## 5. Produto covenant-flow (tag v1.1.0)

- [x] 5.1 `install.sh --pin` copia `.dsh/` **sempre** (como `.opencode/`), inclusive quando overlay omite `clients.dsh`
- [x] 5.2 Skill `implantar` lista a quarta pele `.dsh/` e o pin `v1.1.0`; README do produto: quatro adapters no tree; specs main via deltas desta change
- [x] 5.3 Commit no repo `oalansilva/covenant-flow` e tag **`v1.1.0`** (não major; não vendorar DeepSeek)

## 6. Pin Cripto

- [x] 6.1 `implantar --pin v1.1.0` no Cripto; gravar `clients.dsh.auto: false` e `pin: v1.1.0` no overlay Cripto; `AGENTS.md` regenerado
- [x] 6.2 overlay_doc do consumidor documenta boot `dsh web` (helper `--patch`, URL local, auth); **não** ligar porta 3080 em `environments.dev.services`; **não** systemd; **não** implantar Clara/Hermes

## 7. Testes e verificação

- [x] 7.1 Golden `pytest scripts/process-fsm` (sem GitHub): D1–D20 do `design.md` — D1/D2 deny `file_path`; D3/D4 empty `file_path` deny; D10/D10b mutate+insert `extract_paths()==[produto]` + write_produto; D10c Design+card allow + `extract_paths`; D11 `view` allow; D12 empty path `extract_paths()==[]` + empty_path; D13 plugin restrict `cordis_*`; D19 omit `clients.dsh` aceita; D19b extra `clients.dsh.auto: false` aceita; D20 fail-closed sem JSON
- [x] 7.2 Golden paging dsh: `page()` body injetável ≤20 linhas sem `release-guard`; D16 mapper dsh alimentado com `file_path` **sem** `filePath` → stdin preenchido + `PostToolUse`; turn-stopping → `Stop`; exit 0; nunca block/steer; plugin `{ kind: 'deny' }` no deny (não throw)
- [x] 7.3 `test_agents_md_is_stub`: quatro clientes; não reivindica Auto dsh/OpenCode/Grok; ≤40 linhas; `.dsh/` sem T0–T17; stubs ≤8 linhas
- [x] 7.4 `openspec validate` da change verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)

## 8. Homologação humana (não bloqueia apply; bloqueia Auto)

- [ ] 8.1 Plugin carregado via helper `--patch` no canonical DEV; mesmo worktree `q_git=develop` `write`/`edit`/`bash` ilegal em `backend/` ou `frontend/src/` → deny no UI dsh; editar UI dispara `hook.mjs` sem abortar o turno; residual inventário `:3080` autenticado se a sessão 401 persistir
