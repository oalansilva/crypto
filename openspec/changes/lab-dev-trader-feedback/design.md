# Design: lab-dev-trader-feedback

## Overview

Garantir que quando o Trader rejeita e solicita mudanças estruturais, o Dev Senior receba essas instruções explicitamente no contexto durante o retry, permitindo implementar mudanças reais em vez de apenas otimizar parâmetros.

## Components

### 1. lab_graph.py - _implementation_node

**Alterações:**
- Detectar quando é um retry (`dev_needs_retry=True`)
- Verificar se existe `trader_verdict` com `required_fixes`
- Extrair feedback do trader: `verdict`, `reasons`, `required_fixes`
- Construir mensagem customizada com o feedback
- Passar mensagem customizada no `_run_persona` para dev_senior

**Fluxo:**
```
implementation_started
  ↓
dev_needs_retry=True?
  ├─ NÃO → Chamar dev_senior com contexto normal
  └─ SIM → Extrair trader_verdict
            ↓
      Construir mensagem customizada
      "O Trader rejeitou e pediu: [lista de fixes]"
            ↓
      Chamar dev_senior com mensagem customizada
```

### 2. Nova função _build_dev_retry_message

**Purpose:** Construir mensagem para dev incluindo feedback do trader

**Input:**
- context: Dict com dados do run
- required_fixes: List[str] - lista de ajustes solicitados
- trader_reasons: str - motivos da rejeição

**Output:**
- Mensagem formatada para o dev

**Example:**
```
O Trader rejeitou a estratégia anterior pelos seguintes motivos:
- Sharpe holdout negativo
- Amostra insuficiente

AJUSTES REQUERIDOS (implemente no novo template):
1. Mudar estratégia de reversão para momentum
2. Adicionar filtro de volume > média 20
3. Aumentar período RSI para 14-21

Dados do contexto:
{context_json}

Gere um NOVO template de estratégia implementando os ajustes acima.
```

## Files Modified

1. `backend/app/services/lab_graph.py`
   - `_implementation_node`: detectar retry e passar mensagem customizada
   - Adicionar `_build_dev_retry_message` helper

## Flow Diagram

```
┌─────────────────┐
│  Implementation │
│    (normal)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Trader Validation│
│   → REJECTED    │
│   + required_fixes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ dev_needs_retry │
│     = True      │
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│ _build_dev_retry_message │
│  - Extrai trader_verdict  │
│  - Constroi mensagem      │
│  - Lista required_fixes   │
└────────┬─────────────────┘
         │
         ▼
┌─────────────────┐
│  Dev Senior     │
│ (com mensagem   │
│  customizada)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ NOVO template   │
│ (mudanças       │
│  estruturais)   │
└─────────────────┘
```

## Testing Strategy

1. Criar um Lab run que gere estratégia fraca no holdout
2. Aguardar Trader rejeitar com required_fixes
3. Verificar que no retry, Dev recebe mensagem com feedback
4. Validar que novo template implementa mudanças solicitadas
5. Verificar trace log: "dev_retry_with_trader_feedback"
