# Tasks — Card #92

## Mudança: Unificar Sinais — Um Sinal Consolidado por Ativo

---

## DEV Tasks

- [x] **1. Levantar estrutura de dados de cada fonte**
  
  Documentar formato dos sinais de: AI Dashboard, On-chain, Signals.
  
  **Critério de Aceite:** Estrutura de cada fonte documentada

  Resultado deste turno:
  - Contratos reais registrados em `design.md` na seção `3.1 Contratos Reais das Fontes`
  - Mapeamento inicial de normalização registrado em `design.md` na seção `3.2 Normalização Necessária para o Sinal Unificado`

- [x] **2. Definir lógica de consolidação**
  
  Decidir como combinar três sinais em um (voting, weighted, etc).
  
  **Critério de Aceite:** Lógica documentada e approved por Alan

- [x] **3. Criar API de consolidação**
  
  Endpoint que agrega sinais das três fontes em um sinal único.
  
  **Critério de Aceite:** API retorna um sinal consolidado por ativo

- [x] **4. Implementar display de sinal único**
  
  Mostrar um sinal por ativo na interface, não três.
  
  **Critério de Aceite:** BTC = 1 sinal, não 3 sinais separados

- [x] **5. Implementar indicador de direção/força**
  
  Sinal pode ser: Compra Forte, Compra, Neutro, Venda, Venda Forte.
  
  **Critério de Aceite:** Cada ativo tem indicador claro de direção

- [x] **6. Implementar breakdown por fonte (opcional)**
  
  Opcional: hover/tap mostra quais fontes contribuíram.
  
  **Critério de Aceite:** Se implementado, funciona corretamente

- [x] **7. Tratar sinais conflitantes**
  
  O que fazer quando fontes discordam fortemente?
  
  **Critério de Aceite:** Lógica de consolidação define resultado mesmo com conflito

- [ ] **8. Testar performance**
  
  Garantir que busca de 3 fontes não afeta performance.
  
  **Critério de Aceite:** View carrega em tempo aceitável

---

## QA Tasks

- [ ] **9. Validar que há um sinal por ativo**
  
  BTC, ETH, etc — cada um tem exatamente 1 sinal consolidado.
  
  **Critério de Aceite:** Não há múltiplos sinais para o mesmo ativo

- [ ] **10. Validar indicador de direção**
  
  Sinais mostram direção correta (Compra/Venda/Neutro).
  
  **Critério de Aceite:** Direção corresponde à lógica de consolidação

- [ ] **11. Validar breakdown (se implementado)**
  
  Se mostrar contribuição por fonte, está correto.
  
  **Critério de Aceite:** Breakdown corresponde aos dados reais

- [ ] **12. Testar sinais conflitantes**
  
  Quando fontes discordam, consolidação ainda funciona.
  
  **Critério de Aceite:** Resultado é determinístico

- [ ] **13. Testar mobile**
  
  View consolidada funciona em mobile.
  
  **Critério de Aceite:** Layout responsivo, funcional em mobile

---

## Design Tasks (DESIGN)

- [x] 14. Criar protótipo UI**
  
  **⚠️ OBRIGATÓRIO** — Criar protótipo em `prototype/prototype.html` ou `prototype.html`.
  
  **Critério de Aceite:** Protótipo mostra UM sinal por ativo, não três

---

## Notas

- **⚠️ Prototype obrigatório** — UI complexa precisa de validação visual antes de implementar
- **Dependência:** DESIGN cria protótipo antes de Alan approval
- **ICE:** 224 (Impact: 8, Confidence: 7, Ease: 4)
- **Scope change:** Não mostrar sinais separados por fonte — apenas sinal consolidado
