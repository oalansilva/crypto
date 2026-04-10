# SPEC — Gráfico Expandido (Monitor)

## 1. Conceito & Visão

O "Gráfico Expandido" é um modal fullscreen que mostra o gráfico candlestick maximizado com overlay da estratégia — indicadores, entry/stop lines, e sinais de trade. Inspirado em TradingView mas adaptado ao universo de estratégias do crypto monitor. O modal substitui o card compacto de 280px por uma visão dedicada onde o trader pode analisar entrada, risco e sinais num único lugar.

## 2. Domínio & Escopo

- **Projeto:** crypto
- **Rota:** `/monitor` → botão "Expandir" em cada card de opportunity
- **Componente:** `ExpandedChartModal` (novo) + `MiniCandlesChart` (existente, reutilizado)
- **Biblioteca de gráfico:** `lightweight-charts` (já em uso)

## 3. Data Model (do backend)

来源: `OpportunityResponse` (`opportunity_routes.py`)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `symbol`, `timeframe` | string | Identificação do ativo |
| `next_status_label` | "entry" \| "exit" | **Sinal** — near entry = buy, near exit = sell |
| `entry_price` | float | Preço de entrada (horizontal line no gráfico) |
| `stop_price` | float | Preço de stop (horizontal line no gráfico) |
| `distance_to_stop_pct` | float | Risco em % |
| `indicator_values` | Dict[str, float] | Valores de indicadores (ex: `{ema_9: 67420, rsi_14: 58.3}`) |
| `parameters` | Dict[str, Any] | Params da estratégia (ema_short, ema_long, stop_loss, timeframe) |
| `notes` | string | Notas do trader |

**Nota:** Não há campos explícitos `buy_signal`/`sell_signal`. O sinal é derivado de `next_status_label`.

## 4. Layout

```
┌──────────────────────────────────────────────────────────────┐
│ [Symbol] [timeframe] [SIGNAL BADGE]           $67,432.50 [×] │
├────────────────────────────────────────────┬─────────────────┤
│ [15m][1h][4h][1d] (timeframe selector)     │ Distância Entry │
│                                            │  -0.42%         │
│  ┌──────────────────────────────────────┐  │ ████████░░ 92% │
│  │                                      │  │                 │
│  │        CANDLESTICK CHART             │  │ Risk / Stop     │
│  │  ─ - - - - ENTRY ($67,800) - - -    │  │ Entry: $67,800  │
│  │        ▲ Buy signal                  │  │ Stop:  $66,950  │
│  │                        ▼ Sell       │  │ -1.25% risk     │
│  │  - - - - - STOP ($66,950) - - - -  │  │                 │
│  │                                      │  │ Parameters      │
│  │  ~~~~~~ EMA9 (blue) ~~~~~~~~        │  │ ema_short: 9    │
│  │  ~~~~~~ SMA21 (amber) ~~~~~~~       │  │ ema_long:  21   │
│  └──────────────────────────────────────┘  │ stop_loss: 1.25%│
│  [EMA9] [SMA21] [ATR] (indicator toggles)  │                 │
│                                              │ Indicators      │
│                                              │ ema_9:  67,420  │
│                                              │ ema_21: 66,890  │
│                                              │ rsi_14: 58.3    │
│                                              │                 │
│                                              │ Notes           │
│                                              │ "Confirmação..."│
└────────────────────────────────────────────┴─────────────────┘
│ LEGEND: EMA9 | SMA21 | Entry | Stop | Buy▲ | Sell▼           │
└──────────────────────────────────────────────────────────────┘
```

## 5. Interação

| Elemento | Comportamento |
|----------|--------------|
| Botão "Expandir" no card | Abre `ExpandedChartModal` com `symbol` e `opportunity` props |
| Timeframe selector | Recarrega candles + recalcula `indicator_values` via API |
| Toggle indicadores | Mostra/oculta cada line series no chart |
| Linha ENTRY (tracejada azul) | `chart.addLineSeries()` com `price: entry_price`, cor `#388bfd` |
| Linha STOP (tracejada vermelha) | `chart.addLineSeries()` com `price: stop_price`, cor `#f85149` |
| Indicadores (EMA, SMA, etc.) | `chart.addLineSeries()` para cada `indicator_values` key |
| Botão × / ESC | Fecha modal |
| Click fora do modal | Fecha modal |

## 6. Decisões Visuais

- **Tema:** dark (matching app's `dark:bg-gray-900` / `#0d1117`)
- **Bordas/colunas:** `rgba(48,54,61,0.8)` — subtlety
- **Entrada (ENTRY):** `#388bfd` (azul TradingView-style)
- **Stop (STOP):** `#f85149` (vermelho)
- **Buy signal:** triângulo verde `▲` sobre o candle
- **Sell signal:** triângulo vermelho `▼` sobre o candle
- **Indicadores:** linha azul (`#388bfd`) para EMA curto, âmbar (`#d29922`) para SMA longo
- **Sidebar:** `280px` fixa, scroll interno, background `var(--surface)`
- **Gráfico:** `flex: 1`, altura máxima (preenche espaço restante)

## 7. Rejeições Explícitas

- ❌ **Drawing tools** (linhas de tendência, fibonacci, etc.) — fora do escopo
- ❌ **Múltiplos símbolos simultâneos** — um símbolo por modal
- ❌ **Anotações interativas** no gráfico — notas ficam no sidebar
- ❌ **Alertas de price** — não é parte do "gráfico expandido"

## 8. Componente Proposto

```
src/components/monitor/ExpandedChartModal.tsx
  ├── Props: { symbol: string, opportunity: OpportunityResponse, onClose: () => void }
  ├── Estado interno: selectedTimeframe, visibleIndicators[], chartRef
  ├── useEffect: init lightweight-charts com candlestick + entry/stop lines + indicator lines
  ├── Sidebar: RiskBox, ParametersGrid, IndicatorValuesList, NotesPanel
  └── Legend: indicador de cores
```

## 9. Próximo Passo DEV

1. Criar `ExpandedChartModal.tsx` em `frontend/src/components/monitor/`
2. Reutilizar `MiniCandlesChart` logic para candlestick series
3. Adicionar `chart.addLineSeries()` para cada `indicator_values` entry
4. Adicionar `chart.addLineSeries()` horizontais para `entry_price` e `stop_price`
5. Adicionar marker series para buy/sell signals derivados de `next_status_label`
6. Sidebar com sections: Distance, Risk/Stop, Parameters, Indicator Values, Notes
7. Timeframe selector que recarrega candles + recalcula indicadores
8. Adicionar botão "Expandir" em `OpportunityCard` (ao lado de "Price"/"Strategy")
