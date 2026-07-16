## Why

O Monitor já expõe sinal, parâmetros e indicadores, mas obriga o trader a deduzir por que cada entrada e saída aconteceu. O card #290 precisa transformar a execução real de todas as estratégias ativas em uma explicação auditável por trade, sem inventar justificativas nem misturar regra da estratégia, stop e objetivo.

## What Changes

- Ampliar o manifesto de transparência para descrever regras canônicas de entrada, saída e risco de todas as estratégias ativas.
- Produzir evidência contextual por evento usando direção, candle, timeframe, preço e valores de indicadores do trade.
- Distinguir entradas e saídas `long`/`short`, saída por regra, stop, objetivo e posição ainda aberta.
- Exibir no Monitor uma seção acessível “Entenda este trade” para trades abertos e fechados.
- Mostrar indisponibilidade explícita quando os dados não permitirem uma explicação confiável.
- Cobrir a matriz completa de estratégias com testes tabulares e validar a UI em desktop/mobile conforme `DESIGN.md`.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `strategy-transparency`: adicionar explicações por trade derivadas da regra e dos valores históricos efetivamente executados.
- `monitor`: apresentar entrada, saída realizada ou condições pendentes de cada trade em linguagem de trader.

## Impact

- Backend: metadados/manifestos de estratégias, serialização dos trades de Favoritos/Monitor e testes de contrato.
- Frontend: tipos e componentes do Monitor/modal de trades, estilos responsivos e testes unitários/E2E.
- API: adição compatível de campos explicativos; não altera regras, parâmetros, métricas ou execução das estratégias.
- UX: usa superfícies planas, hairlines, tipografia BinanceNova/BinancePlex, cores semânticas de trading e espaçamento de 4px definidos em `DESIGN.md`.
