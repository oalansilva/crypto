## Why

O Monitor pode exibir `Venda` e encerrar visualmente uma posição comprada quando o último trade armazenado contém uma saída temporalmente incompatível com os candles atuais. O card #280 mostrou divergência entre badge, marcador, posição e gráfico, incluindo evidência de saída posterior ao último candle disponível.

## What Changes

- Validar a coerência temporal do último evento de trade antes de usá-lo como fonte autoritativa do estado do Monitor.
- Impedir que saída futura, fora do intervalo carregado ou incompatível com o candle de referência force `EXIT`/`Venda`.
- Resolver posição, badge, mensagem e marcador do gráfico a partir da mesma evidência válida.
- Preservar `Compra` quando existe entrada ativa sem saída válida posterior.
- Adicionar cobertura backend e frontend para entrada ativa, saída confirmada e saída temporalmente inválida.
- Manter o visual existente do `DESIGN.md`: verde `#0ecb81` para compra, vermelho `#f6465d` para venda e superfícies escuras do Monitor; não há redesign.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `monitor`: exigir coerência temporal e uma única fonte válida para estado da posição, badge, mensagem e marcador.

## Impact

- Backend: `backend/app/services/opportunity_service.py` e testes de estado/serviço do Monitor.
- Frontend: `frontend/src/components/monitor/signalResolution.ts`, `ChartModal.tsx` e testes de resolução/marcadores.
- Dados: leitura defensiva de `favorite_strategies.metrics.trades`; sem migração e sem alteração de parâmetros salvos.
- Runtime alvo: somente DEV nesta etapa.
