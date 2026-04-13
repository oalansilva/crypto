# Contrato de sprint

## Projeto
crypto

## Operational root
/root/.openclaw/workspace/crypto

## Escopo desta sprint
cores das medias
- localizar o componente real que renderiza as medias moveis no monitor
- definir e documentar os thresholds de periodo antes da implementacao da coloracao
- implementar a coloracao por periodo no grafico e nas legendas relacionadas

## Fora de escopo
- alterar RSI ou outros indicadores nao relacionados a medias moveis
- mover card de coluna ou reconciliar workflow fora do claim atual
- implementar a coloracao sem claim dos itens subsequentes

## Comportamentos esperados
- o grafico do monitor usa `frontend/src/components/monitor/ChartModal.tsx` como componente principal
- os periodos das medias sao derivados de `opportunity.parameters` via `indicatorPeriods`
- as tres medias do grafico principal sao renderizadas como line series separadas: `emaShort`, `smaMedium` e `smaLong`
- os thresholds ficam definidos como: curta `< 20`, media `>= 20` e `< 50`, longa `>= 50`
- a cor das medias segue `getMAColor(period)`: vermelho para curta, laranja para media, azul para longa

## Sensores obrigatorios
- inspecao estatica do componente e dos artefatos OpenSpec
- confirmacao do estado canonico do card via API central da board

## Evidencias esperadas
- referencia de codigo em `frontend/src/components/monitor/ChartModal.tsx`
- task 1 marcada como concluida em `openspec/changes/cores-das-medias/tasks.md`
- task 2 marcada como concluida em `openspec/changes/cores-das-medias/tasks.md`
- task 3 marcada como concluida em `openspec/changes/cores-das-medias/tasks.md`
- confirmacao na board canonica de que o card `cores-das-medias` esta em `DEV`
- `npm --prefix frontend run build` concluido com sucesso
- `cd frontend && npx tsc --noEmit` concluido com sucesso

## Riscos conhecidos
- a API detalhada do change em `:8004/api/workflow/projects/crypto/changes/cores-das-medias` nao respondeu nesta rodada
