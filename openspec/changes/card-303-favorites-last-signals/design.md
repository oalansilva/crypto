## Context

O Monitor já entrega `signal_history` no payload de opportunities e o `ChartModal` renderiza markers + lista “Histórico de sinais”. Favoritos abre a análise em `ComboResultsPage` com trades/candles, mas:

1. o navigate state não carrega `signal_history`;
2. o sync com Monitor usa `refresh=true` e timeout curto (2.5s), falhando em silêncio;
3. a UI de resultados não tem o painel de últimos sinais.

## Goals / Non-Goals

**Goals:**

- Paridade dos últimos sinais: se o Monitor tem histórico para estratégia/símbolo/timeframe, Favoritos mostra os mesmos eventos.
- Empty/erro explícito quando não houver histórico confiável ou o sync falhar.
- Reutilizar o contrato público de `signal_history` sem inventar sinais.

**Non-Goals:**

- Alterar geração de sinais no motor.
- Resolver avisos de “configuração de indicadores” fora do bloqueio direto aos sinais.
- Criar histórico paralelo diferente do Monitor.

## Decisions

1. **Fonte canônica = `opportunity.signal_history` do Monitor**  
   Favoritos deriva a lista e os markers desse campo (ou trades `source=monitor_signal_history`), não de um contrato novo.

2. **Sync sem `refresh=true` por padrão**  
   Usar cache do Monitor (`refresh=false`/omitido) no caminho “Ver resultados”, para evitar timeout e perda silenciosa. Timeout dedicado maior (~15s) só para sync de `signal_history`. Backend serve cache **stale** (até ~10 min) em `refresh=false` após o TTL fresh de 30s, para não descartar `signal_history` quando o recompute frio passa de 2.5s.

3. **Propagar `signal_history` no navigate state**  
   Incluir `signal_history` e `monitor_sync_status` (`ok` | `timeout` | `missing` | `empty`) ao abrir ComboResults.

4. **UI compartilhada**  
   Extrair ou espelhar o painel “Histórico de sinais” do `ChartModal` em ComboResults (últimos N, Compra/Venda, empty state).

5. **Markers**  
   Preferir markers derivados de `signal_history` (como no Monitor) além/em vez de só `buildTradeMarkers` do backtest completo.

## Risks / Trade-offs

- [Timeout residual] → Mitigar com cache + status explícito na UI.
- [Timestamps sem candle] → Garantir candles que cobrem os sinais ou filtrar markers sem match sem esconder a lista.
- [Match estratégia errada] → Manter `findMatchingOpportunity` por id/symbol+tf+strategy; status `missing` se não achar.

## Migration Plan

- Deploy frontend-only (preferencial).
- Rollback: reverter branch; Monitor permanece intacto.

## Open Questions

- Nenhum bloqueante. Rework 2026-07-16: evidência de que cache miss + timeout 2.5s escondia entrada 10/07 em BTC/USDT Favoritos.
