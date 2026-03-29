# Prototype v3 — Sentiment INTEGRADO no SignalCard

## Conceito
Sentiment NÃO é seção separada. É um badge interno ao card que reforça ou questiona o sinal.

---

## Layout Visual

```
┌─────────────────────────────────────────────────────┐
│  [🟢 BUY]  BTC/USDT              27/03 14:32       │
│  ✓ Confirma  (badge de sentiment verde)            │
│                                                     │
│  ━━━━━━━━━━━━ ████████░░░░ 78%  Confiança         │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐                  │
│  │   TARGET    │  │  STOP LOSS  │                  │
│  │  $105.420   │  │   $98.200   │                  │
│  └─────────────┘  └─────────────┘                  │
│                                                     │
│  RSI: 68.2    MACD: Alta    Bollinger: 98k-108k   │
│                                                     │
│  🟢 Sentiment: Bullish (integração interna)        │
└─────────────────────────────────────────────────────┘
```

---

## Card 1 — BUY + Sentiment Positivo ("Confirma")

```html
<!-- SignalCard BTC/USDT — BUY + Confirma -->

<div class="signal-card buy">
  <!-- Header -->
  <div class="flex items-start justify-between">
    <div class="flex flex-col gap-2">
      <div class="flex items-center gap-2">
        <!-- Badge BUY -->
        <span class="badge badge-buy">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg>
          BUY
        </span>
        <span class="pair">BTC/USDT</span>
        <!-- Badge Sentiment — INTEGRADO -->
        <span class="badge badge-sentiment-confirm" title="Sentiment confirma direção do sinal">
          ✓ Confirma
        </span>
      </div>
    </div>
    <span class="date">27/03 14:32</span>
  </div>

  <!-- Confidence Gauge -->
  <div class="gauge-section">
    <div class="gauge-bar">
      <div class="gauge-fill" style="width: 78%"></div>
    </div>
    <div class="gauge-label">
      <span class="gauge-value">78%</span>
      <span class="gauge-text">Confiança</span>
      <!-- Sentiment context inline -->
      <span class="sentiment-hint bullish">↑ sentiment fortalece</span>
    </div>
  </div>

  <!-- Targets -->
  <div class="grid-2">
    <div class="metric-card">
      <div class="metric-label">Target</div>
      <div class="metric-value green">$105.420</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Stop loss</div>
      <div class="metric-value red">$98.200</div>
    </div>
  </div>

  <!-- Indicators -->
  <div class="grid-3">
    <div class="metric-card">
      <div class="metric-label">RSI</div>
      <div class="metric-value">68.2</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">MACD</div>
      <div class="metric-value">Alta</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Bollinger</div>
      <div class="metric-value small">$98k — $108k</div>
    </div>
  </div>

  <!-- Sentiment integrado como tag interna (não seção) -->
  <div class="sentiment-footer">
    <span class="sentiment-dot green"></span>
    <span class="sentiment-text">Sentiment: <strong>Bullish</strong> — confirma direção</span>
  </div>
</div>
```

---

## Card 2 — SELL + Sentiment Negativo ("Alerta")

```html
<!-- SignalCard BTC/USDT — SELL + Alerta -->

<div class="signal-card sell">
  <!-- Header -->
  <div class="flex items-start justify-between">
    <div class="flex flex-col gap-2">
      <div class="flex items-center gap-2">
        <!-- Badge SELL -->
        <span class="badge badge-sell">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17 7l-9.2 9.2M7 7v10h10"/></svg>
          SELL
        </span>
        <span class="pair">BTC/USDT</span>
        <!-- Badge Sentiment — INTEGRADO -->
        <span class="badge badge-sentiment-alert" title="Sentiment contradiz direção do sinal">
          ⚠ Alerta
        </span>
      </div>
    </div>
    <span class="date">27/03 14:32</span>
  </div>

  <!-- Confidence Gauge -->
  <div class="gauge-section">
    <div class="gauge-bar">
      <div class="gauge-fill" style="width: 62%"></div>
    </div>
    <div class="gauge-label">
      <span class="gauge-value">62%</span>
      <span class="gauge-text">Confiança</span>
      <!-- Sentiment context inline -->
      <span class="sentiment-hint bearish">↓ sentiment questiona</span>
    </div>
  </div>

  <!-- Targets -->
  <div class="grid-2">
    <div class="metric-card">
      <div class="metric-label">Target</div>
      <div class="metric-value green">$98.200</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Stop loss</div>
      <div class="metric-value red">$105.420</div>
    </div>
  </div>

  <!-- Indicators -->
  <div class="grid-3">
    <div class="metric-card">
      <div class="metric-label">RSI</div>
      <div class="metric-value">72.8</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">MACD</div>
      <div class="metric-value">Baixa</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Bollinger</div>
      <div class="metric-value small">$98k — $108k</div>
    </div>
  </div>

  <!-- Sentiment integrado como tag interna (não seção) -->
  <div class="sentiment-footer">
    <span class="sentiment-dot orange"></span>
    <span class="sentiment-text">Sentiment: <strong>Fear</strong> — requer cautela</span>
  </div>
</div>
```

---

## CSS Suggested

```css
/* Sentiment badge — integrado no header row */
.badge-sentiment-confirm {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #34d399;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}

.badge-sentiment-alert {
  background: rgba(251, 146, 60, 0.15);
  border: 1px solid rgba(251, 146, 60, 0.4);
  color: #fb923c;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}

/* Sentiment hint na gauge label */
.sentiment-hint {
  font-size: 11px;
  margin-left: auto;
}
.sentiment-hint.bullish { color: #34d399; }
.sentiment-hint.bearish { color: #fb923c; }

/* Sentiment footer tag dentro do card */
.sentiment-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 8px 12px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  font-size: 12px;
  color: var(--text-secondary);
}

.sentiment-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.sentiment-dot.green { background: #34d399; box-shadow: 0 0 6px #34d399; }
.sentiment-dot.orange { background: #fb923c; box-shadow: 0 0 6px #fb923c; }
```

---

## O que MUDOU vs v2

| Aspecto | v2 (errado) | v3 (correto) |
|---|---|---|
| FearGreedBanner | Seção separada no topo da página | REMOVIDO |
| Sentiment Breakdown | Seção abaixo dos cards | REMOVIDO |
| SentimentBadge | Não existia | Integrado no header do card |
| Sentiment hint | Não existia | Inline na gauge label |
| Sentiment footer | Não existia | Tag interna na parte inferior do card |
| Score/confiança | Isolado | Considera sentiment como fator interno |

## Pontos-chave

1. **SentimentBadge no header** — aparece ao lado do badge BUY/SELL, dizendo "✓ Confirma" ou "⚠ Alerta"
2. **Sentiment hint na gauge** — texto inline que diz se sentiment fortalece ou questiona o sinal
3. **Sentiment footer tag** — linha discreta na parte inferior com dot colorido + texto explicativo
4. **Nenhuma seção separada** — não existe FearGreedBanner global nem Sentiment Breakdown abaixo dos cards
5. **Tooltip disponível** — hover no badge mostra contexto (ex: "Sentiment confirma direção do sinal")
