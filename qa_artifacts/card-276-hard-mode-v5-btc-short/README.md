# Card 276 - HARD MODE V5 BTC/USDT 1D SHORT

Artefatos finais versionados para a execução do card #276.

## Configuração

- Symbol/timeframe/direction: `BTC/USDT` / `1d` / `short`.
- Execução single-direction: Long e Short não foram misturados.
- Deep Backtest: `deep_15m`, capital inicial 100 USD, entrada 100%, saída/cobertura 100%, pyramiding=0, sem parcial.
- Período completo usado nos backtests finais: `2017-08-17` a `2026-06-07`.
- COLD_START_MODE=true: T0 tinha short=0 e long=8; Long foi excluído de benchmarks obrigatórios.

## Arquivos

- `t0-snapshot-20260629T021300Z.json`: snapshot T0 com favoritos, templates, mapeamentos públicos, Pine Scripts e API.
- `engine-short-support-latest.json`: prova do motor/API para SHORT real em Deep Backtest.
- `cold-start-search-20260629T0219Z.json`: busca cold-start com 1.800 candidatos deep e Pareto inicial.
- `winner-save-validation-latest.json`: prova de salvamento/validação dos Favoritos #198-#202 e da cadeia positiva final aceita.
- `docs/tradingview/card-276-hard-mode-v5-btc-short/*.pine`: Pine Scripts das 5 vencedoras.

## Resultado

| Slot | Favorite | Estratégia | Retorno | Max DD | Sharpe | PF | Trades |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| WINNER_1 | #198 | `quant_btc_1d_short_macd_bear_chain_w1_20260629` | 62.68% | 48.07% | 0.087 | 1.156 | 125 |
| WINNER_2 | #199 | `quant_btc_1d_short_ma_breakdown_chain_w2_20260629` | 63.53% | 44.67% | 0.095 | 1.193 | 101 |
| WINNER_3 | #200 | `quant_btc_1d_short_ma_breakdown_chain_w3_20260629` | 65.08% | 41.31% | 0.097 | 1.221 | 101 |
| WINNER_4 | #201 | `quant_btc_1d_short_ma_defense_chain_w4_20260629` | 65.89% | 35.82% | 0.117 | 1.312 | 75 |
| WINNER_5 | #202 | `quant_btc_1d_short_macd_defense_chain_w5_20260629` | 66.61% | 23.32% | 0.158 | 1.527 | 59 |

## Evidência

- Candidatos deep executados: 1800.
- Sobreviventes com mínimo de trades: 1520.
- Pareto encontrado na busca: 9.
- Fallback negativo: True.
- `/api/favorites/` confirmou `strategy_display_name` e `strategy_description` específicos para cada favorito.
- `/api/favorites/{id}/trades` confirmou trades `type=short` para cada favorito salvo.
- Public mapping source: `backend/app/services/strategy_descriptions.py`.

## Favoritos salvos

- WINNER_1: favorite.id=198, created_at=2026-06-29T02:25:13.395554, name=BTC 1D SHORT WINNER 1 - MACD Bear Control, display=BTC 1D SHORT WINNER 1: MACD de Baixa Controlada.
- WINNER_2: favorite.id=199, created_at=2026-06-29T02:25:16.235575, name=BTC 1D SHORT WINNER 2 - MA Breakdown Defense, display=BTC 1D SHORT WINNER 2: Médias de Quebra Defensiva.
- WINNER_3: favorite.id=200, created_at=2026-06-29T02:25:19.092956, name=BTC 1D SHORT WINNER 3 - MA Breakdown Lower DD, display=BTC 1D SHORT WINNER 3: Médias de Baixa com Menor Queda.
- WINNER_4: favorite.id=201, created_at=2026-06-29T02:25:22.090673, name=BTC 1D SHORT WINNER 4 - MA Bear Defense, display=BTC 1D SHORT WINNER 4: Médias de Baixa Protegida.
- WINNER_5: favorite.id=202, created_at=2026-06-29T02:25:24.997390, name=BTC 1D SHORT WINNER 5 - MACD Short Defense, display=BTC 1D SHORT WINNER 5: MACD Short Defensivo.
