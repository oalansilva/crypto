## Why

O engine composto precisa consumir indicadores técnicos em uma escala comum. Hoje cada indicador possui unidade, direção e faixa própria, o que dificulta composição, peso e comparação entre sinais.

## What Changes

- Adicionar um serviço backend que converte indicadores persistidos em `market_indicator` para scores normalizados `0-10`.
- Carregar regras configuráveis por indicador a partir de arquivo JSON versionado.
- Propagar a versão do ruleset em cada score calculado.
- Documentar o benchmark e fornecer script reproduzível para medir throughput do normalizador.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `market-indicators`: Expande a interface de scoring para oferecer scores técnicos normalizados e versionados a partir dos indicadores persistidos.

## Impact

- Backend: novo serviço de scoring técnico normalizado.
- Configuração: ruleset JSON versionado com override por variável de ambiente.
- Testes: cobertura unitária para limites `0-10`, regras configuráveis, campos ausentes e versionamento.
- Operação: benchmark documentado em `openspec/changes/normalize-indicator-scores/benchmark.md`.
