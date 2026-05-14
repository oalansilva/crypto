## Why

O grafico detalhado do Monitor contradiz a lista principal: a lista mostra `Compra`, mas o modal pode mostrar `ESPERA` para o mesmo ativo. Alem disso, o modo padrao `Algoritmica` esconde contexto, risco e historico, que sao parte do fluxo validado para beta.

## What Changes

- Fazer o estado principal do modal refletir a leitura do Monitor para a estrategia/timeframe do ativo.
- Manter explicacao quando os candles exibidos nao batem com o candle de referencia, sem trocar o estado principal para `Espera`.
- Exibir contexto, risco/stop e historico de sinais no caminho padrao de abertura do grafico.
- Adicionar cobertura E2E focada no caso `Compra` com historico e risco visiveis.

## Capabilities

### New Capabilities

### Modified Capabilities
- `monitor-card-view-mode`: o modal de grafico deve abrir com detalhe operacional visivel para usuario comum.
- `monitor-active-entry-confirmation`: a confirmacao visual de entrada ativa nao pode contradizer o estado principal do Monitor.

## Impact

- Frontend: `frontend/src/components/monitor/ChartModal.tsx` e possivelmente `signalResolution.ts`.
- Testes: `frontend/tests/e2e/monitor-mobile-cards-timeframe.spec.ts` ou novo teste E2E focado.
- Sem impacto esperado em API, banco ou recomendacao financeira.
