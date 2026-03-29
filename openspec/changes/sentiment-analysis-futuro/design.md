# OpenSpec Design Artifact — Sentiment Analysis (Integrated)

## 1. Conceito & Visão

**Nome:** CryptoMind Sentiment (integrado ao Signals)  
**Tagline:** "Confirme seus sinais com o humor do mercado"

**Resumo:** O sentiment analysis é um **incremento** à tela de sinais existente (/signals - Card #53). Em vez de página separada, Fear & Greed Index, news sentiment e Reddit sentiment aparecem como indicadores adicionais nos SignalCards e no topo da página, ajudando o trader a confirmar ou questionar os sinais BUY/SELL/HOLD.

**Proposta de Valor:**
- Validação adicional dos sinais (confirma ou contradiz)
- Visão do humor do mercado sem sair da tela de sinais
- Alerta de divergência (sinal bullish mas sentiment bearish)
- Dados de sentiment integrados ao contexto do sinal

---

## 2. Layout & Estrutura

### 2.1 Arquitetura: Integração na Página /signals

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Logo + Navigation + Wallet Status + User Menu           │
├───────────┬─────────────────────────────────────────────────────┤
│           │                                                     │
│  SIDEBAR  │  SIGNALS PAGE (COM SENTIMENT INTEGRADO)           │
│           │                                                     │
│  - Dashboard│  ┌─────────────────────────────────────────────┐  │
│  - Signals  │  │ 📊 FEAR & GREED: 72 (GREED)  [?tooltip]   │  │
│  - Portfolio│  └─────────────────────────────────────────────┘  │
│  - History  │                                                     │
│  - Settings │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│           │  │ BUY      │ │ BUY      │ │ SELL     │        │
│           │  │ BTC/USDT │ │ ETH/USDT │ │ SOL/USDT │        │
│           │  │ [sent.]  │ │ [sent.]  │ │ [sent.]  │        │
│           │  └──────────┘ └──────────┘ └──────────┘        │
│           │                                                     │
│           │  [Filtros: tipo, confiança, ativo, sentiment]       │
│           │                                                     │
└───────────┴─────────────────────────────────────────────────────┘
```

### 2.2 Integração no SignalCard

**Opção A: Badge de Confirmação (Recomendada)**
```
┌──────────────────────────────────────┐
│ 🟢 BUY  │  BTC/USDT  │  Conf: 87%   │
│─────────┴────────────┴───────────────│
│ Preço Atual: $67,432                 │
│ Preço-Alvo:   $72,500 (+7.5%)        │
│ Stop-Loss:    $64,200 (-4.8%)        │
│─────────────────────────────────────│
│ 😊 Sentiment: +0.72 (confirma)      │
│ 📰 News: +0.45  👽 Reddit: +0.38    │
│─────────────────────────────────────│
│ Updated: 2 min ago                   │
└──────────────────────────────────────┘
```

**Legenda de Confirmação:**
- `confirma` (verde): sentiment alignment com o sinal
- `contradiz` (vermelho): sentiment diverge do sinal
- `neutro` (amarelo): sentiment misto ou fraco

**Opção B: Sentiment Gauge Compacto no Card**
```
┌──────────────────────────────────────┐
│ 🟢 BUY  │  BTC/USDT  │  Conf: 87%   │
│─────────┴────────────┴───────────────│
│ [=========>        ] Fear&Greed: 72 │
│ [=====>            ] News: +0.45   │
│ [=====>            ] Reddit: +0.38  │
└──────────────────────────────────────┘
```

### 2.3 Fear & Greed Banner Global (Topo da Página)

```
┌──────────────────────────────────────────────────────────────┐
│ 📊 Fear & Greed Index: 72 (GREED)  📈  │  😊 News: +0.45  │
│   [sparkline 7d]                      │  👽 Reddit: +0.38 │
│   ↑ +5 nas últimas 24h                │  Agg: +0.62        │
│                                                              │
│  ℹ️ O sentiment geral está alinhado com sinais BUY.          │
└──────────────────────────────────────────────────────────────┘
```

**Estados:**
- Loading: skeleton
- Error: "Sentiment temporariamente indisponível"
- "Dispensar" salva preferência no localStorage

### 2.4 Tooltip de Detalhe (on hover / click)

```
┌──────────────────────────────────────────────────┐
│  📊 SENTIMENT DETAIL — BTC/USDT                │
│  ─────────────────────────────────────────────  │
│  Fear & Greed Index: 72 (Greed)                 │
│  └── 7 dias: [sparkline]                        │
│                                                  │
│  News Sentiment: +0.45 (BULLISH)                │
│  └── 3 notícias positivas, 1 negativa           │
│  └── "BTC sobe com inflow de ETFs"              │
│                                                  │
│  Reddit Sentiment: +0.38 (SLIGHTLY BULLISH)     │
│  └── r/bitcoin: +0.72                           │
│  └── r/cryptocurrency: +0.45                    │
│  └── r/cryptomarkets: -0.12                     │
│                                                  │
│  💡 Recomendação: Sentiment confirma BUY         │
│  ⚠️ divergência: none                           │
└──────────────────────────────────────────────────┘
```

---

## 3. Componentes de UI

### 3.1 FearGreedBanner (Global)
```
┌──────────────────────────────────────────────────────────────┐
│ 📊 Fear & Greed: [72] [GREED] │ 📈 +5 │ [sparkline]        │
└──────────────────────────────────────────────────────────────┘
```
- Posição: topo da página /signals
- Atualização: a cada 15 min (cache)
- Interação: hover → tooltip com histórico 7 dias
- Dismiss: botão "×" salva no localStorage

### 3.2 SignalCard + Sentiment Badge (Componente Modificado)

O SignalCard existente (Card #53) recebe um novo campo:

```
┌──────────────────────────────────────┐
│ [TIPO] │ [ATIVO] │ [CONFIANÇA]      │
│────────┴─────────┴──────────────────│
│ [Preço Atual]                       │
│ [Preço-Alvo] [Stop-Loss]            │
│─────────────────────────────────────│
│ 😊 Sentiment: [+0.72] [confirma]    │
│ 📰 News: +0.45  👽 Reddit: +0.38    │
└──────────────────────────────────────┘
```

**Variações:**
- **confirma** (verde): sentiment_score > 0.3 E alinhado com tipo
- **contradiz** (vermelho): sentiment_score < -0.3 OU divergente
- **neutro** (amarelo): -0.3 <= sentiment_score <= 0.3

### 3.3 SentimentTooltip
- Exibido no hover do badge de sentiment
- Mostra breakdown: Fear&Greed, News, Reddit individual
- Histórico sparkline do Fear&Greed
- Recomendação: "confirma" / "contradiz" / "neutro"

### 3.4 SentimentAlert (Divergência Detectada)
```
┌──────────────────────────────────────────────────────────────┐
│ ⚠️ DIVERGÊNCIA DETECTADA                                    │
│ Sinal BUY para BTC, mas Fear&Greed caiu para 25 (FEAR)      │
│ Historicamente, isso reduz acerto em ~15%                     │
│ [Ver Detalhes]  [Ignorar]  [Não mostrar mais]               │
└──────────────────────────────────────────────────────────────┘
```
- Aparece no topo quando divergência é detectada
- Pode ser global ou por card específico
- "Não mostrar mais" salva no localStorage por ativo

---

## 4. Fluxos de Usuário

### 4.1 Fluxo: Ver Sinais com Sentiment
```
1. Usuário acessa /signals (página existente)
2. FearGreedBanner carrega no topo (cache: 15min)
3. SignalCards carregam com sentiment badges
4. Cada card mostra:
   - Tipo/Ativo/Confiança (existente)
   - Sentiment aggregate (+0.72)
   - Badge: "confirma" / "contradiz" / "neutro"
5. Usuário clica no sentiment badge
6. Tooltip abre com detalhamento
```

### 4.2 Fluxo: Investigar Divergência
```
1. SentimentAlert aparece: "Sinal BUY mas sentiment FEAR"
2. Usuário clica "Ver Detalhes"
3. Modal abre com:
   - Histórico: preço vs. sentiment (7 dias)
   - Breakdown: Fear&Greed, News, Reddit
   - Contexto: últimas notícias negativas
4. Usuário decide se ignora o sinal ou não
```

### 4.3 Fluxo: Filtrar por Sentiment (Feature Adicional)
```
1. Usuário clica em filtro "Sentiment"
2. Opções: Todos | Confirma | Contradiz | Neutro
3. Cards filtrados instantaneamente
4. Badge "X sinais confirmam / Y contradizem"
```

---

## 5. API Endpoints

### 5.1 Fear & Greed Index
```
GET  /api/v1/sentiment/fear-greed
     Query: ?days=7 (default)
     Response: { 
       current: { value: 72, classification: "Greed" },
       previous_day_value: 67,
       change_24h: +5,
       history: [{ date, value }, ...]
     }
```
**Fonte:** alternative.me Fear & Greed API (gratuito)

### 5.2 News Sentiment (por ativo) — Estratégia Híbrida

**Fluxo Paralelo (sempre ambas as fontes):**
```
/api/sentiment/news?asset=BTC
       ↓
[CoinGecko API]     [MiniMax MCP Web Search]
    ↓                        ↓
  ~200ms                   ~2-3s
    ↓________________________↓
          Agrega resultados
                 ↓
          VADER analisa todos os títulos
                 ↓
          Sentiment: 60% CoinGecko + 40% MiniMax
                 ↓
          Redis cache 15min
```

**Pesos:**
- **CoinGecko News API**: 60% — Estruturado, confiável, ~200ms latência, Free tier
- **MiniMax MCP Web Search**: 40% — Tempo real, fontes diversas, ~2-3s latência

**Benefícios:**
- Máxima cobertura de notícias
- Validação cruzada entre fontes
- Resiliência (se uma falhar, outra ainda responde)
- Cobertura em tempo real

```
GET  /api/v1/sentiment/news
     Query: ?asset=BTC&limit=5
     Response: { 
       articles: [{ 
         title, source, url, published_at, 
         sentiment_score: -1 to 1,
         source_type: "coingecko" | "minimax"
       }, ...],
       aggregate_score: 0.45,
       breakdown: {
         coingecko_score: 0.38,    // 60% peso
         minimax_score: 0.55       // 40% peso
       },
       asset: "BTC"
     }
```
**Fontes:** CoinGecko News API (60%) + MiniMax MCP Web Search (40%)

### 5.3 Reddit Sentiment (por ativo)
```
GET  /api/v1/sentiment/reddit
     Query: ?asset=BTC&limit=10
     Response: {
       posts: [{
         title, subreddit, url, 
         score, comments,
         sentiment_score: -1 to 1
       }, ...],
       aggregate_score: 0.38
     }
```

### 5.4 Sentiment para Signal Card
```
GET  /api/v1/sentiment/signal-validation
     Query: ?asset=BTC&signal_type=BUY
     Response: {
       asset: "BTC",
       signal_type: "BUY",
       sentiment_score: 0.72,       // -1 to 1
       sentiment_label: "bullish",
       confirmation: "confirma",     // confirma | contradiz | neutro
       breakdown: {
         fear_greed: { score: 72, value: 72, weight: 0.4 },
         news: { score: 0.45, value: 65, weight: 0.3 },
         reddit: { score: 0.38, value: 63, weight: 0.3 }
       },
       divergence_detected: false,
       divergence_message: null
     }
```

### 5.5 Aggregate Global (para Banner)
```
GET  /api/v1/sentiment/global
     Response: {
       fear_greed: { value: 72, label: "Greed" },
       news: { score: 0.45, label: "bullish" },
       reddit: { score: 0.38, label: "slightly_bullish" },
       aggregate: 0.62,
       updated_at: "2026-03-27T16:50:00Z"
     }
```

---

## 6. Modelo de Dados

### 6.1 SentimentBadge (前端)
```typescript
interface SentimentBadge {
  score: number;              // -1 to 1 (normalized)
  label: 'bullish' | 'bearish' | 'neutral';
  confirmation: 'confirma' | 'contradiz' | 'neutro';
  breakdown: {
    fear_greed: number;       // 0-100
    news: number;             // -1 to 1
    reddit: number;           // -1 to 1
  };
}
```

### 6.2 FearGreedBanner (前端)
```typescript
interface FearGreedBanner {
  value: number;              // 0-100
  label: string;              // "Extreme Fear" | "Fear" | "Neutral" | "Greed" | "Extreme Greed"
  change_24h: number;        // +5 ou -8
  history: Array<{ date: string; value: number }>;
}
```

### 6.3 SignalWithSentiment (Frontend Model)
```typescript
interface SignalWithSentiment extends Signal {
  sentiment?: SentimentBadge;
}
```

---

## 7. Stack Técnica (Minimal Changes)

### Backend
- **Novos endpoints**: `/sentiment/fear-greed`, `/sentiment/news`, `/sentiment/reddit`, `/sentiment/signal-validation`, `/sentiment/global`
- **Reutilizar**: Redis cache (já existente), VADER (já instalado)
- **Novo**: APScheduler para refresh automático a cada 15min

### Frontend
- **Modificar**: SignalCard component (adicionar sentiment badge)
- **Adicionar**: FearGreedBanner (topo da página signals)
- **Adicionar**: SentimentTooltip (tooltip no hover)
- **Adicionar**: SentimentAlert (banner de divergência)
- **Modificar**: Filtros da página signals (adicionar filtro por sentiment)

### Mudanças Mínimas
- Não criar página nova
- Não alterar layout principal da /signals
- Adicionar apenas indicadores visuais nos cards existentes

---

## 8. Métricas de Sucesso

| Métrica | Target | Medição |
|---------|--------|---------|
| Utilização do sentiment | >50% dos usuários clicam no badge | Analytics |
| Confirmação acurada | >70% das confirmações conferem | Backtest |
| Divergências úteis | >60% das divergências indicam reversão | Análise posterior |
| Performance | Sentiment não aumenta load time em >200ms | APM |

---

## 9. Escopo: O Que FAZER e O Que NÃO FAZER

### ✅ MVP (Este Card)

- Fear & Greed Index no topo da /signals (banner)
- Sentiment badge nos SignalCards (confirma/contradiz/neutro)
- Tooltip com detalhamento no hover/click
- Detecção de divergência (alert banner)
- Filtro por sentiment (opcional v1.1)

### ❌ NÃO FAZER (Expansões Futuras)

- Página separada de sentiment
- Gráfico de correlação sentiment × preço
- Alertas push/notificação
- Twitter/X sentiment
- Telegram/Discord sentiment

---

## 10. Riscos & Mitigações

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| APIs gratuitas com rate limit | Alta | Médio | Redis cache 15min |
| VADER não otimizado para crypto | Alta | Médio | Mostrar "confirma" apenas se score > 0.3 |
| Performance (novas APIs na /signals) | Média | Médio | Lazy load sentiment, só quando card visível |
| Cache stale | Baixa | Baixo | Mostrar "atualizado há X min" |

---

## 11. Comparação: Design Original vs. Novo

| Aspecto | Original (Página Separada) | Novo (Integrado) |
|---------|---------------------------|------------------|
| Local | /sentiment (nova página) | /signals (existente) |
| Impacto UX | Maior (nova página) | Mínimo (incremento) |
| Complexidade | Alta (página + componentes) | Baixa (badge + banner) |
| Esforço DEV | ~30h | ~12h (estimativa revisada) |
| Foco | Análise de sentiment | Suporte à decisão de trade |

---

*Design artifact atualizado em: 2026-03-27 16:55 UTC*  
*PO Agent — CryptoTracker Project*
*Integração na página /signals (Card #53)*
