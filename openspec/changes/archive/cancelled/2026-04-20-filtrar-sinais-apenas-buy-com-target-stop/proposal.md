# Proposal: Filtrar Sinais — Apenas BUY com Target e Stop

**Card:** #68  
**change_id:** `filtrar-sinais-apenas-buy-com-target-stop`  
**Estágio:** PO  
**User Story:** Como trader, quero ver apenas sinais BUY com entrada, target e stop para simplificar a tela de sinais e focar em oportunidades de compra.

---

## 1. User Story & Objetivos

**User Story:**
> Como trader, quero ver apenas sinais BUY com entrada, target (lucro) e stop (prejuízo) para simplificar a tela de sinais e focar em oportunidades de compra.

**Critérios de aceite:**
- Apenas sinais BUY são exibidos na interface
- Sinais SELL e HOLD são removidos da exibição
- Cada sinal BUY mostra: ativo, preço de entrada, target (lucro), stop (prejuízo)
- Exit é determinado pelo target/stop do próprio sinal BUY
- Filtro por tipo é removido ou desabilitado (sempre BUY)

**Decisão-chave:** O Card #53 já implementou o pipeline completo de sinais com BUY/SELL/HOLD. O Card #68 é apenas uma mudança de filtragem/UI — os dados já existem no banco (signal_history table). O trabalho é remover SELL/HOLD da exibição e focar em BUY.

---

## 2. Decisões Definidas

| Item | Decisão |
|------|---------|
| Dados | Já existem no banco (Card #53 implementou) |
| Escopo | Apenas filtragem e ajuste de UI |
| Backend | Sem mudanças — dados já corretos |
| Frontend | Remover SELL/HOLD da UI, filtrar API por BUY |

---

## 3. Escopo

### Dentro do escopo
- [ ] Remover tipo SELL e HOLD do dropdown de filtros
- [ ] Frontend sempre envia `type=BUY` na API
- [ ] Backend filtra sinais BUY apenas (opcional: forçar no backend também)
- [ ] Remover badges coloridos de SELL/HOLD da UI
- [ ] Simplificar SignalCard para mostrar apenas BUY

### Fora do escopo
- Alterar lógica de geração de sinais
- Alterar modelo LSTM/RandomForest
- Alterar indicadores (RSI/MACD/Bollinger)

---

## 4. Arquitetura (Mudanças Mínimas)

```
┌─────────────────────────────────────────────────┐
│  Frontend (mudança apenas no filter/display)   │
│  - FilterBar: remove SELL/HOLD do dropdown     │
│  - SignalCard: mostra apenas BUY (badge fixo)  │
│  - API call: GET /signals?type=BUY (fixo)      │
└─────────────────────────────────────────────────┘
                           │
                     ┌─────▼─────┐
                     │ Backend   │
                     │ (sem mud) │
                     └───────────┘
```

**Mudanças:**
- Frontend: 2–3 componentes (FilterBar, SignalList, possivelmente API call)
- Backend: nenhuma mudança necessária (dados já existem)

---

## 5. API Endpoints (Sem Mudança)

Os endpoints existentes já retornam todos os tipos. A mudança é no frontend que filtra/apenas solicita BUY.

| Método | Endpoint | Mudança |
|--------|----------|---------|
| GET | `/signals` | Frontend passa `type=BUY` sempre |
| GET | `/signals/latest` | Frontend passa `type=BUY` sempre |
| GET | `/signals/{id}` | Sem mudança (detalhe) |

**Mudança no frontend (request):**
```json
// Antes:
GET /signals?type=BUY&confidence_min=70

// Depois:
GET /signals?type=BUY&confidence_min=70  // (já era BUY, só remove options)
```

---

## 6. Custos

| Recurso | Custo |
|---------|-------|
| Backend | $0 (sem mudanças) |
| Frontend | $0 (apenas remoção de opções) |
| Testes | $0 |
| **Total** | **$0** |

---

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Usuário quer ver SELL/HOLD | Decisão de produto: focar apenas em BUY |
| Backend não filtra por tipo | Frontend sempre passa `type=BUY` |
| Breaking change para outros consumidores | API não muda, só o frontend filtra |

---

## 8. Próximo Passo

Passar para DESIGN para especificação de UI simplificada.
