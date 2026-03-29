---
spec: openspec.v1
id: ai-dashboard-insights
title: Review PT-BR - AI Dashboard + Insights
card: "#56"
change_id: ai-dashboard-insights
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Review PT-BR: AI Dashboard + Insights

**Card:** #56 | `ai-dashboard-insights`

---

## Resumo Executivo

Este card implementa um dashboard consolidado que agrega dados dos cards #53, #55, #57 e #58 para dar ao trader uma visão unificada.

### O que este card faz:
- Dashboard com AI insights (baseado em regras)
- Exibe indicadores de #55
- Exibe Fear & Greed de #58
- Exibe sinais de #53
- Exibe métricas de #57

### O que este card NÃO faz:
- Não gera insights via LLM real (futuro)
- Não faz trading automático
- Não envia notificações

---

## Pontos de Atenção

1. **DEPENDÊNCIA CRÍTICA:** Este card depende de #53, #55, #57 e #58. Deve ser implementado POR ÚLTIMO.

2. **Graceful degradation:** Se uma API falhar, o resto do dashboard deve continuar funcionando.

3. **AI Insights simples:** São regras if-then, não LLM. Deve estar claro na UI.

---

## Dependências

| Card | O que consome |
|------|--------------|
| #53 | Sinais BUY/SELL/HOLD |
| #55 | RSI, MACD, Bollinger Bands |
| #57 | Métricas e histórico |
| #58 | Fear & Greed Index |

---

## Checklist de Validação

- [ ] Dashboard carrega dados de todas as APIs
- [ ] AI insights gerados por regras
- [ ] Fear & Greed gauge integrado
- [ ] Indicadores exibidos por ativo
- [ ] Sinais recentes listados
- [ ] Métricas de performance
- [ ] Graceful degradation funciona
- [ ] Responsivo em mobile

---

## Status: PRONTO PARA APROVAÇÃO

Este card está pronto para avançar para DESIGN, mas deve ser o ÚLTIMO card a ir para DEV.

---
