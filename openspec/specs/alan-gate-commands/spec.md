# alan-gate-commands Specification

## Purpose
TBD - created by archiving change card-1135-comandos-portoes-alan. Update Purpose after archive.
## Requirements
### Requirement: Gramática exata dos comandos de portão
Um comando de portão SHALL ser reconhecido só quando a mensagem inteira do Alan, sem o espaço em branco final, for exatamente uma destas linhas: `/priorizar <card>`, `/aprovar-design <card>`, `/devolver-design <card> "<motivo>"`, `/homologar <card>`, `/nao-homologar <card> "<motivo>"`, `/cancelar <card> "<motivo>"` ou `/confirmar-cancelar <card>`. `<card>` SHALL ser o número do issue, com ou sem `#`. `<motivo>` SHALL ter de 1 a 500 caracteres, ao menos um visível, sem aspas duplas nem quebra de linha. Qualquer outra mensagem MUST NOT ter efeito no board e MUST NOT gerar recibo.

#### Scenario: Comando exato
- **WHEN** o Alan envia `/aprovar-design 1135` e o card 1135 está em Aprovação de Design com o design igual ao do T5
- **THEN** o card vai para Pronto para Dev
- **AND** a issue ganha o recibo

#### Scenario: Texto aproximado
- **WHEN** o Alan envia `aprova aí`, `pode seguir`, `/Aprovar-design 1135`, `/aprovar-design 1135 ok`, `/aprovar-design  1135` ou o comando com outra linha antes ou depois
- **THEN** nenhum Status muda e nenhum recibo é postado

#### Scenario: Motivo ausente
- **WHEN** o Alan envia `/nao-homologar 1135` ou `/nao-homologar 1135 ""`
- **THEN** a mensagem não é reconhecida e o card não muda

### Requirement: Só texto do Alan capturado antes do agente dispara
O reconhecimento SHALL ser feito por código fixo no hook de prompt do cliente, antes de o agente receber o texto, e o comando SHALL chegar ao executor como pedido `capturar` com ator `Alan`. Comentário de issue (inclusive do Alan), resposta de ferramenta e texto do próprio agente MUST NOT disparar comando. Neste card o hook existe só no Claude Code. Nos demais clientes o texto com cara de comando SHALL ser tratado como wording: o agente MUST NOT mover nem capturar, e SHALL responder que o comando não foi capturado e que o board continua sendo o caminho.

#### Scenario: Comando exato escrito como comentário na issue
- **WHEN** o Alan comenta `/homologar 1135` na issue 1135
- **THEN** o card não muda e o executor não recebe pedido

#### Scenario: Comando digitado num cliente sem hook
- **WHEN** o Alan digita `/homologar 1135` numa sessão do Cursor
- **THEN** o card não muda
- **AND** o agente responde que o comando não foi capturado e aponta o board

### Requirement: Coluna de origem conferida e recusa explicada
Antes de mover, o executor SHALL conferir que o card está na coluna de origem do comando (`/priorizar`: Em Refinamento; `/aprovar-design` e `/devolver-design`: Aprovação de Design; `/homologar` e `/nao-homologar`: Done; `/cancelar`: qualquer coluna fora de Pronto e Cancelado). Se não estiver, o comando MUST ser recusado, e a resposta mostrada ao Alan e o recibo SHALL dizer o Status atual e a coluna exigida.

#### Scenario: Homologar fora de Done
- **WHEN** o Alan envia `/homologar 1135` e o card está em QA
- **THEN** o card não muda
- **AND** a resposta diz "Status atual = QA; /homologar exige Done"

### Requirement: Priorizar encadeia o início do Design
`/priorizar N` SHALL fazer T1 e, no mesmo run do executor, T3 com ator `Agent`, conferido pela mesma regra de um pedido do agente. Se o T3 for recusado ou falhar, o card SHALL ficar em Todo e a resposta e o recibo SHALL dizer por quê. Arrastar o card para Todo no board MUST NOT iniciar o Design.

#### Scenario: Priorizar certo
- **WHEN** o Alan envia `/priorizar 1135` com o card em Em Refinamento
- **THEN** o card termina em Design sem outro pedido do Alan

