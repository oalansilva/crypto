## Context

Status: Design. Briefing copiado do issue #1135 (REST, 2026-10-28) em `proposal.md`. O issue deixou com o Design: o jeito do executor, por qual cliente começar e como o comando chega ao executor.

UI impact: none
live_route: N/A — card de processo/harness, nenhuma tela do produto muda
surface: none

Sem superfície: o card mexe em `scripts/process-fsm/`, na FSM, nas regras escritas, no registro de hooks na conta e na configuração do GitHub. Prototype: N/A. Impeccable: N/A (nenhuma tela, componente ou texto de produto muda; o texto que o Alan lê no chat e na issue é contrato de processo, fixado nas specs).

Fatos verificados em 2026-10-28 (repo no worktree do card, VM `instance-20260525-0958`, aarch64):

- **Usuário do agente = root.** `id`: `ubuntu` (uid 1001) nos grupos `sudo`, `docker` e `lxd`. `sudo -n -l`: `(ALL : ALL) ALL` e `(ALL) NOPASSWD: ALL`. Todos os clientes (Claude Code, Cursor, Codex, OpenCode, Grok, dsh) rodam como `ubuntu`, e os hooks deles também. O deploy de PROD do overlay (`docs/crypto-overlay.md:36`: `git reset` no source PROD `root:root`, `alembic`, build, `systemctl restart`) e os instaladores `install-*-systemd.sh` (`sudo -n`) dependem desse sudo sem senha. O Redis do DEV e o de PROD rodam em Docker (`redis_dev-redis-1`, `redis_prod-redis-1`).
- **Credencial GitHub na VM:** `gh auth status` = `oalansilva`, token `gho_` em `~/.config/gh/hosts.yml`, escopos `admin:public_key, gist, project, read:org, repo, workflow`; nenhum `GH_TOKEN` no ambiente; sem `~/.git-credentials`.
- **Board:** Project 1 (`PVT_kwHOAAHtBM4BV8b2`) é **público**; repo `oalansilva/crypto` é público. Workflows do Project ligados: só "Auto-add sub-issues to project" e "Item added to project" (nenhum muda Status de item já no board).
- **Quem move hoje:** `process_event.py` → `GhBoardMover` (`:99-143`, `gh project item-edit`), chamado por `_safe_move` (`:212`). `HUMAN_EVENTS` (`:74-76`, os seis) recusam com `reason=actor` (`:486-487`). `criar_card` devolve `not_implemented`. O agente também usa `gh project item-add` (`github-project-board/SKILL.md:128`).
- **Bloqueio de hoje:** regex em `board_status.is_status_edit_command` (`:58-78`), usada pela Guard em `guard.py:919-920`. É cooperativo.
- **Digest do design:** `compute_digest` (`process_event.py:236`, sha256 de `design.md` e dos arquivos do protótipo), gravado em `.design-digest` depois do move do T5 (`:782-783`). `guard.py:462-466` nega outra escrita. O yaml põe `freeze_digest` no T7 (`.cursor/process-fsm.yaml:123`), mas a escrita é no T5.
- **Portões na FSM:** `actor: Alan` em T1 (`yaml:117`), T2 (`:118`), T6 (`:122`), T7 (`:123`), T15 (`:131`), T18 (`:132`, guarda `motivo_visivel`). T3 é do Agent (`:119`). `ALAN_GATES` (`fsm.py:63`) e I2 (`yaml:44-45`) citam só T1/T7/T15/T18.
- **Texto always-on:** `AGENTS.md` é gerado por `overlay.render_agents` (`overlay.py:432`; linhas 442 "Chat é wording" e 446 "Alan único em T1/T7/T15/T18"). `test_paging.py:375` exige `T1/T7/T15` no AGENTS.md. A página do processo repete "Chat é wording" (`paging.py:28`, `.cursor/hooks/process-fsm-session-start.sh:9`).
- **Shim da conta:** `~/.config/covenant-flow/shim/current` → 1.1.0. `GATING_EVENTS`/`SESSION_EVENTS` (`cf_shim.py:68-73`) não têm evento de prompt.

Inventário do hook de "texto antes do agente" (string no binário instalado ≠ hook ensaiado):

