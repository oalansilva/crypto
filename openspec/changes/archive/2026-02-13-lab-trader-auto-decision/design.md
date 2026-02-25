# Design: lab-trader-auto-decision

## Overview

Remover o gargalo manual de aprovação do trader, permitindo que o agente LLM "trader" avalie o resultado da estratégia e decida automaticamente. Quando aprovado, salvar estratégia e template nos favoritos sem intervenção humana.

## Components

### 1. lab_graph.py - _trader_validation_node

**Alterações:**
- Garantir que o nó execute automaticamente sem depender de confirmação externa
- O agente trader LLM recebe contexto completo (strategy_draft, metrics, template)
- Retorna veredito em formato JSON estruturado

**Fluxo:**
```
implementation_complete = true
  ↓
trader_validation_node (automático)
  ↓
verdict ∈ {approved, rejected, needs_adjustment}
```

### 2. lab_graph.py - _after_trader_validation

**Alteração importante:**
- Se **approved**: 
  - Chamar função para salvar estratégia nos favoritos
  - Chamar função para salvar template
  - Ir para END (status: done)
- Se **rejected**: ir para END (status: rejected) sem salvar
- Se **needs_adjustment**: voltar para dev_implementation (com retry count)

### 3. lab_graph.py - Funções de salvamento

**Nova função ou integração existente:**
- `_save_strategy_to_favorites(run_id, strategy_data)` - salva estratégia aprovada
- `_save_template(run_id, template_data)` - salva template aprovado
- Estas funções devem ser chamadas automaticamente quando approved

### 4. lab.py - Remover needs_user_confirm

**Local:** Linhas ~2208-2210 e áreas que verificam `not outputs.get("trader_verdict")`

**Alteração:**
- Remover lógica que seta `needs_confirm = True` quando falta trader_verdict
- O trader_verdict será preenchido automaticamente pelo graph, não pelo humano

## Files Modified

1. `backend/app/services/lab_graph.py`
   - _trader_validation_node: garantir execução automática
   - _after_trader_validation: adicionar salvamento automático quando approved
   - Adicionar funções de salvamento ou integrar com existentes
   
2. `backend/app/routes/lab.py`
   - Remover verificação de trader_verdict faltante
   - Remover needs_user_confirm relacionado ao trader

## Flow Diagram

```
┌─────────────────┐
│  Implementation │
│    Complete     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Trader Validation│◄── LLM avalia resultado da estratégia
│   (Automático)   │
└────────┬────────┘
         │
    ┌────┴────┬─────────────┐
    ▼         ▼             ▼
┌───────┐ ┌────────┐ ┌──────────────┐
│Approved│ │Rejected│ │Needs Adjust  │
└───┬───┘ └────┬───┘ └──────┬───────┘
    │          │            │
    ▼          ▼            ▼
┌────────┐  ┌──────┐  ┌──────────────┐
│Save    │  │ Done │  │ Dev Impl     │
│Strategy│  │(no   │  │ (Retry)      │
│+Template│  │save) │  └──────────────┘
└───┬────┘  └──────┘
    │
    ▼
┌────────┐
│  Done  │
└────────┘
```

## Testing Strategy

1. Criar um Lab run com symbol/timeframe válidos
2. Verificar que após implementation, o trader_validation executa automaticamente
3. Confirmar que o veredito é retornado pelo LLM
4. Se approved: verificar que estratégia e template foram salvos nos favoritos
5. Se rejected: verificar que nada foi salvo
