## Why

O closeout da release 2026-08-14 deixou uma divergência entre evidência e estado operacional. O bug #509 foi publicado e o card chegou a `Pronto`, mas a auditoria posterior encontrou a change ainda aberta, quatro tarefas de validação sem baixa e 17 branches classificadas como `preserved (card in flight; not deleted)` quando o snapshot do board não era autoritativo. Isso permitia que o `post` parecesse limpo sem provar a classificação nem a remoção do inventário do pacote.

A correção de #509 já reduziu o custo remoto e foi regularizada depois da auditoria. Este card consolida a prova reproduzível de fail-closed, a medição do orçamento e o closeout das branches, sem reabrir o escopo funcional original.

**UI impact: none.** O trabalho afeta guard operacional, testes/evidências OpenSpec e refs Git; não cria nem altera tela, rota, componente, copy ou interação visual.

## Estado real verificado em 2026-08-14

- A change original está arquivada em `openspec/changes/archive/2026-08-14-card-509-release-guard-graphql-budget/`.
- O `tasks.md` arquivado marca 5.1–5.4 como concluídas.
- `docs/kaizen-log.md` registra a medição de **204 pontos GraphQL** por execução contra cerca de **4.900 pontos** antes da correção, a validação `openspec validate --all` em 137/137 e o sync da capability `release-worktree-hygiene`.
- O mesmo log registra historicamente **17 branches** da release pendentes de deleção e o caso residual em que a saída mostrou `preserved (card in flight; not deleted)` durante falha remota.
- A fotografia read-only atual de `refs/heads` e `refs/remotes/origin` contém sete branches locais no padrão `card-*` (`469`, `502`, `503`, `504`, `516`, `517`, `518`) e somente `origin/card-502-ver-logs-vazio-autoscroll` nesse padrão. Elas são cards atuais e não formam, por si, o inventário histórico da release.
- As três branches historicamente marcadas como “not merged” — `change-470-walk-forward-gate`, `change-482-kaizen-board-issue-rename-note` e `card-480-kaizen-guard-homologacao` — não aparecem nas refs locais ou remotas rastreadas atuais.
- A documentação canônica da release lista os cards 470/480/481/482/489/491/509, mas não preserva os nomes das 17 branches. Portanto, a ausência das três branches conhecidas não basta para provar a limpeza das 17; o manifest exato precisa ser recuperado da evidência original do closeout antes da aceitação final.
- A leitura do guard confirma blocker/warning global para snapshot falho. Porém, o fallback do inventário entre `card_is_terminal` e `state="preserved (card in flight; not deleted)"` ainda exige uma prova focada de que `BOARD_STATE=failed` nunca termina rotulado como preservação.

Nenhum teste, guard, `gh`, fetch ou deleção foi executado durante este gate de Design.

## What Changes

- Reconciliar a evidência já produzida por #509: tasks 5.1–5.4, archive, sync da spec, validação e medição GraphQL.
- Acrescentar uma prova determinística com fake `gh` para snapshot inválido/ausente: `post` retorna não zero com blocker e `audit` emite warning explícito; nenhum dos modos pode classificar a branch como `preserved` ou `card in flight` a partir de estado desconhecido.
- Recuperar e versionar no handoff o manifest exato das 17 branches da release 2026-08-14.
- Para cada branch do manifest, provar integração sem conteúdo exclusivo ou registrar a autorização explícita de descarte antes de remover refs local e remota.
- Revalidar a ausência do manifest, o `release-guard audit` sem warnings dessas branches e `openspec validate --all` verde.
- Não alterar o `scripts/release-guard` por presunção. Se a prova focada revelar o rótulo fail-open residual indicado pela leitura estática, interromper a limpeza e reconciliar o escopo antes de qualquer patch de produção.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `release-worktree-hygiene`: explicita que estado remoto desconhecido não constitui preservação válida, e exige manifest/evidência verificável para a limpeza das branches do pacote.

## Acceptance Criteria

- O archive de `card-509-release-guard-graphql-budget` existe e suas tasks 5.1–5.4 estão concluídas, com evidência vinculada no handoff.
- Uma única execução real e identificada do guard registra delta GraphQL de no máximo aproximadamente 500 pontos, com valor observado de referência de 204 versus aproximadamente 4.900 antes da correção.
- O teste com fake `gh` força internamente `BOARD_STATE=failed`; em `post`, obtém retorno não zero e blocker explícito; em `audit`, warning explícito; em ambos, a saída não contém classificação `preserved`/`card in flight` para a branch cujo status ficou desconhecido.
- O manifest nominal das 17 branches está registrado. Cada nome está ausente em refs locais e em `origin`, ou possui classificação e autorização explícitas ainda pendentes — nunca ausência presumida por amostragem.
- As branches “not merged” citadas no card só são removidas após comparação de árvore/patch contra refs remotas e vínculo da autorização de Alan.
- `openspec validate --all` termina verde e `scripts/release-guard audit` não emite warnings referentes às branches do pacote.

## Impact

- OpenSpec e handoff do card #516.
- Teste focado do `release-guard` e evidência de medição.
- Refs Git locais/remotas da release 2026-08-14, somente após validação e autorização.
- Sem banco, serviço, restart, deploy ou impacto de UI.
