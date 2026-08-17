## ADDED Requirements

### Requirement: Prova de promoção estável no round-trip JSON

O sistema SHALL calcular o digest da prova de promoção walk-forward sobre uma representação canônica recursiva alinhada à precisão numérica observável no transporte JSON/JavaScript. Floats finitos e integrais dentro de `±(2^53-1)` SHALL ser convertidos para inteiros; floats integrais fora desse intervalo SHALL permanecer floats; inteiros fora desse intervalo SHALL ser convertidos para o double IEEE-754 finito mais próximo. Booleans SHALL ser preservados, floats fracionários SHALL NOT ser arredondados e valores não finitos ou conversões com overflow SHALL falhar de forma fechada.

#### Scenario: Float integral emitido retorna como inteiro

- **GIVEN** uma otimização com split emite uma prova sobre um payload que contém `8953.0` em um dicionário ou lista aninhada
- **WHEN** o navegador faz o round-trip JSON e envia o mesmo valor como `8953`
- **THEN** o digest calculado na verificação é igual ao digest da emissão
- **AND** a prova permanece válida se assinatura, propósito, expiração e todo o restante do payload forem válidos

#### Scenario: Calmar real acima do intervalo seguro sobrevive ao browser

- **GIVEN** a emissão calcula a prova com `calmar_ratio=3.290195462758171e16` como float
- **AND** esse valor está acima de `Number.MAX_SAFE_INTEGER`
- **WHEN** `JSON.stringify` envia `32901954627581710` e a API reconstrói esse token decimal como inteiro
- **THEN** a emissão preserva o float e a verificação converte o inteiro inseguro para o mesmo double IEEE-754
- **AND** o digest da verificação é igual ao digest da emissão
- **AND** a prova permanece válida se assinatura, propósito, expiração e todo o restante do payload forem válidos

#### Scenario: Limites de inteiro seguro são respeitados

- **GIVEN** valores numéricos nos limites `±(2^53-1)` e além deles
- **WHEN** o digest canônico é calculado
- **THEN** floats integrais dentro dos limites são representados como inteiros
- **AND** floats integrais fora dos limites permanecem floats
- **AND** inteiros fora dos limites são representados pelo double IEEE-754 finito mais próximo
- **AND** booleans permanecem booleans

#### Scenario: Conteúdo realmente diferente invalida a prova

- **GIVEN** uma prova válida emitida para um payload de promoção
- **WHEN** qualquer valor ainda distinguível após o transporte, chave, item ou ordem de lista coberta pelo payload é alterado
- **THEN** o digest verificado diverge
- **AND** a criação do favorito é rejeitada por prova inválida

#### Scenario: Float fracionário não é arredondado

- **GIVEN** um payload com um float que possui parte fracionária
- **WHEN** o digest canônico é calculado
- **THEN** o valor não é arredondado nem truncado para inteiro
- **AND** um payload com valor numérico diferente não reutiliza a mesma prova

#### Scenario: Valor não finito ou inteiro sem double finito falha fechado

- **GIVEN** um payload contém NaN, Infinity ou um inteiro cuja conversão para float causa overflow ou resultado não finito
- **WHEN** a emissão ou verificação tenta calcular o digest canônico
- **THEN** a operação é rejeitada de forma fechada
- **AND** nenhuma equivalência aproximada ou prova válida é produzida

#### Scenario: Precisão perdida pelo Number não pode ser distinguida

- **GIVEN** dois inteiros acima de `2^53` colapsam no mesmo `Number` JavaScript
- **WHEN** eles passam pelo fluxo browser
- **THEN** a prova vincula o double efetivamente transportado
- **AND** o sistema não alega distinguir a precisão inteira que o transporte descartou

#### Scenario: Prova expirada continua inválida

- **GIVEN** uma prova cuja expiração JWT já venceu
- **WHEN** o payload é verificado, ainda que seus números sejam canonicamente equivalentes
- **THEN** a prova é rejeitada

## MODIFIED Requirements

### Requirement: Bloqueio de promoção a favorito sem GO no holdout

A criação de favorito SHALL exigir uma prova walk-forward válida para payloads OOS e SHALL ser bloqueada para candidatos sem veredito GO no holdout, a menos que um override explícito autorizado seja fornecido. A validade da prova SHALL sobreviver às diferenças de representação numérica introduzidas exclusivamente pelo round-trip JSON/JavaScript, incluindo floats integrais seguros e o inteiro decimal emitido para um double fora do intervalo seguro.

#### Scenario: Tentativa de salvar candidato NO-GO sem override

- **GIVEN** um candidato com veredito NO-GO e prova válida para o payload OOS
- **WHEN** `POST /api/favorites/` é executado sem override
- **THEN** a API responde 422/403 com o motivo explícito do gate NO-GO
- **AND** o favorito não é criado

#### Scenario: Override autorizado após round-trip JSON

- **GIVEN** um candidato NO-GO cuja prova foi emitida com floats integrais seguros ou com `calmar_ratio=3.290195462758171e16`
- **AND** o navegador devolve a representação numérica correspondente, inclusive `32901954627581710` para o calmar real
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
