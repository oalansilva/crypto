# quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54

## Status
- PO: done
- DESIGN: done
- DEV: done
- QA: pending
- Alan (Stakeholder): approved

## Decisions (locked)
- Meta: permitir buscar card pelo código (ex: #54) e abrir diretamente
- Interface: campo de busca no header ou atalho

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54/proposal
- PT-BR review: http://72.60.150.140:5173/openspec/changes/quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54/review-ptbr

## Notes
- Card criado pelo PO para melhorar UX do kanban
- DEV: implementado

## Handoff DEV → QA
- Branch: `feature/card63-search-by-card-number`
- Funcionalidade: usuário digita #54 no campo de busca e o card é aberto diretamente
- Se card não existe, exibe toast informativa
- Build passou sem erros

## Next actions
- [ ] DEV: implementar busca por código de card
