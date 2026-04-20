# Proposal: Visualizar gráfico de estratégia igual TradingView

## User Story

As a trader, when I click on a strategy in the Monitor screen, I want to see an interactive chart similar to TradingView with candles, volume, and technical indicators, so that I can analyze the strategy performance visually.

## Value Proposition

**Current state:** Strategy details in Monitor screen are shown as text/data lists without visual chart representation.

**Target state:** Clicking a strategy opens an interactive chart panel showing:
- Candlestick chart (OHLC)
- Volume bars
- Technical indicators (SMA, EMA, RSI)

**Benefits:**
- Visual analysis of strategy performance
- Industry-standard trading chart experience
- Better decision-making for traders

## Scope In

- Interactive candlestick chart using `lightweight-charts` (already in project)
- Volume bars below candles
- Technical indicators: SMA (9), EMA (21), RSI (14)
- Modal overlay triggered from Monitor strategy click
- Historical data display
- Basic chart interactions: zoom, pan, crosshair
- Timeframe selection: 1h, 4h, 1d

## Scope Out

- Real-time WebSocket data (historical only for MVP)
- Drawing tools (Fibonacci, trendlines)
- Multiple chart types (candlestick only)
- Mobile-optimized chart interactions (desktop-first)
- Price alerts/notifications

## Technical Approach

Based on Party Mode session `eee758e7`:
- Use `lightweight-charts` library (already in project dependency)
- Data source: strategy historical data from existing API
- Modal component for chart display
- Responsive container but desktop-optimized interactions

## Dependencies

1. Confirm strategy data API provides OHLCV data
2. Confirm lightweight-charts version supports required indicators
3. Monitor screen already has strategy click handler (or needs one)

## Acceptance Criteria

1. Clicking strategy in Monitor opens chart modal
2. Chart displays candlesticks with correct OHLC data
3. Volume bars visible below candles
4. SMA, EMA, RSI indicators toggleable
5. Zoom/pan interactions work smoothly
6. Timeframe selector changes chart data
7. Modal closes with X button or backdrop click

## Prototype Requirement

**Prototype is required** before this card can advance to Alan approval.

DESIGN should create a prototype showing the chart modal with sample data.

## Status

Ready for DESIGN prototype.
