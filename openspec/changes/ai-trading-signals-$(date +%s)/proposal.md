# OpenSpec Proposal — AI Trading Signals & Portfolio Optimization

## 1. Resumo Executivo

**Card:** #51 — Implementar IA para Sinais de Trading e Otimização de Portfólio  
**Projeto:** CryptoTracker  
**Diretor:** Alan  
**Data:** 2026-03-26  

---

## 2. O Que É

**CryptoMind AI** é um motor de inteligência artificial que analisa dados de mercado em tempo real e entrega:

1. **Sinais de Trading (BUY/SELL/HOLD)** — gerados por modelos de ML (LSTM + RandomForest Ensemble) com confiança 0-100%
2. **Otimização de Portfólio** — recomendações de alocação baseadas em perfil de risco e métricas (Sharpe, Volatilidade, VaR)
3. **Dashboard Unificado** — visão consolidada com métricas tradicionais e insights de IA

### Diferencial Competitivo

| Concorrente | Limitação | CryptoMind AI |
|-------------|-----------|---------------|
| TradingView | Análise manual, sinais genéricos | Sinais automatizados com confiança |
| CoinGecko | Dados sem inteligência | Insights actionáveis |
| Terminol | Sem IA | ML em tempo real |

---

## 3. Por Que Agora

### 3.1 Necessidade de Mercado

- **Volatilidade alta** em 2026: necessidade de sinais rápidos
- **Sobrecarga de informação**: traders precisam filtrar ruído
- **Demanda por automação**: 73% dos investidores buscam ferramentas de IA (Pesquisa Crypto.com 2025)

### 3.2 Alinhamento Estratégico

- Diferenciação direta vs. concorrentes
- Aumento de retenção (feature premium)
- Receita potencial via assinaturas premium de sinais

### 3.3 Viabilidade Técnica

- Design e protótipo já aprovados
- Stack definida (React + FastAPI + ML)
- API endpoints documentados

---

## 4. Impacto Esperado

### 4.1 Métricas de Negócio

| Métrica | Baseline | Target | Crescimento |
|---------|----------|--------|-------------|
| Sinais gerados/dia | 0 | 50+ | novo |
| Acurácia de sinais | — | >65% | novo |
| Tempo de resposta | — | <200ms | novo |
| Engajamento (views/sinal) | — | 3+ | novo |
| Retorno de portfólio | baseline | +10% | comparativo |

### 4.2 Impacto no Produto

- **Nova seção** no app: "AI Signals" e "Portfolio Optimizer"
- **Gamificação**: cards de sinais com confiança visual (gauge semicircular)
- **Edge**: primeiro produto nacional com ML nativo para crypto

### 4.3 Impacto Operacional

- Equipe DEV precisa de expertise Python/ML
- Infra: Redis (cache), TimescaleDB (séries temporais)
- Compliance: disclaimers obrigatórios ("não é advice financeiro")

---

## 5. Escopo

### 5.1 Inclusões (MVP)

- [ ] Dashboard com resumo de IA
- [ ] SignalCard com BUY/SELL/HOLD
- [ ] Lista de sinais com filtros
- [ ] Portfolio Optimizer (alocação atual vs. recomendada)
- [ ] Simulação de rebalanceamento
- [ ] Métricas de risco (Sharpe, Volatilidade, VaR)
- [ ] AIInsightBanner com tendência

### 5.2 Exclusões (v1.1+)

- WebSocket para sinais em tempo real (v2.0)
- Histórico completo + backtesting (v1.2)
- Notificações push (v2.0)
- Trading automatizado (futuro)

---

## 6. Decisões Definidas (Alan, 2026-03-26)

| Decisão | Valor | Status |
|---------|-------|--------|
| Fonte de dados | **Binance API** (free) | ✅ |
| Confidence threshold | **70%** mínimo para exibir sinal | ✅ |
| Perfil de risco | **Usuário escolhe** (conservative/moderate/aggressive) | ✅ |
| Disclaimer legal | **"Isenção de responsabilidade: este não é advice financeiro. Investimentos em crypto envolvem risco. Decisões são de sua responsabilidade."** | ✅ |
| PostgreSQL | **Já existente na VPS** | ✅ |
| Cache | **In-memory** (sem custo extra) | ✅ |
| Custo infraestrutura | **$0/mês** | ✅ |

---

## 7. Dependências

| Dependência | Tipo | Status | Riscos |
|-------------|------|--------|--------|
| Design Spec | entrada | ✅ Aprovado | — |
| Protótipo | entrada | ✅ Criado | — |
| Binance API | externo | ✅ Definido | latência |
| PostgreSQL (VPS) | infra | ✅ Disponível | — |
| Cache in-memory | infra | ✅ Implementado em código | — |

---

## 8. Disclaimer Legal (MVP)

```
⚠️ ISENÇÃO DE RESPONSABILIDADE

Este produto fornece sinais de trading e recomendações de portfólio gerados por
inteligência artificial. Isto NÃO é advice financeiro.

- Os sinais não garantem lucro
- Investimentos em criptomoedas envolvem risco significativo
- Sempre faça sua própria pesquisa antes de investir
- Decisões de investimento são de sua exclusiva responsabilidade

Este é um produto educacional e de entretenimento.
```

---

## 9. Aprovações Necessárias

- [ ] PO Review (este documento)
- [ ] Design Approval (já aprovado)
- [ ] **Alan Approval** ← próximo gate

---

*Proposal criada pelo PO Agent em: 2026-03-26 21:59 UTC*  
*Card #51 — CryptoTracker Project*
