## Context

Card [#1059](https://github.com/oalansilva/crypto/issues/1059), Status Design no Project 1. O issue é a autoridade de produto; `proposal.md` copia Problema, História, Entra e Não entra. Este arquivo é só o *como*.

HEAD `7393c3d3` já tem o fechamento mecânico, sem a continuidade que o issue pede. A seção Release de `.cursor/skills/covenant-flow/SKILL.md` chama de `Pré-requisito (T18)` a regra do pai em `execucao`, embora T18 seja `nao_homologar`. `openspec-archive-change` abre menu de sync/archive. `openspec_terminal_changes_check` em `scripts/release-guard` só trata change ativa de card `Pronto` ou `Cancelado`. `measure_m_lote` devolve bool e descarta a saída do `post`. `LiveT16Closer.comment_pronto` passa `--package release-guard post` e não passa branches, e o helper preenche `<lista ou pendência>` quando o campo falta. O check de duplicata ativa/arquivada já existe. `.cursor/model-map.yaml` já tem `juizo`/`execucao` e os subblocos `codex`; este card não o edita.

#1022 está em `Em desenvolvimento`. O Design publicado no Gist do #1022 (2026-09-27, crítica PASS) já fechou a via: archive das changes do pacote Homologado em `release-*` por exceção em `decide()`; worktree do card + cherry-pick é desvio a eliminar, não caminho oficial. Este card reutiliza esse `decide()` e não copia uma segunda allow-list. O guard deste HEAD ainda nega essa escrita com `fail_closed` em `release-*` unbound. Até o `decide()` do #1022 estar na árvore, essa negativa é bloqueio real que aponta #1022, não um procedimento deste card.

UI impact: none
live_route: N/A
surface: none

Justificativa: harness/processo de fechamento de release no Codex; nenhuma rota, componente ou copy visível do produto.

## Goals / Non-Goals

**Goals:**

- Um pedido explícito de release percorre as tarefas operacionais já autorizadas até concluir ou até um bloqueio real, com a mesma decisão no Cursor e no Codex.
- Perguntar só lacuna real, uma vez, consolidada por card, com origem registada. Silêncio não aprova.
- Manifesto retomável, diagnóstico da operação avaliada, evidência de Pronto real e idempotente, e o mesmo contexto em preflight, `post` e T16.
- Sync e archive das changes concluídas do pacote antes de T16, com os cards ainda em Homologado, pelo `decide()` do #1022, sem worktree+cherry-pick.
- Corrigir no runbook as três contradições de release: rótulo T18, menu genérico de archive, ordem de limpeza de branches.

**Non-Goals:**

- Pular Design, aprovação humana, QA, homologação ou T16, ou mover card fora da FSM.
- Homologar em nome de Alan, tratar silêncio como aprovação, descartar trabalho alheio ou ignorar deny.
- Implementar o allow de archive de #1022, alterar `guard.decide()`, copiar uma segunda allow-list, formalizar worktree+cherry-pick ou aceitar pacote/card não resolvido.
- Editar `.cursor/process-fsm.yaml`, `.cursor/model-map.yaml`, `backend/**` ou `frontend/src/**`.
- Reivindicar modo Auto, trocar modelo em silêncio ou reabrir a release já publicada.
- Publicar transcript, conteúdo de sessão ou credencial.

## Decisions

1. **Contrato único, FSM intocada.** A continuidade mora na seção Release do runbook e na spec `release-closeout-autonomy`. `AGENTS.md` não cresce. Não há estado, evento, hook nem `enabled_tools` novo. T16 continua `process_event fechar_release` com `M_lote`. T7 continua a aprovação de Design. T15 continua `homologar`. T18 continua `nao_homologar` de Alan. O pai de release continua a ser a faixa `execucao` do mapa; chat `juizo` recusa T16. Codex lê `execucao.codex`; Cursor lê o slug do topo da mesma faixa. Isso não é "o mesmo modelo do pai" nem T18.

2. **Pergunta só com lacuna real.** Antes de perguntar responsável ou classificação, reconciliar board, handoff e manifesto. Precedência: decisão humana explícita e atribuída àquele card; valor já registado; fonte inequívoca; política de classificação. A origem fica no manifesto. Inferência não é decisão de Alan. Resposta sem distribuição entre cards, ou fontes incompatíveis, continua lacuna. As lacunas do pacote saem numa consulta só, com o campo em falta por card. Resposta já dada não se repete depois de retomada ou compactação. Sem resposta, a lacuna permanece e o que já está autorizado segue. O adaptador valida o schema real da ferramenta do cliente e não envia campo desconhecido nem campo duplicado. As seis falhas da release auditada entram na regressão como essas duas classes, sem reconstruir transcript. Sem a ferramenta, as mesmas alternativas vão em texto; a recomendação não conta como aceite.

3. **Manifesto fora do git e fora de uma worktree só.** Um registo por pacote, não commitado, sem segredo e sem transcript: só ids e evidência agregada. Guarda pacote, decisões com origem, referências de evidência, etapas concluídas e a identidade do contexto (cwd, HEAD, `origin/develop`, `origin/main`, branch, `RELEASE_CARDS`). A retomada revalida o que pode ter mudado e continua na primeira etapa incompleta. Não pede a Alan para transportar esse contexto nem relê credencial que já está disponível. Caminho e nomes dos campos são P3.

4. **Archive consome o `decide()` do #1022.** #1022 está em `Em desenvolvimento`. O contrato já publicado é o archive das changes do pacote Homologado em `release-*` pela exceção em `decide()` do #1022. Este card reutiliza esse `decide()` e não copia uma segunda allow-list. Não altera `guard.decide()`. Worktree do card + cherry-pick não é caminho oficial e este card não o formaliza. A seção Release e o overlay não mandam abrir worktree para furar o guard. Até esse `decide()` estar na árvore, deny de archive — pacote ou card não resolvido, ou pacote resolvido em `release-*` unbound com `fail_closed` — é bloqueio real que aponta #1022, não um procedimento paralelo. Não pede a Alan aprovação extra por causa do texto do #1022. Conflito sem resolução, descarte ou exceção real é perguntado como tal, uma vez. Produto e pacote ou card não resolvido continuam negados. O menu "Sync now / Archive without syncing" de `openspec-archive-change` não interrompe o fechamento quando o `decide()` do #1022 já permite a escrita.

5. **Negativa específica e causa de T16 visível.** Cada negativa diz a operação, o path, `q`, `q_git`, `bound_card`, a regra efetiva, a causa e a ação corretiva. Uma negativa não prova que outra operação é proibida. O agente pode consultar o guard para a operação concreta. `fechar_release` com `M_lote` falso mantém `reason` `guard:M_lote` e passa a incluir na `message` os blockers já emitidos pelo `post`, para não obrigar a repetir o `post` só para descobrir a causa. O gate não afrouxa. Falha ao medir continua fail-closed, com a classe da falha na mensagem.

6. **Evidência de Pronto real e idempotente.** O helper de `pronto` recusa placeholder (`<pacote>`, `<lista ou pendência>`, `<deploy PROD pendente>`, branches vazias). T16 envia nome real do pacote, branches reais e `PROD_DEPLOY_EVIDENCE`. Comentário existente do mesmo commit e incompleto é atualizado no lugar. Comentário já completo é deduplicado. Repetir não cria outro comentário. Homologação humana já comprovada (marcador canônico ou arraste/confirmação de Alan) gera o comentário `homologado` pelo helper, sem pedir a Alan para o escrever e sem chamar isso de T7. Sem a decisão humana, o agente não inventa o comentário.

7. **Preflight não é a etapa seguinte.** Antes de publicar, uma lista cobre comentários, campos, documentação, archive, duplicação, integração, contexto e disponibilidade do modelo. O que depende de deploy fica na etapa de deploy. O relatório não anuncia execução de etapa ainda não iniciada. A retomada parte da primeira entrada incompleta.

8. **Pós-condição de archive com card ainda Homologado.** No `post` que antecede T16, change concluída (artefatos presentes e sem task aberta) de card em `RELEASE_CARDS` com Status Homologado tem de estar só em `openspec/changes/archive/` e com o delta já refletido na spec principal, ou com a exceção de header já prevista no closeout quando o delta está de facto na spec. Change ainda ativa falha o `post`. O caso atual `Pronto`/`Cancelado` permanece. Duplicata ativa e arquivada continua blocker. Card fora do pacote, como #1042 no replay, não é arquivado nem promovido por este check.

9. **O mesmo contexto autoriza o fecho.** Preflight, `post` e T16 gravam a identidade do contexto. PASS noutro cwd ou noutro HEAD não autoriza T16. A divergência é explicada e a verificação pertinente corre de novo no contexto que vai executar T16.

10. **Modelo por turno, mapa intocado.** Cada turno lê o mapa e compara com a evidência de runtime. Divergência ou indisponibilidade fica visível. Não há troca silenciosa, fallback, modo Auto nem edição do mapa. Trocar modelo não corrige archive. Se o cliente encaminha sessão, o destino recebe o manifesto. Se não encaminha, o bloqueio e o handoff ficam explícitos, sem alegar encaminhamento feito.

11. **Contradições do runbook, sem playbook novo.** A seção Release deixa de rotular o pré-requisito de `execucao` como T18. A frase do overlay que manda apagar branches depois de Pronto alinha-se ao requisito já existente de `release-worktree-hygiene`: branches do pacote em `RELEASE_BRANCHES` saem antes do `post` PASS e antes de Pronto. Worktree in-flight e `PRESERVED_BRANCHES` continuam preservadas. A frase de Design "mesmo modelo do chat" não é regra de release; a release usa a faixa do mapa. Não se reescreve o spawn de crítica visual.

12. **Integração antes do PR, proteções atuais de pé.** Antes de abrir o PR, simular o merge contra o alvo e juntar a documentação final do pacote nesse PR, em vez de descobrir o conflito depois da suíte (#1055) ou abrir PR só porque o archive chegou tarde. A proposta de checks proporcionais para diff estritamente documental nomeia a cobertura e a regressão e não desliga `qa-gate` nem a allowlist documental já usada pelo `release-guard`. Este card não muda proteção de branch.

13. **Ferramenta e credencial não viram deny alheio.** Flag de `gh` é conferida no binário instalado antes do uso. Credencial já disponível não dispara outra consulta de segredo. Leitura `Permission denied` e erro de GraphQL valem para aquela chamada, não para outra operação.

14. **Replay e ensaio.** O fixture traz #1042 fora de `RELEASE_CARDS`, duplicata ativa/arquivada no nome da change de #1017 e alterações locais alheias. O fecho preserva esse trabalho e não promove conteúdo não homologado. A regressão cobre continuidade, retomada, decisão ambígua, contexto divergente e evidência incompleta. Cursor e Codex executam a mesma tabela de decisão. A diferença permitida é o encoding da pergunta e a chave do mapa. Ensaio vivo no host, quando existir, é evidência de QA; ausência não é declarada como sucesso.

## Risks / Trade-offs

- [Exigir archive com card ainda Homologado bloqueia `post` que antes passava] → o bloqueio é a pós-condição pedida; a causa vem na mensagem de T16, sem segundo `post` cego.
- [PASS de outra worktree parece reutilizável] → a identidade de contexto recusa o fecho e manda repetir a verificação no cwd de T16.
- [Atualizar comentário incompleto edita o comentário errado] → só o marcador de Pronto com o mesmo commit e com placeholder; comentário completo não é reescrito.
- [`decide()` do #1022 ainda não está na árvore e o archive em `release-*` unbound fica `fail_closed`] → bloqueio real que aponta #1022; este card não abre worktree nem cherry-pick para furar o guard.
- [Mensagem de T16 cresce com o log do `post`] → entram as linhas de blocker, não o log inteiro. Limite de tamanho é P3.
- [Skill e overlay voltam a divergir] → as três frases de release ficam cobertas por teste de needle nos dois textos.
- [Replay usa transcript privado] → o fixture usa só ids e o formato dos factos agregados do issue, sem conteúdo de sessão.

## Migration Plan

Só depois de T7 e de `Pronto para Dev`. Apply mexe em runbook, frases de release do overlay, `release-guard`, a mensagem de `fechar_release`, o helper de evidência e testes. Não há deploy de aplicação nem migração de dados. O manifesto é local e não commitado. Rollback é reverter esses arquivos. Cards já Pronto da release auditada não são reabertos.

## Open Questions

Nenhuma pergunta de produto. O issue já fecha o que entra e o que não entra. O allow de archive permanece com #1022.

## P3 detalhe de Apply

Aceites aqui e resolvidos no Apply, sem voltar a Alan:

- Caminho do manifesto e nomes internos dos campos, desde que o conteúdo e a exclusão de segredo sejam os da decisão 3.
- Nomes dos campos da ferramenta de pergunta do Codex, lidos do schema instalado no Apply, desde que campo desconhecido ou duplicado não seja enviado.
- Nome do módulo do diagnóstico, da lista de preflight e da tabela de decisão compartilhada.
- Se a lista de branches vem de `RELEASE_BRANCHES` ou do git, desde que placeholder seja recusado.
- Se o check Homologado é ramo novo dentro de `openspec_terminal_changes_check` ou função ao lado, chamada pelo mesmo `post`.
- Qual frase do overlay e qual da skill se move, desde que as três contradições fechem como nas decisões 1, 4 e 11.
- PATCH do comentário ou substituição que deixe um único comentário, desde que a repetição seja idempotente.
- Teto de caracteres da causa colada na `message` de T16.

## Prototype

N/A

## Impeccable

N/A — harness/processo de fechamento de release no Codex; nenhuma rota, componente ou copy visível do produto. Gates de Design e aprovação humana permanecem.

## Apply contract

- Escrita só após `Status=Pronto para Dev`. Sem código de produto, sem YAML da FSM, sem mapa de modelos, sem alterar `guard.decide()`, sem segunda allow-list e sem worktree+cherry-pick como via de archive.
- Testes do harness cobrem o replay, a causa estruturada de T16, o comentário sem placeholder e a tabela única Cursor/Codex.
- Não homologar, não chamar `fechar_release` neste Design e não reivindicar modo Auto.

## Design Critique

- **P0:** nenhum
- **P1** coordenação com #1022 — fechado no rework. O crítico isolado mostrou que #1022 está `Em desenvolvimento` e que o contrato publicado proíbe formalizar worktree+cherry-pick; o texto antigo dizia que #1022 estava em Design e mandava esse desvio enquanto o `decide()` não estava na árvore. O rework alinhou `design.md`, as specs e as tasks: reutiliza o `decide()` do #1022, não copia allow-list, e trata `fail_closed` em `release-*` unbound como bloqueio que aponta #1022. O orquestrador conferiu essas frases. Sem P1 aberto.
- **P2:** nenhum
- **P3** caminho e campos do manifesto — aceite, detalhe de Apply
- **P3** schema da pergunta no Codex — aceite, detalhe de Apply
- **P3** nomes de módulo do diagnóstico, do preflight e da tabela — aceite, detalhe de Apply
- **P3** origem da lista de branches — aceite, detalhe de Apply
- **P3** ramo versus função do check Homologado — aceite, detalhe de Apply
- **P3** qual frase de overlay/skill se move — aceite, detalhe de Apply
- **P3** PATCH versus substituição do comentário de Pronto — aceite, detalhe de Apply
- **P3** teto da `message` de T16 — aceite, detalhe de Apply

Pendências não bloqueantes: as P3 acima. Sem P0/P1 aberto.

- Prototype: N/A — harness de fechamento de release, sem ecrã
- Snapshot: `.impeccable/critique/1059-design-critic-20260927T203217Z.md`
- Tokens: `UI impact: none` / `live_route: N/A` / `surface: none`

Design Agent verdict: PASS

proxy modelo: design-autor → Grok 4.7 (grok-4.7)
proxy modelo: design-critic → Grok 4.7 (grok-4.7)
proxy modelo: design-autor (rework) → Grok 4.7 (grok-4.7)
