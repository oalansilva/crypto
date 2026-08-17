# Tasks: Discovery selection redesign

## 1. Design gate

- [x] 1.1 Classify UI impact and preserve the current Discovery shell and non-selection surfaces.
- [x] 1.2 Shape the no-scroll workbench interaction and document alternatives, decisions, and risks.
- [x] 1.3 Build the navigable prototype at `frontend/public/prototypes/card-469-selection-redesign/index.html`.
- [x] 1.4 Run deterministic Impeccable detection and desktop/mobile browser assertions.
- [x] 1.5 Obtain independent Assessment A and Assessment B in separate `openai/gpt-5.6-sol` contexts (executados pela sessão principal via Task; PASS após fixes).
- [x] 1.6 Obtain Alan's design approval after the independent-critic blocker is resolved (aprovado em 2026-08-15).
- [x] 1.7 Remover o simulador "Estados críticos verificáveis" da tela de produção (ferramenta de QA; estados reais continuam com superfícies próprias de recuperação).
- [x] 1.8 Remover o mesmo bloco e sua lógica do shell aprovado `card-469-varredura-backtest` (embutido via iframe no protótipo novo), eliminando CSS/JS órfãos.

## 2. Frontend implementation — only after Pronto para Dev

- [x] 2.1 Extract a reusable catalog workbench component for Templates and Symbols (`SelectionWorkbench.tsx`).
- [x] 2.2 Connect real template/symbol catalog data, stable identifiers, categories, search, and bounded pagination.
- [x] 2.3 Implement manual selection plus whole-catalog selection with explicit exclusions.
- [x] 2.4 Keep edits transactional and synchronize applied arrays with the existing preflight request.
- [x] 2.5 Preserve draft-frozen, loading, empty, error, stale, over-limit, permission, history, active-sweep, and leaderboard behavior.
- [x] 2.6 Implement modal semantics, focus trap/restore, keyboard interaction, live regions, reduced-motion handling, and 44 × 44 px targets.

## 3. Validation

- [x] 3.1 Add focused component tests for search, pagination, counts, add/remove, all-plus-exceptions, apply, cancel, and invalid empty axes (coberto pelo spec Playwright do workbench).
- [x] 3.2 Add Playwright coverage at 1440 × 900 and 390 × 844 proving every option remains reachable without catalog scrolling.
- [x] 3.3 Validate no console/page errors, no mobile overflow, focus containment/restoration, and preflight recalculation.
- [ ] 3.4 Run the card's required OpenSpec, frontend, QA visual, integration, restart, and runtime gates.
- [x] 3.5 Desabilitar direção Short no configurador por enquanto (apenas Long roda), com aviso "em breve" no controle.
- [x] 3.6 Tratar 401 na discovery: parar o polling e exibir painel "Sessão expirada" com ação de recarregar, em vez de loop infinito de requisições e mensagem enganosa de "conexão interrompida".
