## ADDED Requirements

### Requirement: Split temporal treino/validação na otimização
A otimização de estratégia (single e batch) SHALL executar com split temporal treino/holdout configurável, com otimização de parâmetros aplicada somente sobre o período de treino e pontuação final calculada no período de validação (holdout).

#### Scenario: Otimização single com split default
- **WHEN** `POST /api/combos/optimize` é executado sem parâmetros de split explícitos
- **THEN** o otimizador usa split 70/30 (70% mais antigo para treino, 30% mais recente para holdout)
- **AND** os parâmetros são otimizados somente no treino
- **AND** o resultado final reporta métricas de treino e de holdout lado a lado

#### Scenario: Split configurável
- **WHEN** o cliente informa frações de split (ex.: 60/40) ou janelas explícitas de treino e validação
- **THEN** o otimizador respeita os períodos informados
- **AND** valida que treino e holdout são disjuntos e contíguos no tempo

#### Scenario: Holdout sem trades suficientes
- **WHEN** o holdout não produz o número mínimo de trades exigido para resultado válido
- **THEN** o resultado marca o candidato como inválido para promoção com motivo explícito (trades insuficientes no holdout)

### Requirement: Veredito GO/NO-GO sobre o holdout
O gate `evaluate_go_nogo` SHALL ser aplicado sobre as métricas do período de validação (holdout), produzindo veredito GO/NO-GO por critério com motivos explícitos.

#### Scenario: Candidato GO no holdout
- **WHEN** o holdout atende todos os critérios GO/NO-GO (`criteria.py`)
- **THEN** o candidato é elegível a favorito
- **AND** o resultado exibe o veredito GO com métricas in-sample vs out-of-sample lado a lado

#### Scenario: Candidato NO-GO no holdout
- **WHEN** o holdout reprova um ou mais critérios
- **THEN** o candidato é inelegível a favorito
- **AND** o motivo explícito do NO-GO (critérios reprovados e valores observados) é exibido na API e na UI

### Requirement: Comparativo de métricas in-sample vs out-of-sample
O resultado de otimização SHALL expor métricas comparativas lado a lado (CAGR, drawdown máximo, Calmar, profit factor, Sharpe, número de trades) para treino e holdout.

#### Scenario: Resultado com comparativo
- **WHEN** a otimização conclui com split válido
- **THEN** o payload de resultado contém as métricas de treino e de holdout no mesmo formato
- **AND** a UI de resultados exibe as duas colunas com veredito por critério

### Requirement: Bloqueio de promoção a favorito sem GO no holdout
A criação de favorito SHALL ser bloqueada para candidatos sem veredito GO no holdout, a menos que um override explícito autorizado seja fornecido.

#### Scenario: Tentativa de salvar candidato NO-GO
- **WHEN** `POST /api/favorites/` recebe um candidato com veredito NO-GO no holdout sem override
- **THEN** a API responde 422/403 com motivo explícito do bloqueio
- **AND** o favorito não é criado

#### Scenario: Override autorizado
- **WHEN** o usuário fornece override explícito com permissão adequada (admin)
- **THEN** o favorito é criado
- **AND** o veredito NO-GO e o override ficam registrados nos dados do favorito

#### Scenario: Salvamento automático do batch
- **WHEN** o batch backtest tenta salvar automaticamente um candidato NO-GO no holdout
- **THEN** o candidato não é salvo como favorito
- **AND** o motivo é registrado no resultado do job do batch

### Requirement: Revalidação de favoritos existentes na janela recente
Favoritos existentes SHALL poder ser revalidados na janela mais recente disponível, produzindo relatório de degradação (métricas in-sample vs janela recente) sem alterar o favorito automaticamente.

#### Scenario: Revalidação manual de favorito
- **WHEN** o usuário solicita revalidação de um favorito existente
- **THEN** o sistema roda o backtest do favorito na janela mais recente
- **AND** exibe relatório comparativo com veredito GO/NO-GO na janela recente
- **AND** o favorito não é alterado automaticamente

#### Scenario: Revalidação com degradação
- **WHEN** o favorito reprova os critérios na janela recente
- **THEN** o relatório sinaliza a degradação com os critérios reprovados
- **AND** o favorito permanece ativo até decisão explícita do usuário

### Requirement: Backfill em massa de revalidação de estratégias salvas
O sistema SHALL prover processo/endpoint que rode a regra walk-forward (split 70/30 + gate GO/NO-GO) na janela recente para TODAS as estratégias já salvas nos favoritos e Monitor, atualizando os dados persistidos de revalidação sem alterar parâmetros da estratégia.

#### Scenario: Backfill de todas as estratégias salvas
- **WHEN** o usuário autorizado (admin) executa o backfill em massa
- **THEN** todas as estratégias salvas (favoritos e favoritos do curated catalog usados pelo Monitor) são revalidadas na janela recente com a mesma regra walk-forward
- **AND** os dados persistidos de cada estratégia são atualizados com o comparativo IS vs janela recente e o veredito GO/NO-GO (`metrics.revalidation*`)
- **AND** parâmetros e configuração da estratégia não são alterados

#### Scenario: Backfill com degradação detectada
- **WHEN** o backfill encontra estratégia reprovando os critérios na janela recente
- **THEN** o veredito NO-GO e os critérios reprovados são persistidos na estratégia
- **AND** o dashboard/Monitor sinaliza a degradação (badge/estado informativo)
- **AND** a estratégia permanece ativa até decisão explícita do usuário

#### Scenario: Backfill em lote com falha parcial
- **WHEN** uma ou mais estratégias falham durante o backfill em massa
- **THEN** as estratégias com sucesso são persistidas normalmente
- **AND** as falhas são registradas no relatório do backfill sem interromper o lote
