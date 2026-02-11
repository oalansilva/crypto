# Tasks: Trader Conversa Fluida

**Change:** trader-conversation-flow  
**Estimated:** ~4h  
**Priority:** high

---

## ✅ Tarefas

### 1. Ajustar gating do status upstream
- [ ] Em `lab.py`, só marcar `ready_for_review` quando `ready_for_user_review=true`
- [ ] Caso contrário, manter `needs_user_input`

### 2. Permitir perguntas adicionais
- [ ] Não bloquear chat após contract aprovado
- [ ] Persistir perguntas extras no upstream

### 3. Atualizar testes
- [ ] Adicionar teste para perguntas extras
- [ ] Garantir status correto

---

## ✅ Critérios de Aceite

- Trader pode perguntar N vezes
- Draft só aparece quando Trader sinaliza
- UI não trava em conversa
