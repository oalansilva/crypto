## Context

Card [#782](https://github.com/oalansilva/crypto/issues/782) (kaizen). Núcleo e três adapters já entregues no [#773](https://github.com/oalansilva/crypto/issues/773) / [#720](https://github.com/oalansilva/crypto/issues/720). Relacionado: [#608](https://github.com/oalansilva/crypto/issues/608) (EFSM), [#611](https://github.com/oalansilva/crypto/issues/611) (tool desconhecida = allow), [#395](https://github.com/oalansilva/crypto/issues/395) (path de plugin singular). Q1=A e Q2=A estão fechadas no issue; este Design não as reabre.

Produto `oalansilva/covenant-flow` (tags atuais `v1.0.0` / `v1.0.1`; Cripto pin `v1.0.1`) guarda núcleo + três peles (`.cursor/` `.grok/` `.opencode/` + `scripts/process-fsm/` + `install.sh`). **Não há `.dsh/` no produto.** `install.sh --pin` copia só as três peles. `CLIENT_KEYS = ("cursor", "grok", "opencode")`. `SCHEMA_MAJOR = 1`. `render_agents()` hoje nomeia Cursor Auto e Grok/OpenCode cooperativos (não dsh). Extra em `clients` já passa: só falta de uma chave em `CLIENT_KEYS` é `OverlayInvalid`.

`guard.py` live: `WRITE_TOOLS` já contém `write`/`edit`; `PATH_KEYS` já contém `file_path` **e** `filePath`; `SHELL_TOOLS` já contém `bash`; `normalize()` já aceita `{ tool, args }` (dialeto OpenCode). `OPENCODE_WRITE_TOOLS = {"write", "edit", "apply_patch"}` faz empty-path deny. OpenCode goldens cobrem `args.filePath`; **não** há golden `{ tool: "write", args: { file_path } }`. Envelope dsh é o mesmo `{ tool, args }` com snake_case.

Pele OpenCode de referência: `.opencode/plugin/process-fsm-guard.js` (`tool.execute.before` → `guard.py` → **throw** no deny) + `.opencode/plugin/impeccable-hook.js` (fail-open) + lib `scripts/process-fsm/opencode_plugin_lib.js` + stubs `opencode_stubs.py`.

Instância dsh viva: `dsh web` em `http://127.0.0.1:3080` (cwd `/tmp/deepseek-harness`, HTTP **401** sem URL autenticado). Inventário deste turno = source em `/tmp/deepseek-harness` (preview `0.1.2-alpha.1`), não a UI autenticada.

Observação Design no source live:

- Plugin Cordis: `export function apply(ctx)` + `name` + `inject`. Tutorial: path do módulo no patch **é absoluto**; `name` do entry **fica literal** (não interpola `!!js`).
- Guard: waterfall `tools/pre-execute(exec, next) → PreToolDecision`. Deny = `{ kind: 'deny', reason }` **sem** `next()`. Throw no listener vira `isError`, **não** deny. `exec.name` + `exec.arguments` (frozen).
- Paging: `PromptSection.text` aceita `string | ((context) => string)` avaliado em cada `assemble`. `agent/session-start` é notificação síncrona sem gate (bridge Claude pode perder o primeiro request).
- Detector: `tools/post-execute` (waterfall; `block` abortaria) + `agent/turn-stopping` (serial; `steer` forçaria outro passo). Fail-open = sempre `next()` / nunca `block` / nunca `steer`.
- Skills: `project-dsh` = `<root>/.dsh/skills` (rank 100); `project-agents` = `<root>/.agents/skills` (rank 200). **Não** descobre `.cursor/skills`.
- Tools: default **`dsh web`** (bundle `web-app`) **desliga** as rows host `tool-fs` / `tool-str-replace-editor` (`disabled: true`); o preset de sessão remonta `write`/`edit` (`file_path`) e `bash` (`command`). `str_replace_editor` (`path` + `command` view|create|str_replace|insert) fica **ligado** no preset **`sdk-minimal`** (e na row `dsh-base` antes do overlay web a desligar). `workflow` (`script`/`meta`) no base. `cordis-host-runner` está no web bundle; tools modelo `cordis_*` **não** estão no bundle (opt-in). MCP = `mcp__<server>__<tool>`.
- Ponte Claude (`@deepseek-ai/dsh-hooks-claude-code`): parse falho = nenhum hook. **Não** é o Guard.

**UI impact: none.** Harness/hooks/docs de processo. Nenhuma rota, shell, componente ou copy de produto. Prototype N/A. Pipeline Impeccable *desta* coluna Design = N/A. Detector automático em sessões dsh futuras = entra (pele, não tela).

## Goals / Non-Goals

**Goals:**

- Quarto adapter dsh sobre o mesmo `decide()` / `page()` / `hook.mjs`. Uma mudança de glob/coluna/Moore no yaml vale nos quatro clientes.
- Fonte da pele em `oalansilva/covenant-flow`; Cripto pin `v1.1.0`. `install.sh` copia `.dsh/` sempre.
- Dialeto nativo `{ tool, args }` com `file_path` / `command` em goldens. Empty `file_path` em write/edit deny.
- Plugin Cordis nativo: pre-execute `{ kind: 'deny' }` fail-closed; detector fail-open; Moore via `systemPrompt.section`.
- `AGENTS.md` / `render_agents()` sempre nomeia os quatro; sem Auto dsh. `CLIENT_KEYS` três; `clients.dsh` opcional; `SCHEMA_MAJOR=1`.
- Specs: três → quatro adapters; quarto harness continua não sendo fonte da lei.

**Non-Goals:**

- Vendorar `deepseek-ai/deepseek-harness` ou `/tmp/deepseek-harness`.
- Overlay Cripto / board ids / systemd / `docs/crypto-overlay.md` no produto (salvo o template `AGENTS.md` gerado).
- Ponte `dsh-hooks-claude-code` como Guard. Copiar T0–T17 para cordis.yml / `.dsh/` / hooks.json Claude.
- Auto dsh (ou herdar Auto do Cursor). Pin major `v2.0.0`. Tornar `clients.dsh` obrigatório. Implantar Clara/Hermes.
- Código de produto `backend/` / `frontend/src/`. UI / HTML. Porta 3080 em `environments.dev.services`.
- Reabrir #608 / #720 / #773. Dual-write Hermes / `~/.codex/skills/`. Tratar dsh como lei.

## Decisions

1. **Quarto adapter, não fonte da lei; pin minor `v1.1.0`.**  
   Pele nasce em `oalansilva/covenant-flow` e o Cripto recebe cópia. `CLIENT_KEYS` fica três; extra `clients.dsh` passa; ausência não invalida overlay e não desliga o Guard da pele copiada. `--init` não emite a chave; `--pin` não a injeta. Overlay Cripto **escreve** `clients.dsh.auto: false` (edit do consumidor). Apply MUST NOT passar a rejeitar chaves `clients.*` desconhecidas (isso quebraria o pin Cripto com `SCHEMA_MAJOR=1`). Alternativa rejeitada: meter `dsh` em `CLIENT_KEYS` e pin `v2.0.0` (Q1=A). Alternativa rejeitada: nascer só no Cripto (pin #773 mentiria).

2. **`render_agents()` sempre nomeia os quatro.**  
   Uma linha: Cursor Agent (Auto permitido); Grok Build, OpenCode e dsh (cooperativos até ensaio deny). Segunda linha: não reivindicar Auto no Grok, OpenCode **nem dsh**. ≤40 linhas não vazias. Nome no stub ≠ claim de Auto. Alternativa rejeitada: condicionar o quarto nome à presença de `clients.dsh` (Q2=A).

3. **Quarto dialeto no mesmo `normalize()`, não um segundo Guard.**  
   Envelope `{ tool, args }` já é o dialeto OpenCode; dsh usa `file_path` (já em `PATH_KEYS`) em vez de `filePath`. `decide()` permanece canônico. Goldens dsh ainda faltam e **entram**. Empty `file_path` em `write`/`edit` = mesma classe `OPENCODE_WRITE_TOOLS` (já contém `write`/`edit`). Apply MUST alargar a mensagem `empty_path` para nomear tools canônicas com path extraível (não só “OpenCode write/edit/apply_patch”). Alternativa rejeitada: fork `guard.py` para dsh.

4. **Família dsh canônica (source live + goldens).**  
   Default **`dsh web`**: write/edit (`args.file_path`) + bash (`args.command`). O overlay `web-app` **desliga** `tool-str-replace-editor`. A tool `str_replace_editor` está **ligada no preset `sdk-minimal`** (row também existe em `dsh-base` antes do overlay web). Goldens D10–D12 cobrem essa tool porque ela existe na família runtime, não porque o web default a exponha.  
   Mutate `str_replace_editor` (`command` ∈ {`create`,`str_replace`,`insert`}) com `args.path` **não vazio** MUST ser `write_produto` via **`extract_paths(args.path)`** (`PATH_KEYS` já tem `path`; Apply MUST incluir as mutate commands no ramo de extração de write, não no de shell). `args.command` (`str_replace` / `create` / `insert` / `view`) MUST NOT virar `_command()` de shell — hoje isso deixa `extract_paths==[]` e **allow**. Apply MUST NOT despejar a tool inteira em `WRITE_TOOLS`: isso extraía `path` no `view` e `bool(command)` faria `view` de `backend/` virar `write_produto`. Empty `path` em create/str_replace/insert = empty_path deny **e** `extract_paths()==[]`. `view` MUST NOT ser write_produto (allow mesmo com path de produto). `workflow` = classe #611. MCP `mcp__*` = #611. Tool fora da lista → allow (#611). Alternativa rejeitada: tratar `str_replace_editor` inteiro como write (bloquearia `view` de `backend/` em develop). Alternativa rejeitada: só deny empty-path na tool sem assert de `extract_paths` (colapsa com G4/G5).

5. **Layout `.dsh/` espelha `.opencode/plugin/*.js`; lib no núcleo.**  
   ```
   .dsh/plugin/process-fsm-guard.js    # apply: tools/pre-execute + systemPrompt.section
   .dsh/plugin/impeccable-hook.js      # apply: tools/post-execute + agent/turn-stopping
   .dsh/cordis.patch.yml               # insert dos dois módulos (ids estáveis)
   .dsh/skills/<name>/SKILL.md         # stubs ≤8 linhas
   scripts/process-fsm/dsh_plugin_lib.js
   scripts/process-fsm/dsh_stubs.py
   ```
   Formato Cordis: `export const name`, `export const inject`, `export function apply(ctx)` (ESM JS, sem build). Dois módulos para o crash do detector não partilhar o caminho fail-closed do Guard. `dsh_plugin_lib.js` é irmão de `opencode_plugin_lib.js`, **não** um copy-paste do mapper OpenCode. Alternativa rejeitada: um único plugin. Alternativa rejeitada: TypeScript que exija compile no consumidor. Alternativa rejeitada: reexportar `mapAfterPayload` do OpenCode.

6. **Boot = `--patch` com `name` absoluto; não `dsh plugin add` como canal de pin.**  
   Live tutorial: path do plugin **deve ser absoluto**; metadata `name` **não** interpola `!!js`. Helper `scripts/process-fsm/dsh_boot.sh` (ou equivalente Python) resolve a raiz do repo, materializa um patch temporário com paths absolutos para os dois `.js`, e exec `dsh web --patch <tmp>` **a partir do canonical DEV** (`overlay canonical_paths.dev` / cwd `/srv/apps/dev/criptofarol/source`). O `.dsh/cordis.patch.yml` versionado documenta os `id`s e é o input do helper. `dsh plugin add file:...` copia para `$DSH_HOME` e deriva do pin — **não** é o canal v1. overlay_doc do **consumidor** documenta o comando e a auth `:3080`; **não** entra em `environments.dev.services` nem systemd. Alternativa rejeitada: só `dsh plugin add` (pele fora do git do consumidor). Alternativa rejeitada: paths relativos no patch (loader resolve a partir do profile, não do workspace — tutorial).

7. **Fail-closed = `{ kind: 'deny' }`, não throw.**  
   OpenCode 1.18.18 honra throw; dsh honra `PreToolDecision`. Write-like (`write`/`edit`/`bash` mutante/`str_replace_editor` mutante/`cordis_*` lifecycle) sem JSON de `decide()` = deny `fail_closed`, **não** `next()`. Allow = `return next()`. Inspect `cordis_inspect_*` permanece #611. Alternativa rejeitada: throw (vira `isError`, não policy deny). Alternativa rejeitada: Claude hooks.json como Guard (parse falho = nenhum hook).

8. **Paging dsh = `ctx.systemPrompt.section` com `text` função.**  
   `page()` continua o compilador. A seção `covenant-flow:moore` (order finito entre persona `0` e tools `1000`, p.ex. `50`) avalia `page().additional_context` em cada assemble (≤20 linhas, stub yaml, sem release playbook). Não gitignore + MUST Read. Não `agent/session-start` + `inject` como único caminho (race no primeiro request, documentado no bridge Claude). Alternativa rejeitada: hop Grok. Alternativa rejeitada: assemble waterfall para *adicionar* seção (`complete` sections são restauradas; o contrato estável é `section({ text: fn })`).

9. **Stubs só para o que o dsh não descobre.**  
   Gerar `.dsh/skills/<name>/SKILL.md` para cada skill em `.cursor/skills/` (corpo ≤8, MUST Read canónico). Impeccable / `design-critic` / `playwright-cli` já estão em `.agents/skills/` — não duplicar. Gerador + CI como `opencode_stubs.py`. Alternativa rejeitada: copiar runbooks. Alternativa rejeitada: descobrir `.cursor/skills` via config dsh (pele traduz; não muda o runtime).

10. **Detector: pele traduz evento; um `hook.mjs`.**  
    `dsh_plugin_lib.js` `mapAfterPayload` MUST ler **`file_path` primeiro** (envelope nativo dsh `exec.arguments.file_path`), depois `path` (`str_replace_editor`), e só então fallbacks. MUST NOT reutilizar o `mapAfterPayload` OpenCode: esse só lê `filePath` / `path` / `patchText` e deixa `hook.mjs` com path vazio em todo `write`/`edit` dsh. `tools/post-execute` → stdin `file_path` + `hook_event_name=PostToolUse`; sempre `next()`; catch-all; **nunca** `{ kind: 'block' }`. `agent/turn-stopping` → `hook_event_name=Stop`; **nunca** `steer`. Fail-open, exit 0. Sem segundo detector.

11. **Restrict Cordis self-modification na pele.**  
    Tools modelo `cordis_define` / `cordis_run` / `cordis_stop` / `cordis_undefine` (e qualquer `exec.name` que comece por `cordis_` excepto `cordis_inspect_*`) = deny no pre-execute **antes** de `decide()` glob. Motivo: podem montar/desmontar o plugin Guard no processo. Host runner sem tool modelo não é deny. Residual: se o web preset passar a montar `dsh-tool-cordis`, o ensaio confirma o deny. Alternativa rejeitada: allow (#611) nessas tools (P0 do issue).

12. **Goldens pytest `scripts/process-fsm`, sem GitHub.**  
    Plugin `{ kind: 'deny' }`: teste de processo (plugin JS + `decide()` mock/stdin) no mesmo tree. Ensaio humano não bloqueia o merge do adapter; bloqueia Auto.

13. **Auto continua gated no ensaio.**  
    Cursor Auto permanece. Grok/OpenCode cooperativos. dsh cooperativo até deny observado na sessão `dsh web` com plugin carregado no canonical DEV. `AGENTS.md` MUST NOT reivindicar Auto dsh.

### Golden cases (pytest `scripts/process-fsm`)

| # | Envelope | `q` / `q_git` | Esperado |
| --- | --- | --- | --- |
| D1 | `{tool:"write", args:{file_path:"backend/app/tasks/discovery_tasks.py"}}` | develop | deny |
| D2 | `{tool:"edit", args:{file_path:"frontend/src/x.tsx"}}` | develop | deny |
| D3 | `{tool:"write", args:{file_path:""}}` | qualquer | deny (`empty_path`; não allow) |
| D4 | `{tool:"edit", args:{file_path:""}}` | qualquer | deny (`empty_path`) |
| D5 | `{tool:"bash", args:{command:"echo x \| tee backend/app/main.py"}}` | I1 falso | deny |
| D6 | `{tool:"bash", args:{command:"gh project item-edit --id X --field-id PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM --single-select-option-id bd47fbe8"}}` | qualquer | deny (`is_status_edit_command`) |
| D7 | `{tool:"edit", args:{file_path:"openspec/changes/card-782-dsh-adapter/design.md"}}` | Design + `card-782-*` | allow (não `write_produto`) |
| D8 | `{tool:"grep", args:{}}` | develop | allow (#611) |
| D9 | Cursor `Write` + Grok `write` + OpenCode `edit`/`filePath` + dsh `write`/`file_path` no mesmo path/yaml | develop | o mesmo deny |
| D10 | `{tool:"str_replace_editor", args:{command:"str_replace", path:"backend/app/main.py", old_str:"a", new_str:"b"}}` | develop | deny **write_produto** **e** `extract_paths()==["backend/app/main.py"]` (não empty_path; prova `args.path`) |
| D10b | `{tool:"str_replace_editor", args:{command:"insert", path:"backend/app/main.py", insert_line:1, new_str:"x"}}` | develop | deny **e** `extract_paths()==["backend/app/main.py"]` |
| D10c | `{tool:"str_replace_editor", args:{command:"str_replace", path:"openspec/changes/card-782-dsh-adapter/design.md", old_str:"a", new_str:"b"}}` | Design + `card-782-*` | allow **e** `extract_paths()==["openspec/changes/card-782-dsh-adapter/design.md"]` |
| D11 | `{tool:"str_replace_editor", args:{command:"view", path:"backend/app/main.py"}}` | develop | allow (não write-like; `evaluate(write_produto)` não corre) |
| D12 | `{tool:"str_replace_editor", args:{command:"create", path:"", file_text:"x"}}` (e o mesmo vazio para `str_replace` / `insert`) | qualquer | deny (`empty_path`) **e** `extract_paths()==[]` |
| D13 | `{tool:"cordis_define", args:{}}` / `cordis_run` | qualquer | deny (restrict pele; golden do plugin) |
| D14 | `{tool:"workflow", args:{script:"return 1", meta:{name:"x", description:"y"}}}` | develop | allow (#611) |
| D15 | `page()` body usado pela seção Moore dsh | Todo | ≤20 linhas, stub yaml, sem `release-guard` |
| D16 | `dsh_plugin_lib.js` `mapAfterPayload` com `arguments.file_path` de UI (sem `filePath`) → stdin `file_path` + `PostToolUse`; turn-stopping → `Stop` | UI file | `file_path` **preenchido** (não o mapper OpenCode); nunca block/steer; exit 0 |
| D17 | `AGENTS.md` | — | ≤40 linhas; quatro clientes; sem Auto dsh/OpenCode/Grok; sem T0–T17 |
| D18 | `.dsh/` | — | sem tabela T0–T17; stubs ≤8 linhas; sem hooks.json Claude |
| D19 | overlay **sem** `clients.dsh` | — | `validate_overlay` aceita; `--init` template sem a chave |
| D19b | overlay **com** extra `clients.dsh.auto: false` | — | `validate_overlay` aceita (testemunha o write Cripto); Apply MUST NOT rejeitar `clients.*` desconhecidas |
| D20 | plugin write-like sem JSON de `decide()` | — | `{ kind: 'deny', reason }` `fail_closed` (não throw, não `next()`) |

## Apply contract

- Ordem: (1) commit no produto `oalansilva/covenant-flow` tag **`v1.1.0`**; (2) `implantar --pin v1.1.0` no Cripto + gravar `clients.dsh.auto: false` no overlay Cripto. Zero produto UI (`frontend/src/`, `backend/` de app).
- Produto: `scripts/process-fsm/` (goldens D1–D20 incluindo D10/D10b/D10c/D12 `extract_paths`, D16 mapper dsh, D19+D19b, `dsh_plugin_lib.js` **com `mapAfterPayload` próprio que lê `file_path`**, `dsh_stubs.py`, `dsh_boot.sh`, `render_agents` quatro nomes, mensagem `empty_path` **não** só “OpenCode”), `.dsh/plugin/*.js`, `.dsh/cordis.patch.yml`, stubs `.dsh/skills/`, `install.sh` copia `.dsh/` sempre, skill `implantar` lista a quarta pele, README do produto: quatro adapters. `CLIENT_KEYS` e `SCHEMA_MAJOR` **não** mudam. `--init` **não** emite `clients.dsh`. `--pin` **não** injeta a chave. Apply MUST NOT rejeitar chaves `clients.*` extra.
- Cripto no pin: `.dsh/` commitado; overlay `pin: v1.1.0` + `clients.dsh.auto: false`; `AGENTS.md` gerado; overlay_doc nota `dsh web` + auth local (não `environments.dev.services`).
- Plugin Guard: `tools/pre-execute` serializa `{ tool: exec.name, args: exec.arguments }` → `guard.py`/`decide()` → `{ kind: 'deny', reason }` no deny. Mutate `str_replace_editor` classifica via `extract_paths(args.path)`; `args.command` não é shell. Detector: `dsh_plugin_lib.mapAfterPayload` lê `file_path` (depois `path`); post-execute + turn-stopping → `hook.mjs`; catch-all; nunca deny/block/steer.
- Paging: `systemPrompt.section` com `text` função = `page().additional_context`.
- Pytest: D1–D20; sem GitHub nos unitários. D9 MUST comparar os quatro dialetos no mesmo path. D10/D10b/D10c MUST assert `extract_paths()`. D12 MUST assert `extract_paths()==[]` **e** empty_path. D16 MUST alimentar o mapper com `file_path` sem `filePath`. D19b MUST validar overlay com o extra presente.
- Homologação (não bloqueia apply; bloqueia Auto): plugin carregado via helper `--patch`; `write`/`edit`/`bash` ilegal em `backend/` ou `frontend/src/` com `q_git=develop` → deny no UI dsh; editar UI dispara `hook.mjs` sem abortar o turno.

## Risks / Trade-offs

- [Plugin não carregado = write passa] → residual, igual Grok/OpenCode sem trust. Homologação registra que o helper `--patch` montou os dois módulos (log de boot / `ctx` inventory). Guard live não substitui o load.
- [Tool dsh nova fora da lista canónica → allow] → classe #611. Golden D8/D14. `str_replace_editor` entra na lista porque **sdk-minimal** a monta (web-app default a desliga). Upgrade de API = card filho.
- [`cordis_*` modelo opt-in hoje] → restrict na pele mesmo assim (D13). Web bundle monta `cordis-host-runner` sem as sete tools; se um overlay local as ligar, deny. Inventário UI :3080 ficou 401 neste turno — residual para critics/ensaio.
- [dsh preview alpha, breaking, SAFETY.md] → não é controle de segurança único; sandbox landlock não é isolamento. Pele traduz; não vendorar o runtime.
- [Processo atual em `/tmp/deepseek-harness`] → workspace errado até relançar no canonical DEV. Auth 401 em `:3080` é do launcher, não do Guard.
- [Ensaio Auto Grok/OpenCode pendente] → este card não herda Auto do Cursor; dsh cooperativo até o próprio ensaio.
- [Detector fail-open] → crash de `hook.mjs` não aborta (já é contrato Cursor/OpenCode). Módulos separados Guard vs detector. Mapper dsh lê `file_path` (D16); copiar o OpenCode deixaria path vazio.
- [Paging `text` função vs inject session-start] → assemble por request evita a race do primeiro turno. Se um preset sombrear a seção pelo mesmo `name`, residual — usar nome `covenant-flow:moore`.
- [`name` absoluto no patch] → helper de boot; o yaml versionado não hardcoda `/srv/apps/...`. Alternativa `dsh plugin add` deriva `$DSH_HOME`.
- [AGENTS.md > 40 linhas] → quatro nomes cabem no bullet existente de clientes; teste de orçamento já existe.
- [Empty-path já coberto por `OPENCODE_WRITE_TOOLS` para write/edit] → goldens D3/D4 ainda obrigatórios (`file_path` vs `filePath`). D10/D12 **não** usam esse atalho: MUST assert `extract_paths`.

## Migration Plan

Aditivo. Ordem de apply: (1) goldens D1–D12/D10b/D10c e D19+D19b no núcleo (`file_path` + empty-path + `str_replace_editor` via `extract_paths(args.path)`, sem promover `args.command` a shell; extra `clients.dsh` valida); (2) `dsh_plugin_lib.js` **próprio** (`mapAfterPayload` lê `file_path`) + plugins `.dsh/plugin/` + helper `--patch` (D13, D16, D20); (3) paging `systemPrompt.section` (D15); (4) stubs `.dsh/skills/` + `dsh_stubs.py`; (5) detector impeccable; (6) `render_agents` quatro nomes + mensagem empty_path genérica + `install.sh` copia `.dsh/` + skill `implantar` + README; (7) tag `v1.1.0`; (8) pin Cripto + `clients.dsh.auto: false` + overlay_doc boot. Rollback = reverter o diff / pin anterior `v1.0.1`; Cursor/Grok/OpenCode #720/#773 permanecem. Sem migration de banco. Sem rebuild de frontend. Homologação = ensaio deny dsh + detector, não `./restart` de produto.

## Open Questions

Nenhuma bloqueante de escopo (Q1=A, Q2=A fechadas; grelha vazia). P1s da Assessment B fechados neste patch (D10/D10b/D10c/`extract_paths`, mapper `file_path`, D19b extra). Residual para critics/ensaio: inventário de tools na sessão autenticada `:3080` (401 neste turno; source cobre web/base); fire de `tools/pre-execute` em subagent/workflow child no mesmo `ctx` raiz.

## UI impact

**none** — harness/hooks/docs de processo. Nenhuma rota, shell, componente ou copy de produto. Nenhuma superfície visual nova ou alterada.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar; o aceite visível é deny `{ kind: 'deny' }` de ferramenta, inject da página Moore, e `hook.mjs` fail-open no quarto cliente. Sem HTML. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual.

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O **detector** Impeccable como pele de harness (dsh → `hook.mjs`) está no escopo deste card; não é o pipeline Impeccable desta coluna.

## Design Critique

- P0: nenhum (A r1, A r2, B r2).
- P1 (B r1, aberto → patch do autor → fechado em r2): D10/D12 `str_replace_editor` colapsavam com empty-path e não provavam `args.path`; D16 copiava o mapper OpenCode (`filePath`/`path`/`patchText`, não `file_path`); D19 omit-only não testemunhava o extra Cripto. Disposition: **closed**. D10/D10b/D10c exigem `extract_paths()`; D12 empty_path **e** `extract_paths()==[]`; D16 `mapAfterPayload` lê `file_path` primeiro; D19b overlay com `clients.dsh.auto: false` valida; Apply MUST NOT rejeitar `clients.*` extra (`SCHEMA_MAJOR=1`).
- P2 (accepted-residual): plugin não carregado / `--patch` omitido / `export default` em vez de `export function apply(ctx)` = waterfall `allow`; `:3080` 401; `workflow` / `subagent` / MCP / tool nova → allow (#611); tasks 1.x–4.x soam a worktree consumidor vs ordem produto `v1.1.0` → pin (`install.sh` live ainda não copia `.dsh/`; consumer-first + pin apagaria o núcleo); Proposal Why stale («Guard não vê `file_path`») — live já nega `write`/`edit`/`bash`; processo actual em `/tmp/deepseek-harness` até relançar no canonical DEV; OpenCode live `WRITEISH` sem `str_replace_editor` (copiar o set = fail-closed só em write/edit); dois remotes (tag produto, depois pin); paging `persona.complete: true` no preset web `minimal` pode sombrear `systemPrompt.section` (Guard ainda resolve `q`).
- P3 (accepted-residual): preset de sessão web `minimal` também monta `str_replace_editor` (D4 nomeia sobretudo `sdk-minimal`); sem golden nomeado `create` nonempty; títulos OpenSpec stale (`two`/`three` adapters) com corpo four; mensagem `empty_path` live ainda diz «OpenCode»; spec D20 exemplifica só `write`/`edit`; D16 não exige import negativo do mapper OpenCode; D10 texto `write_produto` vs live `reason=I1` (G3 #720); `render_agents()` live três nomes; task 7.4 sem `--strict` no texto; docstring `guard.py` «Cursor + Grok + OpenCode»; `PreToolDecision.ask` existe (D20 já exige `{ kind: 'deny' }`); `pwsh` no preset Windows = #611 neste host.

Prototype: N/A — harness/hooks/docs; nenhuma tela de produto.

Snapshot (git-tracked; Gist não envia esta pasta; T7 abre estes arquivos):
- `.impeccable/critique/782-card-782-dsh-adapter-A.md` (Assessment A round 2, PASS)
- `.impeccable/critique/782-card-782-dsh-adapter-B.md` (Assessment B round 2, PASS; detector de pele)

Design Agent verdict: PASS
