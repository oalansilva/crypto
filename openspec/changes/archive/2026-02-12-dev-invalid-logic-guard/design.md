# Design: Guard de Lógica Inválida (Dev)

## Overview
Adicionar um preflight determinístico que valida `entry_logic` e `exit_logic` antes do backtest. Se inválido, o Dev corrige (reescreve para booleano válido) e re-tenta automaticamente, com limite de tentativas e trace de auditoria.

## Componentes

### 1) Pré-validação de lógica
- Nova função `validate_logic(template_data) -> {ok, errors}` em `backend/app/routes/lab.py` ou helper dedicado.
- Usa o mesmo parser/validador do motor (ou wrapper leve) para detectar tokens inválidos antes do backtest.

### 2) Auto-correção
- Reutilizar `_apply_dev_adjustments(...)` e expandir para:
  - Converter frases comuns para booleano (ex.: “ema50 acima da ema200” → `ema50 > ema200`)
  - Remover palavras não suportadas (ex.: “quando”, “cruza”, “pullback”)
  - Reescrever em expressão padrão `AND/OR` com colunas válidas
- Persistir `dev_logic_correction` no trace com `errors` e `changes`.

### 3) Fluxo
- Antes de `_run_backtest_job`, executar preflight.
- Se `ok == false`:
  - aplicar auto-correção
  - re-validar
  - se corrigido → backtest
  - se ainda inválido após N tentativas → marcar erro controlado e retornar

## Observabilidade
- Trace types:
  - `logic_preflight_failed` (errors)
  - `logic_correction_applied` (changes, attempt)
  - `logic_correction_failed` (errors, attempt)

## Limites
- `max_logic_corrections` = 2 (configurável via input ou constante)
