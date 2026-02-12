# Change Proposal: Dev Template Notation (auto-correção)

**Status:** 🟡 draft  
**Created:** 2026-02-12  
**Author:** amigoalan (OpenClaw)  
**Priority:** high  
**Type:** enhancement

---

## Why

O Dev está gerando templates com **texto livre** em `entry_logic`/`exit_logic` e `stop_loss` como string, o que o engine **não interpreta**. Resultado: **0 trades** e backtests inválidos.

Precisamos garantir que o Dev **sempre use a notação esperada** (expressões booleanas simples) e, caso gere algo inválido, **detecte e corrija automaticamente** antes de retornar o template.

---

## 📋 Contexto

Exemplo real (run 14d382b3):
- `entry_logic`: "rsi14 cruza acima de 55" → **inválido**
- `exit_logic`: texto em português → **inválido**
- `stop_loss`: string → **inválido**

Isso causa **0 trades** e bloqueia a validação.

---

## 🎯 Objetivo

1. **Prompt do Dev** deve exigir notação correta do engine.
2. **Auto-checagem** do Dev: se gerar lógica inválida, corrigir.
3. Garantir que `stop_loss` seja **float**.

---

## ✅ Critérios de Aceite

1. Dev só retorna templates com `entry_logic`/`exit_logic` em sintaxe válida.
2. `stop_loss` sempre numérico.
3. Se houver erro de sintaxe, o Dev corrige antes de finalizar.

---

## 📝 Notas de Implementação

Ver `design.md` e `tasks.md`.
