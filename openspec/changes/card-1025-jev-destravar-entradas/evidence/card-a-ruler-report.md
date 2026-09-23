# Card A — régua Jev (read-only)

- log: `/srv/apps/dev/criptofarol/source/backend/scalp_jev_diagnostic.log`
- OHLCV: OHLCV falhou na leitura (OperationalError)
- chamadas: 0 com janela / 0 com retorno
- janelas de 900 s: 0 decisões, **0 não sobrepostas**
- confiança máxima observada: 0
- custo por round-trip considerado: 2 × 14.00 bp = 28.00 bp

## Previsão vs realizado (janelas não sobrepostas)

| n | n com preço | alvo +35 bp | stop −28 bp | sem barreira | média assinada (bp) | expectancy líq. (bp) | |realizado| p50 (bp) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 | — | — | — |

## Regime

#### Por σ da janela (`vol_bp`)

| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | 0 | 0 | — | 0 | 0 | 0 | sim |

#### Pelo predicado do gate (`expected_move_bp ≥ entry_hurdle_bp × 1,5`)

| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calmo (previsão < hurdle × 1,5) | 0 | 0 | — | 0 | 0 | 0 | sim |
| activo (previsão ≥ hurdle × 1,5) | 0 | 0 | — | 0 | 0 | 0 | sim |

## Buckets

#### Por `score` de `expected_move_bp`

| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | 0 | 0 | — | 0 | 0 | 0 | sim |

#### Por `confidence`

| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |
| --- | --- | --- | --- | --- | --- | --- | --- |
| — | 0 | 0 | — | 0 | 0 | 0 | sim |

## Curva de calibração (`confidence` → |realizado|)

| confidence | n | |realizado| p50 (bp) | |realizado| médio (bp) |
| --- | --- | --- | --- |

## Recusas registadas no log

Sem recusas registadas.

## Declaração / gate

**Amostra insuficiente** — nenhum limiar ou geometria é proposto:

- log ausente/vazio: nenhuma chamada Jev registada
- realizado indisponível: OHLCV falhou na leitura (OperationalError)
- 0 janela(s) não sobreposta(s) de 900 s < mínimo de 30

Consequência (task 1.5): `CONFIDENCE_MIN` mantém o default actual, `EXIT_TARGET_BP`/`EXIT_STOP_BP` mantêm os valores actuais e `HOLD_AFTER_FILL_S` fica nos 900 s de produto. O motivo fica registado na evidência.

