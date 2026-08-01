## Context

- Card: [#355](https://github.com/oalansilva/crypto/issues/355)
- Branch: `change-355-remove-internal-kanban`
- Board operacional oficial: GitHub Project 1 — `https://github.com/users/oalansilva/projects/1/views/1`
- Superfície a remover: `https://dev.criptofarol.com.br/kanban` (`KanbanPage`)
- `#354` (bypass de design no Kanban interno) foi **Cancelado**; este card substitui o problema real (existência da página)
- **UI impact: affected** — remoção de tela existente; protótipo parte do shell atual e mostra ausência do board interno
- Base do sistema: shell autenticado (`AppNav` 224px + header workspace), rota atual `/kanban` (`KanbanPage`)

Hoje:
- Rota SPA `/kanban` renderiza board interno completo (colunas, drag-drop, drawer, comentários)
- Nav principal **não** lista Kanban (acesso por URL/bookmark)
- `Layout` usa `page-shell-wide` só em `/kanban`
- APIs `/api/workflow/kanban/*` alimentam a página **e** o snapshot de changes na `HomePage`
- Specs `kanban` / `mobile-kanban-ui` ainda exigem UI board no app

## Goals / Non-Goals

**Goals:**
- Eliminar a UI de board interno `/kanban` do produto
- Deixar explícito que o board operacional é só o GitHub Project 1
- Manter contratos de dados necessários para Home/agents
- Ajustar testes/snapshots da superfície removida
- Passar Design → Aprovação → Pronto para Dev antes de `/opsx:apply`

**Non-Goals:**
- Alterar colunas/campos do GitHub Project 1
- Remover ou renomear `/api/workflow/kanban/*` neste card
- Card #353 (Admin Backfill)
- Reescrever workflow DB / stage gates

## Decisions

1. **Remover página + rota; bookmark `/kanban` redireciona para `/monitor`**
   - Alternativa: 404 vazio no shell — pior UX para bookmarks.
   - Alternativa: página stub “use o Project 1” — ainda é superfície paralela; Alan quer ausência.
   - Escolha: `Navigate to="/monitor" replace` (ou equivalente) sem renderizar `KanbanPage`.

2. **Manter APIs `/api/workflow/kanban/*`**
   - Home e automação ainda consomem listagem/tasks/comments.
   - Remoção de API seria breaking maior e fora do pedido (“página não deveria existir”).
   - Documentar no OpenSpec; card futuro se Alan quiser descontinuar o prefixo.

3. **Remover testes E2E da UI Kanban; retirar cenários/snapshots visuais de `/kanban`**
   - Mantém mocks de API só onde Home/visual homepage ainda precisam.

4. **CSS `.kanban-page` e wide-shell**
   - Remover usos mortos com a página; limpeza mínima sem refatorar o design system.

## Risks / Trade-offs

- [Bookmark antigo `/kanban`] → Mitigação: redirect para `/monitor`.
- [Confusão “API kanban ainda existe”] → Mitigação: decisão explícita neste design/proposal; UI ausente.
- [Home ainda mostra changes via API kanban] → Aceito: não é board; é snapshot. Fora de escopo mudar Home neste card.
- [Specs antigas exigem UI] → Mitigação: deltas REMOVED/MODIFIED em `kanban` e `mobile-kanban-ui`.

## Migration Plan

1. Design aprovado por Alan (`Pronto para Dev`).
2. Aplicar remoção de UI + redirect + testes + docs/specs.
3. PR → `develop`, QA visual (baselines kanban removidos/atualizados), `./restart`.
4. Rollback: restaurar rota/`KanbanPage` do commit anterior se necessário.

## Open Questions

- Nenhuma bloqueante. Remoção do prefixo API fica para card futuro se Alan pedir.

## Prototype

- **URL HTTP navegável:** `https://dev.criptofarol.com.br/prototypes/card-355-remove-internal-kanban/`
- **Caminho versionado:** `frontend/public/prototypes/card-355-remove-internal-kanban/index.html`
- **Escopo:** desktop + mobile
- **Base:** shell autenticado atual + simulação da rota `/kanban` (Antes = board interno; Depois = redirect/ausência + nota Project 1)
- **Delta:** board interno ausente; nav sem item Kanban (já é o estado real); mensagem de destino operacional no Project 1
- **Toggle:** Antes / Depois

## Prototype Validation

- **URL servida:** `https://dev.criptofarol.com.br/prototypes/card-355-remove-internal-kanban/`
- **Ferramenta:** Playwright Chromium (headless) — desktop 1440×900 + mobile 390×844
- **Estado padrão (Depois):** `#kanban-view` hidden; `#monitor-view` visible; URL simulada `/monitor`
- **Interação:** toggle Antes → board `#kanban-heading` visible + URL `/kanban`; Depois → board hidden novamente
- **Asserts (todos ok):**
  - nav principal sem item “Kanban” (count=0)
  - Depois: board ausente/invisível; Monitor visível
  - Antes: board visível com heading Kanban
  - link Project 1 presente no Depois
  - sem `pageerror` / console error
- **Evidência local:** `/tmp/card-355-prototype-validation.json`, `/tmp/card-355-proto-desktop.png`, `/tmp/card-355-proto-mobile.png`
- **Resultado:** PASS

## Design Critique

- **Fidelidade:** shell `AppNav` 224px + tokens `--bg-*` / `--accent-primary` / Inter; nav real sem item Kanban (como no produto); delta = ausência do board em `/kanban` + redirect `/monitor`.
- **Produto:** remove board paralelo; aponta Project 1; APIs mantidas para Home/agents — coerente com escopo.
- **UX:** Antes/Depois claros; bookmark tratado com redirect; sem stub de “use o Project” como página permanente.
- **A11y:** toggle com `aria-pressed`; heading/list labels no mock Antes; link Project 1 com texto legível.
- **Responsividade:** desktop + mobile validados no browser.
- **Estados:** default Depois; Antes/Depois cobertos. Loading/erro N/A (remoção).
- **Achados bloqueantes:** nenhum (corrigidos antes do PASS).
- **Pendências não bloqueantes:** Home ainda consome API kanban (fora de escopo); limpeza/renomeação de API em card futuro.
- **Design Agent verdict: PASS**
