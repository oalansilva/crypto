# Walk-forward OOS Gate Specification

## ADDED Requirements

### Requirement: O gate SHALL avaliar IS e OOS com perfis independentes

O sistema SHALL avaliar Treino (IS) e Holdout (OOS) separadamente. IS SHALL usar os critérios globais atuais, incluindo no mínimo 100 trades fechados e Sharpe 0.8. OOS SHALL usar no mínimo 20 trades fechados e Sharpe absoluto 0.30, mantendo os demais critérios globais vigentes. O sistema SHALL NOT somar trades de IS e OOS para satisfazer qualquer mínimo.

#### Scenario: IS aprovado e OOS abaixo do mínimo de trades

- **GIVEN** IS atende todos os critérios atuais
- **AND** OOS possui 19 trades fechados
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é NO-GO
- **AND** a razão identifica `Holdout (OOS)`, o valor 19 e o mínimo 20

#### Scenario: OOS no limite inclusivo de trades

- **GIVEN** IS atende todos os critérios atuais
- **AND** OOS possui exatamente 20 trades fechados e atende todos os demais critérios
- **WHEN** o gate walk-forward é avaliado
- **THEN** a contagem de trades OOS é aprovada
- **AND** o resultado inclui aviso de amostra pequena

#### Scenario: OOS com amostra pequena aprovada

- **GIVEN** IS atende todos os critérios atuais
- **AND** OOS possui entre 20 e 29 trades fechados
- **AND** OOS atende Sharpe absoluto, retenção e todos os demais critérios
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é GO
- **AND** existe aviso legível de amostra OOS pequena

### Requirement: OOS SHALL preservar ao menos 50% do Sharpe IS

Além do piso absoluto 0.30, o Sharpe OOS SHALL ser maior ou igual a 50% do Sharpe IS. O limiar efetivo SHALL ser `max(0.30, 0.50 × Sharpe IS)`. A igualdade SHALL ser aprovada.

#### Scenario: IS aprovado e OOS abaixo do piso absoluto

- **GIVEN** IS atende todos os critérios atuais
- **AND** OOS possui trades suficientes
- **AND** Sharpe OOS é 0.29
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é NO-GO
- **AND** a razão identifica Sharpe OOS 0.29 e piso absoluto 0.30

#### Scenario: degradação IS→OOS acima do tolerado

- **GIVEN** IS atende todos os critérios atuais com Sharpe 1.00
- **AND** OOS possui trades suficientes e Sharpe 0.45
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é NO-GO
- **AND** a razão informa retenção 45%, mínimo 50% e limiar OOS 0.50

#### Scenario: limite relativo inclusivo

- **GIVEN** IS atende todos os critérios atuais com Sharpe 0.80
- **AND** OOS possui trades suficientes, Sharpe 0.40 e atende os demais critérios
- **WHEN** o gate walk-forward é avaliado
- **THEN** os critérios absoluto e relativo de Sharpe OOS são aprovados

### Requirement: O gate combinado SHALL ser fail-closed

O resultado final SHALL ser GO somente quando IS, OOS e consistência IS→OOS forem aprovados. Um segmento SHALL NOT compensar a reprovação do outro. Métricas obrigatórias ausentes, nulas, `NaN` ou infinitas SHALL produzir NO-GO com razão segmentada.

#### Scenario: IS fraco e OOS forte

- **GIVEN** IS reprova qualquer critério vigente
- **AND** OOS atende todos os critérios OOS e de consistência aplicáveis
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é NO-GO
- **AND** ao menos uma razão identifica `Treino (IS)`

#### Scenario: IS aprovado e OOS fraco

- **GIVEN** IS atende todos os critérios atuais
- **AND** OOS reprova qualquer critério OOS
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é NO-GO
- **AND** ao menos uma razão identifica `Holdout (OOS)` ou `Consistência IS→OOS`

#### Scenario: métrica OOS ausente

- **GIVEN** IS atende todos os critérios atuais
- **AND** uma métrica obrigatória OOS está ausente ou não finita
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é NO-GO
- **AND** a razão identifica o segmento e a métrica inválida

### Requirement: O caso 23 trades e Sharpe OOS 0.32 SHALL ser reprovado

Quando IS estiver aprovado, um OOS com 23 trades e Sharpe 0.32 SHALL aprovar a contagem com aviso, SHALL aprovar o piso absoluto e SHALL reprovar a consistência relativa, pois um IS aprovado possui Sharpe de pelo menos 0.80.

#### Scenario: caso de referência com IS no mínimo

- **GIVEN** IS atende todos os critérios atuais com Sharpe 0.80
- **AND** OOS possui 23 trades, Sharpe 0.32 e atende os demais critérios
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é NO-GO
- **AND** existe aviso de amostra pequena
- **AND** a razão informa retenção 40%, mínimo 50% e limiar OOS 0.40

### Requirement: Mensagens SHALL explicar o resultado por segmento

Razões e avisos SHALL identificar `Treino (IS)`, `Holdout (OOS)` ou `Consistência IS→OOS`, SHALL incluir o valor observado e SHALL incluir o limite relevante. Falhas SHALL ser ordenadas por IS, OOS e consistência. Um resultado GO SHALL confirmar que os três componentes foram aprovados.

#### Scenario: múltiplas falhas

- **GIVEN** IS e OOS reprovam critérios distintos
- **WHEN** o gate walk-forward é avaliado
- **THEN** todas as razões relevantes são preservadas
- **AND** razões de IS aparecem antes das razões de OOS
- **AND** razões de consistência aparecem depois das razões dos segmentos

#### Scenario: gate combinado aprovado

- **GIVEN** IS atende todos os critérios atuais
- **AND** OOS atende todos os critérios OOS
- **AND** Sharpe OOS preserva ao menos 50% do Sharpe IS
- **WHEN** o gate walk-forward é avaliado
- **THEN** o resultado final é GO
- **AND** o resumo confirma aprovação de IS, OOS e consistência

### Requirement: Override administrativo SHALL permanecer explícito

Um NO-GO combinado SHALL continuar bloqueando a criação de favorito. Somente um administrador, por ação explícita no fluxo já existente, MAY aplicar override. O override SHALL NOT apagar nem alterar as razões calculadas pelo gate.

#### Scenario: usuário sem override diante de NO-GO

- **GIVEN** o gate combinado retorna NO-GO
- **AND** não existe override administrativo explícito válido
- **WHEN** a criação de favorito é solicitada
- **THEN** a criação é bloqueada
- **AND** as razões segmentadas são retornadas

#### Scenario: admin aplica override explícito

- **GIVEN** o gate combinado retorna NO-GO
- **AND** um administrador aplica o override explícito existente
- **WHEN** a criação de favorito é solicitada
- **THEN** o fluxo segue conforme a política de override vigente
- **AND** o veredito original e suas razões permanecem disponíveis para auditoria
