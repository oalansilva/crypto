# quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54

## Status
- PO: done
- DESIGN: done
- DEV: done
- QA: pending (retaque após fix desktop)
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

## QA Pendente

- [ ] QA: abrir http://72.60.150.140:5173/kanban, clicar 🔍 Buscar no desktop, digitar #63, verificar drawer
- [ ] Salvar evidência em `/root/.openclaw/workspace/crypto/qa-evidence/`
- [ ] Comentar caminhos das evidências neste arquivo

## Evidência QA
