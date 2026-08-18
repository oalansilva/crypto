## MODIFIED Requirements

### Requirement: Análise de imagem na sessão Cursor
A sessão Cursor SHALL analisar imagens com a ferramenta `Read` no modelo do chat quando esse modelo aceitar pixels. Um subagent de visão com modelo fixo Qwen/OpenCode MUST NOT ser obrigatório.

#### Scenario: Imagem anexada ou screenshot no disco
- **WHEN** a tarefa exige julgamento visual de um PNG/JPEG/WebP existente
- **THEN** o agente confirma que o path existe
- **AND** abre o arquivo com `Read` na sessão (ou Task `inherit` se a sessão principal for cega)
- **AND** NÃO exige `vision-router` nem `opencode-go/qwen3.7-plus`

#### Scenario: Modelo da sessão não vê pixels
- **WHEN** o modelo do chat não aceita imagem
- **THEN** a sessão declara o bloqueio e pede a Alan um modelo com visão, ou spawna Task em modelo com visão autorizado no chat
- **AND** NÃO cai automaticamente para Qwen/OpenCode

## REMOVED Requirements

### Requirement: Roteamento automático de análise de imagem
### Requirement: Agente vision com modelo fixo
### Requirement: Evidência de roteamento
