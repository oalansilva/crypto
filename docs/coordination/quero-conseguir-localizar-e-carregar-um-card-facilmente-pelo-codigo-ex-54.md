# quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54

## Status
- PO: done
- DESIGN: done
- DEV: done
- QA: done
- Homologation: approved
- Archived: 2026-04-03 13:38 UTC (Alan homologado)
- DEV fix: commit 626abc0 — botão 🔍 Buscar adicionado no toolbar mobile
- DEV fix 2: commit `fix: adiciona modal de busca funcional no desktop` — modal desktop com desktopSearchOpen state
- Alan (Stakeholder): approved

## Decisions (locked)
- Meta: permitir buscar card pelo código (ex: #54) e abrir diretamente
- Interface: campo de busca no header ou atalho

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54/proposal
- PT-BR review: http://72.60.150.140:5173/openspec/changes/quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54/review-ptbr

## Notes
- Card criado pelo PO para melhorar UX do kanban

## Handoff DEV → QA
- Branch: `feature/card63-search-by-card-number`
- Funcionalidade: usuário digita #54 no campo de busca e o card é aberto diretamente
- Se card não existe, exibe toast informativa

## Fix Desktop Modal (2026-04-03 12:53 UTC)

**Bug:** O botão 🔍 Buscar no desktop setava `mobileSearchOpen(true)`, mas o search bar estava dentro de `sm:hidden` — não aparecia nada no desktop.

**Correção:** Criado `desktopSearchOpen` state + modal desktop dedicado (`fixed inset-0 z-50`) com input centralizado. Enter ou clique em "Buscar" encontra o card e abre o drawer.

- Commit: `fix: adiciona modal de busca funcional no desktop`
- Build: passou
- Backend/Frontend: healthy (restart 12:53 UTC)

## QA ✅ PASSOU (2026-04-03 13:20 UTC)

Teste via Playwright (node test-search.mjs):
- ✅ Login funcionou
- ✅ 🔍 Buscar button visível no toolbar desktop
- ✅ Modal abriu ao clicar no botão
- ✅ `#6` (parcial) NÃO abriu drawer — bug do onChange corrigido
- ✅ `#63` + Enter abriu drawer do card #63

**Evidência:** `/root/.openclaw/workspace/crypto/qa-evidence/card63-session-test.png` (screenshot mostra drawer do card #63 aberto após Enter)

Teste executado pelo orchestrator via Playwright node script (autenticação via UI real).

## QA ✅ PASSOU - Teste Detalhado (2026-04-03 13:32 UTC)

**Teste via playwright-cli (browser automation):**
- ✅ Login: o.alan.silva@gmail.com / TempPass123! — funcionou
- ✅ 🔍 Buscar button visível no toolbar desktop (ref=e140)
- ✅ Modal abriu ao clicar no botão — heading "Localizar Card" apareceu
- ✅ Digitou `#6` → aguardou 2s → drawer NÃO abriu — BUG DO onChange CORRIGIDO
- ✅ Digitou `#63` → pressionou Enter → drawer do card #63 abriu

**Evidências:**
- `card63-qa-01-kanban-loaded.png` — kanban carregado com botão Buscar visível
- `card63-qa-02-no-drawer-after-6.png` — após digitar #6, modal ainda aberto, sem drawer
- `card63-qa-03-drawer-opened.png` — após Enter, drawer do #63 aberto com detalhes

**Screenshot final:** `/root/.openclaw/workspace/crypto/qa-evidence/card63-qa-evidence.png` (copiado do teste 03)

Teste executado pelo QA subagent via playwright-cli.