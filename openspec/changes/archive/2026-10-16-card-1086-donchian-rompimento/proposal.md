## Why

O template Canal Donchian + volume não consegue reconhecer rompimentos porque compara o fechamento com um canal que inclui a máxima desse mesmo candle. O card #1086 corrige a entrada e exige prova de compra efetiva no backtest.

## Problema

O operador da Descoberta não consegue obter entradas com o template Canal Donchian + volume, mesmo diante de um rompimento válido, porque a comparação usa um canal que inclui o próprio candle avaliado.

## História

Como operador da Descoberta, quero que o template Donchian reconheça um rompimento válido do canal anterior para que ele possa gerar entradas em backtests.

## Entra

- O template reconhece o rompimento pela comparação do fechamento com o limite superior do canal formado pelos N candles anteriores, mantendo a confirmação de volume já existente.
- Com histórico suficiente, sem posição aberta, fechamento acima do limite superior anterior e confirmação de volume atendida, o backtest registra uma entrada comprada real; apenas executar sem erro ou produzir uma coluna de sinais não basta.
- Com fechamento igual ou abaixo do limite superior anterior, não há entrada por rompimento, mesmo com volume suficiente. Uma máxima acima do canal sem fechamento acima também não gera entrada.
- Com fechamento acima do canal anterior, mas sem atender à confirmação de volume, não há entrada.
- A decisão de entrada usa somente informações disponíveis até o candle avaliado: alterar candles futuros não muda entradas já decididas, e o candle avaliado não compõe o canal de referência do próprio rompimento.
- Demonstrar os casos de entrada e de ausência de entrada em 4h, 1h e 15m, os timeframes de validação dos templates no #1074, sem fixar o template a um timeframe.
- Preservar o comportamento dos demais templates e indicadores fora da correção; qualquer impacto necessário deve ser demonstrado no Design.

## Não entra

- Alterar os thresholds de aprovação, taxa, slippage ou a promoção de favoritos.
- Reabrir o Status Homologado do #1074 ou antecipar Design/aprovação/Apply deste novo card.

## What Changes

- Usar o limite superior dos N candles anteriores na condição de entrada do template existente, preservando a confirmação de volume.
- Demonstrar compras reais e rejeições de rompimentos inválidos em 4h, 1h e 15m, sem lookahead.
- Preservar os indicadores compartilhados, a saída e os demais templates.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `discovery-catalog-selection`: acrescentar contrato verificável de rompimento Donchian com entrada efetiva e confirmação de volume.

## Impact

Alteração esperada no `entry_logic` de `donchian_volume_breakout` em `backend/config/combo_templates_export.json`, consumido por ComboStrategy e pelo seed existente. Testes cobrirão o motor real de backtest, regressão dos indicadores e carga do template. Sem alteração de API, tela, dependência ou schema de banco.
