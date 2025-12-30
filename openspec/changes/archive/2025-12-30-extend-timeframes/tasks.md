# Tarefas: Estender Timeframes

- [ ] Atualizar Schema do Backend `app/schemas/backtest.py` (Adicionar `full_period`, `since` opcional)
- [ ] Atualizar Serviço Backend `app/services/backtest_service.py` (Tratar lógica de `full_period`)
- [ ] Atualizar Constantes do Frontend (Adicionar `5m`, `2h`)
- [ ] Atualizar Componentes do Frontend (`BacktestWizard`, `SimpleBacktestWizard`) para incluir checkbox "Todo o período"
- [ ] Verificar se API aceita `full_period`
- [ ] Verificar se Data Loader busca desde 2017 quando `full_period=True`
