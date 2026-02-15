> Note: Use project skills in `.codex/skills` when applicable (architecture-review, api-contract-checker, integration-test-planner, accessibility-basic-check, debugging-checklist).

## 1. Backend Orchestration

- [x] 1.1 Inserir etapa obrigatória de otimização do Combo no fluxo de execução do Lab antes da validação final do Trader
- [x] 1.2 Aplicar automaticamente `best_parameters` retornados pelo Combo no template da run
- [x] 1.3 Garantir que a etapa Combo altere apenas parâmetros e preserve lógica/estrutura da estratégia base
- [x] 1.4 Garantir paridade de limites com Combo standalone (ranges, guardrails, constraints)
- [x] 1.5 Garantir que templates criados incluam `optimization_schema.parameters` com `min/max/step` e `correlated_groups` seguindo o padrão do template `multi_ma_crossover`
- [x] 1.5 Garantir que templates criados no fluxo Lab usem `optimization_schema` no padrão do `multi_ma_crossover` (`parameters` com `min`/`max`/`step` + `correlated_groups`)

## 2. Run Persistence and API Payload

- [x] 2.1 Persistir em `run.backtest.combo_optimization` os campos de status, best params, metrics, stages e limits snapshot
- [x] 2.2 Adicionar eventos de trace para início, aplicação e falha da etapa Combo
- [x] 2.3 Validar que os endpoints de status/run retornam os campos de Combo sem recomputar no frontend

## 3. Frontend Lab UI

- [x] 3.1 Implementar seção "Combo Optimization" em `LabRunPage` com status e timestamp
- [x] 3.2 Exibir parâmetros aplicados e limits snapshot usando apenas dados persistidos no run
- [x] 3.3 Sinalizar que métricas exibidas são resultado final pós-Combo usado para validação do Trader
- [x] 3.4 Exibir estado de erro da etapa Combo com mensagem persistida no run

## 4. Verification

- [x] 4.1 Cobrir fluxo backend com testes (sucesso e falha da etapa Combo)
- [x] 4.2 Validar renderização frontend para status sucesso/erro da etapa Combo
- [x] 4.3 Rodar `openspec validate lab-combo-integration --type change`
