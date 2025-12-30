# Tasks: Interface Unificada de Backtest

## Fase 1: Backend (Estimativa: 1-2 dias)

### 1.1 Schemas e Validação
- [ ] Criar `ParameterValue` model em `backend/app/models.py`
  - [ ] Implementar validação mutually exclusive (value XOR range)
  - [ ] Adicionar property `is_range`
  - [ ] Adicionar method `to_scalar()`
- [ ] Atualizar `BacktestRunCreate` schema para aceitar `ParameterValue`
- [ ] Escrever testes unitários para `ParameterValue`

### 1.2 Lógica de Detecção de Modo
- [ ] Implementar `detect_mode()` em `backend/app/services/backtest_service.py`
- [ ] Atualizar `run_backtest()` para chamar `detect_mode()` automaticamente
- [ ] Garantir backward compatibility com formato antigo
- [ ] Testes unitários para detecção de modo

### 1.3 Processamento de Parâmetros
- [ ] Modificar `_run_optimization()` para aceitar novo formato
- [ ] Converter `ParameterValue` para valores escalares em mode='run'
- [ ] Expandir ranges em mode='optimize'
- [ ] Testes de integração

## Fase 2: Frontend Core (Estimativa: 2-3 dias)

### 2.1 Componente ParameterInput
- [ ] Criar `frontend/src/components/ui/ParameterInput.tsx`
  - [ ] Implementar toggle de otimização
  - [ ] Renderização condicional (single value vs range)
  - [ ] Lógica de transição entre modos
  - [ ] Sugestão inteligente de ranges
- [ ] Criar testes de componente (Vitest)
- [ ] Adicionar Storybook stories (opcional)

### 2.2 Componente OptimizationBadge
- [ ] Criar `frontend/src/components/ui/OptimizationBadge.tsx`
  - [ ] Implementar cálculo de combinações
  - [ ] Renderização com cores baseadas em thresholds
  - [ ] Animações de transição
- [ ] Testes de componente

### 2.3 Atualização do Wizard
- [ ] Modificar `frontend/src/components/SimpleBacktestWizard.tsx`
  - [ ] Remover seleção de modo (run/optimize)
  - [ ] Substituir inputs de parâmetros por `ParameterInput`
  - [ ] Adicionar `OptimizationBadge`
  - [ ] Implementar lógica de montagem de payload
- [ ] Atualizar state management
- [ ] Testes E2E do wizard

## Fase 3: Resultados (Estimativa: 1-2 dias)

### 3.1 Renderização Condicional
- [ ] Modificar `frontend/src/pages/ResultsPage.tsx`
  - [ ] Detectar `result.mode`
  - [ ] Renderizar `BacktestResults` para ambos os modos
  - [ ] Renderizar `OptimizationResults` apenas em mode='optimize'
- [ ] Garantir que gráfico de dispersão funciona corretamente
- [ ] Testes de renderização

### 3.2 Ação Rápida
- [ ] Adicionar botão "Executar com Melhor Configuração"
  - [ ] Extrair melhores parâmetros de optimization_results
  - [ ] Preencher wizard com esses valores
  - [ ] Executar backtest padrão
- [ ] Testes de integração

## Fase 4: Polish e Documentação (Estimativa: 1 dia)

### 4.1 UX Enhancements
- [ ] Adicionar tooltips em todos os toggles
- [ ] Implementar animações de transição
- [ ] Melhorar feedback visual
- [ ] Testes de acessibilidade

### 4.2 Documentação
- [ ] Atualizar README com nova interface
- [ ] Criar guia de usuário
- [ ] Documentar API changes
- [ ] Screenshots/GIFs da nova interface

## Testes de Regressão

### Backend
- [ ] Todos os testes existentes passam
- [ ] Endpoints antigos ainda funcionam
- [ ] Performance não degradou

### Frontend
- [ ] Fluxo de backtest padrão funciona
- [ ] Fluxo de otimização funciona
- [ ] Histórico de runs funciona
- [ ] Export de resultados funciona

## Critérios de Aceitação

- [ ] ✅ Usuário pode executar backtest padrão sem ativar otimização
- [ ] ✅ Usuário pode ativar otimização em qualquer parâmetro
- [ ] ✅ Badge mostra número correto de combinações
- [ ] ✅ Sistema detecta modo automaticamente
- [ ] ✅ Resultados são exibidos corretamente para cada modo
- [ ] ✅ Botão "Melhor Configuração" funciona
- [ ] ✅ Nenhuma regressão em funcionalidades existentes
- [ ] ✅ Documentação atualizada

## Notas de Implementação

### Prioridades
1. **P0 (Crítico)**: Fases 1 e 2 - Funcionalidade core
2. **P1 (Importante)**: Fase 3 - Resultados adaptativos
3. **P2 (Desejável)**: Fase 4 - Polish e docs

### Riscos
- **Complexidade do ParameterInput**: Componente com muita lógica
  - Mitigação: Quebrar em subcomponentes menores
- **Backward compatibility**: Não quebrar fluxos existentes
  - Mitigação: Manter suporte para formato antigo
- **Performance**: Cálculo de combinações em tempo real
  - Mitigação: Debounce e memoization

### Dependências
- Nenhuma dependência externa nova
- Usa bibliotecas existentes (React, Pydantic, etc.)