| Cliente (versão) | Mecanismo no host | Registrado hoje | Neste card |
|---|---|---|---|
| Claude Code 2.1.308 (cli); app desktop por SSH relatou host 2.1.309 | `UserPromptSubmit` (58 linhas no binário; pode bloquear o prompt, mostrar `systemMessage` e dar `additionalContext`) | não: `~/.claude/settings.json` tem SessionStart, PreToolUse, PostToolUse, SubagentStop, Stop | **começa aqui** |
| Cursor Agent 2026.10.01 | `beforeSubmitPrompt` (presente no JS do `cursor-agent`) | não: `~/.cursor/hooks.json` tem sessionStart, preToolUse, beforeShellExecution, afterFileEdit, stop, subagentStop | só board |
| Codex CLI 0.163.0 | `UserPromptSubmit` (13 linhas no binário nativo); exige também a revisão `/hooks` do Codex | não: `~/.codex/hooks.json` tem SessionStart, PreToolUse, PostToolUse, Stop | só board |
| OpenCode 1.18.32 | plugin `chat.message` (4 linhas no binário) | não: `.opencode/adapter` tem `tool.execute.before` (guard) e `tool.execute.after`/`event` (impeccable); plugin global `covenant-flow-shim.js` | só board |
| Grok Build 1.0.25 | `UserPromptSubmit` (19 linhas no binário) | não: `.grok/hooks/process-fsm.json` tem PreToolUse, SessionStart, PostToolUse | só board |
| dsh 0.1.5-rc.2 | nenhuma ocorrência de `UserPromptSubmit` no pacote; mecanismo não identificado | não | só board |

Regra de confiança R/A (`covenant-flow/SKILL.md`, "Registro dos hooks na conta"): hook novo só conta depois de `install.sh --account`, da revisão do operador (`cf_shim.py trust --record`) e de uma sessão nova. Hook não revisado não é garantia.

## Goals / Non-Goals

**Goals:**

- O Alan passa os seis portões com um comando exato no chat do Claude Code, com recibo na issue.
- Nenhum processo na VM tem token que escreva no Project 1. Todo movimento passa pelo executor, que confere coluna de origem, evento e ator.
- O agente continua andando pelo fluxo pelo `process_event`, sem passo novo para o Alan além da migração.
- A garantia real de cada caminho fica escrita, sem prometer mais do que a máquina dá.

**Non-Goals:**

- O que o issue lista em "Não entra".
- Tirar o root do usuário do agente (ver D5: vira card próprio).
- Hook de prompt em Cursor, Codex, OpenCode, Grok e dsh.
- Fazer o executor medir de novo as guardas que o `process_event` mede (G_design, checks_green, M_lote, reviewers_ok).

## Decisions

### D1. Executor fora da VM, em GitHub Actions

O executor é um workflow de GitHub Actions num repositório próprio (nome no Apply; aqui, "repo do executor"). Só ele guarda o token que escreve no Project: um PAT clássico do Alan com `project` e `public_repo`, como secret de um environment `portao` cujas branches de deploy são só `main`. O disparo é `repository_dispatch` (que sempre roda o workflow da branch padrão) com um pedido JSON. Cada pedido ganha um `request_id`, e o workflow roda com `concurrency` por card, então dois pedidos para o mesmo card nunca se cruzam.

Por que fora da VM: na VM, o usuário do agente tem sudo sem senha e está em `docker` e `lxd`, o que dá root por três caminhos. Um executor local em outro usuário (por exemplo `cf-portao`, com sudo restrito) teria o token num arquivo que o agente lê com `sudo cat`. Só valeria tirando o root do `ubuntu`, e isso quebra o deploy de PROD, os instaladores `sudo -n` e o Docker do Redis. Fora da VM, o token fica fora do alcance do agente mesmo com root.

Alternativas descartadas:

- (a) Usuário local com sudo restrito: descartada pelo root, como acima.
- (b) Serviço sempre ligado fora da VM (worker HTTP): exige infra nova e não ganha garantia sobre (D1).
- (c) GitHub App: não alcança Project de conta pessoal, só de organização (documentação; **não verificado**).
- (d) Workflow no próprio `crypto`: o agente faz merge em `develop` (T14) e em `main` (T16) e poderia mudar o workflow que segura o token.

Custo aceito: cada movimento leva o tempo de subir um job (estimado em 15–60 s, **não medido**). Se o GitHub Actions cair, o agente não move e o Alan continua arrastando.

### D2. Login próprio do agente

