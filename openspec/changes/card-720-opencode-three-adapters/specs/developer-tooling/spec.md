## MODIFIED Requirements

### Requirement: Configuração versionada de ferramenta de desenvolvimento
O repositório SHALL conter configuração versionada do Cursor Agent em `.cursor/` (rules, skills, commands, hooks), do Grok Build em `.grok/`, e do adapter OpenCode 1.18.18 em `.opencode/plugin/` (auto-load). `opencode.json` MUST NOT permanecer como contrato ativo de modelo, MCP ou permission. `.opencode/plugins/` MUST NOT ser versionado em paralelo com `.opencode/plugin/`. Lock machine, `opencode.db` no kaizen, lease e attestation continuam proibidos.

#### Scenario: Config presente e válida
- **WHEN** o Cursor Agent inicia no repo
- **THEN** a configuração versionada em `.cursor/` é carregada
- **AND** nenhuma instrução Cursor aponta para `opencode.json` como fonte obrigatória de modelo/MCP/permission

#### Scenario: OpenCode plugin auto-load
- **WHEN** o OpenCode 1.18.18 inicia no repo
- **THEN** os módulos em `.opencode/plugin/` carregam sem `opencode.json`

#### Scenario: Sem segredos no repo
- **WHEN** a configuração versionada é inspecionada
- **THEN** nenhum token, chave ou credencial está presente nos arquivos versionados

### Requirement: Proteção de design system na edição de UI
Edições de arquivos de UI em Cursor, Grok Build e OpenCode 1.18.18 SHALL acionar a detecção Impeccable no mesmo `.agents/skills/impeccable/scripts/hook.mjs` sem quebrar o turno. A pele só traduz o evento nativo. Não é um segundo detector.

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
