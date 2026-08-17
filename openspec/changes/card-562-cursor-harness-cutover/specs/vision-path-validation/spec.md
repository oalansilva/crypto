## MODIFIED Requirements

### Requirement: Path-check antes de análise visual
Antes de abrir uma imagem para julgamento visual, o fluxo SHALL confirmar que o path existe (`ls`/glob) e que URLs são resolvíveis. Path inexistente ou URL inválida bloqueia a leitura.

#### Scenario: Path inexistente
- **WHEN** um path de imagem/artefato não existe
- **THEN** o agente NÃO chama `Read` nesse path
- **AND** gera o artefato no caminho canônico antes de tentar de novo

#### Scenario: URL inválida
- **WHEN** uma URL não é resolvível (404/erro)
- **THEN** o fluxo não trata a URL como evidência visual e registra o bloqueio

#### Scenario: Paths validados
- **WHEN** os paths existem
- **THEN** a análise visual na sessão (ou Task `inherit`) segue sem respawn do mesmo path inexistente
