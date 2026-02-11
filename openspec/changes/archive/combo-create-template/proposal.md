---
spec: openspec.v1
id: combo-create-template
title: Criar método create_template no ComboService
status: draft
owner: Alan
created_at: 2026-02-11
updated_at: 2026-02-11
---

# 0) One-liner
Adicionar create_template no ComboService para gerar templates a partir de strategy_draft e eliminar falhas seed_template_missing.

# 1) Context
- Problem: o fluxo upstream falha ao converter strategy_draft porque ComboService não possui create_template.
- Why now: logs recentes mostram erro recorrente `strategy_draft_conversion_error` e `seed_template_missing`.
- Constraints: manter compatibilidade com templates existentes e banco atual.

# 2) Goal
## In scope
- Implementar método `create_template` no ComboService.
- Ajustar o fluxo que chama `create_template` para usar a nova implementação.
- Garantir fallback seguro quando o draft não puder gerar template.

## Out of scope
- Mudanças de UI/UX.
- Alterações no schema do banco além do necessário para salvar template.

# 3) User stories
- Como usuário do Lab, quero que a estratégia aprovada gere um seed template automaticamente, para seguir para execução sem erros.

# 4) UX / UI
- Entry points: aprovação do upstream.
- States:
  - Loading
  - Error (mensagem clara se falhar)
- Copy (PT-BR): não altera.

# 5) API / Contracts
## Backend endpoints
- Sem novas rotas.

## Security
- Auth: sem mudanças.
- Rate limits: sem mudanças.

# 6) Data model changes
- DB: reusar tabela `combo_templates`.
- Migrations: nenhuma.

# 7) VALIDATE (mandatory)
## Proposal link
- Proposal URL (filled after viewer exists): http://31.97.92.212:5173/openspec/changes/combo-create-template/proposal
- Status: draft → validated → approved → implemented

# 8) Acceptance criteria (Definition of Done)
- [ ] `ComboService.create_template` existe e é usado no fluxo de conversão.
- [ ] Um strategy_draft válido gera template salvo e retorna metadados consistentes.
- [ ] Erros de conversão são tratados com mensagem clara e sem `seed_template_missing` indevido.

# 9) Test plan
## Automated
- [ ] Teste unitário simples para `create_template` (ou teste de serviço).

## Manual smoke
1. Aprovar upstream com strategy_draft.
2. Verificar que o seed template foi criado e o run avança.

# 10) Implementation plan
- Step 1: mapear formato de strategy_draft → template_data.
- Step 2: implementar `create_template` no ComboService.
- Step 3: ajustar chamadas atuais para usar o método.
- Step 4: adicionar testes.

# 11) Rollout / rollback
- Rollout: deploy padrão.
- Rollback: reverter commit.

# 12) USER TEST (mandatory)
- Test URL(s): /lab
- What to test (smoke steps): rodar fluxo upstream até execução.
- Result:
  - [ ] Alan confirmed: OK

# 13) Notes / open questions
- Precisamos confirmar o mapeamento de indicadores do draft para template_data.
