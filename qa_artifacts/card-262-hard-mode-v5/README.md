# Card 262 - HARD MODE V5 BTC/USDT 1D Long

Artefatos finais versionados para a execução do card #262.

## Arquivos

- `t0-snapshot-latest.json`: snapshot T0 com favoritos, templates, mapeamentos públicos e Pine Scripts relacionados.
- `api-favorites-t0-latest.json`: leitura da API de Favoritos no T0 para BTC/USDT 1d Long.
- `benchmark-revalidation-latest.json`: revalidação full-period Deep Backtest dos favoritos T0.
- `targeted-chain-search-2026-06-07T025330+0000.json`: busca final com 7.677 candidatos Deep e cadeia sequencial 5/5.
- `winner-save-validation-latest.json`: prova de salvamento/validação dos favoritos #193-#197.

## Resultado

Período completo: 2017-08-17 a 2026-06-07.
Config: BTC/USDT, 1d, long, Deep Backtest `deep_15m`, capital 100 USD, 100% in/out, pyramiding=0, sem parcial.

| Slot | Favorite | Retorno | Max DD | Sharpe | PF | Trades |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| WINNER_1 | #193 | 20076.69% | 10.77% | 0.321 | 6.024 | 45 |
| WINNER_2 | #194 | 20618.21% | 10.46% | 0.330 | 5.624 | 41 |
| WINNER_3 | #195 | 20773.78% | 9.79% | 0.380 | 4.514 | 84 |
| WINNER_4 | #196 | 20903.78% | 8.84% | 0.339 | 4.665 | 69 |
| WINNER_5 | #197 | 21490.76% | 7.99% | 0.341 | 8.527 | 41 |

Todos os novos favoritos passaram leitura negativa para `Estratégia Cripto Farol`, têm `strategy_display_name` e `strategy_description` públicos, e `/api/favorites/{id}/trades` confirmou `execution_mode=deep_15m`.
