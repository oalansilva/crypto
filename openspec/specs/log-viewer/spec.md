# log-viewer Specification

## Purpose
TBD - created by archiving change card-502-combo-ver-logs-vazio-autoscroll. Update Purpose after archive.
## Requirements
### Requirement: Cada abertura inicia uma sessão visual limpa
O visualizador de logs SHALL capturar um cursor no fim do arquivo ao abrir e SHALL manter a área de conteúdo vazia até existir conteúdo gravado depois desse cursor. Conteúdo anterior à captura SHALL NOT ser renderizado nessa sessão.

#### Scenario: Abrir com histórico acumulado
- **GIVEN** o arquivo de log já contém linhas anteriores
- **WHEN** o usuário abre **Ver logs**
- **THEN** a área de log SHALL iniciar sem essas linhas
- **AND** a interface SHALL informar `Aguardando eventos…`

#### Scenario: Reabrir após uma sessão com conteúdo
- **GIVEN** o usuário recebeu eventos e fechou o modal
- **WHEN** ele reabre **Ver logs**
- **THEN** conteúdo e cursor da sessão anterior SHALL ser descartados
- **AND** uma nova sessão vazia SHALL começar no fim atual do arquivo

### Requirement: Eventos posteriores são entregues uma vez e em ordem
O endpoint `GET /api/logs/tail` SHALL aceitar um cursor opcional `after_offset` em bytes e, quando fornecido, SHALL retornar somente conteúdo posterior ao cursor, em ordem de gravação, junto com o próximo offset utilizável. O cliente SHALL acumular os incrementos sem duplicar conteúdo já consumido.

#### Scenario: Poll incremental com novas linhas
- **GIVEN** o cliente capturou o offset `N` ao abrir
- **AND** novas linhas completas foram anexadas depois de `N`
- **WHEN** o cliente consulta `/api/logs/tail?after_offset=N`
- **THEN** a resposta SHALL conter somente os bytes novos em ordem
- **AND** SHALL fornecer `next_offset` para a próxima consulta

#### Scenario: Poll sem conteúdo novo
- **WHEN** nenhum byte foi anexado depois do cursor informado
- **THEN** a resposta incremental SHALL ter conteúdo vazio
- **AND** `next_offset` SHALL permanecer estável

#### Scenario: Resposta limitada por bytes não perde conteúdo
- **GIVEN** mais bytes novos do que `MAX_INCREMENTAL_BYTES` foram gravados desde o cursor
- **WHEN** o endpoint processa a consulta incremental
- **THEN** a resposta SHALL conter no máximo `MAX_INCREMENTAL_BYTES` de conteúdo novo
- **AND** `next_offset` SHALL apontar para o último byte efetivamente entregue
- **AND** o cliente SHALL continuar do `next_offset` no próximo poll, sem voltar ao tail histórico

#### Scenario: Caractere UTF-8 dividido entre respostas
- **GIVEN** o fim da leitura corta um caractere multibyte no meio
- **WHEN** o endpoint processa a consulta incremental
- **THEN** os bytes incompletos SHALL ser retidos para a próxima resposta
- **AND** nenhum caractere SHALL ser corrompido ou duplicado entre respostas

### Requirement: Rotação e truncamento de arquivo são detectados por identidade
O endpoint SHALL expor uma identidade estável do arquivo (`file_id`) no snapshot e SHALL sinalizar `cursor_reset: true` quando a identidade atual diferir da informada na consulta ou quando `after_offset` exceder o tamanho atual. O cliente SHALL reiniciar a sessão a partir do início do arquivo atual ao receber `cursor_reset`, sem misturar conteúdo antigo.

#### Scenario: Arquivo truncado ou rotacionado
- **GIVEN** o cursor informado é maior que o tamanho atual do arquivo
- **WHEN** o endpoint processa a consulta incremental
- **THEN** ele SHALL sinalizar que o cursor foi resetado
- **AND** SHALL continuar a partir do início do arquivo atual sem falhar

