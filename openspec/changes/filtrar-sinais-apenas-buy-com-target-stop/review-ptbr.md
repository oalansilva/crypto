# Review: Filtrar Sinais — Apenas BUY com Target e Stop

**Card:** #68  
**change_id:** `filtrar-sinais-apenas-buy-com-target-stop`  
**Estágio:** PO  
**Reviewer:** PO Agent  
**Data:** 2026-03-28

---

## 1. Resumo da Mudança

Simplificar a tela de sinais para exibir apenas sinais BUY, removendo SELL e HOLD da interface. O Exit é determinado pelo target/stop do próprio sinal BUY.

### O que muda:
- **Removido:** Dropdown de filtro por tipo (Todos/BUY/SELL/HOLD)
- **Removido:** Badge colorido dinâmico (sempre BUY = verde)
- **Adicionado:** Badge verde fixo "BUY" em todos os cards
- **Adicionado:** Campo "Entrada" visível no card

### O que NÃO muda:
- Backend/APIs (dados já existem no banco)
- Lógica de geração de sinais
- Indicadores (RSI/MACD/Bollinger)
- RiskProfileSelector
- DisclaimerBanner

---

## 2. Critérios de Aceite

| # | Critério | Status |
|---|----------|--------|
| 1 | Apenas sinais BUY são exibidos na interface | ✅ Implementável |
| 2 | Sinais SELL e HOLD são removidos da exibição | ✅ Implementável |
| 3 | Cada sinal BUY mostra: ativo, preço de entrada, target, stop | ✅ Já existe |
| 4 | Exit determinado pelo target/stop do sinal BUY | ✅ Já existe |
| 5 | Filtro por tipo removido ou fixo em BUY | ✅ Implementável |

---

## 3. Decisões de Design

| Decisão | Justificativa |
|---------|---------------|
| Remover dropdown tipo | Simplicidade — usuário não escolhe mais |
| Badge BUY fixo verde | Clareza visual,对齐 com card #53 |
| Mostrar entrada explícita | Facilita leitura do trade setup |
| Sem mudança no backend | Dados já existem, trabalho é só de UI |

---

## 4. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Usuário precisa de SELL/HOLD | Decisão de produto: focar apenas em BUY |
| Backend retorna mais que BUY | Frontend filtra no frontend se necessário |
| Breaking change | API não muda, só UI |

---

## 5. Estimativa

- **Complexidade:** Baixa (apenas remoções e ajustes de UI)
- **Tempo estimado:** 2–4 horas
- **Files afetados:** FilterBar, SignalCard, SignalList (frontend)
- **Files NÃO afetados:** Backend, APIs, banco de dados

---

## 6. Checks

- [x] Proposal completo e claro
- [x] Design com protótipo HTML
- [x] Tasks detalhadas e realistas
- [x] Critérios de aceite definidos
- [x] Sem mudanças de backend necessárias
- [x] Escopo bem definido

---

## 7. Próximo Passo

Enviar para DESIGN para revisão de UI e protótipo.

---

## 8. Notas para DESIGN

1. Focar na simplicidade — menos opções, menos ruído
2. Badge BUY verde deve ser visível mas não dominante
3. Campo "Entrada" deve ficar claro — é o preço de entrada na operação
4. Empty state deve ser amigável quando não há sinais BUY

