## 0. Ensaio do host (antes da task 1 e da 5.2)

- [x] 0.1 Preparar um hook `UserPromptSubmit` descartável que só grava o prompt recebido num arquivo em `.cursor/tmp/`, sem shim, executor ou rede, e o texto para o Alan registrar e remover (bash comum).
- [x] 0.2 Alan registra o hook, abre sessão nova e digita `/priorizar 1` e uma frase comum no cli e no app desktop por SSH. Registrar no card se disparou em cada um e o texto recebido.
- [x] 0.3 **Parada:** se não disparar no desktop, ou se `/priorizar 1` não chegar cru (barrado ou só o corpo expandido), parar o Apply, remover o hook descartável e devolver ao Alan a escolha: só cli, outro texto de comando ou parar o card. Nenhuma task seguinte começa sem essa resposta. Se passar, remover o hook descartável e seguir.

## 1. Núcleo do executor (`scripts/process-fsm/portao/`)

- [x] 1.1 Criar a função pura de decisão do executor (D3): recebe pedido, Status vivo e FSM e devolve `movido De → Para` ou `recusado: motivo` (`de` ≠ Status vivo, `no_edge`, `actor`, `lei_invalida`). `pedir` aceita só `Agent`/`Guard`/`CI`. Inclui a invariante dos seis portões só `Alan`.
- [x] 1.2 Regras por comando (D7): cadeia T1+T3 do `/priorizar` com T3 recusado deixando Todo; comparação de digest do `/aprovar-design` com o último T5; motivo em T6/T18/T2; pendência de `/cancelar` com prazo de 10 min, conferida pelo input do run anterior; `criar_card` (issue existe e não está no board).
- [x] 1.3 Formatador do recibo (D4): linha de motivo primeiro (`Devolver design:`, `Não homologar:`, `Cancelar:`), comando ou evento, resultado, data e hora BRT, cliente/superfície/versão, sessão, URL do run, SHA da lei.
- [x] 1.4 Adaptador GitHub do executor (lê Status, move, adiciona item, comenta, lista runs anteriores pelo input), isolado atrás de interface. Testes só com quadro falso.
- [x] 1.5 Testes unitários do núcleo cobrindo os cenários de `specs/board-executor` e `specs/alan-gate-commands` (sem GitHub). Rodar `pytest scripts/process-fsm` e registrar a saída.

## 2. Cliente na VM e `process_event`

- [x] 2.1 `portao_client.py` com `pedir` e `capturar`: monta o `client_payload` (D4), dispara `repository_dispatch` com o token do `gh` e espera o run pelo `request_id` até o teto. Devolve `executor:timeout`/`executor:indisponivel` sem presumir resultado.
- [x] 2.2 Trocar `BoardMover.set_status` por `move(issue, evento, de, para, ator, extras)`; `ExecutorMover` usa o cliente; `FakeMover` acompanha. Seleção pelo overlay `board.executor` (sem a chave, o mover atual) (D9).
- [x] 2.3 Ligar os pontos de move do `process_event`: T3, T5 com `digest`, T8–T14, T16 (um pedido por card), T17a/b com ator `Guard`; `criar_card` deixa de ser `not_implemented`. Recusa vira `reason=executor:<motivo>`.
- [x] 2.4 Testes de `process_event` com executor falso para os cenários de `specs/process-fsm-event`, incluindo eventos do Alan ainda recusados com `actor` sem chamar o executor.

## 3. Hook de prompt do Claude Code

- [x] 3.1 Matcher da gramática (D6) como função pura, com a tabela de aceitos e recusados do D11 em teste.
- [x] 3.2 `claude_adapter.py prompt-submit`: casou → `capturar` (com digest do worktree `card-N-*` no `/aprovar-design`) → resposta sem bloquear, com `systemMessage` e `additionalContext` (D8); não casou → sem saída.
- [x] 3.3 Shim (`cf_shim.py`) e registro na conta: `UserPromptSubmit` do Claude como evento que gateia; `install.sh --account` do nucleus com a entrada nova; `adapters.json` atualizado. Testes do instalador (preserva hooks alheios, `--check`).
- [x] 3.4 Confirmar com o hook real o que a task 0 viu (dispara no cli e no desktop e recebe o comando cru), e aplicar a escolha do Alan se a task 0 parou. Registrar o resultado no card.

## 4. Guard e regras escritas

- [x] 4.1 Guard: negar `capturar` e `dispatches` do repositório do executor fora de `process_event.py`; manter a regra de `item-edit`; testes dos cenários de `specs/process-fsm-guard`.
- [x] 4.2 `overlay.render_agents` (linhas 442 e 446), `paging.py:28`, `.cursor/hooks/process-fsm-session-start.sh:9`, regenerar `AGENTS.md`; ajustar `test_paging.py` (linha 375 passa a exigir os seis portões).
- [x] 4.3 `fsm.py` `ALAN_GATES` com T1, T2, T6, T7, T15, T18; `process-fsm.yaml`: texto de I2 com os seis, `freeze_digest` no T5 e `check_digest` no T7; `test_fsm.py` verde.
- [x] 4.4 `covenant-flow/SKILL.md` (linhas 40, 172, 176 e subseção "Comandos de portão" com gramática, nível cooperativo (run e recibo apagáveis pelo agente; recibo não avisa o Alan) e regra do texto sem contexto do executor) e `github-project-board` (SKILL 42–43 e 128–140; `references/project-board-commands.md` 38–40, 83 e 101) conforme D10, incluindo a restauração de arrasto fora de δ só por comentário.

## 5. Repositório do executor e migração

- [ ] 5.1 Preparar o workflow do executor (checkout do `PIN`, environment `portao`, `concurrency` por card, `run-name` com o `request_id`) e o texto do passo a passo do operador (Migration Plan, passos 1, 3 e 5), com comandos para colar em bash comum. <!-- covenant-flow:after-commit -->
- [ ] 5.2 Alan executa os passos 1 e 3 (conta do agente, repo do executor, ruleset, environment, PAT, `PIN` = SHA revisado, `install.sh --account`, revisão R/A, sessão nova). Registrar no card. <!-- covenant-flow:after-commit -->
- [ ] 5.3 Ligar `board.executor` no overlay no último commit do card, só depois do ensaio 6.1 passar. <!-- covenant-flow:after-commit -->
- [ ] 5.4 Alan executa o passo 5 (login do `gh` da VM com a conta do agente, chave SSH, revogação do token do GitHub CLI do `oalansilva`, inventário de credenciais). Registrar no card. <!-- covenant-flow:after-qa -->

## 6. Verificação viva

- [ ] 6.1 Num issue de ensaio no Project 1, com o Alan digitando no cli e no app desktop: cada comando certo move e deixa recibo; texto aproximado e o comando como comentário na issue não fazem nada; `/priorizar` termina em Design; arrasto para Todo fica em Todo; `/aprovar-design` com `design.md` alterado depois do T5 é recusado; `/cancelar` sem confirmação não move. Links dos recibos e runs no card. <!-- covenant-flow:after-commit -->
- [ ] 6.2 `process_event pedir_review` (ou outra transição do agente no issue de ensaio) move pelo executor, e `process_event aprovar_design` é recusado. Pedido `pedir` forjado de `aprovar_design` direto ao executor é recusado com `actor`. <!-- covenant-flow:after-commit -->
- [ ] 6.3 Depois do passo 5: no terminal do Alan, com o token do agente, `gh project item-edit` do Status falha por permissão; o inventário de credenciais da VM só mostra o token do agente. <!-- covenant-flow:after-qa -->