#### Scenario: Arquivo recriado com tamanho igual ou maior
- **GIVEN** o arquivo foi recriado/rotacionado mantendo ou aumentando o tamanho
- **WHEN** o endpoint processa a consulta incremental com o `file_id` antigo
- **THEN** ele SHALL detectar a troca de identidade
- **AND** SHALL sinalizar `cursor_reset: true` para o cliente recomeçar

### Requirement: Polling é single-flight e respostas obsoletas são descartadas
O visualizador SHALL nunca iniciar um novo poll enquanto o anterior estiver em voo e SHALL descartar respostas de sessões fechadas ou fora de ordem, garantindo que cada incremento seja aplicado exatamente uma vez.

#### Scenario: Poll anterior ainda em andamento
- **WHEN** o intervalo de polling dispara com uma requisição anterior ainda em voo
- **THEN** o cliente SHALL não iniciar outra requisição
- **AND** SHALL agendar o próximo poll somente após a resposta atual

#### Scenario: Resposta tardia de sessão fechada
- **GIVEN** o usuário fechou o modal
- **WHEN** uma resposta de uma requisição antiga chega
- **THEN** o cliente SHALL descartá-la
- **AND** a reabertura SHALL iniciar uma sessão vazia nova, sem conteúdo residual

### Requirement: Rolagem automática respeita intenção manual
Enquanto a área de log estiver no final, o visualizador SHALL rolar para a última linha após anexar eventos. Se o usuário se afastar do final, o visualizador SHALL pausar a rolagem automática e SHALL NOT puxá-lo de volta até que ele retorne ao final.

#### Scenario: Eventos chegam com o usuário no final
- **GIVEN** a rolagem automática está ativa
- **WHEN** novos eventos são anexados
- **THEN** a última linha SHALL permanecer visível
- **AND** o estado SHALL indicar `Rolagem automática`

#### Scenario: Usuário consulta histórico da sessão
- **WHEN** o usuário rola acima do limiar de 24 px do final
- **THEN** a rolagem automática SHALL pausar
- **AND** eventos seguintes SHALL ser anexados sem alterar a posição de leitura
- **AND** a interface SHALL indicar `Rolagem pausada` e oferecer **Ir para o fim**

#### Scenario: Usuário retorna ao final
- **WHEN** o usuário rola até o limiar de 24 px do final ou aciona **Ir para o fim**
- **THEN** a rolagem automática SHALL retomar
- **AND** eventos seguintes SHALL manter a última linha visível

### Requirement: Fechamento e acessibilidade do modal são preservados
O visualizador SHALL continuar fechando pelo botão **Fechar**, pelo fundo escuro e pela tecla Escape, SHALL manter foco contido enquanto aberto e SHALL devolver foco ao acionador ao fechar.

#### Scenario: Fechar pelo botão ou fundo
- **WHEN** o usuário aciona **Fechar** ou clica no fundo escuro fora do painel
- **THEN** o modal SHALL fechar
- **AND** o polling da sessão SHALL parar

#### Scenario: Operar por teclado
- **WHEN** o modal está aberto
- **THEN** seu título e estado SHALL possuir nomes acessíveis
- **AND** o foco SHALL permanecer no modal até o fechamento
- **AND** Escape SHALL fechar o modal e devolver foco ao botão **Ver logs**

### Requirement: O contrato legado de tail permanece compatível
Chamadas a `GET /api/logs/tail` que omitem `after_offset` SHALL continuar retornando as últimas `lines` linhas com os campos atuais `name`, `path`, `lines` e `content`. Os campos adicionais de cursor SHALL ser aditivos.

#### Scenario: Consumidor existente solicita últimas linhas
- **WHEN** um consumidor chama `/api/logs/tail` apenas com `name` e `lines`
- **THEN** a seleção e o conteúdo das últimas linhas SHALL permanecer equivalentes ao comportamento anterior
- **AND** nenhum parâmetro novo SHALL ser obrigatório

