## 1. PO + DESIGN Alignment

- [ ] 1.1 Confirmar escopo exato do MVP (o que entra / o que fica fora)
- [ ] 1.2 Definir as ações obrigatórias no mobile (ex.: abrir card, mover card, criar/editar, filtros)
- [ ] 1.3 Definir breakpoint e princípios de UI (tamanhos, espaçamentos, navegação)

## 2. DESIGN Prototype

- [ ] 2.1 Criar protótipo HTML/CSS do Kanban mobile (layout + estados principais)
- [ ] 2.2 Garantir touch targets e tipografia legível (mínimo 44px para áreas tocáveis quando aplicável)
- [ ] 2.3 Publicar protótipo em `frontend/public/prototypes/mobile-pwa-kanban-mvp/`

## 3. DEV Implementation (Frontend)

- [ ] 3.1 Implementar layout mobile para `/kanban` sem alterar o desktop (escopo + breakpoint)
- [ ] 3.2 Ajustar interações touch-first (tap/scroll/drag ou alternativa definida no escopo)
- [ ] 3.3 Validar navegação no Kanban mobile (drawer/menu/atalhos necessários)

## 4. PWA (Minimum)

- [ ] 4.1 Adicionar/ajustar `manifest.webmanifest` (name, short_name, icons, start_url)
- [ ] 4.2 Adicionar ícones PWA (set mínimo para Android + iOS)
- [ ] 4.3 Validar execução em modo standalone e acesso direto ao Kanban

## 5. QA + Acceptance

- [ ] 5.1 Testar fluxo de instalação PWA em Android (Chrome)
- [ ] 5.2 Testar fluxo de instalação PWA em iOS (Safari)
- [ ] 5.3 Rodar checklist de regressão no Kanban desktop (layout e ações)

> Note: Use relevant project skills under `.codex/skills` when applicable (frontend, tests, debugging).
