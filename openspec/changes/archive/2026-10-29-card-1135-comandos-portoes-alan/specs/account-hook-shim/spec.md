## ADDED Requirements

### Requirement: Registro na conta do Claude Code inclui o hook de prompt
O registro na conta do Claude Code SHALL incluir uma entrada `UserPromptSubmit` que chama o shim, e o shim SHALL tratar esse evento como evento que gateia o Claude Code: confere consumidor, pin e revisão R/A e chama `claude_adapter.py` pinado com o payload original. Adapter ausente, divergente ou não revisado SHALL falhar visível, e o comando MUST NOT ser capturado. A entrada nova muda o digest R e SHALL exigir revisão do operador e sessão nova, como qualquer mudança de registro. Cursor, Codex, OpenCode, Grok Build e dsh MUST NOT ganhar hook de prompt neste card.

#### Scenario: Hook de prompt sem revisão
- **WHEN** a entrada `UserPromptSubmit` foi instalada e o operador ainda não rodou `cf_shim.py trust --record`
- **THEN** o hook falha visível com `hooks_unreviewed`
- **AND** nenhum comando do Alan chega ao executor

#### Scenario: Instalador preserva hooks alheios
- **WHEN** `install.sh --account` adiciona a entrada `UserPromptSubmit` a um `~/.claude/settings.json` com hooks de terceiros
- **THEN** os hooks de terceiros continuam iguais e `--check` mostra a entrada nova
