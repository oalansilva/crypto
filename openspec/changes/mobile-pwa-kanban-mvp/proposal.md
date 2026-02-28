## Why

Hoje o Kanban é útil no desktop, mas no celular a experiência é ruim (layout pensado para PC, interações pequenas para touch, navegação pouco “app-like”). Isso atrasa o uso diário e reduz retenção.

Precisamos de um **MVP mobile (PWA)** focado **exclusivamente no Kanban**, instalável e confortável de usar no telefone, sem mexer no layout do PC.

## What Changes

- Tornar a rota **`/kanban` mobile-friendly** (touch-first, legibilidade, navegação simples)
- Adicionar suporte a **PWA instalável**:
  - `manifest.webmanifest` (nome, ícones, start_url)
  - modo **standalone** (feel de app)
  - assets básicos (ícones)
- Ajustes de UI **apenas em mobile** (não alterar layout do desktop/PC)

## Capabilities

### New Capabilities
- `mobile`: Um modo mobile (PWA) para o Kanban com layout e interações apropriadas para telefone, mantendo o desktop inalterado.

### Modified Capabilities
- (none)

## Impact

- Frontend: CSS/layout condicional por breakpoint (mobile) para `/kanban`.
- PWA: inclusão/ajuste de manifest + ícones e configuração de modo standalone.
- QA: testes manuais em iOS/Android (Chrome/Safari PWA install flow) + regressão no Kanban desktop.
