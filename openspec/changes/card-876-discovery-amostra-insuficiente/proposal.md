## Why

O administrador que dispara uma varredura grande em produção espera horas enquanto pares cuja listagem no timeframe é curta demais para alguma vez atingir 30 negócios ainda correm o grid completo (~16 mil parâmetros, 1–2 min cada). O progresso conta isso como sucesso e o ranking parcial fica poluído. Incidente PROD 2026-09-08 (run `#c243f729`, 694 combinações, VPS saturada) mostrou o caso (ex.: BLZ/USDT ~27 diárias).

## What Changes

- Worker mede o comprimento da listagem **antes** do grid. Combinação curta demais para alguma vez ter 30 negócios no ranking (incl. split treino/holdout 70/30 da Descoberta) termina em segundos, **sem** otimização.
- **BREAKING** no invariante de progresso: `N processadas = X sucesso + Y falha + Z ignoradas + W amostra insuficiente`. Quarto saco persistido; não reusa `sucesso` nem `ignoradas`.
- `Sucesso` continua = rodou e deixou candidato (inclui `Baixa amostra` pós-grid). `Ignoradas` = não rodou (cancelar). `Amostra insuficiente` = listagem curta, sem otimização.
- No Decidir a linha **aparece**: rank «—», selo `Amostra insuficiente` (não misturar com `Baixa amostra`), Calmar/queda/negócios N/A, sem CTA promover, fora do top-5 do Acompanhar e do rank.
- Varredura só com listagem curta **conclui** (`0` sucesso + `N` amostra insuficiente), não falha operacional do worker.
- Limite «1 por sweep» nesta VPS de 4 cores **permanece**. Par com histórico cheio segue o caminho feliz (otimização + ranking + selo `Baixa amostra` só depois do backtest).

Fora (grelha): concorrência/Celery; redesign 3 modos/top-5 (#852); operação da run `#c243f729`; universo 694; Calmar inflado com histórico cheio; poupar tempo em par com anos de candles e poucos negócios.

## Capabilities

### New Capabilities

- (nenhuma) — o comportamento entra nas capacidades já existentes da Descoberta.

### Modified Capabilities

- `discovery-sweep`: gate de listagem antes do grid; quarto contador `amostra insuficiente`; combinação com estado próprio (não `succeeded`/`skipped`/`failed`); reconciliação trata `0` sucesso + `N` amostra insuficiente como `completed`, não falha operacional.
- `discovery-leaderboard`: persistir/exibir candidato `insufficient_sample` distinto de `low_sample`; sem rank, sem promover, métricas N/A; não entra no top do Acompanhar nem no rank do Decidir.
- `discovery-three-modes`: linha de progresso do Acompanhar inclui o quarto termo; Decidir mostra a linha com selo `Amostra insuficiente` e sem CTA promover.

## Impact

- Backend: `run_combination` em `backend/app/tasks/discovery_tasks.py` (gate antes de `ComboOptimizer.run_optimization`); reconciliação `_reconcile_locked` / fórmula `processed`; modelo/API de sweep (quarto contador); persistência de resultado/combinação com `eligibility=insufficient_sample`.
- Frontend: `DiscoveryPage.tsx` — fórmula no Acompanhar (`data-testid=counter-invariant`); linha do Decidir (selo, rank —, N/A, sem promover); parciais top-5 não incluem amostra insuficiente.
- Specs canónicas: `openspec/specs/discovery-sweep`, `discovery-leaderboard`, `discovery-three-modes`.
- Sem mudança de concorrência, fila, «1 por sweep», modos da tela (#852) ou universo de símbolos.
