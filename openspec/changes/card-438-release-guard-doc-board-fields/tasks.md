## 1. Guard post — evidência documental

- [x] 1.1 Adicionar check: doc do pacote de release commitada e sem placeholders (marcadores de template: `<!--`, `TBD`, `TODO`, `<...>`, lorem) em `docs/release-<data>*.md`; falha em modo estrito
- [x] 1.2 Adicionar check: 2+ docs de release da mesma data com conteúdo divergente = blocker instruindo consolidação (doc canônica única)

## 2. Guard post — campos do board

- [x] 2.1 Adicionar check via `gh project`: cards do pacote com Responsável/Prioridade/Tipo vazios = blocker; falha clara de auth quando `gh` sem escopo project
- [x] 2.2 Integrar consistência de título board/issue no check (vínculo #430)

## 3. Docs

- [x] 3.1 Atualizar AGENTS.md/docs de release conforme novo comportamento do guard

## 4. Validação

- [x] 4.1 Testar cenários: doc com placeholder, docs duplicadas divergentes, card sem campos (todos bloqueiam); cenário limpo passa
- [x] 4.2 Rodar validação OpenSpec da change
