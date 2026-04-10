# SPEC — Visualizar Gráfico TradingView (#87)

## 1. Conceito & Visão

Quando o trader clicar em uma estratégia na tela Monitor, abrir um modal com gráfico interativo estilo TradingView mostrando candles, volume e indicadores técnicos. A experiência deve ser familiar para traders que usam TradingView — mesma paleta de cores, mesma disposição de elementos, mesma interatividade.

## 2. Domínio & Escopo

- **Projeto:** crypto
- **Rota:** `/monitor` → click em strategy row
- **Componente:** `ChartModal` (novo) — também usado por card #88
- **Biblioteca:** `lightweight-charts` (já em uso no projeto)

## 3. Data Model

来源: `OpportunityResponse` do backend

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `symbol` | string | Par de trading (ex: BTCUSDT) |
| `timeframe` | string | Timeframe (1h, 4h, 1d) |
| `next_status_label` | "entry" \| "exit" | Sinal — near entry = buy, near exit = sell |
| `entry_price` | float | Preço de entrada |
| `stop_price` | float | Preço de stop |
| `distance_to_stop_pct` | float | Risco em % |
| `indicator_values` | Dict[str, float] | Valores de indicadores |
| `parameters` | Dict[str, Any] | Params da estratégia |
| `notes` | string | Notas do trader |

## 4. Layout

```
┌──────────────────────────────────────────────────────────────┐
│ [Symbol] [timeframe] [SIGNAL]           $67,432.50 [×]      │
├────────────────────────────────────────────┬────────────────┤
│ [15m][1h][4h][1d] (timeframe selector)    │ Distância Entry │
│                                            │ -0.42%          │
│  ┌────────────────────────────────────┐   │ ████████░░ 92% │
│  │        CANDLESTICK CHART            │   │                 │
│  │  ─ - - - - ENTRY ($67,800) - - -   │   │ Risk / Stop     │
│  │         ▲ Buy signal                │   │ Entry: $67,800  │
│  │                         ▼ Sell      │   │ Stop:  $66,950  │
│  │  - - - - - STOP ($66,950) - - - -  │   │ -1.25% risk     │
│  │  ~~~~~~ EMA9 (blue) ~~~~~~~~       │   │                 │
│  │  ~~~~~~ SMA21 (amber) ~~~~~~~      │   │ Parameters      │
│  └────────────────────────────────────┘   │ ema_short: 9    │
│  [VOLUME BARS]                             │ ema_long:  21   │
│  [EMA9] [SMA21] [RSI] [ATR] (toggles)     │ stop_loss: 1.25%│
│                                              │                 │
│                                              │ Indicators      │
│                                              │ ema_9:  67,420  │
│                                              │ ema_21: 66,890  │
│                                              │ rsi_14: 58.3    │
│                                              │                 │
│                                              │ Notes           │
│                                              │ "Confirmação..."│
└────────────────────────────────────────────┴────────────────┘
│ LEGEND: EMA9 | SMA21 | Entry | Stop | Buy▲ | Sell▼          │
└─────────────────────────────────────────────────────────────┘
```

## 5. Visual Decisions

| Elemento | Valor |
|----------|-------|
| **Tema** | Dark (matching app: `#0d1117`) |
| **Entry line** | `#388bfd` (azul), dashed, 2px |
| **Stop line** | `#f85149` (vermelho), dashed, 2px |
| **EMA9 line** | `rgba(56, 139, 253, 0.7)`, solid, 1px |
| **SMA21 line** | `#d29922` (âmbar), solid, 1px |
| **Buy signal** | Triângulo verde `▲` sobre candle |
| **Sell signal** | Triângulo vermelho `▼` sobre candle |
| **Sidebar** | `280px` fixa, scroll interno |
| **Chart area** | `flex: 1`, preenche espaço restante |

## 6. Trigger

Card #87: Click em qualquer parte da strategy row no Monitor → abre ChartModal
Card #88: Click em botão "Expandir" no OpportunityCard → abre ChartModal (mesmo modal)

**Nota:** Card #87 e #88 usam o MESMO `ChartModal`. A diferença é só o trigger:
- #87: click na row → `onClick={() => openChart(symbol, opportunity)}`
- #88: click no botão "Expandir" → `onExpandChart(symbol, opportunity)`

## 7. Interação

| Elemento | Comportamento |
|----------|--------------|
| Click em strategy row | Abre `ChartModal` com dados da oportunidade |
| Timeframe selector | Recarrega candles + recalcula `indicator_values` |
| Toggle indicadores | Mostra/oculta line series no chart |
| Entry/Stop lines | `chart.addLineSeries()` horizontais |
| Botão × ou ESC | Fecha modal |
| Click fora do modal | Fecha modal |

## 8. Rejeições Explícitas

- ❌ **Drawing tools** (fibonacci, trendlines) — fora do escopo
- ❌ **Múltiplos símbolos simultâneos** — um símbolo por modal
- ❌ **Anotações interativas** no gráfico — notas ficam no sidebar
- ❌ **Alertas de price** — não faz parte do scope
- ❌ **WebSocket real-time** — dados históricos apenas (MVP)

## 9. Componente

```
src/components/monitor/ChartModal.tsx
  ├── Props: { symbol: string, opportunity: OpportunityResponse, onClose: () => void }
  ├── Estado: selectedTimeframe, visibleIndicators[], chartRef
  ├── useEffect: init lightweight-charts com candlestick + entry/stop lines
  ├── Sidebar: DistanceBox, RiskBox, ParametersGrid, IndicatorValuesList, NotesPanel
  └── Legend: indicador de cores

src/components/monitor/MonitorDashboardTab.tsx
  └── Adicionar onClick na strategy row: openChartModal(symbol, opportunity)
```

## 10. Próximo Passo DEV

1. Criar `ChartModal.tsx` em `frontend/src/components/monitor/`
2. Reutilizar lógica do `MiniCandlesChart` para candlestick series
3. Adicionar `chart.addLineSeries()` para entry/stop price
4. Adicionar `chart.addLineSeries()` para cada `indicator_values`
5. Sidebar com 5 seções: Distance, Risk/Stop, Parameters, Indicators, Notes
6. Timeframe selector que recarrega candles
7. Adicionar `onClick` handler na strategy row do Monitor
8. Card #88 reutiliza o mesmo `ChartModal` — não duplicar
