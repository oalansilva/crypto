# kaizen-continuous-improvement Delta Specification

## MODIFIED Requirements

### Requirement: Registro de melhorias como cards PO no board

Cada melhoria acionável da auditoria SHALL ser registrada como 1 issue separada no repo, em formato de proposta PO (`## Proposta (PO)` com Contexto, Escopo, Critérios de aceite), com label `kaizen`, `Status=Em Refinamento` no Project 1, campos preenchidos (`Prioridade` P0/P1/P2, `Tipo`, `Frente`, `Responsavel`, `Semana`) e dependências linkadas.

#### Scenario: Card criado como entrada
- **WHEN** o Kaizen (via orquestrador de closeout) registra uma melhoria
- **THEN** a issue é criada com label `kaizen` e `Status=Em Refinamento` no board
- **AND** o fluxo normal do board (`Em Refinamento` → `Todo` → Design → …) é seguido a partir daí

#### Scenario: Limite de 3 cards por release
- **WHEN** uma análise gera mais de 3 melhorias
- **THEN** apenas os 3 de maior prioridade entram como cards na release atual
- **AND** as demais permanecem no backlog kaizen para releases seguintes

## ADDED Requirements

### Requirement: Evidência de materialização Kaizen no fechamento de release

Antes de concluir o `release-guard post`, a entrada canônica de `/kaizen release` em `docs/kaizen-log.md` para a data da release MUST evidenciar materialização de melhorias acionáveis: (a) 1 a 3 issues novas listadas na tabela cujo heading `###` **começa com** `Cards kaizen criados` (sufixo livre) sob o(s) heading(s) `## YYYY-MM-DD — Kaizen release`, ou (b) linhas `(não criado)` com `coberto por` seguido de um ou mais `#N` (todos em fluxo no Project 1: Status presente e não `Pronto`/`Cancelado`), ou (c) marcador explícito `Sem achados acionáveis` quando não houver linhas de dados na união das tabelas. Qualquer linha de dados inválida (ex. `(não criado)` sem cobertura, `observação; sem card novo`) MUST falhar o check mesmo se houver cards criados ou marcador. A auditoria da skill `kaizen` permanece read-only; a criação de issues é responsabilidade do orquestrador de closeout e o guard apenas valida.

#### Scenario: Post bloqueia sem cards nem dedupe válido
- **WHEN** o `post` encontra heading Kaizen da data mas a união das tabelas `Cards kaizen criados` não tem issues novas nem dedupe válido nem marcador sem achados acionáveis
- **THEN** o guard emite blocker e não autoriza promover o pacote a `Pronto`

#### Scenario: Post passa com cards listados
- **WHEN** a união das tabelas lista entre 1 e 3 issues `#N` criadas, sem linhas inválidas, e qualquer dedupe extra tem todas as coberturas em fluxo
- **THEN** o check de materialização Kaizen passa

#### Scenario: Post passa com zero cards e dedupe em fluxo
- **WHEN** não há issues novas na tabela e cada linha `(não criado)` cita `coberto por` com um ou mais `#N`, e **todos** esses `#N` estão em Status de fluxo no Project 1
- **THEN** o check de materialização Kaizen passa

#### Scenario: Post passa com marcador sem achados acionáveis
- **WHEN** a união das seções da data não tem linhas de dados na(s) tabela(s) (ausente ou só header) e o corpo contém `Sem achados acionáveis` (case-insensitive)
- **THEN** o check de materialização Kaizen passa

#### Scenario: Marcador não salva linhas inválidas
- **WHEN** existe marcador `Sem achados acionáveis` e também há linha de dados inválida ou dedupe malformado na tabela
- **THEN** o guard emite blocker

#### Scenario: Dedupe com cobertura Pronto ou Cancelado falha
- **WHEN** uma linha `(não criado)` cita `coberto por #N` (um ou vários) e qualquer `#N` está `Pronto` ou `Cancelado` (ou ausente no board)
- **THEN** o guard emite blocker

#### Scenario: Mais de 3 cards na data falha
- **WHEN** a união das tabelas da data lista mais de 3 issues distintas criadas
- **THEN** o guard emite blocker

#### Scenario: Linha inválida falha mesmo com cards criados
- **WHEN** a tabela tem 1–3 `#N` criados e também uma linha `(não criado)` sem `coberto por #N` (ou `observação; sem card novo`)
- **THEN** o guard emite blocker

#### Scenario: Board indisponível com dedupe falha fechado
- **WHEN** há ao menos uma linha dedupe que exige checagem de cobertura e o snapshot do Project 1 está indisponível ou incompleto
- **THEN** o guard emite blocker fail-closed
