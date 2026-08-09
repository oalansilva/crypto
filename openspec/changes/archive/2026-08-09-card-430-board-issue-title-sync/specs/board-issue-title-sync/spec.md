## ADDED Requirements

### Requirement: Sincronização de título board/issue no fechamento
No momento do `Done`, o título do card no board SHALL ser igual ao título da issue, ou o card deve conter comentário registrando divergência aprovada.

#### Scenario: Títulos divergentes no Done
- **WHEN** um card é movido para `Done` com título do board diferente do título da issue e sem comentário de divergência aprovada
- **THEN** o fechamento sincroniza o título do board com a issue ou registra a divergência

#### Scenario: Títulos iguais
- **WHEN** o título do board e o título da issue são idênticos no `Done`
- **THEN** nenhuma ação adicional é necessária

### Requirement: Troca de modelo de subagent exige sessão nova
A troca de modelo/configuração de um subagent SHALL exigir nova sessão (nova sessão principal ou nova worktree com recarga de configuração); sessões/spawns em voo continuam no modelo antigo e não devem ser assumidos como atualizados.

#### Scenario: Merge muda modelo do subagent
- **WHEN** um merge altera a configuração de modelo de um subagent
- **THEN** spawns em sessões em voo permanecem no modelo antigo e a nova configuração só vale em sessões novas
- **AND** a documentação orienta iniciar nova sessão após troca de modelo

#### Scenario: Auditoria detecta modelo antigo pós-merge
- **WHEN** a auditoria kaizen analisa sessões da release
- **THEN** ela reporta o sinal "modelo antigo pós-merge" para spawns com modelo divergente da configuração vigente
