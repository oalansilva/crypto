## Why

O grafico aberto pelo Monitor ainda parece tecnico e pouco orientado ao uso, enquanto o anexo do card #218 mostra uma composicao mais clara para leitura de estrategia, sinais, risco e historico. A mudanca melhora a experiencia do usuario sem alterar regras de sinal, dados ou backend.

## What Changes

- Refazer o layout visual do modal de grafico do Monitor com inspiracao no arquivo `Estrategia.html` do anexo do card #218.
- Priorizar leitura operacional: cabecalho com ativo/status, grafico amplo, controles compactos, resumo do candle, risco, distancia, historico de sinais e notas.
- Manter o grafico interativo atual, zoom por botoes/scroll, timeframes permitidos e marcadores de compra/venda.
- Preservar redacao de parametros protegidos para usuario comum.
- Atualizar testes E2E do Monitor para cobrir o novo layout e evitar regressao dos controles principais.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `monitor`: O modal de grafico do Monitor deve renderizar uma tela de estrategia mais legivel e operacional, mantendo os dados e guardrails atuais.
- `chart-visualization`: O grafico do Monitor deve preservar zoom, marcadores, barras visiveis e contexto lateral no novo layout.

## Impact

- Frontend: `frontend/src/components/monitor/ChartModal.tsx`.
- Testes: `frontend/tests/e2e/monitor-mobile-cards-timeframe.spec.ts`.
- Sem migracao de banco, sem nova API e sem dependencia externa.
