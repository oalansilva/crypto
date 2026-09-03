## MODIFIED Requirements

### Requirement: Configuração versionada de ferramenta de desenvolvimento
O repositório SHALL conter configuração versionada do Cursor Agent em `.cursor/` (rules, skills, commands, hooks), do Grok Build em `.grok/`, do adapter OpenCode 1.18.18 em `.opencode/plugin/` (auto-load), e do adapter dsh em `.dsh/plugin/` (Cordis `apply(ctx)` + `.dsh/cordis.patch.yml`). `opencode.json` MUST NOT permanecer como contrato ativo de modelo, MCP ou permission. `.opencode/plugins/` MUST NOT ser versionado em paralelo com `.opencode/plugin/`. Lock machine, `opencode.db` no kaizen, lease e attestation continuam proibidos. A ponte Claude `hooks.json` MUST NOT ser o Guard dsh.

#### Scenario: Config presente e válida
- **WHEN** o Cursor Agent inicia no repo
- **THEN** a configuração versionada em `.cursor/` é carregada
- **AND** nenhuma instrução Cursor aponta para `opencode.json` como fonte obrigatória de modelo/MCP/permission

#### Scenario: OpenCode plugin auto-load
- **WHEN** o OpenCode 1.18.18 inicia no repo
- **THEN** os módulos em `.opencode/plugin/` carregam sem `opencode.json`

#### Scenario: dsh plugin layout is versioned
- **WHEN** o consumidor está pinado em `v1.1.0`
- **THEN** `.dsh/plugin/process-fsm-guard.js` e `.dsh/plugin/impeccable-hook.js` existem no git
- **AND** `.dsh/cordis.patch.yml` declara os ids de insert
- **AND** não há `hooks.json` Claude como Guard

#### Scenario: Sem segredos no repo
- **WHEN** a configuração versionada é inspecionada
- **THEN** nenhum token, chave ou credencial está presente nos arquivos versionados

### Requirement: Proteção de design system na edição de UI
Edições de arquivos de UI em Cursor, Grok Build, OpenCode 1.18.18 e dsh SHALL acionar a detecção Impeccable no mesmo `.agents/skills/impeccable/scripts/hook.mjs` sem quebrar o turno. A pele só traduz o evento nativo. Não é um segundo detector.

#### Scenario: Hook de UI dispara na edição Cursor
- **WHEN** um arquivo de frontend é editado pelo Cursor
- **THEN** o hook em `.cursor/hooks.json` roda `.agents/skills/impeccable/scripts/hook.mjs` e reporta achados sem interromper a sessão

#### Scenario: Hook de UI dispara na edição Grok
- **WHEN** um arquivo de frontend é editado pelo Grok Build
- **THEN** `PostToolUse` / `Stop` em `.grok/hooks/` rodam o mesmo `hook.mjs` e reportam achados sem interromper a sessão

#### Scenario: Hook de UI dispara na edição OpenCode
- **WHEN** um arquivo de frontend é editado pelo OpenCode 1.18.18
- **THEN** `tool.execute.after` / `session.idle` no plugin rodam o mesmo `hook.mjs` e reportam achados sem interromper a sessão
- **AND** `tool.execute.after` mapeia `args.filePath` para `file_path` no stdin de `hook.mjs` com `hook_event_name=PostToolUse`
- **AND** `session.idle` mapeia `hook_event_name=Stop`

#### Scenario: Hook de UI dispara na edição dsh
- **WHEN** um arquivo de frontend é editado pelo dsh
- **THEN** `tools/post-execute` / `agent/turn-stopping` no plugin Cordis rodam o mesmo `hook.mjs` e reportam achados sem interromper a sessão
- **AND** `dsh_plugin_lib.js` `mapAfterPayload` lê `arguments.file_path` primeiro (envelope nativo; sem `filePath`) e depois `path` (`str_replace_editor`) para o stdin `file_path` de `hook.mjs` com `hook_event_name=PostToolUse`
- **AND** o mapper MUST NOT ser o `mapAfterPayload` OpenCode (só `filePath` / `path` / `patchText`; copiá-lo deixa `hook.mjs` com path vazio em todo `write`/`edit` dsh)
- **AND** `agent/turn-stopping` mapeia `hook_event_name=Stop`
- **AND** o detector não devolve `{ kind: 'block' }` e não chama `steer`

### Requirement: Consumer git commits materialized harness skins
A pinned consumer SHALL keep `.cursor/`, `.grok/`, `.opencode/`, `.dsh/`, `scripts/process-fsm/`, `.agents/skills/` (impeccable, design-critic, playwright-cli), and generated `AGENTS.md` as committed trees produced by `implantar --pin`. Those paths MUST NOT be gitignored as the install method and MUST NOT be a submodule as the v1 channel. Skill `implantar` SHALL list `.dsh/` among the copied skins.

#### Scenario: Pinned consumer shows skins in git
- **WHEN** Cripto is pinned in the card worktree at `v1.1.0`
- **THEN** `git ls-files` includes `.cursor/hooks.json`, `.grok/` adapter files, `.opencode/plugin/`, `.dsh/plugin/`, `scripts/process-fsm/`, `.agents/skills/impeccable/`, and `AGENTS.md`
- **AND** overlay `.covenant-flow/overlay.yaml` contains `pin` matching the product tag
