# Proposal: Cores das Médias Móveis no Gráfico TradingView-like

## User Story

**Como** usuário do monitor  
**Eu quero** ver as médias móveis com cores diferenciadas por período no gráfico  
**Para** facilitar a identificação visual de qual média é qual

---

## Value Proposition

- **Melhora legibilidade** do gráfico — usuário identifica rapidamente qual média está vendo
- **UX melhor** — padrão visual consistente com plataformas de trading
- **Reduz confusão** — cores diferenciadas evitam misturar médias de diferentes períodos

---

## Scope In

- Aplicar esquema de cores às médias móveis (SMA, EMA) exibidas no gráfico do monitor
- **Curta (período < 20):** VERMELHO
- **Média (período 20-50):** LARANJA
- **Longa (período > 50):** AZUL

**Tipos de média afetados:**
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)

**Contexto:** Gráfico TradingView-like na tela monitor (`/monitor`)

---

## Scope Out

- Não altera indicadores RSI ou outros não-MA
- Não altera cores de candles
- Não muda tipo de gráfico (mantém candlestick)

---

## Color Palette

| Tipo | Threshold | Cor | Hex |
|------|-----------|-----|-----|
| Curta | período < 20 | 🔴 Vermelho | `#FF5252` |
| Média | período 20-50 | 🟠 Laranja | `#FF9800` |
| Longa | período > 50 | 🔵 Azul | `#2196F3` |

**Nota:** Cores subjectivas ao design system do projeto — confirmar com DESIGN.

---

## Technical Notes

**Implementação localizada em:**
- `frontend/src/components/monitor/ChartModal.tsx`
- Períodos resolvidos no objeto `indicatorPeriods`
- Séries das médias criadas com `mainChart.addLineSeries()` para `emaShort`, `smaMedium` e `smaLong`

**Biblioteca:** `lightweight-charts` (TradingView) — suporta `lineStyle`, `lineWidth`, `color` nas séries de linha

**Exemplo de API:**
```typescript
chart.addLineSeries({
  color: period < 20 ? '#FF5252' : period < 50 ? '#FF9800' : '#2196F3',
  lineWidth: 2
});
```

---

## Dependencies

- **Card #87** (Visualizar gráfico TradingView) deve estar implementado — este card complementa com estilização
-确认 OHLCV data source existe para os períodos de MA

---

## Risks

1. **Low** — Mudança de cor simples em configuração de série
2. **MA sem período definido** — se período não está no dado, pode usar cor default
3. **Escala de cores subjetiva** — "curta/média/longa" pode variar

---

## ICE Score

- Impact: 7 (UX improvement, visual clarity)
- Confidence: 7 (clear requirement, implementation straightforward)
- Ease: 8 (color assignment based on period threshold)
- **ICE: 392**
