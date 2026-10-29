Nota: usar as skills do projeto quando couber (`.cursor/skills/`, em especial `covenant-flow` e `openspec-apply-change`). Card sem tela: o gate de Design (Design → Aprovação de Design → Pronto para Dev, com `design-critic` e aprovação do Alan) vale antes destas tasks.

## 1. Limite do job

- [x] 1.1 Em `.github/workflows/ci.yml`, job `process-fsm`, trocar `timeout-minutes: 5` pela linha exata do D1 (`timeout-minutes: 10` com o comentário do #1152 na mesma linha).
- [x] 1.2 Conferir que `git diff origin/develop -- .github/workflows/ci.yml` mostra só essa linha (1 removida, 1 adicionada) e que os `timeout-minutes: 30` de `backend-unit-tests` e `e2e-playwright` e o `needs` do `qa-gate` ficaram iguais.
- [x] 1.3 Conferir que o YAML continua válido: `python -c "import yaml,sys; d=yaml.safe_load(open('.github/workflows/ci.yml')); assert d['jobs']['process-fsm']['timeout-minutes']==10"`.
- [x] 1.4 `openspec validate card-1152-ci-limite-process-fsm --strict` válido.

## 2. PR sem rodada repetida

- [ ] 2.1 Commit, push e PR para `develop`; registrar o link da rodada do CI. <!-- covenant-flow:after-commit -->
- [ ] 2.2 Na rodada do commit do topo do PR, conferir o critério D3: `jobs?filter=all&per_page=100` com uma única tentativa do `process-fsm`, `run_attempt == 1`, `conclusion == "success"`, `head_sha` = topo do PR; anotar a duração. Não repetir o job; se for cancelado por tempo, parar e voltar ao Alan como P0. <!-- covenant-flow:after-commit -->

## 3. Histórico no card

- [ ] 3.1 Refazer a medição do D2 (rodadas do `ci.yml` desde 2026-10-18 até a rodada do PR; tentativas com `filter=all&per_page=100`; motivo de cada cancelamento pelas annotations). Scripts só no scratchpad, nada novo no repositório. <!-- covenant-flow:after-commit -->
- [ ] 3.2 Comentar no #1152 o texto do D2 ("Texto do card") com a tabela dos grupos A–D, a lista de todas as tentativas e a rodada do PR como a primeira com 10 min. A rodada `39270686134` aparece como não medida (estimativa do log), nunca somada às medidas. Registrar o link do comentário. <!-- covenant-flow:after-commit -->

## 4. Verificação

- [ ] 4.1 `qa-gate` verde no topo do PR com o `process-fsm` da task 2.2; registrar o link no card. <!-- covenant-flow:after-qa -->
