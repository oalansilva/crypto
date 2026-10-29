# board-executor Specification

## Purpose
TBD - created by archiving change card-1135-comandos-portoes-alan. Update Purpose after archive.
## Requirements
### Requirement: Só o executor escreve no Project 1
O token com escrita no Project 1 SHALL existir só como secret do environment `portao` do repositório do executor, com branches de deploy restritas a `main`, e o workflow do executor SHALL ser disparado por `repository_dispatch`. Nenhum arquivo, variável de ambiente ou cofre acessível na VM MUST guardar token GitHub com escrita no Project 1. O login do agente MUST NOT ter papel no Project 1.

#### Scenario: Agente com o próprio login tenta mudar o Status
- **WHEN** o comando `gh project item-edit` do campo Status do Project 1 roda com o token do agente
- **THEN** o GitHub recusa por permissão
- **AND** o Status do card não muda

#### Scenario: Inventário de credenciais na VM depois da migração
- **WHEN** o operador confere `~/.config/gh/hosts.yml`, o ambiente e os cofres da VM
- **THEN** o único token GitHub encontrado é o do agente, sem escrita no Project 1

### Requirement: Executor confere coluna de origem, evento e ator antes de mover
Para cada pedido, o executor SHALL ler o Status vivo do card com o próprio token, achar a transição da FSM do SHA fixado para `(Status vivo, evento)` e mover só quando o `de` do pedido for igual ao Status vivo e ao `from` da transição, e o ator do pedido pertencer ao `actor` da transição. Pedido do tipo `pedir` SHALL aceitar só os atores `Agent`, `Guard` e `CI`; evento cuja transição tem `actor: Alan` MUST ser recusado com motivo `actor`. Recusa MUST deixar o Status inalterado e devolver o motivo.

#### Scenario: Transição do agente com coluna certa
- **WHEN** chega um pedido `pedir` de `pedir_review` com `de=Em desenvolvimento` e o card está em Em desenvolvimento
- **THEN** o executor move para Code Review e devolve `movido`

#### Scenario: Transição do agente com coluna errada
- **WHEN** chega um pedido `pedir` de `pedir_review` com `de=Em desenvolvimento` e o card está em QA
- **THEN** o executor recusa com o Status atual no motivo
- **AND** o Status não muda

#### Scenario: Portão do Alan pedido pelo agente
- **WHEN** chega um pedido `pedir` de `aprovar_design`, `priorizar`, `homologar`, `nao_homologar`, `devolver_design` ou `cancelar`
- **THEN** o executor recusa com motivo `actor`
- **AND** o Status não muda

### Requirement: Lei e código do executor só mudam com o Alan
O workflow do executor SHALL fazer checkout do SHA do `crypto` registrado no arquivo `PIN` do repositório do executor e ler `.cursor/process-fsm.yaml` desse SHA como dado (`yaml.safe_load`), sem rodar código da branch de trabalho do agente. A `main` do repositório do executor SHALL exigir PR aprovado pelo Alan, sem bypass para a conta do agente. Se a FSM do SHA fixado não tiver T1, T2, T6, T7, T15 e T18 só com ator `Alan`, o executor MUST recusar todo pedido com motivo `lei_invalida`.

#### Scenario: FSM fixada dá um portão ao agente
- **WHEN** a FSM do SHA fixado lista `Agent` no ator de T7
- **THEN** todo pedido é recusado com `lei_invalida` e nenhum Status muda

#### Scenario: Pedido válido no worktree e sem aresta na lei fixada
- **WHEN** um pedido do agente cita um evento sem transição na FSM do SHA fixado para o Status vivo
- **THEN** o executor recusa com `no_edge` e o Status não muda

### Requirement: Todo movimento deixa recibo e run
Cada pedido SHALL produzir um run no repositório do executor com o pedido no input, e cada comando reconhecido do Alan e cada movimento pedido pelo agente SHALL deixar um comentário de recibo na issue com: o comando ou evento, o resultado (`De → Para` ou recusa com motivo), data e hora, cliente, superfície e versão do host, sessão, URL do run e SHA da lei. Quando houver motivo (T6, T18, T2), a primeira linha do comentário SHALL ser `Devolver design: <motivo>`, `Não homologar: <motivo>` ou `Cancelar: <motivo>`. Pedidos para o mesmo card MUST ser serializados.

#### Scenario: Recibo de não homologar satisfaz o motivo visível
- **WHEN** o executor move um card de Done para Em desenvolvimento por `/nao-homologar N "texto"`
- **THEN** a issue N ganha um comentário cuja primeira linha é `Não homologar: texto`
- **AND** o comentário traz cliente, data e hora e a URL do run

#### Scenario: Dois pedidos simultâneos para o mesmo card
- **WHEN** dois pedidos para o card N chegam ao mesmo tempo
- **THEN** o segundo só é avaliado depois de o primeiro terminar, contra o Status vivo de então

