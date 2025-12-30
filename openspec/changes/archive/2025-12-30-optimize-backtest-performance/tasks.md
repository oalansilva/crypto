# Tarefas: Otimização de Performance do Backtest

- [x] Criar `backend/app/workers/optimization_worker.py` <!-- id: create-worker-module -->
    - Implementar função `evaluate_combination`.
    - Implementar `init_worker` para dados compartilhados.
    - Implementar lógica de cache de sinais.
- [x] Refatorar `BacktestService.py` para usar `ProcessPoolExecutor` <!-- id: refactor-service-parallel -->
    - Importar `optimization_worker`.
    - Agrupar combinações em chunks.
    - Gerenciar ciclo de vida do pool (shutdown ao pausar/parar).
    - Lidar com agregação de resultados.
- [x] Implementar Armazenamento em Streaming para Resultados (ADIADO para V2) <!-- id: implement-streaming-results -->
    - Modificar `JobManager` para ler/escrever resultados de um fluxo separado (arquivo/db) em vez de um objeto JSON gigante.
    - Atualizar Frontend para buscar páginas de resultados em vez da lista completa (se ainda não estiver paginado).
- [x] Atualizar lógica `evaluate_go_nogo` para usar Numba/Vetorização (Bônus - ADIADO) <!-- id: optimize-core-logic -->
- [x] Verificar Melhoria de Performance <!-- id: verify-performance -->
    - Rodar benchmark com 10k combinações.
    - Comparar tempo vs linha de base existente.
