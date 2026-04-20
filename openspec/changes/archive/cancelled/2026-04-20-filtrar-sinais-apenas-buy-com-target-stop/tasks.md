# Tasks: Filtrar Sinais — Apenas BUY com Target e Stop

**Card:** #68  
**change_id:** `filtrar-sinais-apenas-buy-com-target-stop`  
**Estágio:** PO → DESIGN

---

## 1. Backend (Nenhuma mudança necessária)

- [x] **1.1** API `/signals` já retorna sinais BUY com entry_price, target_price, stop_loss (Card #53)
- [x] **1.2** API `/signals/latest` já suporta filtro `type=BUY`
- [x] **1.3** signal_history table já tem campos: type, entry_price, target_price, stop_loss

---

## 2. Frontend — FilterBar

- [ ] **2.1** Remover dropdown "Tipo" do componente FilterBar (ou desabilitar e fixar em BUY)
- [ ] **2.2** Garantir que todas as chamadas à API `/signals` incluam `type=BUY` (hardcoded no componente de sinais)
- [ ] **2.3** Garantir que `/signals/latest` também seja chamado com `type=BUY`

---

## 3. Frontend — SignalCard

- [ ] **3.1** Remover badge colorido dinâmico (BUY=verde, SELL=vermelho, HOLD=cinza)
- [ ] **3.2** Fixar badge verde com texto "BUY" em todos os cards
- [ ] **3.3** Garantir que campo `entry_price` está sendo exibido no card (se disponível no response)
- [ ] **3.4** Garantir que campos `target_price` e `stop_loss` estão sendo exibidos corretamente

---

## 4. Frontend — SignalList

- [ ] **4.1** Verificar se a lista de sinais filtra corretamente apenas BUY (mesmo se API retornar outros tipos)
- [ ] **4.2** Atualizar empty state: "Nenhum sinal BUY encontrado" (não mais "Nenhum sinal encontrado")
- [ ] **4.3** Garantir que filtros por ativo e confidence continuam funcionando

---

## 5. Frontend — RiskProfileSelector

- [ ] **5.1** Verificar que RiskProfileSelector continua funcionando (sem mudança necessária)

---

## 6. Frontend — Disclaimer

- [ ] **6.1** Verificar que DisclaimerBanner continua visível (sem mudança necessária)

---

## 7. Testes

- [ ] **7.1** Testar FilterBar: dropdown tipo não deve aparecer ou deve estar desabilitado
- [ ] **7.2** Testar SignalCard: todos os cards devem mostrar badge BUY verde
- [ ] **7.3** Testar empty state: quando não há sinais BUY, mostrar mensagem apropriada
- [ ] **7.4** Testar filtros: ativo e confidence mínima devem funcionar
- [ ] **7.5** Verificar que SELL/HOLD não aparecem em nenhuma parte da UI de sinais

---

## 8. Documentação

- [ ] **8.1** Atualizar README ou nota do Card #53 referenciando Card #68 como mudança de UI

---

## Dependências

- Card #53 (sinais-de-trading-buy-sell-hold) — implementação base
- Sem novas dependências de API ou backend

---

## Critérios de Done

- [ ] Dropdown "Tipo" removido ou desabilitado na FilterBar
- [ ] Badge BUY verde fixo em todos os SignalCards
- [ ] Campo entry_price visível no card
- [ ] Empty state atualizado para "Nenhum sinal BUY encontrado"
- [ ] Nenhum SELL ou HOLD aparece na UI
- [ ] Filtros por ativo e confidence funcionam
- [ ] Disclaimer visível
- [ ] Testes passando