Uma conta GitHub do agente (nome no Apply) entra como colaboradora `write` no `crypto` (push, PR, merge, comentário, body do issue, Gist) e no repo do executor (para disparar). O `write` no repo do executor não é opcional: `POST /repos/{owner}/{repo}/dispatches` exige `Contents: write` (fine-grained) ou escopo `repo` (clássico) (docs do GitHub, "Permissions required for fine-grained personal access tokens" e "Create a repository dispatch event", consultadas em 2026-10-28). Esse mesmo `write` deixa o agente apagar run de workflow no repo do executor ("Write access to the repository is required", doc "Delete a workflow run"; endpoint `DELETE .../actions/runs/{id}` = `Actions: write`) e apagar comentário de issue no `crypto` (`DELETE .../issues/comments/{id}` = `Issues: write`). Ela não recebe papel no Project 1, que é público: o agente lê e não escreve. Permissão de Project é por papel no projeto inteiro e não vem do papel no repo (documentação do GitHub; **não testado**). O token dessa conta substitui o `oalansilva` em `~/.config/gh/hosts.yml` e passa a ser o único token GitHub na VM.

Efeito colateral bom: comentário do agente sai com o login do agente. A guarda `motivo_visivel` (spec `process-fsm`, "Agent-only comment MUST NOT satisfy") passa a ter como distinguir autor.

### D3. O que o executor confere e de onde vem a lei

O código do executor mora no `crypto` (`scripts/process-fsm/portao/`, testado no CI com quadro falso, sem GitHub). O repo do executor só tem o workflow e um arquivo `PIN` com o SHA do `crypto` que ele roda. O workflow faz checkout desse SHA e lê a FSM do mesmo SHA com `yaml.safe_load`. Trocar o `PIN` exige PR aprovado pelo Alan (ruleset na `main` do repo do executor, sem bypass para a conta do agente). Assim, nem código nem lei do executor mudam sem o Alan, o mesmo papel que a revisão A tem para o adapter.

A cada pedido, o executor:

1. lê o Status vivo do card com o próprio token;
2. acha a transição da FSM para `(Status vivo, evento)` e exige `de` do pedido = Status vivo = `from`;
3. exige ator do pedido ∈ `actor` da transição. Pedido do tipo `pedir` (agente) só aceita `Agent`, `Guard` e `CI`; evento com `actor: Alan` vira `recusado: actor`;
4. aplica a regra própria do evento (D7);
5. move, posta o recibo e devolve `{resultado, de, para, motivo, recibo_url, run_url}`.

Invariante embutida: se a FSM do `PIN` não tiver T1, T2, T6, T7, T15 e T18 só com `Alan`, o executor recusa tudo (`lei_invalida`). As guardas medidas no VM (G_design, checks_green, M_lote, reviewers_ok) continuam no `process_event`, cooperativas como hoje.

### D4. Contrato do pedido e do recibo

Pedido (`client_payload`): `request_id`, `tipo` (`pedir` | `capturar`), `evento`, `card`, `de`, `ator`, `cliente`, `superficie`, `versao_host`, `sessao`, e extras por evento (`digest` no T5 e no T7, `motivo` em T6/T18/T2, `pacote` no T16).

Recibo: comentário na issue, postado com o token do executor. Para comando do Alan, o recibo sai em todo comando reconhecido, tenha movido ou sido recusado. Texto que não casa com a gramática não gera nada. Formato:

```
<linha de motivo, quando houver: "Devolver design: …" | "Não homologar: …" | "Cancelar: …">
Portão: `<comando como digitado>` — <movido De → Para | recusado: motivo>
Quando: <AAAA-MM-DD HH:MM BRT> · Cliente: <cliente>/<superfície> <versão> · Sessão: <id curto>
Executor: <run_url> · Lei: crypto@<SHA do PIN>
```

A linha de motivo vem primeiro para o detector atual de `Não homologar:` seguir valendo. Movimento pedido pelo agente leva o mesmo recibo com `Pedido do agente: <evento>`. Recibo e run são registro, não prova: o agente apaga os dois com o `write` que já tem (D2), e nenhum deles avisa o Alan (D5).

### D5. Captura do comando: o que dá para garantir

