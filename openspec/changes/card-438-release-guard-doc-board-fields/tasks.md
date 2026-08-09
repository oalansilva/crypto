## 1. Guard post — evidência documental

- [ ] 1.1 Adicionar check: doc do pacote de release commitada e sem placeholders (marcadores de template: `<!--`, `TBD`, `TODO`, `<...>`, lorem) em `docs/release-<data>*.md`; falha em modo estrito
- [ ] 1.2 Adicionar check: 2+ docs de release da mesma data com conteúdo divergente = blocker instruindo consolidação (doc canônica única)

## 2. Guard post — campos do board

- [ ] 2.1 Adicionar check via `gh project`: cards do pacote com Responsável/Prioridade/Tipo vazios = blocker; falha clara de auth quando `gh` sem escopo project
- [ ] 2.2 Integrar consistência de título board/issue no check (vínculo #430)

## 3. Docs

- [ ] 3.1 Atualizar AGENTS.md/docs de release conforme novo comportamento do guard

## 4. Validação

- [ ] 4.1 Testar cenários: doc com placeholder, docs duplicadas divergentes, card sem campos (todos bloqueiam); cenário limpo passa
- [ ] 4.2 Rodar validação OpenSpec da change
