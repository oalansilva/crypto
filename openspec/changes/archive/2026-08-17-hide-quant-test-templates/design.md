# Design: Excluir templates de teste Quant e favoritos órfãos

## Context

A tela `/combo/select` lista templates via `GET /api/combos/templates` → `ComboService.list_templates()`. Existem 16 templates `quant_btc_1d_*` no banco (gerados por scripts de descoberta dos cards 261/262/277) e 10 favoritos do Monitor que os referenciam. Alan solicitou (2026-08-13): **excluir fisicamente** templates e favoritos — limpeza completa da descoberta de teste, não apenas ocultação da listagem.

UI impact: **none** (exclusão de dados; nenhuma superfície visual nova ou alterada — a tela apenas deixa de receber os itens).

## Goals / Non-Goals

**Goals**
- Excluir os 16 templates `quant_*` de `combo_templates`.
- Excluir os 10 favoritos que referenciam templates `quant_*` (sem órfãos no Monitor).
- Preservar evidência da deleção (backup de auditoria) antes de excluir.

**Non-Goals**
- Não alterar otimizador, batch, meta endpoints, Monitor ou frontend.
- Não excluir templates/favoritos não-Quant.

## Decisions

### D1 — Exclusão física em rotina única (script de manutenção)
Script executado uma vez (via venv, com banco DEV/PROD) que:
1. Grava backup JSON dos 16 templates e 10 favoritos afetados.
2. Deleta favoritos com `strategy_name` em templates `quant_*`.
3. Deleta templates com nome `quant_*` (case-insensitive).
4. Registra resumo (deletados, ids) em log.
- Alternativa: filtro na listagem (ocultar) — rejeitado por Alan (quer exclusão física).
- Razão: limpeza de dados de teste com trilha de auditoria; sem mudança de runtime.

### D2 — Sem mudança de schema/API contract
`TemplateListResponse` permanece igual; a resposta simplesmente não contém mais os templates (excluídos).

## Risks / Trade-offs

- [Favorito futuro criado com template quant_*] → Mitigação: templates não existem mais; criação exigiria template existente.
- [Perda irreversível] → Mitigação: backup JSON antes da deleção + revisão de Alan (já aprovada).

## Migration Plan

Nenhuma migration de schema. Exclusão de dados via script com backup. Rollback: restaurar do backup JSON se necessário.

## Prototype

**N/A** — `UI impact: none` (exclusão de dados; nenhuma superfície visual nova/alterada).

## Impeccable

- Brief/Critique/Audit/Trace: N/A — sem superfície visual (justificativa: exclusão de dados de teste; a tela existente apenas deixa de receber itens).

## Design Critique

- **Produto**: remove definitivamente o lixo de templates de teste e favoritos órfãos — decisão explícita de Alan, reversível via backup.
- **UX**: sem mudança visual; tela menos poluída; Monitor sem estratégias órfãs.
- **Acessibilidade/Responsividade/Theming**: N/A (sem UI).
- **Estados**: listagem sem templates quant_*; Monitor sem favoritos quant_* (nenhum órfão); backup gravado antes da deleção.
- **Riscos**: perda de dados mitigada por backup + aprovação de Alan.

**Design Agent verdict: PASS** — `UI impact: none`, exclusão física com backup de auditoria conforme solicitação de Alan; verificação pós-exclusão (listagem e Monitor) planejada. Aprovação humana (`Aprovação de Design -> Pronto para Dev`) pertence a Alan.
