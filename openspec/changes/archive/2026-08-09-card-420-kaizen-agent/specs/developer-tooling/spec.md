# developer-tooling Specification

## Purpose
Configuração versionada de ferramenta de desenvolvimento (opencode) no repositório: agents, commands, skills e proteções de edição.

## ADDED Requirements

### Requirement: Subagent kaizen e command disponíveis
O opencode SHALL carregar o subagent auditor `kaizen` (`.opencode/agent/kaizen.md`, read-only) e o command `/kaizen` (`.opencode/commands/kaizen.md`) a partir da configuração versionada.

#### Scenario: Subagent kaizen carregado
- **WHEN** o opencode inicia no repo
- **THEN** o subagent `kaizen` está disponível como agente de auditoria read-only
- **AND** o command `/kaizen` (e modos `card`/`release`) executa o fluxo de auditoria

#### Scenario: Auditoria sem mutação
- **WHEN** o subagent kaizen é usado
- **THEN** ele não edita arquivos, não altera board/Git/PRs e não reinicia serviços
