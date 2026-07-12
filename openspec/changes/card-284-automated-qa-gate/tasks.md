## 1. Processo e board

- [x] 1.1 Adicionar `QA` entre `Code Review` e `Done` no Status do Project 1 e atualizar o README do board.
- [x] 1.2 Criar a label `qa-visual-skip` e documentar a autorização por comentário do Alan.
- [x] 1.3 Atualizar a skill global `alan-workflow` e as regras locais `AGENTS.md`/`rules.md` com a transição, ciclo de falha, evidência e critérios de Done.

## 2. QA automatizado

- [x] 2.1 Criar scripts frontend para executar todos os testes unitários e a suíte visual Playwright.
- [x] 2.2 Criar regressão visual determinística desktop/mobile com baselines versionados e dados estáveis.
- [x] 2.2.1 Estabilizar a suíte funcional Playwright existente para que seja dependência confiável do `qa-gate`.
- [x] 2.3 Atualizar CI para executar Playwright visual por padrão, validar opt-out autorizado e publicar todos os artefatos de falha.
- [x] 2.4 Adicionar validação OpenSpec, endurecer cobertura diferencial e implementar o job agregado `qa-gate` para PRs em develop.
- [x] 2.5 Configurar proteção de branch com `qa-gate` sem remover checks existentes e documentar o fluxo de PR para develop.

## 3. Validação e entrega

- [x] 3.1 Executar testes focados de CI/Playwright, build frontend e validações OpenSpec da change.
- [x] 3.2 Mover o card para Code Review, revisar o diff exato e corrigir/classificar achados.
- [x] 3.3 Commitar/publicar a branch, verificar o `qa-gate` e registrar evidências no card.
- [ ] 3.4 Integrar em develop, executar `./restart`, validar runtime e mover para Done técnico.

## Nota de execução

Use as skills do projeto quando aplicáveis: OpenSpec para artifacts/implementação/verificação, `playwright` para validação visual, `github-project-board` para Status/board e `alan-workflow` para evidências, review e fechamento.
