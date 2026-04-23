## 1. OpenSpec Alignment

- [x] 1.1 Validar que `proposal.md`, `design.md`, `tasks.md` e specs abaixo estão consistentes.
- [x] 1.2 Executar `openspec validate 2026-04-23-indicadores-basicos-timeframes-scoring --type change`.
- [x] 1.3 Corrigir inconsistências antes do início de implementação.

## 2. Data model

- [x] 2.1 Criar/ajustar migration para `market_indicator` com constraints únicas e índices `(symbol, timeframe, ts)`.
- [ ] 2.2 Definir retenção e política de limpeza (se necessário) conforme retenção do histórico de candles.
- [x] 2.3 Incluir colunas de metadados (`source`, `provider`, `is_recomputed`, `source_window`, `row_count`, `updated_at`).

## 3. Pipeline de cálculo incremental

- [x] 3.1 Implementar engine de indicadores com `TA-Lib` para EMA/SMA/RSI/MACD.
- [x] 3.2 Definir e registrar parâmetros padrão: EMA(9,21), SMA(20,50), RSI(14), MACD(12,26,9).
- [x] 3.3 Mapear timeframes ativos: `1m,5m,15m,1h,4h,1d`.
- [x] 3.4 Implementar recálculo incremental por checkpoint de última vela processada.
- [x] 3.5 Aplicar recálculo incremental retroativo (janela segura de segurança) em caso de late-fix/correção.
- [x] 3.6 Garantir idempotência e escrita upsert em `(symbol,timeframe,ts)`.

## 3.b Dependências e compatibilidade de runtime

- [x] 3.b.1 Adicionar dependência `TA-Lib` em `backend/requirements.txt` e validar packaging no ambiente alvo.
- [x] 3.b.2 Atualizar documentação/ops de ambiente (build wheels ou container) para garantir `talib` disponível.
- [x] 3.b.3 Remover `pandas-ta` dos caminhos de indicadores desta change:
  - retirar imports de `pandas-ta` dos fluxos de indicadores;
  - manter o fluxo operacional **exclusivamente com TA-Lib**;
  - substituir fluxo inline de scoring para leitura de `market_indicator` + fallback mínimo necessário.

## 4. Consumo por scoring e APIs

- [x] 4.1 Expor leitura dos indicadores para pipelines de scoring.
- [x] 4.2 Atualizar scoring para não recalcular indicadores inline.
- [x] 4.3 Criar endpoint administrativo de reprocesseamento:
  - `POST /api/admin/indicators/recompute`

## 5. Validação de precisão

- [x] 5.1 Criar fixtures de comparação com TradingView (mínimo 2 ativos, 2 timeframes).
- [x] 5.2 Implementar testes automatizados com tolerância (`atol/rtol`) por indicador.
- [x] 5.3 Validar aquecimento inicial, gaps de dados e alinhamento temporal UTC.
- [x] 5.4 Confirmar que as diferenças de benchmark (TA-Lib vs TradingView) estão dentro da tolerância acordada.
- [x] 5.5 Documentar procedimento para atualizar fixtures.

## 6. QA / evidência de integração

- [x] 6.1 Executar smoke de pipeline de um ativo com 1d e 1h.
  - Comando: `backend/scripts/qa_market_indicator_pipeline_smoke.py`.
- [x] 6.2 Verificar tabela `market_indicator` para unicidade e cobertura de timeframes.
  - Coberto pelo resultado `latest_rows` + `uniqueness_and_tz` do script acima.
- [x] 6.3 Rodar teste de TradingView e anexar evidência de aprovação.
  - Comando: `pytest tests/unit/test_market_indicator_tradingview_fixtures.py -q`.
- [x] 6.4 Registrar evidência consolidada em `qa_evidence.md`.
