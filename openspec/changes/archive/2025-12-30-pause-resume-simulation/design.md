# Design: Arquitetura de Pausa e Retomada

## 1. Job Manager & Persistência
Introduziremos um componente `JobManager` responsável pelo ciclo de vida dos trabalhos de backtest.

### Schema do Estado (`job_<uuid>.json`)
Localizado em `backend/data/jobs/`.
```json
{
  "job_id": "uuid",
  "status": "PAUSED", // RUNNING, COMPLETED, FAILED
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "config": { ... }, // Payload original da requisição
  "progress": {
    "current_iteration": 150,
    "total_iterations": 3000,
    "strategy_index": 0
  },
  "results": [ ... ] // Lista de objetos de resultado computados até agora
}
```

## 2. Modificação do Loop de Execução
O loop `_run_single_strategy_optimization` no `BacktestService` será refatorado:

*   **Verificação de Iteração**: No início de cada iteração do loop, verificar `JobManager.should_pause(run_id)`.
*   **Checkpointing**: A cada N iterações (ex: 50 ou baseado em tempo), chamar `JobManager.save_checkpoint(run_id, state)`.
*   **Retomada**: Ao iniciar, verificar se `resume=True` foi passado. Se sim:
    1.  Carregar estado do disco.
    2.  Regerar o grid de parâmetros (deve ser determinístico).
    3.  Pular os primeiros `current_iteration` itens.
    4.  Inicializar a lista `results` com os resultados salvos.

## 3. Mudanças na API
*   `POST /api/backtest/pause/{run_id}`: Define estado para PAUSING. O loop detecta isso e salva o checkpoint final -> PAUSED.
*   `POST /api/backtest/resume/{run_id}`: Carrega o estado e chama `run_backtest(config, resume=True)`.
*   `GET /api/backtest/jobs`: Lista trabalhos ativos/pausados.

## 4. UX do Frontend
*   **Barra de Progresso**: Adicionar botão [Pausar] quando estiver rodando.
*   **Prompt de Retomada**: Ao carregar, verificar trabalhos `PAUSED`. Se encontrar, mostrar modal: "Simulação pausada encontrada (45%). Continuar? [Sim] [Não]".
