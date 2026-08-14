## ADDED Requirements

### Requirement: Prova de promoção estável no round-trip JSON

O sistema SHALL calcular o digest da prova de promoção walk-forward sobre uma representação canônica recursiva do payload, tratando todo `float` finito e integral como equivalente ao inteiro de mesmo valor, sem alterar valores fracionários, strings, booleans, valores nulos, estrutura de objetos ou ordem de listas.

#### Scenario: Float integral emitido retorna como inteiro

- **GIVEN** uma otimização com split emite uma prova sobre um payload que contém `8953.0` em um dicionário ou lista aninhada
- **WHEN** o navegador faz o round-trip JSON e envia o mesmo valor como `8953`
- **THEN** o digest calculado na verificação é igual ao digest da emissão
- **AND** a prova permanece válida se assinatura, propósito, expiração e todo o restante do payload forem válidos

#### Scenario: Conteúdo realmente diferente invalida a prova

- **GIVEN** uma prova válida emitida para um payload de promoção
- **WHEN** qualquer valor não equivalente, chave, item ou ordem de lista coberta pelo payload é alterado
- **THEN** o digest verificado diverge
- **AND** a criação do favorito é rejeitada por prova inválida

#### Scenario: Float fracionário não é arredondado

- **GIVEN** um payload com um float que possui parte fracionária
- **WHEN** o digest canônico é calculado
- **THEN** o valor não é arredondado nem truncado para inteiro
- **AND** um payload com valor numérico diferente não reutiliza a mesma prova

#### Scenario: Prova expirada continua inválida

- **GIVEN** uma prova cuja expiração JWT já venceu
- **WHEN** o payload é verificado, ainda que seus números sejam canonicamente equivalentes
- **THEN** a prova é rejeitada

## MODIFIED Requirements

### Requirement: Bloqueio de promoção a favorito sem GO no holdout

A criação de favorito SHALL exigir uma prova walk-forward válida para payloads OOS e SHALL ser bloqueada para candidatos sem veredito GO no holdout, a menos que um override explícito autorizado seja fornecido. A validade da prova SHALL sobreviver a diferenças de representação `float` integral versus inteiro introduzidas exclusivamente pelo round-trip JSON.

#### Scenario: Tentativa de salvar candidato NO-GO sem override

- **GIVEN** um candidato com veredito NO-GO e prova válida para o payload OOS
- **WHEN** `POST /api/favorites/` é executado sem override
- **THEN** a API responde 422/403 com o motivo explícito do gate NO-GO
- **AND** o favorito não é criado

#### Scenario: Override autorizado após round-trip JSON

- **GIVEN** um candidato NO-GO cuja prova foi emitida com floats integrais no payload
- **AND** o navegador devolve os mesmos valores como inteiros
- **WHEN** um admin envia `override_oos: true` com a prova válida
- **THEN** a verificação da prova é aceita
- **AND** o favorito é criado com o veredito NO-GO preservado

#### Scenario: Override sem permissão continua bloqueado

- **GIVEN** um candidato NO-GO com prova válida
- **WHEN** um usuário sem permissão de admin envia `override_oos: true`
- **THEN** o favorito não é criado
- **AND** a API informa o bloqueio de autorização/gate

#### Scenario: Candidato GO não requer override

- **GIVEN** um candidato com veredito GO e prova válida para o payload OOS
- **WHEN** `POST /api/favorites/` é executado sem override
- **THEN** o favorito é criado

#### Scenario: Salvamento automático do batch

- **WHEN** o batch backtest tenta salvar automaticamente um candidato NO-GO no holdout
- **THEN** o candidato não é salvo como favorito
- **AND** o motivo é registrado no resultado do job do batch
