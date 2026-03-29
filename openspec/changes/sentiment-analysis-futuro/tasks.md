# OpenSpec Tasks — Sentiment Analysis (Integrated)

## Card #58 — CryptoMind Sentiment Integration Tasks

**Projeto:** CryptoTracker  
**Owner:** DEV Agent  
**PO Review:** ✅ Aprovado  
**Design:** ✅ Pronto para Design Agent  
**Alan Approval:** ⏳ Pendente  

**Nota de Escopo:** Este card **incrementa** a página /signals (Card #53), não cria página separada. Sentiment aparece como badge nos SignalCards e banner no topo.

---

## 1. Tarefas de Infraestrutura

### 1.1 Setup Backend

- [ ] Criar módulo `sentiment/` no backend
- [ ] Configurar Redis para cache (TTL: 15min para global, 1h para Fear&Greed)
- [ ] Configurar APScheduler para refresh automático (a cada 15min)
- [ ] Variáveis de ambiente: `SENTIMENT_CACHE_TTL=900` (15min em segundos)

---

## 2. Tarefas de Backend — API

### 2.1 Fear & Greed Endpoint

- [ ] `GET /api/v1/sentiment/fear-greed`
  - Chamar alternative.me API
  - Retornar: current value, label, change_24h, history (7 dias)
  - Cache Redis: 1 hora

### 2.2 News Sentiment Endpoint (Estratégia Híbrida)

- [ ] `GET /api/v1/sentiment/news?asset=BTC&limit=5`
  - **Fetch paralelo de ambas as fontes:**
    - CoinGecko News API (~200ms, 60% peso)
    - MiniMax MCP Web Search via script `mcp_web_search.js` (~2-3s, 40% peso)
  - Agregar resultados de ambas as fontes
  - Aplicar VADER em todos os títulos
  - Calcular aggregate_score: `60% * CoinGecko + 40% * MiniMax`
  - Retornar: articles[], aggregate_score, breakdown (coingecko_score, minimax_score)

### 2.3 Reddit Sentiment Endpoint

- [ ] `GET /api/v1/sentiment/reddit?asset=BTC&limit=10`
  - Buscar posts via PSAW (Pushshift) ou praw
  - Aplicar VADER no título
  - Retornar: posts[], aggregate_score

### 2.4 Signal Validation Endpoint (CORE)

- [ ] `GET /api/v1/sentiment/signal-validation?asset=BTC&signal_type=BUY`
  - Combinar Fear&Greed (40%) + News (30%) + Reddit (30%)
  - Calcular `confirmation`: `confirma` | `contradiz` | `neutro`
  - Lógica:
    ```
    IF sentiment_score > 0.3 AND signal_type IN ['BUY', 'HOLD'] → 'confirma'
    IF sentiment_score < -0.3 AND signal_type IN ['SELL', 'HOLD'] → 'confirma'
    IF sentiment_score < -0.3 AND signal_type IN ['BUY'] → 'contradiz'
    IF sentiment_score > 0.3 AND signal_type IN ['SELL'] → 'contradiz'
    ELSE → 'neutro'
    ```
  - Detectar divergência e retornar `divergence_detected: true/false`

### 2.5 Global Sentiment Endpoint

- [ ] `GET /api/v1/sentiment/global`
  - Agregado geral (sem asset específico)
  - Para FearGreedBanner no topo da /signals
  - Cache Redis: 15min

### 2.6 Error Handling

- [ ] Retry logic (1 retry com exponential backoff)
- [ ] Fallback: se API falha, retornar cache ou null
- [ ] Log estruturado para debugging

---

## 3. Tarefas de Frontend — Integração na Página /signals

### 3.1 FearGreedBanner (Topo da Página)

- [ ] Criar componente `FearGreedBanner`
- [ ] Posição: topo da página /signals, abaixo do header
- [ ] Layout: `📊 Fear & Greed: [72] (GREED) | 📈 +5 | [sparkline]`
- [ ] Tooltip no hover: histórico 7 dias
- [ ] Botão "×" para dispensar (localStorage)
- [ ] Loading state: skeleton
- [ ] Error state: "Sentiment indisponível" (não bloqueia)

### 3.2 SignalCard + Sentiment Badge (Modificação)

O SignalCard existente (Card #53) recebe novos campos:

- [ ] Adicionar campo `sentiment` ao tipo Signal (ou接收 do backend)
- [ ] Exibir badge abaixo de preço-alvo:
  ```
  😊 Sentiment: +0.72 (confirma)
  📰 News: +0.45  👽 Reddit: +0.38
  ```
- [ ] Cores do badge:
  - `confirma` → borda/texto verde
  - `contradiz` → borda/texto vermelho
  - `neutro` → borda/texto amarelo
- [ ] Click no badge → abre SentimentTooltip

### 3.3 SentimentTooltip (Detalhamento)

- [ ] Criar componente `SentimentTooltip`
- [ ] Exibir no click/hover do sentiment badge
- [ ] Conteúdo:
  - Fear & Greed: valor + sparkline
  - News: score + últimas 3 notícias resumidas
  - Reddit: score + subreddits breakdown
  - Recomendação: "confirma" / "contradiz" / "neutro"
- [ ] Position: tooltip acima ou abaixo do card (autoposicionar)

### 3.4 SentimentAlert (Divergência)

- [ ] Criar componente `SentimentAlert`
- [ ] Condição: `divergence_detected: true` na resposta da API
- [ ] Layout:
  ```
  ⚠️ DIVERGÊNCIA: Sinal BUY para BTC, mas Fear&Greed em 25 (FEAR)
  [Ver Detalhes] [Ignorar]
  ```
- [ ] "Ver Detalhes" → abre modal com histórico
- [ ] "Ignorar" → dismiss (localStorage por ativo)

### 3.5 Filtros (Opcional v1.1)

- [ ] Adicionar filtro "Sentiment" na barra de filtros da /signals
- [ ] Opções: Todos | Confirma | Contradiz | Neutro
- [ ] Contador: "X confirmam, Y contradizem"

---

## 4. Tarefas de UX/UI

### 4.1 Estados e Edge Cases

- [ ] Sentiment indisponível: mostrar "—" no badge, não bloquear card
- [ ] Loading: skeleton pulse no badge
- [ ] Cache stale (>30min): mostrar " desatualizado" com timestamp
- [ ]API timeout: fallback graceful, sentiment não aparece

### 4.2 Responsividade

- [ ] Mobile: FearGreedBanner em 2 linhas
- [ ] Mobile: SentimentBadge compacto (apenas score + cor)
- [ ] Tooltip: full width em mobile

---

## 5. Tarefas de ML/Processing

### 5.1 VADER Configuration

- [ ] Configurar VADER para inglês (padrão)
- [ ] Adicionar crypto lexicon básico:
  ```
  positive: moon, lambos, hodl, fomo, bullish, ATH, pump
  negative: dump, rekt, scam, rug, bearish, ATL, panic
  ```
- [ ] Testar com 10 samples conhecidos

### 5.2 Confirmation Logic

- [ ] Implementar lógica de confirmação conforme especificado em 2.4
- [ ] Normalizar scores: VADER (-1 a 1) → aggregate (0 a 100 ou -1 a 1)
- [ ] Detectar divergência: `|sentiment - signal_alignment| > threshold`

---

## 6. Tarefas de Testes

### 6.1 Backend Tests

- [ ] Unit tests para signal-validation logic
- [ ] Unit tests para confirmation calculation
- [ ] Integration tests com APIs mockadas
- [ ] Teste de cache Redis

### 6.2 Frontend Tests

- [ ] Component tests para FearGreedBanner
- [ ] Component tests para SentimentBadge (no SignalCard)
- [ ] Component tests para SentimentTooltip
- [ ] Integration tests: página /signals carrega com sentiment

### 6.3 E2E Tests (Playwright)

- [ ] Fluxo: abrir /signals → ver FearGreedBanner → ver SentimentBadge nos cards
- [ ] Fluxo: clicar badge → tooltip abre → fecha
- [ ] Fluxo: divergência detectada → alert aparece → ignorar

---

## 7. Tarefas de Deploy

### 7.1 Backend

- [ ] Deploy em staging (mesmo serviço)
- [ ] Verificar que endpoints /sentiment/* funcionam

### 7.2 Frontend

- [ ] Build de produção
- [ ] Testar /signals em staging
- [ ] Verificar FearGreedBanner e SentimentBadge

---

## 8. Checklist de Homologação

### Funcionalidades

- [ ] FearGreedBanner aparece no topo da /signals
- [ ] FearGreedBanner mostra valor + change + sparkline
- [ ] SignalCards mostram SentimentBadge
- [ ] Badge exibe "confirma" / "contradiz" / "neutro" com cores corretas
- [ ] Click no badge abre SentimentTooltip
- [ ] Tooltip mostra breakdown completo
- [ ] SentimentAlert aparece quando diverge
- [ ] Dismiss funciona (localStorage)

### Performance

- [ ] Página /signals carrega em <3s (mesmo com sentiment)
- [ ] Sentiment não bloqueia render dos cards
- [ ] Cache funciona (segunda visita mais rápida)

### UX

- [ ] Sentiment indisponível não quebra UI
- [ ] Mobile funciona
- [ ] Loading states visíveis

---

## 9. Estimativa de Esforço (REVISADA)

| Fase | Tasks | Estimativa |
|------|-------|------------|
| Infra + Backend APIs | 5 endpoints + cache | 8h |
| Frontend: FearGreedBanner | 1 componente | 2h |
| Frontend: SentimentBadge | Modificar SignalCard | 2h |
| Frontend: SentimentTooltip | 1 componente | 2h |
| Frontend: SentimentAlert | 1 componente | 2h |
| Tests + Fixes | Unit + E2E | 4h |
| **Total MVP** | | **20h** |

**Revisão:** Reduziu de ~30h para ~20h porque:
- Não cria página nova
- Reusa layout da /signals
- SignalCard já existe (só adiciona badge)

---

## 10. Dependências

```
[Backend APIs] → [/signals page loads]
                        ↓
              [SignalCard + SentimentBadge]
                        ↓
              [SentimentTooltip + Alert]
```

**Dependência crítica:** Card #53 (Signals Page) deve estar pronto antes ou em paralelo.

---

## 11. Notas para DEV

1. **Começar por**: Fear & Greed API (mais simples)
2. **Cache primeiro**: Redis cache evitar rate limits
3. **Signal-validation endpoint** é o mais importante (alimenta o badge)
4. **Graceful degradation**: se sentiment falhar, cards devem funcionar sem ele
5. **Não alterar**: layout principal da /signals, só adicionar indicadores

---

## 12. Data Sources (APIs Gratuitas)

| API | Endpoint | Rate Limit | Auth |
|-----|----------|------------|------|
| alternative.me | https://api.alternative.me/fng/ | 1/min | None |
| CoinGecko | https://api.coingecko.com/api/v3/ | 10-30/min | Optional |
| Reddit/PSAW | https://api.reddit.com/ + Pushshift | 60/min | None |
| MiniMax MCP | /root/.openclaw/workspace/scripts/mcp_web_search.js | N/A | None |

---

## 13. Escopo Delimitado (Não Fazer no MVP)

- ❌ Página separada de sentiment
- ❌ Gráfico de correlação sentiment × preço
- ❌ Alertas push
- ❌ Twitter/X Sentiment
- ❌ Telegram/Discord Sentiment
- ❌ Filtro "Sentiment" na /signals (v1.1)

---

*Tasks atualizadas pelo PO Agent em: 2026-03-27 16:55 UTC*  
*Card #58 — CryptoTracker Project*  
*Integração na página /signals (Card #53) — escopo reduzido*
