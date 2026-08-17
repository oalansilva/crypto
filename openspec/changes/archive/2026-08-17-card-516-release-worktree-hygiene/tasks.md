## 1. Reconciliar a change #509

- [x] 1.1 Confirmar o archive em `openspec/changes/archive/2026-08-14-card-509-release-guard-graphql-budget/`.
- [x] 1.2 Confirmar no artefato arquivado que as tasks 5.1–5.4 estão marcadas como concluídas.
- [x] 1.3 Confirmar em `docs/kaizen-log.md` o sync de `release-worktree-hygiene`, a validação histórica 137/137 e a medição histórica de 204 pontos versus aproximadamente 4.900.
- [x] 1.4 Vincular no handoff final os caminhos, commit e evidências da regularização de #509, distinguindo evidência histórica de validação executada neste card.

## 2. Provar fail-closed com fake gh

- [x] 2.1 Criar fixture com branch `change-100-a`, snapshot de PRs válido e fake `gh` que faça a consulta do Project falhar pelo caminho público, produzindo internamente `BOARD_STATE=failed`.
- [x] 2.2 Em `post`, afirmar retorno não zero, blocker `board snapshot failed or invalid` e causa original.
- [x] 2.3 Em `post`, afirmar ausência de `preserved (card in flight; not deleted)` e de qualquer classificação `preserved` para a branch de status desconhecido.
- [x] 2.4 Em `audit`, afirmar retorno diagnóstico, warning explícito da mesma falha e ausência dos mesmos rótulos de preservação.
- [x] 2.5 Rodar o teste focado de `backend/tests/integration/test_release_guard.py`; se os asserts negativos falharem, registrar blocker e reconciliar o escopo antes de alterar código de produção.

## 3. Registrar a medição GraphQL

- [x] 3.1 Escolher uma janela sem automação concorrente conhecida e registrar UTC, commit, modo e variáveis relevantes.
- [x] 3.2 Capturar `graphql.remaining`, `limit` e `reset` imediatamente antes, executar o guard exatamente uma vez e capturar os mesmos campos imediatamente depois.
- [x] 3.3 Calcular e registrar o delta; aceitar somente valor atribuível ao run e de no máximo aproximadamente 500 pontos. Marcar como inconclusivo se houver consumo concorrente.
- [x] 3.4 Vincular o delta atual à referência histórica documentada de 204 versus aproximadamente 4.900 pontos.

## 4. Recuperar e validar o manifest da release

- [x] 4.1 Recuperar da evidência original do closeout os 17 nomes exatos e registrar o manifest nominal no handoff.
- [x] 4.2 Atualizar/prunar refs remotas e, para cada nome, registrar presença local/remota, tip SHA e worktree associada.
- [x] 4.3 Provar integração por `merge-base --is-ancestor`, igualdade de árvore, `git cherry` sem `+` ou diff material vazio nos arquivos tocados.
- [x] 4.4 Para `change-470-walk-forward-gate`, `change-482-kaizen-board-issue-rename-note` e `card-480-kaizen-guard-homologacao`, registrar comparação de árvore/patch e a autorização explícita de Alan antes de qualquer deleção forçada, caso as refs existam.
- [x] 4.5 Bloquear qualquer branch com worktree ativa, conteúdo exclusivo sem classificação ou fora do manifest.

## 5. Limpar e provar ausência

- [x] 5.1 Remover localmente apenas branches aprovadas e seguras; usar deleção forçada somente nos casos autorizados e documentados.
- [x] 5.2 Remover as refs remotas correspondentes e executar novo fetch/prune.
- [x] 5.3 Provar, para cada um dos 17 nomes, ausência em `refs/heads/<branch>` e resposta vazia de `git ls-remote --heads origin refs/heads/<branch>`, ou registrar classificação/autorização pendente.
- [x] 5.4 Confirmar que branches atuais fora do manifest, incluindo cards em voo, não foram alteradas.

## 6. Validação e handoff

- [x] 6.1 Rodar `openspec validate --all` até resultado terminal verde.
- [x] 6.2 Rodar `scripts/release-guard audit` e confirmar ausência de warnings referentes às branches do pacote; classificar separadamente qualquer dívida fora do escopo.
- [x] 6.3 Registrar comandos, resultados, manifest, SHAs, autorizações, medição GraphQL e ausência pós-limpeza no handoff do card.
- [ ] 6.4 Publicar novamente os artefatos OpenSpec do card após a execução e solicitar a transição permitida pelo fluxo, sem autoaprovar `Aprovação de Design -> Pronto para Dev`.