Ponto central: o texto que o Alan digita só chega a processos da VM que rodam como `ubuntu`: o host do cliente, o hook e as ferramentas do agente. O hook não tem nada que o agente não possa ler, escrever ou imitar. O agente pode montar o mesmo payload e chamar o mesmo caminho de captura, editar o transcript (mesmo dono) ou, com root, qualquer outra coisa. Conferir árvore de processos não resolve: a ferramenta Bash do agente também é filha do host, e `exec` deixa o processo dela com a mesma forma de um hook.

Conclusão, dita explicitamente: **com a arquitetura atual (ferramentas do agente no mesmo usuário do sistema do host, e esse usuário com root), nenhum cliente chega a "não forjável". Neste card, a captura do comando do Alan é "cooperativa".** O rastro também é cooperativo, pelos três fatos abaixo. Este card entrega esse nível no Claude Code e deixa os outros clientes só com o board.

Por que o rastro não segura um agente decidido:

1. **O agente apaga o rastro.** Ele tem `write` no repo do executor (exigido para disparar) e no `crypto` (D2), o que basta para apagar o run e o recibo.
2. **O recibo não avisa o Alan.** Ele sai com o PAT do Alan, então o autor é `oalansilva`. O GitHub não notifica a pessoa da própria atividade (comportamento conhecido; as páginas de notificação consultadas não tratam disso: **não verificado** em documentação). Um recibo forjado fica na issue sem chegar ao Alan.
3. **O run não distingue o verdadeiro do forjado.** Todo disparo, o do hook e o forjado, sai com o mesmo token da VM (o do agente depois da migração). Forjar um portão é um `gh api repos/<executor>/dispatches` com `tipo=capturar` e `ator=Alan`, e quem segura isso é só a regex da Guard (D9).

O que este card garante de verdade:

- O agente não tem token que escreva no Project 1, com root ou sem root (D1, D2). Não existe mais `item-edit` direto, só pedido ao executor.
- O executor só move por aresta da FSM fixada no `PIN`, com coluna de origem conferida. Isso vale até para pedido forjado: um `capturar` forjado só passa um portão que esteja de fato na coluna de origem.
- Pedido `pedir` com evento do Alan é recusado (`actor`). Forjar exige montar um `capturar`, um ato deliberado que a Guard nega (cooperativo) e que, se não for apagado, fica no run e no recibo.

O que este card não garante: que um agente decidido a burlar não consiga forjar um comando do Alan e apagar o que ficou.

Alternativa avaliada e deixada para o card de separação de usuário: tirar o rastro do alcance de escrita do agente. O pedido viraria uma issue aberta pela conta do agente num repo de entrada onde ela não tem papel, e um workflow disparado pelo evento `issues` conferiria o autor. O Alan seria avisado pelo watch do repo, porque a issue tem outro autor. Não entra aqui por três motivos: muda o canal de disparo; depende de comportamento do GitHub **não verificado** (quem apaga issue, notificação por watch, filtro de autor no evento); e mesmo assim só avisaria depois, sem impedir a forja nem distinguir o verdadeiro do forjado. Para chegar a "não forjável", as ferramentas do agente teriam de rodar num usuário do sistema diferente do host que recebe o texto, e esse usuário não poderia ter root (sem sudo livre, `docker` e `lxd`, com deploy de PROD e instaladores por regra estreita ou por usuário de deploy). Nenhum cliente instalado faz essa separação hoje. Fica como card seguinte, que o Alan decide abrir. Aqui ele só é nomeado; o card não é criado.

