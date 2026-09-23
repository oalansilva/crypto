# Card A — régua Jev (read-only)

- log: `/srv/apps/dev/criptofarol/source/backend/scalp_jev_diagnostic.log`
- OHLCV: OHLCV BTC/USDT 15m (granularidade 15 min): 23 candles (limit=23); cobertura parcial da janela: o último candle 2026-09-23 15:45:00 não chega ao fim 2026-09-23 17:54:02.321000
- janela do log: 2026-09-23 13:26:57.542000 → 2026-09-23 17:39:02.321000 (252.1 min)
- chamadas: 781 com janela / 781 com retorno
- janelas de 900 s: 781 decisões, **3 não sobrepostas**
- confiança máxima observada: 0.39
- custo por round-trip considerado: 2 × 10.00 bp = 20.00 bp

## Previsão vs realizado (janelas não sobrepostas)

| n | n com preço | alvo +35 bp | stop −28 bp | sem barreira | média assinada (bp) | expectancy líq. (bp) | |realizado| p50 (bp) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 1 | 0 | 0 | 0 | 2.93 | -17.07 | 2.52 |

## Regime

#### Por σ da janela (`vol_bp`)

| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calmo (vol_bp < 0.00) | 0 | 0 | — | 0 | 0 | 0 | sim |
| activo (vol_bp ≥ 0.00) | 3 | 1 | -17.07 | 0 | 0 | 0 | sim |

#### Pelo predicado do gate (`expected_move_bp ≥ entry_hurdle_bp × 1,5`)

| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calmo (previsão < hurdle × 1,5) | 2 | 0 | — | 0 | 0 | 0 | sim |
| activo (previsão ≥ hurdle × 1,5) | 1 | 1 | -17.07 | 0 | 0 | 0 | sim |

## Buckets

#### Por `score` de `expected_move_bp`

| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| score 0 | 1 | 0 | — | 0 | 0 | 0 | sim |
| score 1 | 1 | 0 | — | 0 | 0 | 0 | sim |
| score 6 | 1 | 1 | -17.07 | 0 | 0 | 0 | sim |

#### Por `confidence`

| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [0.0, 0.1) | 1 | 1 | -17.07 | 0 | 0 | 0 | sim |
| [0.2, 0.3) | 1 | 0 | — | 0 | 0 | 0 | sim |
| [0.3, 0.4) | 1 | 0 | — | 0 | 0 | 0 | sim |

## Curva de calibração (`confidence` → |realizado|)

| confidence | n | |realizado| p50 (bp) | |realizado| médio (bp) |
| --- | --- | --- | --- |
| [0.0, 0.1) | 1 | 2.93 | 2.93 |
| [0.2, 0.3) | 0 | — | — |
| [0.3, 0.4) | 1 | 2.12 | 2.12 |

## Recusas registadas no log

| skip_reason | n |
| --- | --- |
| hold | 374 |
| jev_target | 1496 |
| low_confidence | 406 |
| no_book | 117 |
| switch_off | 1 |
| window_empty | 1 |

## Declaração / gate

**Amostra insuficiente** — nenhum limiar ou geometria é proposto:

- 3 janela(s) não sobreposta(s) de 900 s < mínimo de 30
- 1 janela(s) com preço (`n_priced`) < mínimo de 30
- buckets/regimes com menos de 20 trades com preço

Consequência (task 1.5): `CONFIDENCE_MIN` mantém o default actual, `EXIT_TARGET_BP`/`EXIT_STOP_BP` mantêm os valores actuais e `HOLD_AFTER_FILL_S` fica nos 900 s de produto. O motivo fica registado na evidência.

