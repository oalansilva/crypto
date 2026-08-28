## Why

Abrir o Cripto no DeepSeek Harness (`dsh`) hoje não é contrato: o Guard não vê o envelope nativo `{ tool, args }` com `file_path` / `command`, e um write ilegal em `backend/` com `q_git=develop` passa. Sem pele no produto `oalansilva/covenant-flow`, o pin #773 mente (a quarta pele nasceria só no consumidor) e copiar T0–T17 para cordis.yml reabre o anti-padrão #584/#668/#720. Card [#782](https://github.com/oalansilva/crypto/issues/782) (kaizen P1). Relacionado: [#608](https://github.com/oalansilva/crypto/issues/608), [#720](https://github.com/oalansilva/crypto/issues/720), [#773](https://github.com/oalansilva/crypto/issues/773).

## What Changes

- Quarto adapter `dsh` (DeepSeek Harness, Cordis nativo) sobre o mesmo `decide()` / `page()` / detector `hook.mjs`. Adapter = tradução. Sem dual-write da lei. Sem Auto dsh até ensaio deny. Sem ponte `dsh-hooks-claude-code` como Guard.
- Fonte da pele em `oalansilva/covenant-flow`; Cripto recebe cópia no pin **`v1.1.0`**. Não vendorar `deepseek-ai/deepseek-harness`. `SCHEMA_MAJOR` permanece 1. `CLIENT_KEYS` permanece `("cursor", "grok", "opencode")`. `clients.dsh` é chave extra opcional; `--init` não a emite; `--pin` não a injeta. Overlay Cripto **escreve** `clients.dsh.auto: false`.
- `install.sh --pin` copia `.dsh/` sempre (como `.opencode/`). Overlay sem `clients.dsh` (Clara/Hermes) continua válido e ainda assim recebe a pele.
- `render_agents()` **sempre** nomeia os quatro clientes (Cursor Auto permitido; Grok Build, OpenCode e dsh cooperativos até ensaio deny). Não reivindica Auto dsh. Stub ≤ 40 linhas não vazias.
- Plugin Cordis nativo em `.dsh/plugin/` (espelho de `.opencode/plugin/*.js`) + lib em `scripts/process-fsm/` + gerador de stubs `dsh_stubs.py`. Waterfall `tools/pre-execute` devolve `{ kind: 'deny' }` (não throw, não `next()` no deny). Write-like sem JSON de decisão = fail-closed. Detector `tools/post-execute` + `agent/turn-stopping` → o mesmo `hook.mjs` (fail-open).
- Dialeto nativo dsh no `normalize()`: tools `write` / `edit` (`file_path`) e `bash` (`command`). Goldens do 4º dialeto (OpenCode usa `filePath`; dsh usa `file_path`). Empty `file_path` em write/edit = deny (mesma classe OpenCode empty path).
- Skills: stubs em `.dsh/skills/` (dsh descobre `.dsh/skills` + `.agents/skills`, **não** `.cursor/skills`). Corpo ≤ 8 linhas apontando ao canónico.
- Restrict das tools Cordis de self-modification (`cordis_define` / `cordis_run` / `cordis_stop` / `cordis_undefine`) na pele. `str_replace_editor` mutante entra como write-like (`args.path`).
- Spec `process-harness`: três → **quatro** adapters. Quarto harness continua **não** sendo fonte da lei. Skill `implantar` lista a quarta pele. README do produto: quatro adapters no tree.
- Sem produto Cripto (`backend/` / `frontend/src/`). Sem UI / protótipo HTML. Sem ligar porta 3080 em `environments.dev.services`. Sem implantar Clara/Hermes. Sem pin major `v2.0.0`.

## Capabilities

### New Capabilities

- (nenhuma) — a pele dsh é o quarto adapter do núcleo já descrito em `process-harness`; não é um segundo processo nem uma spec de produto.

### Modified Capabilities

- `process-harness`: três → quatro adapters; `AGENTS.md` / `render_agents()` nomeia Cursor, Grok Build, OpenCode e dsh; dual-write da lei continua proibido; o quarto harness (dsh) **não** é fonte da lei; detector Impeccable nos quatro; Auto dsh gated no ensaio deny.
- `covenant-flow`: `implantar --pin` copia `.dsh/` além de `.cursor/` `.grok/` `.opencode/`; pin **`v1.1.0`**; `clients.dsh` opcional (não `CLIENT_KEYS`; extra permitido; `--init` não emite; `--pin` não injeta); `SCHEMA_MAJOR` permanece 1; quarto adapter ainda não é yaml.
- `process-fsm-guard`: quarto dialeto nativo `{ tool, args }` com `file_path` / `command`; empty `file_path` em `write`/`edit` deny; plugin Cordis `{ kind: 'deny' }` fail-closed; `str_replace_editor` mutante; restrict `cordis_*` lifecycle.
- `process-fsm-paging`: dsh injeta a página Moore via `ctx.systemPrompt.section` (texto função por assemble); mesma substância do yaml; ≤20 linhas; sem playbook de release.
- `developer-tooling`: pele `.dsh/` versionada no git do consumidor; detector no quarto cliente; skill `implantar` lista quatro peles; `git ls-files` inclui `.dsh/` após pin.
- `cursor-harness`: `AGENTS.md` nomeia os quatro clientes; sem Auto dsh (nem herdar Auto do Cursor); lock machine permanece morto.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` (tag `v1.1.0`) — `scripts/process-fsm/` (`normalize` / goldens 4º dialeto / `dsh_plugin_lib.js` / `dsh_stubs.py` / `render_agents`), `.dsh/plugin/` + `.dsh/cordis.patch.yml` + stubs `.dsh/skills/`, `install.sh` (copia `.dsh/`), skill `implantar`, README do produto, specs main via archive.
- Altera no Cripto no pin: cópia `.dsh/`; overlay `clients.dsh.auto: false` e `pin: v1.1.0`; `AGENTS.md` gerado com quatro nomes; nota de boot `dsh web` no `overlay_doc` (não em `environments.dev.services`).
- Não toca `backend/` de produto, `frontend/src/`, yaml T0–T17, `CLIENT_KEYS`, `SCHEMA_MAJOR`, lock machine, monorepo DeepSeek, Clara/Hermes, systemd, porta 3080 no overlay de services.
- `UI impact: none`. Prototype N/A. Pipeline Impeccable *desta* coluna Design = N/A. Detector automático em sessões dsh futuras = entra.
- Origem: issue #782. Homologação: ensaio deny dsh no mesmo worktree com plugin carregado (bloqueia Auto, não o merge do adapter).
