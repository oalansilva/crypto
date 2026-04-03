# quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54

## Status
- PO: done
- DESIGN: done
- DEV: done
- QA: pending
- Alan (Stakeholder): approved
- Bug: IMPLEMENTADO — falta UI de busca (campo não existe na tela)

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
- Build passou sem erros

## Bug Encontrado - QA

### Bug: Campo de busca NÃO EXISTE na UI do Kanban

**Severidade: CRÍTICO**

**Descrição:**
A funcionalidade de busca foi implementada no código (lógica de `#54` no useEffect e filteredItems), mas **NÃO HÁ nenhum elemento de UI para o usuário acessar essa funcionalidade**.

**Análise técnica:**
1. O `useEffect` que detecta padrão `#54` e abre o card diretamente EXISTE (KanbanPage.tsx linhas 334-348)
2. O `filteredItems` com suporte a `#54` EXISTE (linhas 369-377)
3. O estado `mobileSearchOpen` que controla o input de busca mobile EXISTE (linha 332)
4. O input de busca mobile existe no JSX (linhas 898-914), porém:
   - **NÃO HÁ nenhum botão para definir `mobileSearchOpen = true`**
   - O input mobile só aparece quando `mobileSearchOpen` é `true`, mas nunca é_triggered
   - O toolbar mobile (linhas 950-1015) só tem: Filter, Sort, Bug toggle e Column tabs — SEM busca
   - **No desktop (`hidden sm:block`), NÃO HÁ nenhum input de busca**

**Evidências:**
- Playwright: 0 inputs encontrados na página `/kanban` (após login)
- Console: 502/503 errors (backend instável)
- Código: `setMobileSearchOpen(true)` nunca é chamado em nenhum lugar

**O que funciona:**
- API `/api/workflow/kanban/changes` retorna cards com `card_number`
- Card #54 (Portfolio Optimizer) existe no banco

**O que NÃO funciona:**
- O usuário não consegue ver nenhum campo de busca
- Não há como disparar a funcionalidade de `#54`

**Próximo passo:**
- DEV precisa adicionar um botão/ícone de busca no toolbar do Kanban que defina `mobileSearchOpen = true`
- OU adicionar um campo de busca no header/desktop do Kanban

## Next actions
- [x] QA: validar feature — **FALHOU com bug**
- [ ] DEV: adicionar UI de busca (botão/trigger para mobileSearchOpen ou campo desktop)
