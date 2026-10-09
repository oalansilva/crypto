Apply só depois de `Status=Pronto para Dev`. Usar as skills canônicas em `.cursor/skills/` (`covenant-flow`, `openspec-apply-change`). Não editar `.cursor/process-fsm.yaml`, `.cursor/model-map.yaml` nem código de produto. Não alterar `guard.decide()`, não copiar uma segunda allow-list e não formalizar worktree+cherry-pick. O allow de archive em `release-*` é o `decide()` do #1022, que está `Em desenvolvimento`.

## 1. Contrato compartilhado no runbook

- [x] 1.1 Na seção Release de `.cursor/skills/covenant-flow/SKILL.md`, tirar o rótulo `Pré-requisito (T18)` da regra do pai `execucao`, manter a recusa de chat `juizo` e apontar Codex para `execucao.codex` sem editar o mapa.
- [x] 1.2 Na seção Release e nas frases de release do overlay que falem de archive, tornar sync e archive o caminho normal da release pedida pelo `decide()` do #1022, sem menu genérico, sem segunda allow-list e sem worktree+cherry-pick. Até esse `decide()` estar na árvore, deny de archive — pacote ou card não resolvido, ou pacote resolvido em `release-*` unbound com `fail_closed` — é bloqueio real que aponta #1022. Conflito não resolvido, descarte ou exceção real continuam perguntados. Não alterar `guard.decide()` nem pedir a Alan aprovação extra por causa do texto do #1022.
- [x] 1.3 Alinhar a seção Release e as frases de release de `docs/crypto-overlay.md` para que branches de `RELEASE_BRANCHES` saiam antes do `post` PASS e antes de Pronto, preservando `PRESERVED_BRANCHES` e worktree in-flight, sem desligar `qa-gate`.

## 2. Decisão, pergunta e manifesto

- [x] 2.1 Extrair uma tabela de decisão única, usada por Cursor e Codex, que segue tarefa já autorizada, pede lacuna real uma vez e para em bloqueio externo explicado.
- [x] 2.2 Reconciliar responsável e classificação pela precedência do design, gravar a origem e não atribuir inferência a Alan quando a resposta não distribui o valor por card.
- [x] 2.3 Validar a pergunta no schema real do cliente, recusar campo incompatível ou duplicado e, sem a ferramenta, emitir as mesmas alternativas em texto sem aceitar a recomendação.
- [x] 2.4 Persistir o manifesto retomável fora do git e fora de uma worktree só, sem segredo nem transcript, e retomar na primeira etapa incompleta revalidando o que pode ter mudado.

## 3. Diagnóstico e causa de T16

- [x] 3.1 Fazer a negativa reportar operação, path, `q`, `q_git`, `bound_card`, regra efetiva, causa e ação corretiva, sem generalizar o deny para outra operação.
- [x] 3.2 Em `fechar_release`, manter `reason=guard:M_lote` quando o `post` falha e incluir na `message` os blockers já emitidos, sem afrouxar `M_lote` nem criar evento de FSM.
- [x] 3.3 Amarrar preflight, `post` e T16 à mesma identidade de contexto (pacote, cwd, HEAD, refs) e recusar PASS de outro contexto.

## 4. Evidência idempotente

- [x] 4.1 Fazer o helper de `pronto` recusar placeholder e nome genérico de pacote, e fazer T16 enviar pacote, branches e deploy reais.
- [x] 4.2 Atualizar comentário de Pronto incompleto do mesmo commit no lugar e não criar segundo comentário quando a evidência já está completa.
- [x] 4.3 Publicar o comentário canônico de homologação só quando a decisão humana já está comprovada, sem pedir a Alan para o escrever e sem chamar isso de T7.

## 5. Preflight, archive e integração

- [x] 5.1 Acrescentar ao `release-guard post` a pós-condição de sync e archive das changes concluídas de cards Homologado em `RELEASE_CARDS`, mantendo o check de `Pronto`/`Cancelado` e o blocker de duplicata ativa/arquivada.
- [x] 5.2 Fazer o preflight listar pendências de comentários, campos, documentação, archive, duplicação, integração, contexto e modelo sem anunciar etapa de deploy ou T16 como já iniciada.
- [x] 5.3 Verificar o merge contra o alvo antes de abrir o PR, agrupar a documentação final nesse PR e registrar a proposta de checks documentais sem desligar `qa-gate` nem a allowlist atual.
- [x] 5.4 Conferir flag de `gh` no binário instalado e não tratar `Permission denied` ou erro de GraphQL como deny de outra operação.

## 6. Regressão e ensaio comparável

- [x] 6.1 Cobrir com testes o replay: #1042 fora do pacote, duplicata ativa/arquivada da change de #1017 e alterações locais alheias permanecem e não são promovidos.
- [x] 6.2 Cobrir continuidade, retomada, decisão ambígua, contexto divergente e evidência incompleta, mais a tabela única nos dois clientes com diferença só de encoding e chave do mapa.
- [x] 6.3 Verificar por turno o par do mapa contra a evidência de runtime, sem fallback, sem modo Auto e sem alegar encaminhamento quando o cliente não o faz.