Por que começar no Claude Code: é a superfície que o Alan usa hoje (comentários do grill do #1135: `claude-desktop`). O `UserPromptSubmit` documenta bloquear, mostrar mensagem ao usuário e injetar contexto, e o registro na conta, o shim e o adapter Claude já existem (#1101/#1103).

### D6. Gramática exata

Casa só se a mensagem inteira, sem o espaço final, for uma destas linhas. Diferença de maiúscula, palavra a mais, segunda linha ou espaço duplo não casa:

```
/priorizar <card>
/aprovar-design <card>
/devolver-design <card> "<motivo>"
/homologar <card>
/nao-homologar <card> "<motivo>"
/cancelar <card> "<motivo>"
/confirmar-cancelar <card>
```

`<card>` = número do issue, com ou sem `#` (`1135` ou `#1135`). `<motivo>` = texto entre aspas duplas, sem aspas nem quebra de linha dentro, com pelo menos um caractere visível, até 500 caracteres.

Fontes que nunca disparam:

- Comentário de issue: o executor não lê comentários como entrada.
- Resposta de ferramenta: não passa pelo hook de prompt.
- Texto colado junto com outra coisa: a mensagem inteira não casa.

O host não diferencia colar a linha exata, sozinha, de digitá-la (**não verificado** se o Claude Code marca colagem no payload). Nesse caso o comando vale, porque é o Alan no teclado mandando exatamente o comando. Isso fica visível para o Alan aqui e no crítico.

### D7. Semântica por comando

- `/priorizar N`: o executor faz T1 (exige Em Refinamento) e, no mesmo run, T3 com ator `Agent`, conferido pela mesma regra de um pedido do agente (Todo → Design). Se o T3 falhar (Status mudou entre os dois, erro do board, cota), o card fica em Todo e a resposta e o recibo dizem por quê. A pré-checagem de hooks que o `process_event` faz para `iniciar_design` já está satisfeita: o adapter só roda depois de o shim conferir R/A. O worktree `card-N-*` continua com o agente (Guard não condiciona `git worktree add` ao Status). Arrastar para Todo continua só T1.
- `/aprovar-design N`: exige Aprovação de Design. O hook acha o worktree `card-N-*` e a change do card, calcula `compute_digest` e manda junto. O executor compara com o digest do último T5 do card (vindo no pedido do agente no T5 e guardado no input do run e no recibo). Se forem diferentes, recusa com "design mudou desde o envio para aprovação (T5 em <data>)". Sem worktree ou sem T5 registrado, também recusa, dizendo qual. O Alan não digita digest. No yaml, `freeze_digest` sai do T7 e vai para o T5, e o T7 ganha `check_digest` (fsm.py não valida ações). O `.design-digest` local continua para I4/T17.
- `/devolver-design N "m"` (T6), `/nao-homologar N "m"` (T18), `/cancelar N "m"`: motivo obrigatório; sem motivo a gramática não casa. Linha de motivo no recibo: `Devolver design: m`, `Não homologar: m` (satisfaz `motivo_visivel`), `Cancelar: m`.
- `/cancelar N "m"`: o executor confere que o card está numa coluna viva, não move e responde `Cancelar #N «<título>»? Para confirmar: /confirmar-cancelar N`. O recibo diz "pendente". `/confirmar-cancelar N` só move se houver `/cancelar` pendente do mesmo card nos últimos 10 minutos. O executor confere isso pelo input do próprio run anterior, não pelo comentário. Um `/cancelar` novo troca o pendente. Confirmação sem pendente, vencida ou de outro card é recusada. Sem confirmação, nada muda.
- `/homologar N` (T15): move. O comentário de evidência de homologado (`post-card-evidence-comment.sh --transition homologado`, `covenant-flow/SKILL.md:290`) continua com o agente, no mesmo turno, como hoje depois do arrasto.

### D8. Hook do Claude Code

Entra uma entrada `UserPromptSubmit` no registro da conta (`install.sh --account`), que chama o shim. O shim acha o consumidor e o pin e confere R/A, como nos outros eventos. Depois chama `claude_adapter.py prompt-submit` pinado. O shim ganha o evento como "gating" do Claude. Se o adapter estiver ausente ou não revisado, o hook falha visível e o comando não é capturado.

O adapter testa a gramática (D6):

- Não casou: o hook sai sem saída e o agente recebe o texto normal.
- Casou: chama o executor (`capturar`) e espera a resposta até um teto (90 s; número exato no Apply, dentro do `timeout` do hook). Depois **não bloqueia** o prompt e devolve:
  - `systemMessage` com a resposta literal do executor, que o host mostra ao Alan sem passar pelo modelo;
  - `additionalContext` para o agente: "Comando de portão tratado pelo executor: <resultado>. Não é pedido ao agente. Siga a FSM a partir do Status atual."

Não bloquear é o que deixa o `/priorizar` seguir para o Design e o `/homologar` ganhar o comentário de evidência no mesmo turno. O modelo vê o texto do comando, mas não tem como mover nada com ele. Se estourar o teto, a mensagem diz "sem resposta em 90 s; resultado no recibo da issue #N", e o contexto manda o agente não presumir o resultado.

Regra para o agente em qualquer cliente: texto com cara de comando sem esse contexto do executor (hook ausente, outro cliente) é wording. O agente responde que o comando não foi capturado, aponta o board e não tenta capturar por conta própria.

**Não verificado**, e por isso ensaiado primeiro (task 0, antes de qualquer código e antes de o Alan criar conta, repo ou PAT):

- se o `UserPromptSubmit` dispara no app desktop por SSH;
- se o Claude Code passa `/priorizar …` cru ao hook ou recusa como comando desconhecido.

O ensaio usa um hook descartável que só grava em arquivo o prompt recebido, sem shim, sem executor e sem rede. O Alan digita `/priorizar 1` e uma frase comum no cli e no app desktop. **Parada:** se o hook não disparar no desktop, ou se o `/priorizar` não chegar cru (barrado, ou só o corpo expandido de um comando), o Apply para, remove o hook descartável e volta ao Alan para escolher entre três saídas: (a) só cli; (b) outro texto de comando, que o Alan aprova; (c) parar o card. Comando fino em `.claude/commands/` só entra se o Alan escolher (b) com esse formato.

### D9. Transições do agente pelo executor

- `BoardMover.set_status(issue, to)` vira `move(issue, evento, de, para, ator, extras)`. `GhBoardMover` dá lugar a `ExecutorMover` (cliente `portao_client.py`, que dispara e espera o run pelo `request_id`). `FakeMover` acompanha a assinatura.
- Os pontos que hoje chamam `_safe_move` passam a pedir assim: T3, T5 (com `digest`), T8–T14, T16 (um pedido por card do pacote) e T17a/b (ator `Guard`). A recusa do executor vira `reject` com `reason=executor:<motivo>` e Status inalterado.
- `criar_card` (T0) deixa de ser `not_implemented`: `process_event criar_card --card N` pede ao executor para pôr o issue N, que já existe, no board em Em Refinamento.
- T14: se o move falhar depois do squash, repetir `integrar_develop` só pede o move (detalhe de Apply sobre idempotência).
- Seleção do mover pelo overlay: com `board.executor` (repo e workflow), usa `ExecutorMover`; sem ele, o mover atual. Assim a migração não deixa o fluxo sem mover (Migration Plan).
- Guard: continua negando `item-edit`/GraphQL de Status e passa a negar Bash que chame o caminho `capturar` ou o endpoint `dispatches` do repo do executor fora de `process_event.py`. Cooperativo, como a regra atual.
- Arrasto fora de δ (Done → Em desenvolvimento sem `Não homologar:`): o agente não tem mais como restaurar Done. Ele comenta pedindo o motivo e não segue o Apply até o comentário existir.

### D10. Regras escritas

- `overlay.render_agents` (AGENTS.md), mesmas contagens de linha:
  - `:442` → "Texto livre é wording; comando exato capturado fora do agente é evento do Alan. NLU ≠ δ. `implemente` ∉ δ."
  - `:446` → "Portões do Alan: T1, T2, T6, T7, T15, T18 (board ou comando exato). Agent não move Status: pede pelo `process_event`. T16 = `process_event fechar_release`."
  - `test_paging.py:375` passa a exigir os seis portões em vez de `T1/T7/T15`.
- `paging.py:28` e `process-fsm-session-start.sh:9`: mesma troca da frase de wording.
- `covenant-flow/SKILL.md`: linha 172 (gates humanos com T6 e T2 e o caminho por comando), tabela da linha 176, linha 40 ("Pai orquestra: `process_event`…" passa a dizer que o move é do executor) e uma subseção curta "Comandos de portão" com a gramática, o nível "cooperativo" (o agente apaga run e recibo, e o recibo não avisa o Alan) e a regra do texto sem contexto do executor.
- `github-project-board/SKILL.md` (linhas 42–43 e 128–140) e `references/project-board-commands.md` (38–40, 83, 101): `item-add`/`item-edit` saem do roteiro do agente e entram "o agente não move nem adiciona; pede pelo `process_event`". A restauração de arrasto fora de δ segue D9.
- `fsm.py:63` `ALAN_GATES` com os seis. Texto de I2 (`yaml:45`) com os seis. Ações de T5/T7 conforme D7.

### D11. Verificação

Testes unitários (CI, sem GitHub; executor com quadro falso):

- Para cada um dos seis comandos e para a confirmação: a linha exata move. Variações não casam: "aprova aí", `/Aprovar-design 1135`, `/aprovar-design 1135 ok`, texto antes, duas linhas, espaço duplo, motivo vazio ou sem aspas.
- Coluna de origem errada recusa com o Status atual no motivo.
- `/priorizar` com T3 recusado deixa em Todo com motivo.
- Digest diferente do T5 recusa.
- `/confirmar-cancelar` sem pendente ou vencido recusa.
- Pedido `pedir` de qualquer evento do Alan → `actor`.
- `pedir` de T9 com `de` certo move; com `de` errado recusa.
- FSM com Agent num portão → `lei_invalida`.
- `process_event` com `FakeExecutor`: T0, T5 com digest, T16 por card.
- Guard nega `capturar`/`dispatches`.
- Textos do AGENTS.md e da página.

Ensaio vivo (QA, num issue de ensaio no Project 1, comandos digitados pelo Alan no cli e no app desktop):

- cada comando certo move e deixa recibo; o aproximado e o mesmo texto como comentário na issue não fazem nada;
- `/priorizar` termina em Design sem outro pedido;
- arrastar para Todo fica em Todo;
- `/aprovar-design` depois de mexer no `design.md` é recusado;
- `/cancelar` sem confirmação não move;
- `process_event pedir_review` move pelo executor e `process_event aprovar_design` é recusado;
- no terminal do Alan, com o token do agente, `gh project item-edit` do Status falha por permissão.

## Risks / Trade-offs

- [Comando do Alan forjado por agente deliberado] → nível declarado "cooperativo" (D5). Forjar é um `dispatches` com `tipo=capturar`, que só a regex da Guard nega. O executor ainda exige a coluna de origem certa. Run e recibo podem ser apagados pelo agente e não avisam o Alan. A diferença para a História fica com o card de separação de usuário (futuro, não criado), nomeado no `proposal.md`.
- [GitHub Actions lento ou fora] → o agente recebe recusa visível (`executor:timeout`/`executor:indisponivel`) e não presume nada. O Alan arrasta no navegador, que não depende da VM.
- [PAT clássico do Alan com `public_repo` alcança todos os repos públicos dele] → só existe como secret do environment `portao` (branch `main`, sem bypass). Rotação documentada. Fine-grained não alcança Project pessoal (**não verificado**).
- [Lei do executor (`PIN`) atrás da lei do worktree] → pedido válido no worktree e inválido no `PIN` é recusado visível (`executor:no_edge`). Mudar a FSM passa a exigir subir o `PIN`, o que é raro e aprovado pelo Alan.
- [Hook não dispara no app desktop, ou `/priorizar` não chega cru] → task 0, antes da task 1 e do passo 1 do Alan, com parada e volta ao Alan (D8: só cli, outro texto ou parar). Nada de conta, repo, PAT ou código é feito antes dessa resposta.
- [Agente apaga recibo ou run] → aceito no nível "cooperativo". Não há rastro durável fora do alcance do agente neste card (D5).
- [Digest medido na VM] → o executor só guarda e compara, então a conferência é cooperativa. O ganho é pegar mudança feita depois do T5 por descuido, que é o caso do issue.

## Migration Plan

Ordem pensada para nunca ficar sem mover o board. O arrasto do Alan no navegador funciona em todos os passos.

0. **Ensaio do host (task 0), antes de tudo:** o Alan registra o hook descartável (D8), digita no cli e no app desktop, e o resultado vai para o card. Se falhar, para aqui e volta ao Alan. Só depois vêm o passo 1 e a task 1.
1. **Alan, no GitHub:** cria a conta do agente e a convida (`write`) no `crypto`. Cria o repo do executor, com ruleset na `main` (PR com aprovação do Alan, sem bypass para o agente) e environment `portao` (só `main`). Cria o PAT clássico (`project`, `public_repo`) como secret do environment. Convida o agente (`write`) no repo do executor.
2. **Apply do card:** executor, cliente, `ExecutorMover`, hook, Guard e regras. A chave `board.executor` do overlay **ainda desligada**, então o card anda com o mover atual.
3. **Alan:** sobe o workflow e o `PIN` (SHA revisado no Code Review) no repo do executor e aprova. Roda `install.sh --account` (entrada `UserPromptSubmit`), faz a revisão R/A e abre sessão nova.
4. **Ensaio com o token antigo ainda na VM:** pedido do agente pelo executor e comandos do Alan no issue de ensaio (D11). Passou: liga `board.executor` no último commit do card antes do T14. A partir do merge, o `process_event` move pelo executor.
5. **Alan, na VM e no GitHub:** `gh auth login` com a conta do agente (substitui `oalansilva` em `hosts.yml`) e chave SSH do agente para `git push`. Revoga o token do GitHub CLI do `oalansilva` em Settings → Applications. Isso revoga todos os tokens desse app, então o Alan confere antes se usa o `gh` em outra máquina. Inventário de outras credenciais GitHub do Alan na VM (bws, `.env`): remover as que tiverem `project`.
6. **Teste final:** com o token do agente, `item-edit` do Status falha. O agente passa uma transição pelo executor. O Alan passa um comando.

Card em Aprovação de Design na hora da virada não tem T5 registrado no executor, então o `/aprovar-design` dele é recusado. O Alan arrasta esse card no board ou o agente o devolve e reenvia (T6 + T5 pelo executor).

Volta: desligar `board.executor` (PR) devolve o mover antigo, mas ele só funciona se o `gh` da VM voltar a ter escrita no Project, o que significa o Alan logar de novo de propósito. Enquanto isso, o board por arrasto continua.

## Detalhes de Apply aceitos

P3 do crítico, resolvidos no Apply e não reabertos:

- Card em Aprovação de Design na virada, sem T5 no executor: arrastar ou reenviar (Migration Plan).
- `timeout` do hook `UserPromptSubmit` ≥ teto de espera. O padrão de 60 s fica abaixo dos 90 s, então o registro na conta fixa um valor explícito.
- Latência do Actions: medir no ensaio (Open Questions).
- `test_paging.py:344` também testa `T1/T7/T15` (`not in`) e entra no ajuste junto com a linha 375.
- Origem do `/cancelar`: alinhar a "coluna viva" do executor com o `from: Vivo` do T2 em `fsm.py`.
- GitHub App e PAT fine-grained sem alcance em Project pessoal: **não verificado**. O Apply confere antes do passo 1 do Alan.
- Ordem de ligar `board.executor` em relação ao T14 deste card: o Apply fixa se o commit que liga a chave entra antes ou depois do move do próprio T14.

## Open Questions

- Nomes da conta do agente e do repo do executor: escolha do Alan no passo 1, sem efeito no contrato.
- Teto de espera do hook (90 s) e latência real do Actions: medir no ensaio. Se a latência for alta demais para o fluxo, o ajuste é de número, não de desenho.

## Design Critique

- P1 — Garantia da História vs D5: o rastro estava prometido acima do que entrega (o agente com `write` apaga runs e recibos; o recibo sai como `oalansilva` e não avisa o Alan; todo disparo sai com o token da VM; forjar um portão é um `dispatches` com `capturar`, segurado só pela regex da Guard). Disposition: resolvido no rework. O nível declarado baixou para "cooperativo" (D2, D4, D5, D10, Risks, spec `alan-gate-commands`), e o `proposal.md` diz o que a História pede, o que este card entrega e que a diferença fica para o card de separação de usuário (futuro). O Alan decide essa diferença na Aprovação de Design.
- P2 — Riscos do host (`UserPromptSubmit` no app desktop por SSH; `/priorizar` cru no hook) sem ponto de parada. Disposition: resolvido no rework com a task 0 (hook descartável que só registra o prompt, rodado pelo Alan no cli e no desktop antes da task 1 e da 5.2; se falhar, o Apply para e volta ao Alan).
- P3 — detalhe de Apply (aceito): cards em Aprovação de Design na virada sem T5 no executor; `timeout` do hook ≥ teto de espera; latência do Actions a medir no ensaio; `test_paging.py:344`; origem do `/cancelar` alinhada com `from: Vivo`; GitHub App e PAT fine-grained não verificados; ordem de ligar `board.executor` em relação ao T14 deste card. Registrados em "Detalhes de Apply aceitos".
- Sem achado: tokens `UI impact`/`live_route`/`surface` parseáveis e coerentes com sem-tela; briefing idêntico ao issue; todo bullet de Entra tem decisão, cenário e task; Não entra respeitado; AGENTS.md curto com os seis portões.
- Teto: 1 autor + 1 crítico + 1 rework (sem-tela), fechado.
- Verdict: approve após rework.
