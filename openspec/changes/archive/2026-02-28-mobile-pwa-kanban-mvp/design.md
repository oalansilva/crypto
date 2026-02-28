## Context

Objetivo: entregar um **MVP mobile (PWA)** para uso do **Kanban** no celular, com “cara de app” (standalone) e interação touch.

Restrição principal: **não mexer no layout do PC** por enquanto.

Stakeholders:
- Alan (aprovação / direção)
- PO/DESIGN (escopo + protótipo)
- DEV (implementação)
- QA (validação mobile + regressão desktop)

## Goals / Non-Goals

**Goals:**
- Melhorar a experiência de `/kanban` em telas pequenas (touch-first)
- Permitir instalação como PWA (manifest + ícones + standalone)
- Garantir que o Kanban desktop continue visualmente e funcionalmente igual

**Non-Goals:**
- Reestruturar o Kanban desktop
- Criar offline-first completo (cache sofisticado, sync, etc.) no MVP
- Refatorar arquitetura global de navegação (apenas o necessário para o Kanban mobile)

## Decisions

1. **Mobile-only UI via breakpoint (sem afetar desktop)**
   - Decisão: aplicar UI mobile-friendly apenas abaixo de um breakpoint (ex.: `max-width: 768px`) e/ou via classe/flag de layout.
   - Racional: garante que o desktop não muda e reduz risco de regressão.
   - Alternativas: criar rota separada (`/m/kanban`); rejeitada para MVP por aumentar complexidade e duplicar rotas.

2. **Prototype-first para a UI mobile do Kanban**
   - Decisão: DESIGN entregar um protótipo HTML/CSS do Kanban mobile antes do DEV codar.
   - Racional: acelera, reduz retrabalho e deixa claro o que “entra no MVP”.

3. **PWA mínimo (instalável + standalone)**
   - Decisão: implementar o mínimo necessário para instalação (manifest + ícones + start_url), evitando prometer offline robusto.
   - Racional: foco em valor rápido e menor risco.

## Risks / Trade-offs

- [CSS mobile vaza para desktop] → Mitigação: isolar estilos por breakpoint e/ou escopo do container do Kanban.
- [Fluxo de instalação PWA inconsistente entre iOS/Android] → Mitigação: documentar “como instalar” no QA checklist e testar nos navegadores principais.
- [Touch targets pequenos / drag & drop difícil] → Mitigação: aumentar área clicável, espaçamento e considerar interações alternativas (ex.: abrir card → ações) no MVP.

## Migration Plan

- Implementar UI mobile para `/kanban` sob breakpoint.
- Adicionar manifest + ícones.
- Rollback: reverter estilos mobile e remover links/registro PWA se necessário.

## Open Questions

- Quais interações do Kanban são obrigatórias no mobile MVP? (ex.: mover cards por drag, ou pode ser via ação “Mover para”?)
- Precisamos de um drawer/nav específico no Kanban mobile, ou o menu existente já atende?
- Lista mínima de dispositivos a validar: Android (Chrome) + iOS (Safari) — confirmar.
