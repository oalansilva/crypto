## ADDED Requirements

### Requirement: Configuração versionada de ferramenta de desenvolvimento
O repositório SHALL conter configuração de ferramenta de desenvolvimento (opencode) versionada, incluindo `opencode.json` na raiz e arquivos em `.opencode/` (agents, commands, plugin).

#### Scenario: Config presente e válida
- **WHEN** a ferramenta de desenvolvimento opencode é iniciada no repo
- **THEN** a configuração versionada em `opencode.json` e `.opencode/` é carregada sem erro de schema

#### Scenario: Sem segredos no repo
- **WHEN** a configuração versionada é inspecionada
- **THEN** nenhum token, chave ou credencial está presente nos arquivos versionados

### Requirement: Skills e fluxo OpenSpec disponíveis no opencode
O opencode SHALL carregar as skills do projeto (OpenSpec `/opsx:*`, design-critic, impeccable, playwright-cli) a partir dos diretórios canônicos `.agents/skills/` e `.claude/skills/`, sem duplicação de conteúdo.

#### Scenario: Skills carregadas automaticamente
- **WHEN** o opencode inicia no repo
- **THEN** as skills `openspec-*`, `design-critic`, `impeccable` e `playwright-cli` estão disponíveis

#### Scenario: Commands opsx disponíveis
- **WHEN** o usuário invoca `/opsx:<new|ff|apply|verify|archive|continue|explore|sync|onboard|bulk-archive>`
- **THEN** o command correspondente em `.opencode/command/` executa o fluxo OpenSpec

### Requirement: Proteção de design system na edição de UI
Edições de arquivos de UI no opencode SHALL acionar a detecção de desvios do design system (impeccable) sem quebrar o turno.

#### Scenario: Hook de UI dispara na edição
- **WHEN** um arquivo de frontend é editado pelo opencode
- **THEN** o plugin impeccable-hook roda o detector e reporta achados sem interromper a sessão
