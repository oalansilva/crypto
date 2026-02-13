# Tasks: lab-trader-auto-decision

## Task 1: Atualizar _trader_validation_node em lab_graph.py

**File:** `backend/app/services/lab_graph.py`

**Actions:**
- [ ] Verificar que _trader_validation_node é chamado automaticamente após implementation
- [ ] Garantir que o prompt do trader inclua instrução clara para avaliar resultado da estratégia
- [ ] Validar que o parse do veredito funciona corretamente

**Validation:**
```bash
cd /root/.openclaw/workspace/crypto/backend
./.venv/bin/python -c "from app.services.lab_graph import _trader_validation_node; print('OK')"
```

## Task 2: Implementar salvamento automático quando approved

**File:** `backend/app/services/lab_graph.py`

**Actions:**
- [ ] Identificar funções existentes para salvar estratégia nos favoritos (ver _execute_strategy_save)
- [ ] Identificar funções existentes para salvar template
- [ ] No _after_trader_validation ou no final do graph, quando verdict == "approved":
  - [ ] Chamar função para salvar estratégia nos favoritos
  - [ ] Chamar função para salvar template
  - [ ] Logar no trace que foi salvo automaticamente

**Code pattern:**
```python
if verdict == "approved":
    # Salvar estratégia nos favoritos
    _save_strategy_to_favorites(run_id, strategy_data)
    # Salvar template
    _save_template(run_id, template_data)
    status = "done"
```

## Task 3: Remover needs_user_confirm de lab.py

**File:** `backend/app/routes/lab.py`

**Actions:**
- [ ] Localizar código que seta needs_confirm quando falta trader_verdict (~linha 2208)
- [ ] Remover essa lógica - o trader_verdict virá do LLM, não do humano
- [ ] Garantir que needs_user_confirm só seja usado para budget_limit, não para trader

**Code to modify:**
```python
# REMOVER ou MODIFICAR:
if not outputs.get("trader_verdict") or not outputs.get("validator_verdict"):
    needs_confirm = True
else:
    needs_confirm = False
```

## Task 4: Validar fluxo _after_trader_validation

**File:** `backend/app/services/lab_graph.py`

**Actions:**
- [ ] Verificar que approved → salva + vai para END
- [ ] Verificar que rejected → vai para END (sem salvar)
- [ ] Verificar que needs_adjustment → vai para dev_implementation (se retry < max)
- [ ] Verificar retry count incrementa corretamente

## Task 5: Testar fluxo end-to-end

**Actions:**
- [ ] Criar um Lab run via API
- [ ] Aguardar passar por implementation → trader_validation
- [ ] Confirmar que trader_validation executa sem needs_user_confirm
- [ ] Verificar que veredito é gerado pelo LLM
- [ ] Se approved: verificar que estratégia foi salva nos favoritos
- [ ] Se approved: verificar que template foi salvo

**Test command:**
```bash
cd /root/.openclaw/workspace/crypto
./backend/.venv/bin/python test_trader_auto_decision.py
```

## Done When

- [ ] Lab executa trader_validation sem parar para confirmação humana
- [ ] Agente trader avalia resultado da estratégia e retorna veredito via LLM
- [ ] Quando approved: estratégia salva nos favoritos automaticamente
- [ ] Quando approved: template salvo automaticamente
- [ ] Quando rejected: run finaliza sem salvar
- [ ] Quando needs_adjustment: volta para dev_implementation automaticamente
