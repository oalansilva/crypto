# Design Spec: Filtrar Sinais — Apenas BUY com Target e Stop

**Card:** #68  
**change_id:** `filtrar-sinais-apenas-buy-com-target-stop`  
**Estágio:** DESIGN  
**Dependência:** Card #53 (sinais BUY/SELL/HOLD)

---

## 1. Layout Geral (Simplificado)

```
┌─────────────────────────────────────────────────────────┐
│  📊 Sinais de Trading                         [🔔] [⚙️] │
├─────────────────────────────────────────────────────────┤
│  Risk Profile:  [Conservative] [Moderate] [Aggressive]  │
├─────────────────────────────────────────────────────────┤
│  Filtros:  Ativo [BTC ▼]   ≥Conf [%]                   │
│            (dropdown tipo REMOVIDO)                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SignalCard (BUY fixo)                           │   │
│  │ 🟢 BUY  │  BTCUSDT  │  82%  │  Target: 97.5k  │   │
│  │ Entrada: 93k │ Stop: 91k │ RSI: 35 │  12:00    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SignalCard (BUY fixo)                           │   │
│  │ 🟢 BUY  │  ETHUSDT  │  78%  │  Target: 3.5k  │   │
│  │ Entrada: 3.2k │ Stop: 3.0k │ MACD: bullish │ 12:05│   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ⚠️ Isenção de responsabilidade: este não é advice     │
│     financeiro.                 [Ver mais sinais ▼]    │
└─────────────────────────────────────────────────────────┘
```

**Mudanças em relação ao Card #53:**
1. Dropdown "Tipo" removido do FilterBar (sempre BUY)
2. Badge verde "BUY" fixo em todos os cards (sem badge vermelho/cinza)
3. Card mostra "Entrada:" além de Target e Stop
4. Removida opção de filtro SELL/HOLD

---

## 2. Componentes

### 2.1 SignalCard (Versão BUY-Only)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `type` | string fixa | Sempre "BUY" (badge verde fixo) |
| `asset` | string | ex: BTCUSDT |
| `entry_price` | number | Preço de entrada em USDT |
| `confidence` | int 0–100 | Score do modelo |
| `confidenceBar` | gauge | Barra visual 0–100%, threshold 70% |
| `target_price` | number | Preço-alvo em USDT |
| `stop_loss` | number | Stop-loss em USDT |
| `indicators` | object | RSI, MACD, BB |
| `created_at` | datetime | Timestamp do sinal |

**Mudanças do Card #53:**
- Removido badge colorido dinâmico (sempre verde BUY)
- Adicionado campo `entry_price` explícito
- Removido campo `risk_profile` do card (já está no seletor acima)

### 2.2 ConfidenceGauge (Sem Mudança)

- Igual ao Card #53

### 2.3 RiskProfileSelector (Sem Mudança)

- Igual ao Card #53

### 2.4 FilterBar (Versão Simplificada)

