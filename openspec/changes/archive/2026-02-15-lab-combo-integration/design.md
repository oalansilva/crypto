## Context

O Lab já executa um fluxo autônomo com `strategy_draft`, backtest e validação final, mas a otimização de parâmetros do Combo não aparece como etapa explícita, rastreável e sempre aplicada antes da validação do Trader.  
O briefing define que o Combo deve apenas ajustar parâmetros (sem mudar lógica da estratégia), com os mesmos limites atuais, e que o resultado deve ficar visível para qualquer usuário na UI do Lab.

## Goals / Non-Goals

**Goals:**
- Integrar o fluxo de otimização do Combo no pipeline padrão do Lab sem alterar o Combo.
- Garantir aplicação automática dos melhores parâmetros antes do backtest final.
- Persistir no run um registro claro da otimização para auditoria e UI.
- Exibir no frontend do Lab o resultado da etapa Combo para todos.

**Non-Goals:**
- Alterar algoritmo, ranges default, limites de busca ou guardrails internos do Combo.
- Criar etapa manual de aprovação intermediária de parâmetros.
- Substituir a validação final do Trader por decisão automática.

## Decisions

### 1) Fluxo textual obrigatório no Lab

Fluxo único para runs com upstream aprovado:
1. Dev/Trader definem e aprovam template base (`strategy_draft` -> template seed).
2. Lab chama otimização de parâmetros do Combo para esse template.
3. Lab recebe `best_parameters` e aplica automaticamente no template da run.
4. Lab executa backtest final já com os parâmetros aplicados.
5. Trader valida somente o resultado final (não o baseline intermediário).

Regra de domínio: a etapa Combo ajusta apenas parâmetros numéricos/otimizáveis; estrutura de indicadores e lógica de entrada/saída permanecem da estratégia base. **Todo template criado no fluxo** deve usar o contrato do `multi_ma_crossover`, com `optimization_schema.parameters` contendo `min/max/step` e `correlated_groups` obrigatório.

### 2) Consumo do resultado do Combo e persistência no run

O backend reaproveita o resultado já retornado por `ComboOptimizer.run_optimization(...)` (ou fluxo equivalente já exposto no backend), incluindo `best_parameters`, `best_metrics`, `stages` e metadados da execução.

Persistência proposta no JSON do run:
- `run.backtest.combo_optimization.status`: `completed` | `failed` | `skipped`
- `run.backtest.combo_optimization.template_name`
- `run.backtest.combo_optimization.best_parameters`
- `run.backtest.combo_optimization.best_metrics`
- `run.backtest.combo_optimization.stages`
- `run.backtest.combo_optimization.limits_snapshot` (snapshot dos limites/ranges usados no Combo)
- `run.backtest.combo_optimization.applied_at_ms`
- `run.backtest.combo_optimization.error` (quando houver falha)

Também registrar eventos de trace (`combo_optimization_started`, `combo_optimization_applied`, `combo_optimization_failed`) para inspeção operacional.

### 3) Aplicação automática no template da run

Após sucesso do Combo, o Lab atualiza o template da run com `best_parameters` e executa o backtest final sem intervenção manual.  
Se a otimização falhar, o run marca falha da etapa e segue política de erro definida pelo Lab (não simular aprovação sem parâmetros aplicados).

### 4) Exposição na UI do Lab

`LabRunPage` passa a renderizar bloco "Combo Optimization" lendo exclusivamente `data.backtest.combo_optimization`:
- status da etapa;
- parâmetros aplicados (chave/valor);
- métricas do melhor resultado;
- limites/ranges utilizados;
- indicador explícito de que o backtest exibido é pós-aplicação do Combo.

Esse bloco fica visível para qualquer usuário que abra `/lab/runs/:runId`, mantendo transparência entre execução técnica e validação do Trader.

### 5) Contrato obrigatório para templates criados no fluxo

Qualquer template criado/normalizado durante o fluxo do Lab deve seguir o mesmo formato estrutural já usado no template Combo `multi_ma_crossover` (página `/combo/edit/multi_ma_crossover`):

- `optimization_schema.parameters`: mapa por nome de parâmetro, com `min`, `max` e `step` (além de `default` quando houver);
- `optimization_schema.correlated_groups`: lista de grupos de parâmetros correlacionados, referenciando apenas chaves existentes em `parameters`.

Não será aceito formato legado plano de parâmetros sem `correlated_groups`, para manter compatibilidade entre editor, otimizador e persistência do run.

**Exemplo (multi_ma_crossover):**
- `sma_medium`: default 21, min 10, max 40, step 1
- `sma_long`: default 50, min 20, max 100, step 1
- `stop_loss`: default 0, min 0.005, max 0.13, step 0.002
- `ema_short`: default 9, min 3, max 20, step 1

## Risks / Trade-offs

- [Tempo maior por run] -> Mitigação: manter os mesmos limites do Combo e evitar loops extras fora do pipeline já existente.
- [Custo computacional/tokens maior] -> Mitigação: executar otimização apenas uma vez por run aprovado, com reaproveitamento de dados já carregados quando possível.
- [Payload do run maior] -> Mitigação: persistir apenas resumo necessário (`best_parameters`, `best_metrics`, `stages` enxuto) e manter detalhes extensos no trace.
- [Falhas na etapa Combo interrompem fluxo] -> Mitigação: status explícito de erro + trace com causa para retry operacional.
