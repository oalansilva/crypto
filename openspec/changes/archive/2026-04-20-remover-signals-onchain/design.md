---
spec: openspec.v1
id: remover-signals-onchain
title: Design - Remover /signals/onchain
card: "#114"
change_id: remover-signals-onchain
stage: DESIGN
status: draft
owner: Alan
created_at: 2026-04-20
updated_at: 2026-04-20
---

# Design: Remover /signals/onchain

**Card:** #114  
**change_id:** `remover-signals-onchain`

---

## Step 1 — Required outputs

- **Domain:** remoção de capability existente em `signals`
- **Color world:** manter o produto atual, sem nova camada visual
- **Signature:** saída limpa, sem rota órfã, sem CTA residual, sem estado visual quebrado
- **Defaults to reject:** tela substituta improvisada, redirect temporário, banner explicativo permanente, redesign sem necessidade

## Step 2 — Proposal

### Direction

Não criar prototype. Tratar esta change como **remoção sem impacto de nova UX**.

### Rationale

O escopo aprovado pelo PO define remoção completa da capability `/signals/onchain`, sem substituição, sem redirect e sem redesign. No estágio DESIGN, a decisão correta é preservar a consistência visual do produto **eliminando os pontos de entrada** e deixando os fluxos adjacentes intactos.

### Explicit rejections

- Não criar nova tela vazia ou placeholder para `/signals/onchain`
- Não criar redirect para outra área de signals
- Não alterar arquitetura visual de menus além da retirada dos itens ligados à capability removida

## Step 3 — Implementation brief

### Intent

Garantir que DEV remova a capability de forma invisível para o restante da experiência, sem introduzir nova interface.

### Palette rationale

Sem alteração. A mudança é subtrativa.

### Depth and surfaces

Sem novas superfícies. Apenas remoção de rota, navegação, CTAs e referências visuais associadas.

### Typography

Sem alteração.

### Spacing system

Após remoção de cards, links ou atalhos, manter o espaçamento original dos componentes remanescentes, sem deixar lacunas ou alinhamentos quebrados.

## Decision

**Prototype não necessário.** Esta change não pede exploração visual nem definição de novo fluxo, apenas remoção consistente de elementos existentes.

## Visual QA notes

Validar após DEV:

- não existe item visual apontando para `/signals/onchain`
- menus e listas não ficam com gap, alinhamento quebrado ou heading órfão
- áreas adjacentes de `signals` continuam com hierarquia e espaçamento consistentes
- acesso direto à rota removida não expõe interface antiga

## Next step

Pronto para `@Alan` approval e depois handoff para `DEV`.
