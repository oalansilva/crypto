# Design: Lab - Persistência Condicional de Templates

## Visão Geral

O Lab atualmente salva templates em `combo_templates` durante o fluxo de desenvolvimento. Precisamos separar:
- **Dados temporários da run**: Mantidos em `lab_runs/` (logs/memória)
- **Templates aprovados**: Persistidos em `combo_templates` (banco permanente)

## Componentes

### 1. Lab Runner (Backend)
**Arquivo**: `backend/app/lab/runner.py` ou similar

**Mudança**: Remover chamadas a `save_combo_template()` durante geração de candidatos.

**Fluxo atual (problemático)**:
```
Gerar candidato → Salvar em combo_templates → Aguardar aprovação
```

**Fluxo novo (correto)**:
```
Gerar candidato → Guardar em memória/run log → Aguardar aprovação → [Se aprovado] Salvar em combo_templates
```

### 2. API de Aprovação (Backend)
**Arquivo**: Endpoint de aprovação do Trader

**Mudança**: Adicionar lógica de persistência no momento da aprovação.

**Nova lógica**:
```python
@router.post("/lab/{run_id}/approve")
def approve_strategy(run_id: str, ...):
    # 1. Recuperar dados da run
    run_data = get_lab_run(run_id)
    
    # 2. Criar template no banco (só aqui!)
    template = ComboTemplate(
        name=generate_template_name(run_data),
        description=run_data.description,
        template_data=run_data.template_data,
        ...
    )
    db.add(template)
    db.commit()
    
    # 3. Marcar run como aprovada
    run_data.status = "approved"
```

### 3. Rejeição (Backend)
**Mudança**: Simplesmente não fazer nada (não criar template).

```python
@router.post("/lab/{run_id}/reject")
def reject_strategy(run_id: str, ...):
    # Apenas marcar como rejeitada - sem persistência de template
    run_data.status = "rejected"
    # NENHUM template é criado!
```

### 4. UI - Tela de Review do Trader
**Arquivo**: `frontend/src/pages/LabReviewPage.tsx` ou similar

**Mudança**: Garantir que os botões "Aprovar"/"Rejeitar" chamem as APIs corretas.

## Modelo de Dados

### Tabela `combo_templates`
Só contém templates aprovados. Nunca contém drafts/candidatos.

### Tabela/Lóg `lab_runs`
Mantém todo o histórico de desenvolvimento (incluindo rejeitados).

## Pontos de Integração

1. **Lab Runner**: Remover `save_template_to_db()` do fluxo de candidato
2. **API Approve**: Adicionar `create_template_in_db()` 
3. **API Reject**: Garantir que não chama nenhum save de template
4. **Cleanup**: Opcionalmente remover templates "lab_" existentes (já feito!)
