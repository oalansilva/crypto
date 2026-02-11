# Design: Trader Conversa Fluida

**Change:** trader-conversation-flow  
**Author:** amigoalan  
**Date:** 2026-02-10

---

## 🏗️ Arquitetura Atual

- Upstream decide “approved” quando symbol/timeframe preenchidos
- Draft aparece automaticamente após aprovação
- Perguntas adicionais podem ficar travadas por status

---

## 🎯 Arquitetura Proposta

- **Trader controla readiness**: só define draft pronto quando achar necessário
- **Upstream continua em chat** até `ready_for_user_review=true`
- **Status permanece `needs_user_input`** enquanto Trader está perguntando

---

## 📂 Componentes Afetados

### `backend/app/routes/lab.py`

**Mudanças principais:**

1. **Gating do status**
   - Se `ready_for_user_review=false`, manter `needs_user_input`
   - Mesmo com contract aprovado

2. **Persistência de perguntas**
   - Trader pode continuar perguntando após contract aprovado
   - UI mostra como conversa normal

---

## 🔄 Fluxo

```
User → Trader
   ↕ (quantas perguntas quiser)
Trader ready_for_user_review=true
   ↓
Draft aparece → User aprova
```

---

## 🧪 Testes

- Cenário com perguntas extras
- Draft não aparece até Trader sinalizar
- Status permanece `needs_user_input`
