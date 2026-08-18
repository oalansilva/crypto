## Why

A otimização de estratégias pontua candidatos no período inteiro (in-sample), permitindo que uma estratégia "descoberta" por overfit seja promovida a favorito sem nenhuma evidência de desempenho fora da amostra. O único walk-forward histórico (70/30 com holdout) foi removido junto com o Strategy Lab, e `evaluate_go_nogo` (`criteria.py`) é apenas informativo no resultado do backtest — nenhum gate usa o veredito. Isso cria risco real: favorito overfitado segue para o Monitor e gera sinais com base em desempenho que não se repete no presente.

## What Changes

- Otimização single e batch passa a executar split temporal treino/validação configurável (default 70/30), com otimização somente no treino e pontuação final no holdout.
- `ComboOptimizer.run_optimization` aceita parâmetros de split (frações ou janelas) e produz métricas in-sample vs out-of-sample lado a lado (CAGR, DD, Calmar, PF, Sharpe, nº trades).
- Aplicação do gate `evaluate_go_nogo` no período de validação (holdout): candidato reprovado fica inelegível a favorito, com motivo explícito.
- Bloqueio na API/UI: `POST /api/favorites/` e o salvamento automático do batch recusam candidato NO-GO no holdout (ou exigem override explícito com permissão).
- Relatório de revalidação para favoritos existentes na janela mais recente (degradação in-sample vs recente), sem alterar o favorito automaticamente.
- **Backfill em massa de revalidação (solicitação de Alan, card 470):** processo/endpoint que roda a mesma regra walk-forward sobre TODAS as estratégias já salvas nos favoritos e monitor (178 favoritos no DEV), calculando veredito GO/NO-GO e comparativo IS/OOS na janela recente e **atualizando os dados persistidos** do favorito (métricas de revalidação, veredito e marcação de degradação), sem alterar parâmetros da estratégia. Estratégias do Monitor (curated catalog) são cobertas pelo mesmo processo quando são favoritos.
- Resultado do backtest exibe métricas in-sample vs out-of-sample lado a lado com veredito GO/NO-GO por critério.
- Testes de backend cobrindo split temporal, gate, comparativo de métricas e backfill em massa.

## Capabilities

### New Capabilities
- `walk-forward-validation`: split treino/holdout na otimização, métricas out-of-sample e gate de elegibilidade GO/NO-GO sobre o holdout.

### Modified Capabilities
- `optimization-engine`: otimização passa a usar split temporal treino/validação e a pontuar no holdout em vez de validar no mesmo período de otimização.
- `favorites`: criação de favorito passa a exigir veredito GO no holdout (ou override autorizado) e passa a expor revalidação na janela recente; revalidação em massa atualiza dados persistidos de todos os favoritos existentes.
- `monitor`: estratégias salvas do Monitor passam a ser revalidadas pelo backfill em massa com a mesma regra, refletindo degradação/veredito no estado observado.

## Impact

- **Backend**: `backend/app/services/combo_optimizer.py` (split + gate), `backend/app/services/batch_backtest_service.py` (salvamento automático), `backend/app/routes/favorites.py` e `backend/app/schemas/favorite.py` (bloqueio/override), `backend/app/metrics/criteria.py` (reuso do gate), `backend/app/services/favorite_backtest_refresh_service.py` (revalidação), novo módulo/endpoint de backfill em massa (`POST /api/favorites/revalidate-all` ou job dedicado) para atualizar dados de todos os favoritos existentes.
- **API**: `POST /api/combos/optimize`, `POST /api/combos/backtest/batch`, `POST /api/favorites/`, novo endpoint de revalidação de favorito e novo endpoint de backfill em massa.
- **Frontend**: telas de resultados de otimização (comparativo IS/OOS), modal de salvar favorito (veredito/motivo), dashboard de favoritos (badge de revalidação/degradadação) e estado do Monitor refletindo revalidação.
- **Dados**: campos adicionais de métricas OOS, veredito e revalidação no payload de favorito (sem migration destrutiva; `metrics` é JSON).
- **Dependências**: nenhuma nova; reutiliza `criteria.py`, métricas existentes e o pipeline atual de backtest.
