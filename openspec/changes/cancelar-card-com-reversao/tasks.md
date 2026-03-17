# Tasks: Cancelar card com reversão

## Tasks

### 1. Backend - Endpoint de reativação

**Arquivo:** `backend/app/routes/workflow.py`

- [ ] Criar endpoint `POST /api/workflow/changes/{change_id}/reactivate`
- [ ] Implementar lógica para mover card de archive de volta para Pending
- [ ] Implementar lógica para remover card da pasta archive ( filesystem)
- [ ] Retornar status atualizado do card

**Estimativa:** 2h

---

### 2. Frontend - Botão de reativação

**Arquivo:** `frontend/src/pages/KanbanPage.tsx`

- [ ] Substituir botão "Já cancelado" por "Reativar card" na UI
- [ ] Adicionar mutation para chamar endpoint de reativação
- [ ] Adicionar toast de sucesso/erro
- [ ] Atualizar estado local após reativação

**Estimativa:** 1h

---

### 3. Testes

**Arquivo:** `backend/tests/`, `frontend/playwright/`

- [ ] Teste unitário do endpoint de reativação
- [ ] Teste E2E: arquivar card -> reativar card -> verificar que aparece em Pending

**Estimativa:** 1h

---

## Total Estimado: 4h