| Elemento | Antes (#53) | Depois (#68) |
|----------|-------------|--------------|
| Dropdown tipo | Todos/BUY/SELL/HOLD | **REMOVIDO** |
| Dropdown ativo | Presente | Presente |
| Slider confidence | Presente | Presente |
| Botão limpar | Presente | Presente |

**Mudança:**
- Dropdown "Tipo" removido completamente
- Filtro `type=BUY` é enviado automaticamente pelo frontend

### 2.5 DisclaimerBanner (Sem Mudança)

- Igual ao Card #53

---

## 3. Fluxo de Dados (Atualizado)

```
1. Usuário acessa página de sinais
2. Frontend busca GET /signals?type=BUY&risk_profile=...&confidence_min=70
   (type=BUY é fixo, não selecionável pelo usuário)
3. Backend retorna apenas sinais BUY (ou todos — frontend filtra)
4. Frontend renderiza SignalCards BUY (sem badges SELL/HOLD)
5. Filtros: apenas ativo e confidence mínima
```

---

## 4. Estados Especiais

| Estado | UI |
|--------|-----|
| Loading | Skeleton cards (3 items) — igual Card #53 |
| Empty (sem sinais BUY) | "Nenhum sinal BUY encontrado" + limpar filtros |
| Error | Toast erro + retry — igual Card #53 |
| Dados desatualizados | Badge "Dados podem estar desatualizados" — igual Card #53 |

---

## 5. Responsividades

| Breakpoint | Layout |
|------------|--------|
| Desktop (≥1024px) | 3 cards por linha |
| Tablet (768–1023px) | 2 cards por linha |
| Mobile (<768px) | 1 card por linha, filtros colapsáveis |

---

## 6. Protótipo HTML

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sinais BUY Only</title>
<style>
  :root {
    --green: #22c55e;
    --green-light: #bbf7d0;
    --bg: #0f1117;
    --card-bg: #1a1d27;
    --border: #2a2d3a;
    --text: #e2e8f0;
    --text-muted: #94a3b8;
  }
  body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
  
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
  .header h1 { margin: 0; font-size: 1.5rem; }
  
  .risk-profile { display: flex; gap: 8px; margin-bottom: 16px; }
  .risk-btn { padding: 8px 16px; border: 1px solid var(--border); background: var(--card-bg); color: var(--text); border-radius: 8px; cursor: pointer; }
  .risk-btn.active { background: var(--green); color: #000; border-color: var(--green); }
  
  .filter-bar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; }
  .filter-bar select, .filter-bar input { padding: 8px 12px; border: 1px solid var(--border); background: var(--card-bg); color: var(--text); border-radius: 8px; }
  .filter-bar label { color: var(--text-muted); font-size: 0.875rem; }
  
  .signals-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
  
  .signal-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
  .signal-card:hover { border-color: var(--green); }
  
  .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
  .badge-buy { background: var(--green); color: #000; padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: 0.875rem; }
  .badge-buy::before { content: '🟢 '; }
  .asset { font-weight: 600; font-size: 1.125rem; }
  
  .confidence-bar { height: 8px; background: var(--border); border-radius: 4px; margin: 8px 0; overflow: hidden; }
  .confidence-fill { height: 100%; background: var(--green); border-radius: 4px; }
  .confidence-label { font-size: 0.75rem; color: var(--text-muted); }
  
  .prices { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 12px 0; }
  .price-item { background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; }
  .price-label { font-size: 0.75rem; color: var(--text-muted); }
  .price-value { font-weight: 600; font-size: 1rem; }
  .price-value.target { color: var(--green); }
  .price-value.stop { color: #ef4444; }
  .price-value.entry { color: #3b82f6; }
  
  .indicators { font-size: 0.875rem; color: var(--text-muted); margin-top: 8px; }
  .timestamp { font-size: 0.75rem; color: var(--text-muted); margin-top: 8px; text-align: right; }
  
  .disclaimer { margin-top: 24px; padding: 12px; background: rgba(255,255,0,0.1); border: 1px solid rgba(255,255,0,0.2); border-radius: 8px; font-size: 0.875rem; color: #fcd34d; }
  .disclaimer::before { content: '⚠️ '; }
</style>
</head>
<body>

<div class="header">
  <h1>📊 Sinais de Trading</h1>
</div>

<div class="risk-profile">
  <button class="risk-btn">Conservative</button>
  <button class="risk-btn active">Moderate</button>
  <button class="risk-btn">Aggressive</button>
</div>

<div class="filter-bar">
  <label>Ativo:</label>
  <select>
    <option>BTCUSDT</option>
    <option>ETHUSDT</option>
    <option>BNBUSDT</option>
  </select>
  <label>≥Conf:</label>
  <input type="number" value="70" min="0" max="100" style="width: 60px;">
</div>

<div class="signals-grid">
  <div class="signal-card">
    <div class="card-header">
      <span class="badge-buy">BUY</span>
      <span class="asset">BTCUSDT</span>
    </div>
    <div class="confidence-bar"><div class="confidence-fill" style="width: 82%"></div></div>
    <div class="confidence-label">82% confiança</div>
    <div class="prices">
      <div class="price-item">
        <div class="price-label">Entrada</div>
        <div class="price-value entry">$93,000</div>
      </div>
      <div class="price-item">
        <div class="price-label">Target</div>
        <div class="price-value target">$97,500</div>
      </div>
      <div class="price-item">
        <div class="price-label">Stop</div>
        <div class="price-value stop">$91,000</div>
      </div>
    </div>
    <div class="indicators">RSI: 35 • MACD: bullish • BB: 95k-92k</div>
    <div class="timestamp">12:00 BRT</div>
  </div>

  <div class="signal-card">
    <div class="card-header">
      <span class="badge-buy">BUY</span>
      <span class="asset">ETHUSDT</span>
    </div>
    <div class="confidence-bar"><div class="confidence-fill" style="width: 78%"></div></div>
    <div class="confidence-label">78% confiança</div>
    <div class="prices">
      <div class="price-item">
        <div class="price-label">Entrada</div>
        <div class="price-value entry">$3,200</div>
      </div>
      <div class="price-item">
        <div class="price-label">Target</div>
        <div class="price-value target">$3,500</div>
      </div>
      <div class="price-item">
        <div class="price-label">Stop</div>
        <div class="price-value stop">$3,000</div>
      </div>
    </div>
    <div class="indicators">RSI: 42 • MACD: bullish • BB: 3.4k-3.1k</div>
    <div class="timestamp">12:05 BRT</div>
  </div>
</div>

<div class="disclaimer">
  Isenção de responsabilidade: este não é advice financeiro.
</div>

</body>
</html>
```

---

## 7. Acessibilidade

- Badge BUY sempre visível (cor não é唯一的 diferenciador — texto BUY sempre presente)
- ConfidenceGauge: aria-label com valor numérico
- Focus visível em todos os elementos interativos
- Contraste WCAG AA

---

## 8. Dependências

- Card #53: implementação base de sinais (já completo)
- Sem novas dependências de API ou backend
