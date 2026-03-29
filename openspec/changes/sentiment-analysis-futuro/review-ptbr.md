# OpenSpec Review — Sentiment Analysis (Integrated)

## Review PT-BR — Card #58

**Projeto:** CryptoTracker  
**Feature:** CryptoMind Sentiment — Incremento na Tela de Sinais (/signals)  
**Data do Review:** 2026-03-27 16:55 UTC  
**Revisor:** PO Agent  
**Status:** ✅ Pronto para Design Agent

---

## 1. Resumo da Mudança

**Decisão do Alan:** Inteirar sentiment analysis DENTRO da tela de sinais existente (/signals - Card #53), não criar página separada.

**Impacto da decisão:**
- Menos confusão para o usuário (tudo em um lugar)
- Menos esforço de desenvolvimento (~20h vs ~30h)
- Design mais coeso (sentiment valida os sinais diretamente)
- Zero novas páginas para manter

---

## 2. Análise de Escopo

### 2.1 O Que Muda

| Antes (Página Separada) | Agora (Integrado) |
|-------------------------|-------------------|
| Nova página `/sentiment` | Incremento na `/signals` |
| Dashboard completo de sentiment | Badge nos SignalCards + Banner |
| 5+ componentes de página | 2 componentes novos + 1 modificado |
| ~30h de implementação | ~20h de implementação |

### 2.2 Componentes do MVP

| Componente | Tipo | Descrição |
|------------|------|-----------|
| FearGreedBanner | Novo | Banner no topo da /signals |
| SignalCard + SentimentBadge | Modificado | Badge de confirmação nos cards |
| SentimentTooltip | Novo | Detalhamento no hover/click |
| SentimentAlert | Novo | Alerta de divergência |

### 2.3 O Que NÃO Está no MVP

Conforme orientação do Alan:
- ❌ Nova página de sentiment
- ❌ Gráfico de correlação sentiment × preço
- ❌ Filtro de sentiment na /signals (v1.1)
- ❌ Twitter/X, Telegram, Discord sentiment

---

## 3. Análise de Design (design.md)

### 3.1 Arquitetura de Integração

```
/signals (Card #53) — PÁGINA EXISTENTE
    │
    ├── FearGreedBanner (TOPO) — componente novo
    │       └── Exibe: valor atual, mudança 24h, sparkline
    │
    ├── SignalCard (MODIFICADO)
    │       └── Adicionado: SentimentBadge (confirma/contradiz/neutro)
    │
    ├── SentimentTooltip (NOVO)
    │       └── Detalhamento no hover/click do badge
    │
    └── SentimentAlert (NOVO)
            └── Alerta quando divergência é detectada
```

### 3.2 SignalCard com SentimentBadge

```
┌──────────────────────────────────────┐
│ 🟢 BUY  │  BTC/USDT  │  Conf: 87%   │
│─────────┴────────────┴───────────────│
│ Preço Atual: $67,432                 │
│ Preço-Alvo:   $72,500 (+7.5%)       │
│ Stop-Loss:    $64,200 (-4.8%)       │
│─────────────────────────────────────│
│ 😊 Sentiment: +0.72 (confirma)      │  ← NOVO
│ 📰 News: +0.45  👽 Reddit: +0.38   │
└──────────────────────────────────────┘
```

**Lógica de Confirmação:**
- `confirma` (verde): sentiment alinhado com tipo do sinal
- `contradiz` (vermelho): sentiment oposto ao tipo do sinal
- `neutro` (amarelo): sentiment misto ou fraco

### 3.3 API Core: Signal Validation

O endpoint mais importante é `/api/v1/sentiment/signal-validation` que retorna:
- `sentiment_score` (-1 a 1)
- `confirmation`: `confirma` | `contradiz` | `neutro`
- `breakdown`: Fear&Greed, News, Reddit individuais
- `divergence_detected`: boolean

---

## 4. Análise de Tasks (tasks.md)

### 4.1 Comparativo de Esforço

| Fase | Original (Página Separada) | Novo (Integrado) |
|------|---------------------------|------------------|
| Backend APIs | 15 tasks | 10 tasks |
| Frontend: Página nova | 12 tasks | 0 tasks |
| Frontend: Componentes | 12 tasks | 7 tasks |
| Tests | 6 tasks | 6 tasks |
| **Total tasks** | ~45 | ~25 |
| **Estimativa** | ~30h | ~20h |

### 4.2 Priorização

1. **Primeiro**: Backend - FearGreed API + Signal Validation endpoint
2. **Segundo**: Frontend - FearGreedBanner
3. **Terceiro**: Frontend - SentimentBadge (modificar SignalCard)
4. **Quarto**: Frontend - SentimentTooltip + Alert
5. **Quinto**: Tests

---

## 5. Viabilidade Técnica

### 5.1 O Que Está Pronto

- [x] Design spec completo (integrado na /signals)
- [x] Tasks detalhadas (~25 items)
- [x] APIs gratuitas identificadas
- [x] Redis cache existente
- [x] Card #53 (Signals) como base

### 5.2 O Que Ainda Precisa

- [ ] **Design Agent**: revisar design.md (confirmar integração)
- [ ] **Alan**: aprovar para DEV
- [ ] **DEV**: implementar (~20h)
- [ ] **QA**: validar badges e alertas

### 5.3 Riscos

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| Rate limits | Alta | Médio | Redis cache 15min + estratégia híbrida |
| Performance /signals | Média | Médio | Lazy load sentiment |
| VADER impreciso | Alta | Médio | Threshold alto (0.3) para confirmação |
| MiniMax MCP lenta/falha | Média | Baixo | CoinGecko ainda responde (60% peso) |

---

## 6. Estimativas Finais

### Esforço

| Fase | Estimativa |
|------|------------|
| Backend APIs | 8h |
| Frontend (banner + badge + tooltip + alert) | 8h |
| Tests | 4h |
| **Total MVP** | **20h** |

### Custo

| Serviço | Custo |
|---------|-------|
| Redis (existente) | $0 |
| alternative.me | $0 |
| CoinGecko (free tier) | $0 |
| Reddit/PSAW | $0 |
| MiniMax MCP Web Search | $0 (script existente) |
| **Total** | **$0/mês** |

---

## 7. Comparação: Original vs. Novo

| Aspecto | Original | Novo (Alan Decision) |
|---------|----------|---------------------|
| Escopo | Nova página | Incremento |
| Impacto UX | Alto (nova página) | Mínimo |
| Esforço DEV | ~30h | ~20h |
| Complexidade | Média-alta | Baixa-média |
| Manutenção | 2 páginas | 1 página |
| Valor para usuário | Análise isolada | Suporte direto ao trade |

**Conclusão:** A decisão do Alan de integrar na /signals é mais pragmática e entrega valor mais rápido.

---

## 8. Recomendações

### Para Design Agent

1. **Foco**: não criar página nova, só modificar/incrementar /signals
2. **SignalCard**: o badge de sentiment deve ser discreto mas visível
3. **Cores**: verde=confirma, vermelho=contradiz, amarelo=neutro
4. **Mobile**: SentimentBadge deve funcionar bem em tela pequena

### Para DEV

1. **Começar pelo endpoint** `signal-validation` (é o core)
2. **Cache Redis**: implementar primeiro para evitar rate limits
3. **Graceful degradation**: se sentiment falhar, /signals funciona sem
4. **Card #53**: garantir que SignalCard está pronto antes de adicionar badge

### Para Alan

1. **Aprovar** esta versão integrada
2. **Prioridade**: #58 → #57 → #56 → #65
3. **v1.1**: adicionar filtro de sentiment depois

---

## 9. Veredicto

| Critério | Status |
|----------|--------|
| Escopo correto (integrado) | ✅ |
| Design detalhado | ✅ |
| Tasks completas | ✅ |
| Viável tecnicamente | ✅ |
| Custo zero | ✅ |
| Esforço reduzido | ✅ |
| Pronto para Design | ✅ SIM |
| Pronto para DEV | ⏳ Após Design + Alan Approval |

---

## 10. Próximos Passos

1. **Design Agent** ← você está aqui
   - Revisar design.md (integração na /signals)
   - Confirmar que SignalCard será modificado corretamente

2. **Alan Approval**
   - Revisar design e tasks
   - Aprovar para DEV

3. **DEV** (após aprovação)
   - Implementar backend (8h)
   - Implementar frontend (8h)
   - Tests (4h)

4. **QA**
   - Validar FearGreedBanner
   - Validar SentimentBadge nos cards
   - Validar SentimentTooltip e Alert

5. **Alan Homologação**

6. **Archive**

---

## 11. Nota Importante

Este card **incrementa** o Card #53 (Signals Page). A página /signals já existe e está em uso. O sentiment é um **incremento**, não uma mudança de arquitetura.

**Ordem de desenvolvimento sugerida:**
1. Card #53 ( Signals Page) — base existente
2. Card #58 (Sentiment) — incremento na /signals

Se #53 ainda não está pronto, #58 pode começar pelo backend e FearGreedBanner primeiro.

---

*Review atualizado pelo PO Agent em: 2026-03-27 16:55 UTC*  
*Card #58 — CryptoTracker Project*  
*Integração na página /signals — escopo revisado conforme decisão do Alan*
