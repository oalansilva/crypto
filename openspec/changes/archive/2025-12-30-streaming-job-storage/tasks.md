# Tasks: Streaming Storage para Jobs de Otimização

## Fase 1: Database Setup
- [ ] Criar schema SQLite em `data/jobs/results.db`
- [ ] Adicionar índices para performance
- [ ] Testar conexão e queries básicas

## Fase 2: JobManager Refactoring
- [ ] Adicionar método `_init_database()`
- [ ] Implementar `save_result(job_id, result, index)`
- [ ] Implementar `get_results(job_id, page, limit)`
- [ ] Atualizar `save_state()` para remover campo `results`
- [ ] Adicionar fallback para ler JSONs antigos (compatibilidade)
- [ ] Testes unitários para JobManager

## Fase 3: BacktestService Integration
- [ ] Atualizar loop de otimização para chamar `save_result()` individualmente
- [ ] Remover acumulação de `opt_results` em memória
- [ ] Atualizar lógica de "re-run best result"
- [ ] Testar pause/resume com novo storage

## Fase 4: API Endpoints
- [ ] Criar endpoint `GET /api/backtest/jobs/{id}/results?page=1&limit=50`
- [ ] Atualizar endpoint `GET /api/backtest/jobs` para não incluir `results`
- [ ] Adicionar paginação ao schema de resposta
- [ ] Testes de API

## Fase 5: Frontend Updates
- [ ] Atualizar componente de histórico para buscar resultados paginados
- [ ] Adicionar controles de paginação (Next/Previous)
- [ ] Lazy loading de resultados ao scroll
- [ ] Indicador de loading durante fetch

## Fase 6: Testing & Validation
- [ ] Teste: Otimização com 1000 combinações
- [ ] Teste: Pause/Resume durante otimização
- [ ] Teste: Consulta de resultados durante execução
- [ ] Teste: Zero corrupção após 100 otimizações
- [ ] Benchmark: Tempo de resposta `/api/backtest/jobs` < 200ms
- [ ] Benchmark: Uso de memória < 50MB

## Fase 7: Cleanup & Documentation
- [ ] Mover arquivos `.corrupted` para backup
- [ ] Atualizar README com nova arquitetura
- [ ] Documentar schema SQLite
- [ ] Criar guia de migração para usuários

## Notas
- **Prioridade Alta**: Fases 1-3 (resolve o problema crítico)
- **Prioridade Média**: Fases 4-5 (melhora UX)
- **Prioridade Baixa**: Fases 6-7 (polish)
