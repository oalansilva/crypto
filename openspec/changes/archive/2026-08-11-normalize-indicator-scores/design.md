## Context

`market_indicator` já é a fonte dedicada de indicadores técnicos. A nova camada não deve recalcular EMA, SMA, RSI, MACD ou indicadores avançados; ela apenas interpreta os valores persistidos com regras declarativas.

## Decisions

### Ruleset JSON versionado

As regras ficam em `backend/config/indicator_score_rules.v1.json` e possuem:

- `version`: identificador estável do ruleset.
- `indicators`: lista de regras nomeadas.
- `type`: algoritmo de normalização.
- `inputs`: colunas de `market_indicator` consumidas.

O caminho pode ser sobrescrito com `INDICATOR_SCORE_RULES_PATH`, permitindo benchmark, QA ou rollout controlado sem alterar código.

### Score contract

Cada score retornado inclui:

- `name`
- `score` entre `0.0` e `10.0`
- `rule_version`
- `rule_type`
- `inputs`

Campos ausentes, nulos ou inválidos não geram score, preservando warmup dos indicadores.

### Rule types

- `linear`: normaliza um valor entre `min` e `max`.
- `centered_tanh`: normaliza distância de um centro com `tanh`, útil para histogramas.
- `crossover`: compara indicador rápido/lento em diferença percentual.
- `band_width`: pontua largura relativa de bandas.
- `ratio_linear`: pontua razão entre dois campos.
- `range_width`: pontua largura relativa entre suporte/resistência e pivô.

## Benchmark

O benchmark é scriptado em `backend/scripts/benchmark_indicator_score_service.py` e documentado em `benchmark.md`. Ele mede normalização em memória sobre linhas sintéticas com todos os campos usados pelo ruleset padrão.
