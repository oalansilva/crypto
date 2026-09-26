# QA e fechamento técnico — #1042

Verificação em 2026-09-26 UTC. PR [#1046](https://github.com/oalansilva/crypto/pull/1046), SHA `d72a21a904c3427ad6e24b7a35ae32b1bf5fcce0`.

## Checks e OpenSpec

Run [36183984432](https://github.com/oalansilva/crypto/actions/runs/36183984432) passou em `changes`, `openspec-validate`, `qa-policy`, `backend-format`, `frontend-lint`, `frontend-tests`, `frontend-build`, `process-fsm`, `backend-unit-tests`, `backend-tests`, `new-route-playwright-coverage`, `e2e-playwright`, `backend-coverage-gate` e `qa-gate`. `deploy-staging` ficou `SKIPPED`. O job `qa-gate` (108236903315) terminou `SUCCESS`.

Localmente, `openspec status --change card-1042-codex-adapter --json` reportou schema `spec-driven` e os quatro artefatos presentes; `openspec validate card-1042-codex-adapter` retornou `valid`. O check `process-fsm` também passou no run acima.

## Pin v1.1.19 — task 4.2

O overlay do consumidor mudou `pin` de `v1.1.16` para `v1.1.19`. A referência GitHub `refs/tags/v1.1.19` existe e resolve para o commit do produto `5d16ddb03ebb079d8ab9eebc7bdf2f49b5f7148b` (objeto tag `e404a9f14347193143377d807057e8039957b705`).

Comparei os blocos do mapa de `origin/develop` com `HEAD`: os bytes das linhas top-level `juizo.label/slug`, `execucao.label/slug` e do bloco integral `forbid` são iguais. O diff acrescenta apenas os subblocos Codex `juizo=gpt-6-sol/high` e `execucao=gpt-6-luna/max`. A revisão final do pin registrou a mesma preservação byte a byte e aprovação do `verify-wave`/checklist: [comentário do card](https://github.com/oalansilva/crypto/issues/1042#issuecomment-5838736710). A sequência do card alcançou `Done` via T14, confirmada abaixo.

## Filhos, proxies e limites

- Juízo: Codex CLI `0.156.1`, filho real com retorno `JUÍZO_1042_OK`; `turn_context` observou `gpt-6-sol/high`. Evidência e digest em [cli-apply-validation.md](cli-apply-validation.md).
- Execução/Apply: comentário do card registra `apply-coluna → GPT-6 Luna (gpt-6-luna/max)`, retorno `completed` e payload de P0: [handoff de Apply](https://github.com/oalansilva/crypto/issues/1042#issuecomment-5826989531).
- Code Review: dois filhos Codex CLI distintos, `gpt-6-luna/max`, read-only, `completed` com payloads separados e o mesmo diff (`c14e0b2ae72f1e882c03a0e336358b0043e1ad744e6bfb691cb11ce146f05211`): [revisão final pré-commit](https://github.com/oalansilva/crypto/issues/1042#issuecomment-5838736710). O fechamento contra `develop` retornou payload e não relatou P0: [comentário pós-commit](https://github.com/oalansilva/crypto/issues/1042#issuecomment-5838839212).
- QA CLI: sessão isolada `01a0db04-661e-7d22-abc1-13e1de8eeb91`, Codex CLI `0.156.1`, `model=gpt-6-luna`, `reasoning effort=max`, sandbox `read-only`; o cabeçalho registrou os valores observados e a sessão retornou `QA_1042_OK merge=209a6e7... pin=v1.1.19`. O log `.cursor/tmp/qa-1042-cli-local-session.log` tem SHA-256 `45071b099bda8ea507141d6afa3fb5d036cc3fa91e9e644fb2552d790a607392`; o payload `.cursor/tmp/qa-1042-cli-local-final.txt` tem SHA-256 `78a23fbabe3bbc63cde35bb0948f858a653cdb60e02786b320099e7a9365637e`. O snapshot dos checks da PR conferido pela sessão tem SHA-256 `c18363786099bc28ebfaef9849fcbc1b25fcde26a17e824a6a8a53ad0aa885da`; `codex_proxy` registrou `successful=true` e o pai observou `qa-gate SUCCESS`.
- Uma primeira tentativa de sessão não alcançou `api.github.com` no sandbox `read-only`; não houve alteração de código. A sessão acima repetiu a validação em sandbox `read-only` e passou. Esta instância de documentação não foi contada como prova de modelo observado; a prova considerada é a sessão CLI isolada `01a0db04-661e-7d22-abc1-13e1de8eeb91`.
- Os achados do ensaio real sobre spawn nativo fora de `PreToolUse` seguem como limite cooperativo aceito por Alan. Não se alega cobertura de IDE local nem modo Auto; ver [cli-spawn-routing-p0.md](cli-spawn-routing-p0.md) e comentário de escopo [no card](https://github.com/oalansilva/crypto/issues/1042#issuecomment-5829267348). O pin/review e o board mantêm essa limitação explícita.

## Piloto T14 e descrição do board — tasks 5.4/5.5

PR #1046 foi mergeado em `develop` em `2026-09-25T23:52:42Z`, merge SHA `209a6e7eb445859f3ec891589e1f2703ed1f6148`. A consulta pontual do Project 1 retornou Status `Done`. O handoff T14 registra `qa-gate green`, restart canônico de DEV e health `200`: [comentário de fechamento técnico](https://github.com/oalansilva/crypto/issues/1042#issuecomment-5841231121). O percurso documentado do card inclui Design/aprovação, Apply, dois reviews, QA e Done técnico.

Li a descrição atual do Project 1 via `gh project view 1 --owner oalansilva --format json`. Ela identifica `Cursor Agent` e `Codex CLI` como cooperativos, declara que hooks cobrem as rotas observadas e que spawn nativo pode ficar fora de `PreToolUse`, e diz explicitamente que não há modo Auto nem validação da IDE local. A afirmação de Codex inativo foi removida sem ampliar a cobertura declarada.