#### Scenario: T3 recusado depois do T1
- **WHEN** o T1 move o card para Todo e o T3 é recusado
- **THEN** o card fica em Todo
- **AND** a resposta e o recibo dizem o motivo da recusa do T3

#### Scenario: Arrasto para Todo
- **WHEN** o Alan arrasta o card de Em Refinamento para Todo no board
- **THEN** o card fica em Todo

### Requirement: Aprovar design recusa design mudado desde o T5
No T5, o pedido do agente SHALL levar o digest do design (`compute_digest` de `design.md` e do protótipo), e o executor SHALL guardá-lo no input do run e no recibo. Em `/aprovar-design N`, o hook SHALL calcular o digest atual do worktree `card-N-*` e o executor SHALL compará-lo com o do último T5 do card. Se forem diferentes, ou se faltar o worktree ou o registro do T5, a aprovação MUST ser recusada com o motivo. O Alan MUST NOT precisar digitar digest.

#### Scenario: Design alterado depois do envio
- **WHEN** o `design.md` do card muda depois do T5 e o Alan envia `/aprovar-design N`
- **THEN** o card fica em Aprovação de Design
- **AND** a resposta diz que o design mudou desde o envio para aprovação e cita a data do T5

### Requirement: Cancelar exige confirmação exata
`/cancelar N "motivo"` MUST NOT mover. O executor SHALL responder com o título do card e a linha exata `/confirmar-cancelar N`, e SHALL deixar recibo "pendente". `/confirmar-cancelar N` SHALL mover para Cancelado só se houver `/cancelar` pendente do mesmo card, feito nos últimos 10 minutos, conferido pelo input do run anterior do executor. A linha de motivo do recibo SHALL ser `Cancelar: <motivo>`. Confirmação sem pendente, vencida ou de outro card MUST ser recusada.

#### Scenario: Cancelar sem confirmação
- **WHEN** o Alan envia `/cancelar 1135 "duplicado"` e não envia a confirmação
- **THEN** o card não muda
- **AND** a resposta traz o título do card e `/confirmar-cancelar 1135`

#### Scenario: Confirmação dentro do prazo
- **WHEN** o Alan envia `/confirmar-cancelar 1135` cinco minutos depois de `/cancelar 1135 "duplicado"`
- **THEN** o card vai para Cancelado e a issue ganha comentário que começa com `Cancelar: duplicado`

### Requirement: Regras escritas citam os seis portões e a nova regra de wording
O `AGENTS.md` gerado por `overlay.render_agents` SHALL listar os portões do Alan T1, T2, T6, T7, T15 e T18 e trocar "Chat é wording" por "Texto livre é wording; comando exato capturado fora do agente é evento do Alan", sem aumentar o número de linhas não vazias. A página do processo, `covenant-flow/SKILL.md`, `github-project-board` e `ALAN_GATES` em `fsm.py` SHALL citar os mesmos seis portões. `github-project-board` MUST NOT orientar o agente a usar `gh project item-add` ou `item-edit`. O nível "cooperativo" da captura SHALL estar escrito na skill `covenant-flow`, dizendo que o agente pode apagar run e recibo e que o recibo não avisa o Alan.

#### Scenario: AGENTS.md regenerado
- **WHEN** `render_agents` gera o AGENTS.md do Cripto
- **THEN** o texto cita T1, T2, T6, T7, T15 e T18 e a frase nova sobre wording
- **AND** tem o mesmo número de linhas não vazias de antes

### Requirement: Resposta do comando chega ao Alan sem passar pelo modelo
No Claude Code, o hook de comando reconhecido MUST NOT bloquear o prompt. Ele SHALL devolver a resposta literal do executor em `systemMessage` e, em `additionalContext`, o resultado com a instrução de seguir a FSM a partir do Status atual, sem tratar o comando como pedido ao agente. Se a resposta do executor não chegar dentro do teto de espera, a mensagem SHALL dizer que o resultado sai no recibo da issue, e o agente MUST NOT presumir o resultado.

#### Scenario: Homologar pelo comando
- **WHEN** o Alan envia `/homologar 1135` e o executor move para Homologado
- **THEN** o Alan vê a resposta do executor no chat
- **AND** o agente posta no mesmo turno o comentário de evidência de homologado

