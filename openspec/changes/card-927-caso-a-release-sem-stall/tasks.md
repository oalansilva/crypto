## 1. Guard post: produção contida na develop

- [x] 1.1 Trocar o predicado de alinhamento em `scripts/release-guard` `post`: PASS se mesmo commit **ou** `origin/main` ancestral de `origin/develop`; extra na develop = warn; FAIL se develop não contém produção; remover exigência de árvores iguais e de develop ancestral de main
- [x] 1.2 Actualizar testes/fixtures do guard para o Caso A (develop à frente com árvore diferente) PASS com aviso, e FAIL quando `origin/main` não é ancestral de `origin/develop`

## 2. Guard post: commit em produção por card

- [x] 2.1 Em `post` com `RELEASE_CARDS`, bloquear se algum id do pacote não tiver commit alcançável em `origin/main` que referencie `#<id>`
- [x] 2.2 Cobrir o gate com fixture (pacote presente vs id ausente); MUST NOT fechar #916/#917

## 3. Preflight de pacote incompleto

- [x] 3.1 Em `pre` em `release-*` com PR de código, fail-closed se compile frontend local falhar por módulo ausente; MUST NOT escrever `frontend/dist` tracked; MUST NOT seguir para `gh pr create`
- [x] 3.2 Documentar o corte no runbook Caso A (overlay) se o `pre` não invocar o compile

## 4. Overlay 5b e 1 PR merge normal

- [x] 4.1 Actualizar `docs/crypto-overlay.md` passo 5b: develop contém produção + extra = aviso; 1 PR merge normal `main → develop`; recusar #926 e #913+#914+#915
- [x] 4.2 Recortar o mesmo predicado na skill `covenant-flow` só se o pin duplicar o passo 5b; `AGENTS.md` MUST NOT crescer

## 5. CI: e2e não arranca sem frontend-build

- [x] 5.1 Em `.github/workflows/ci.yml`, `e2e-playwright` `needs` `frontend-build` e não arranca se `frontend-build` ≠ success; manter `timeout-minutes: 30`; MUST NOT mudar o watcher 35 min

## 6. T16: próxima acção no git errado

- [x] 6.1 `fechar_release` com `q_git` `main` / `docs-*` / `sync-*` rejeita sem mover Status e sem switch de git; `message` diz mudar para develop ou `release-*` e repetir; `reason` MUST NOT ser só `unbound`
- [x] 6.2 Actualizar testes injectados (`test_process_event.py` / vizinhos) para `main`, `docs-*` e `sync-*`; paging unbound em develop/release-* permanece não-deny

## 7. Verify

- [x] 7.1 `openspec validate card-927-caso-a-release-sem-stall` verde; pytest focado de `scripts/process-fsm` e do guard tocado
- [x] 7.2 Helper `scripts/release-casoa-closeout.sh` só se overlay + guard não cobrirem (MAY)
