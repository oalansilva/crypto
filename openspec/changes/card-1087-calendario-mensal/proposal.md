## Why

O #1087 corrige a divergência de calendário do #1078: a mesma opção precisa avaliar a mesma janela no Combo e na Descoberta.

## Problema

O review independente do lote 2026-10-12 encontrou divergência de calendário nos períodos mensais do #1078. No dia 2026-03-31, “1 mês” começa em 2026-03-03 no Combo (`setUTCMonth`) e em 2026-02-28 na Descoberta (`relativedelta`). A mesma opção pode avaliar dados diferentes.

## História

Como operador do Combo e da Descoberta, quero que a mesma opção de período use a mesma regra de calendário nas duas telas para comparar backtests na mesma janela.

## Entra

- Unificar a regra mensal preservando o dia quando ele existir e limitando-o ao último dia do mês de destino quando necessário.
- Para a mesma data de referência e a mesma opção mensal ou anual, Combo e Descoberta devem apresentar a mesma data inicial e usar a mesma janela no backtest.
- Quando o dia existir no mês de destino, preservá-lo: com referência em 2026-05-15, “1 mês” começa em 2026-04-15 nas duas telas.
- Quando o dia não existir no mês de destino, usar seu último dia sem avançar para o mês seguinte: com referência em 2026-03-31, “1 mês” começa em 2026-02-28 nas duas telas; com referência em 2026-05-31, começa em 2026-04-30.
- Respeitar fevereiro em ano bissexto: com referência em 2024-03-31, “1 mês” começa em 2024-02-29 nas duas telas.
- Aplicar a mesma regra às opções anuais: com referência em 2024-02-29, o período de um ano começa em 2023-02-28 nas duas telas; com referência em 2026-05-15, começa em 2025-05-15.
- Validar todas as opções mensais e anuais já disponíveis nas duas telas, incluindo as que atravessam a virada do ano, sem mudar a data final do período.
- Preservar os resultados atuais de seleção de período por dias, personalizado e todo o histórico: para as mesmas entradas, suas datas inicial e final permanecem iguais às anteriores à correção.

## Não entra

- Alterar o ranking, execução do backtest ou a lista de opções do #1078.
- Reabrir o Status Homologado do #1078 ou antecipar os gates deste novo card.

## What Changes

- Alinhar a subtração de meses e anos à regra de calendário com limite no último dia do mês.
- Fixar critérios de paridade para todas as opções mensais/anuais e regressões para dias, personalizado e todo o histórico.

## Capabilities

### New Capabilities

- `sweep-calendar-parity`: contrato de calendário entre Combo e Descoberta, preservando data final e opções não mensais.

### Modified Capabilities

Nenhuma. A spec `backtest-config` não define calendário mensal entre Combo e Descoberta.

## Impact

- `frontend/src/lib/sweepPeriod.ts`: resolução usada pelo Combo e pelos payloads da Descoberta.
- `backend/app/tasks/discovery_tasks.py`: referência de comportamento (`relativedelta`), preservada e coberta por testes de paridade.
- Testes de período frontend e resolução da Descoberta; sem novas dependências ou mudanças de API.
