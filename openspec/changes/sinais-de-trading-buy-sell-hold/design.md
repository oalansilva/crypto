# Design Spec: Sinais de Trading BUY/SELL/HOLD

**Card:** #53  
**change_id:** `sinais-de-trading-buy-sell-hold`  
**Estágio:** DESIGN  
**Dependência:** Card #51 (decisões) | Card #55 (indicadores)

---

## 1. Layout Geral

```
┌─────────────────────────────────────────────────────────┐
│  📊 Sinais de Trading                         [🔔] [⚙️] │
├─────────────────────────────────────────────────────────┤
│  Risk Profile:  [Conservative] [Moderate] [Aggressive]  │
├─────────────────────────────────────────────────────────┤
│  Filtros:  Tipo [Todos ▼]   Ativo [BTC ▼]   ≥Conf [%]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SignalCard                                      │   │
│  │ 🟢 BUY  │  BTCUSDT  │  82%  │  Target: 97.5k  │   │
│  │         │  Stop: 91k  │  RSI: 35  │  12:00    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SignalCard                                      │   │
│  │ 🔴 SELL │  ETHUSDT  │  75%  │  Target: 3.2k  │   │
│  │         │  Stop: 3.5k  │  MACD: bearish  │ 12:05│   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ⚠️ Isenção de responsabilidade: este não é advice     │
│     financeiro.                 [Ver mais sinais ▼]    │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Componentes

### 2.1 SignalCard

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `type` | enum | BUY (verde) / SELL (vermelho) / HOLD (cinza) |
| `asset` | string | ex: BTCUSDT |
| `confidence` | int 0–100 | Score do modelo |
| `confidenceBar` | gauge | Barra visual 0–100%,threshold 70% marcado |
| `target_price` | number | Preço-alvo em USDT |
| `stop_loss` | number | Stop-loss em USDT |
| `indicators` | object | RSI, MACD, BB (referência Card #55) |
| `created_at` | datetime | Timestamp do sinal |
| `risk_profile` | enum | conservative / moderate / aggressive |

**Estados:**
- Default: card com borda normal
- Hover: elevação + borda colorida
- Loading: skeleton
- Error: mensagem de erro + retry

### 2.2 ConfidenceGauge

- Barra horizontal 0–100%
- Threshold 70% marcado com linha vertical
- Cor: verde ≥70%, amarelo 50–69%, vermelho <50%
- Animação de preenchimento ao carregar

### 2.3 RiskProfileSelector

- 3 botões toggle: Conservative | Moderate | Aggressive
- Persiste escolha no localStorage
- Afeta quais sinais são exibidos (threshold varia por profile)

### 2.4 FilterBar

- Dropdown tipo: Todos / BUY / SELL / HOLD
- Dropdown ativo: lista de ativos disponíveis
- Slider ou input para confidence mínima
- Botão "Limpar filtros"

### 2.5 DisclaimerBanner

- Texto: "Isenção de responsabilidade: este não é advice financeiro."
- Visível em todas as páginas de sinais
- Ícone ⚠️ sempre presente
- Posição: fixo no rodapé da seção ou bottom sheet

---

## 3. API Endpoints (Design)

### GET `/signals`

**Request:**
```
GET /signals?type=BUY&confidence_min=70&asset=BTCUSDT&risk_profile=moderate&limit=20
```

**Response:**
```json
{
  "signals": [
    {
      "id": "uuid-v4",
      "asset": "BTCUSDT",
      "type": "BUY",
      "confidence": 82,
      "target_price": 97500.00,
      "stop_loss": 91000.00,
      "indicators": {
        "RSI": 35,
        "MACD": "bullish",
        "BollingerBands": { "upper": 98000, "lower": 92000 }
      },
      "created_at": "2026-03-26T12:00:00Z",
      "risk_profile": "moderate"
    }
  ],
  "total": 1,
  "cached_at": "2026-03-26T12:05:00Z"
}
```

### GET `/signals/{id}`

Mesma estrutura para um único sinal.

### GET `/signals/latest`

Retorna os 5 sinais mais recentes com confidence ≥70%.

---

## 4. Fluxo de Dados

```
1. Usuário acessa página de sinais
2. Frontend busca GET /signals com risk_profile do localStorage
3. Backend valida params, consulta cache (5 min TTL)
4. Se cache miss: consulta Binance API + calcula sinais
5. Retorna sinais filtrados (confidence ≥ 70%)
6. Frontend renderiza SignalCards em lista
7. Filtros interativos disparam nova busca (debounce 300ms)
```

---

## 5. Modelos (Reference Only — Card #55)

O modelo de sinais é um **LSTM + RandomForest Ensemble**:

- **LSTM**: captura dependências temporais de preço
- **RandomForest**: classificação baseada em features de indicadores
- **Ensemble**: média ponderada das probabilidades

**Features de entrada:**
- Preço histórico (OHLCV) — Binance
- RSI (Card #55)
- MACD (Card #55)
- Bollinger Bands (Card #55)
- Volume profile

**Output:**
```
{
  "type": "BUY" | "SELL" | "HOLD",
  "confidence": 0.0–1.0,
  "target_price": float,
  "stop_loss": float,
  "risk_profile_scores": {
    "conservative": 0.75,
    "moderate": 0.82,
    "aggressive": 0.90
  }
}
```

---

## 6. Responsividades

| Breakpoint | Layout |
|------------|--------|
| Desktop (≥1024px) | 3 cards por linha |
| Tablet (768–1023px) | 2 cards por linha |
| Mobile (<768px) | 1 card por linha, filtros colapsáveis |

---

## 7. Dependências Visuais

- Ícones: Lucide React (já no projeto)
- Cores: variáveis CSS do tema existente
- Tipografia: igual ao resto do app
- Badge de confiança: pill colorido (verde/amarelo/vermelho)

---

## 8. Estados Especiais

| Estado | UI |
|--------|-----|
| Loading | Skeleton cards (3 items) |
| Empty (sem sinais) | Empty state + ilustração + "Aguardando novos sinais" |
| Error | Toast de erro + botão retry |
| All filtered out | "Nenhum sinal atende aos filtros" + botão limpar |
| Stale data (cache >5min) | Badge "Dados podem estar desatualizados" |

---

## 9. Teste de Snapshot (referência)

- SignalCard com BUY, confidence 82
- SignalCard com SELL, confidence 71
- SignalCard com HOLD, confidence 90
- FilterBar com filtros ativos
- DisclaimerBanner

---

## 10. Acessibilidade

- Cor não é o único diferenciador (ícones + texto)
- ConfidenceGauge: aria-label com valor numérico
- Focus visível em todos os elementos interativos
- Contraste WCAG AA
