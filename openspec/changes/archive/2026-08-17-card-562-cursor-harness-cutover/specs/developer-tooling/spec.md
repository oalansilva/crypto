## MODIFIED Requirements

### Requirement: Configuração versionada de ferramenta de desenvolvimento
O repositório SHALL conter configuração versionada do Cursor Agent em `.cursor/` (rules, skills, commands, hooks). `opencode.json` e `.opencode/` MUST NOT permanecer como contrato ativo.

#### Scenario: Config presente e válida
- **WHEN** o Cursor Agent inicia no repo
- **THEN** a configuração versionada em `.cursor/` é carregada
- **AND** nenhuma instrução ativa aponta para `.opencode/` como fonte obrigatória

#### Scenario: Sem segredos no repo
- **WHEN** a configuração versionada é inspecionada
- **THEN** nenhum token, chave ou credencial está presente nos arquivos versionados

### Requirement: Skills e fluxo OpenSpec disponíveis no Cursor
O Cursor SHALL carregar as skills do projeto (OpenSpec `/opsx-*`, design-critic, impeccable, playwright-cli, kaizen) a partir de `.cursor/skills/`, `.cursor/commands/` e `.agents/skills/`, sem duplicar o conteúdo canônico das skills de produto.

#### Scenario: Skills carregadas automaticamente
- **WHEN** o Cursor inicia no repo
- **THEN** as skills `openspec-*`, `design-critic`, `impeccable`, `playwright-cli` e `kaizen` estão disponíveis

#### Scenario: Commands opsx disponíveis
- **WHEN** o usuário invoca `/opsx-new`, `/opsx-ff`, `/opsx-apply`, `/opsx-verify`, `/opsx-archive` ou equivalentes
- **THEN** o command em `.cursor/commands/` executa o fluxo OpenSpec via CLI

### Requirement: Proteção de design system na edição de UI
Edições de arquivos de UI no Cursor SHALL acionar a detecção Impeccable sem quebrar o turno.

#### Scenario: Hook de UI dispara na edição
- **WHEN** um arquivo de frontend é editado pelo Cursor
- **THEN** o hook em `.cursor/hooks.json` roda `.agents/skills/impeccable/scripts/hook.mjs` e reporta achados sem interromper a sessão

### Requirement: Subagent kaizen e command disponíveis
O Cursor SHALL expor o command `/kaizen` e um fluxo de auditoria read-only equivalente ao subagent kaizen.

#### Scenario: Command kaizen carregado
- **WHEN** o Cursor inicia no repo
- **THEN** `/kaizen` (e modos `card`/`release`) está disponível

#### Scenario: Auditoria sem mutação
- **WHEN** a auditoria kaizen é usada
- **THEN** ela não edita arquivos de produto, não altera board/Git/PRs e não reinicia serviços
