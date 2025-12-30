# Lista de Tarefas: Otimização de Estratégias

- [ ] Backend: Lógica de Geração de Parâmetros <!-- id: 20 -->
    - [x] Criar esquema `RangeParam` em `schemas/backtest.py`.
    - [x] Implementar utilitário `generate_combinations` em `backtest_service.py`.
    - [x] Atualizar `run_backtest` para lidar com o loop do modo `optimize`.
- [ ] Frontend: Wizard de Otimização (`SimpleBacktestWizard.tsx`) <!-- id: 21 -->
    - [ ] Adicionar alternância de "Modo" (Padrão vs Otimização).
    - [ ] Implementar componente `RangeInput`.
    - [ ] Substituir entradas padrão por `RangeInput` quando estiver no modo Otimização.
    - [ ] Adicionar "Contador de Combinações" para avisar o usuário sobre explosão combinatória.
- [ ] Frontend: Resultados da Otimização (`ResultsPage.tsx`) <!-- id: 22 -->
    - [ ] Detectar resultado do modo `optimize`.
    - [ ] Renderizar `OptimizationHeatmap` ou `ScatterPlot`.
    - [ ] Renderizar `TopResultsTable` (Tabela de Melhores Resultados).
