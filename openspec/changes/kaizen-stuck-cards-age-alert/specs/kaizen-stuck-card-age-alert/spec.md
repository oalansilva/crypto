## ADDED Requirements

### Requirement: Inventário de cards por idade de coluna no guard audit
O `scripts/release-guard audit` SHALL listar os cards do board com idade por coluna (dias desde a última atualização registrada), emitindo warn informativo para cards com mais de 30 dias sem atualização na coluna atual.

#### Scenario: Card preso há mais de 30 dias
- **WHEN** `release-guard audit` encontra um card com mais de 30 dias desde a última atualização na coluna atual
- **THEN** o guard emite WARN informativo com número do card, título, coluna e idade em dias
- **AND** a saída não bloqueia a execução de outros checks (warn informativo)

#### Scenario: Cards dentro do limite de idade
- **WHEN** todos os cards estão com menos de 30 dias de idade na coluna atual
- **THEN** o guard não emite warnings de idade de cards

#### Scenario: Coluna ou idade indisponível
- **WHEN** o guard não consegue obter a data de atualização de um card
- **THEN** o guard registra a falha como warn sem interromper o restante do inventário

### Requirement: Triagem do card #195 com decisão registrada
O card #195 SHALL ser triado (avançar para `Todo`, cancelar ou transferir) com comentário de decisão no card, registrando motivo e prioridade.

#### Scenario: Triagem concluída
- **WHEN** a triagem do #195 é executada
- **THEN** o card recebe status de destino (`Todo`/`Cancelado`/transferência) com comentário de decisão explícito
- **AND** a decisão é registrada no `docs/kaizen-log.md`
