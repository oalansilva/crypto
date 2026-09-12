## Why

Quem abre a análise de uma estratégia vê dezenas de operações no resumo/lista e anos de velas no gráfico, mas as setas de Compra/Venda só cobrem um recorte recente (hoje pintadas a partir do histórico recente do Monitor). No BTC/USDT 1d isso começa por volta de 05/01/26; o mesmo furo aparece em outros ativos. Dá para achar que a estratégia não operou, ou que o gráfico está quebrado.

## What Changes

- Na tela de análise (`/combo/results`, aberta pelos Favoritos ou após Combo), o gráfico marca **cada** operação da lista na vela correspondente (entrada e, se fechada, saída).
- Lista e gráfico contam a mesma história: não há operação na lista sem seta, nem seta sem operação na lista (1:1).
- Vale para qualquer ativo e timeframe dessa tela.
- O zoom inicial continua no recorte recente (~180 velas) para leitura; o histórico antigo permanece na série e aparece ao afastar o zoom, arrastar ou usar Menos. Resetar volta o recorte, sem apagar as setas da série.
- Origem das setas = lista de operações da análise — não o recorte recente de sinais do Monitor.
- Densidade visual de muitos marcadores é decisão de Design (setas menores / rótulo só no recorte apertado); **não** corta história.
- Catálogo de landmarks T5 ganha a chave `/combo/results` (hoje ausente no HEAD).

Fora: cards ao vivo do Monitor; métricas de promoção da Descoberta; redesenhar layout do gráfico ou da tabela; Excel extra; forçar todas as velas visíveis ao abrir.

## Capabilities

### New Capabilities

- `analysis-complete-trade-history`: contrato visível 1:1 lista↔setas na tela de análise (`/combo/results`) para qualquer ativo/timeframe; origem das setas = lista da análise; zoom inicial recente sem cortar a série.

### Modified Capabilities

- `chart-visualization`: o gráfico da análise deixa de usar o histórico recente do Monitor como fonte exclusiva dos marcadores; as setas seguem a lista completa da análise; o recorte inicial de ~180 velas permanece.
- `favorites`: abrir «Ver análise completa» não substitui as setas da lista pelo `signal_history` curto do Monitor.

## Impact

- Frontend: `ComboResultsPage` (`/combo/results`), `buildTradeMarkers` / `buildSignalHistoryMarkers`, `StrategyChartSurface` (marcadores na série vs viewport).
- Sem mudança de API obrigatória: a lista e as velas já existem no payload da análise (`/api/favorites/{id}/trades` e resultado Combo).
- Catálogo: `scripts/process-fsm/route-landmarks.yaml` chave `/combo/results`.
- Protótipo: `frontend/public/prototypes/card-917-historico-completo-analise/index.html`.
- Monitor ao vivo, Descoberta e layout da tabela ficam fora.
