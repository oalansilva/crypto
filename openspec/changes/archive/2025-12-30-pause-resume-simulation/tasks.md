# Tarefas: Implementação de Pausa e Retomada

- [x] Criar classe `JobManager` no backend em `app/services/job_manager.py` <!-- id: scaffold-job-manager -->
- [x] Implementar métodos `save_state` e `load_state` com serialização JSON <!-- id: implement-persistence -->
- [x] Refatorar `BacktestService._run_single_strategy_optimization` para aceitar `job_id` e lidar com lógica de checkpoint <!-- id: refactor-optimization-loop -->
- [x] Adicionar verificação `check_pause_signal` dentro do loop de otimização <!-- id: add-pause-check -->
- [x] Implementar lógica de `resume` para pular iterações já processadas <!-- id: implement-resume-skip -->
- [x] Adicionar endpoints da API `/pause/{id}` e `/resume/{id}` em `app/routers/backtest.py` <!-- id: add-api-endpoints -->
- [x] Atualizar Frontend `SimpleBacktestWizard` para consultar status do job e suportar ação de Pausar <!-- id: frontend-pause-ui -->
- [x] Implementar Prompt de Retomada e lógica de recuperação no Frontend <!-- id: frontend-resume-ui -->
- [ ] Verificar Ponta-a-Ponta: Iniciar -> Pausar -> Reiniciar Servidor -> Continuar -> Concluir <!-- id: verify-e2e -->
