# Tasks: lab-dev-trader-feedback

## Task 1: Criar função _build_dev_retry_message

**File:** `backend/app/services/lab_graph.py`

**Actions:**
- [ ] Criar função auxiliar `_build_dev_retry_message(context, required_fixes, trader_reasons)`
- [ ] Formatar mensagem incluindo:
  - Cabeçalho indicando que é retry
  - Motivos da rejeição
  - Lista de ajustes requeridos numerados
  - Contexto completo em JSON
  - Instrução clara para gerar novo template

**Validation:**
```python
msg = _build_dev_retry_message(
    context={"symbol": "BTC/USDT"},
    required_fixes=["mudar para momentum", "adicionar filtro de volume"],
    trader_reasons="Sharpe negativo no holdout"
)
assert "mudar para momentum" in msg
assert "Sharpe negativo" in msg
```

## Task 2: Modificar _implementation_node para detectar retry

**File:** `backend/app/services/lab_graph.py`

**Actions:**
- [ ] Antes de chamar dev_senior, verificar `outputs.get("dev_needs_retry")`
- [ ] Se for retry e tiver `trader_verdict`:
  - [ ] Extrair `verdict`, `reasons`, `required_fixes` via `_parse_trader_verdict_payload`
  - [ ] Chamar `_build_dev_retry_message` para construir mensagem
  - [ ] Passar mensagem customizada no `_run_persona`
- [ ] Se não for retry: manter comportamento atual

**Code to modify:**
```python
# Existing code:
budget, outputs, ok = _run_persona(
    state=state,
    persona="dev_senior",
    output_key="dev_summary",
    system_prompt=DEV_SENIOR_PROMPT,
)

# New code:
if outputs.get("dev_needs_retry") and outputs.get("trader_verdict"):
    verdict, required_fixes = _parse_trader_verdict_payload(
        outputs.get("trader_verdict")
    )
    message = _build_dev_retry_message(
        context=state.get("context"),
        required_fixes=required_fixes,
        trader_reasons=verdict
    )
    budget, outputs, ok = _run_persona(
        state=state,
        persona="dev_senior", 
        output_key="dev_summary",
        system_prompt=DEV_SENIOR_PROMPT,
        message=message,  # Custom message
    )
else:
    # Normal flow
    budget, outputs, ok = _run_persona(...)
```

## Task 3: Validar fluxo _after_trader_validation

**File:** `backend/app/services/lab_graph.py`

**Actions:**
- [ ] Verificar que approved → salva + vai para END
- [ ] Verificar que rejected → vai para END (sem salvar)
- [ ] Verificar que needs_adjustment → vai para dev_implementation (se retry < max)
- [ ] Verificar retry count incrementa corretamente

## Task 4: Testar fluxo end-to-end

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
./backend/.venv/bin/python test_dev_trader_feedback.py
```

## Done When

- [ ] Quando Trader rejeita com required_fixes, Dev recebe essas instruções no retry
- [ ] Mensagem do Dev inclui feedback do Trader explicitamente
- [ ] Dev implementa mudanças estruturais quando solicitado
- [ ] Não apenas otimiza parâmetros existentes
- [ ] Trace log mostra "dev_retry_with_trader_feedback"
