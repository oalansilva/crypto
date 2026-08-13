## 1. Split temporal no otimizador

- [x] 1.1 Adicionar parâmetros de split (frações ou datas de corte) em `ComboOptimizer.run_optimization` com default 70/30
- [x] 1.2 Dividir candles ordenados em treino/holdout contíguos e validar disjunção
- [x] 1.3 Rodar etapas de otimização somente no treino
- [x] 1.4 Após `best_params`, rodar final backtest no treino e no holdout
- [x] 1.5 Calcular `best_metrics_holdout` com mínimo de trades exigido no holdout (candidato inválido com motivo quando insuficiente)

## 2. Gate de elegibilidade no holdout

- [x] 2.1 Aplicar `evaluate_go_nogo` sobre métricas do holdout (reutilizando `DEFAULT_CRITERIA`/`criteria.py`)
- [x] 2.2 Expor `oos_verdict` (GO/NO-GO + motivos por critério) no resultado de otimização
- [x] 2.3 Bloquear `POST /api/favorites/` sem GO no holdout (422/403 com motivo), exceto override admin explícito
- [x] 2.4 Registrar override NO-GO com log de auditoria quando disponível
- [x] 2.5 Batch: não salvar candidato NO-GO e registrar motivo no job result

## 3. Comparativo IS/OOS na UI

- [x] 3.1 Exibir seção "Treino vs Holdout" nas telas de resultados quando `oos_metrics` presente
- [x] 3.2 Desabilitar botão salvar favorito com motivo explícito quando NO-GO (override admin visível)
- [x] 3.3 Badge de revalidação no `FavoritesDashboard` quando houver relatório NO-GO na janela recente

## 4. Revalidação de favoritos

- [x] 4.1 Endpoint `POST /api/favorites/{id}/revalidate` com backtest na janela recente e relatório de degradação
- [ ] 4.2 UI de revalidação com comparativo IS vs janela recente sem alterar favorito automaticamente
- [x] 4.3 Cobertura de payloads legados: sem `oos_metrics`, manutenção do comportamento atual de criação

## 4b. Backfill em massa de revalidação (solicitação de Alan)

- [x] 4b.1 Endpoint `POST /api/favorites/revalidate-all` (admin) que roda a regra walk-forward na janela recente para TODAS as estratégias salvas (favoritos e favoritos do curated catalog do Monitor)
- [x] 4b.2 Atualizar dados persistidos de cada favorito: `metrics.revalidation` (comparativo IS vs janela recente), `metrics.revalidation_verdict` (GO/NO-GO), `metrics.revalidation_at`, sem alterar parâmetros nem `auto_refresh_status`
- [x] 4b.3 Execução em lote com limite de itens por run, cache OHLCV reusado e relatório de resumo (revalidados, falhas, NO-GO)
- [x] 4b.4 Badge/estado "Degradado"/"Revalidação" no `FavoritesDashboard` e no Monitor alimentados pelos dados do backfill
- [x] 4b.5 Testes: backfill idempotente, limite de lote, persistência dos campos de revalidação, falha por favorito não interrompe o lote

## 5. Testes e validação

- [x] 5.1 Testes unitários: split temporal (frações, datas, disjunção), gate GO/NO-GO no holdout, mínimo de trades
- [ ] 5.2 Testes de API: bloqueio sem GO, override admin, batch NO-GO não salvo
- [ ] 5.3 Testes de revalidação: relatório de degradação sem auto-alteração; backfill em massa com atualização de dados
- [ ] 5.4 `qa-gate` verde e validação OpenSpec da change

## 6. Ajustes pós-Done (feedback Alan 2026-08-13)

- [x] 6.1 `_tail_lines` reescrito com seek-from-end (leitura do fim do arquivo) — modal de logs responde <1s mesmo com full_execution_log de 335MB (era ~3s lendo o arquivo inteiro a cada poll)
- [x] 6.2 `opportunity_service`: `_resolve_stop_loss` extrai `default` de dict (stop_loss normalizado por get_template_metadata) — corrige `float() ... not 'dict'` que pulava 10 favoritos quant_btc_1d_* no Monitor
- [x] 6.3 Testes: tail seek (arquivo grande + linhas longas) e _resolve_stop_loss (dict/número/None)
