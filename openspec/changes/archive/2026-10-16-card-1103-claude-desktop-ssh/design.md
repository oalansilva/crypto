UI impact: none
live_route: N/A — harness de processo; superfície do app desktop do Claude, sem tela do produto
surface: none

Ausência justificada: este card muda só o processo local (shim da conta, adapter Claude Code, coletor de evidência, Guard, instalador, regras e runbook) para valer também no app desktop do Claude no Windows ligado à VM por SSH. O app é do fornecedor; não há tela, rota ou componente do Cripto Farol. Prototype: N/A; nenhum HTML gerado ou copiado. Impeccable: N/A, porque não existe superfície visual do produto; crítica de Design e aprovação humana (T7) continuam obrigatórias.

## Context

O body grelhado do #1103 é a história; este documento só define o *como*. O #1101 (Done técnico, `78d09838` em `develop`) entregou o adapter Claude Code cooperativo e não oficial, com registro dos hooks na conta, shim, revisão de confiança em duas partes e aceitação de versão pelo formato, e o provou **só no terminal** da VM. O app desktop ficou para cá (#1101 design §7 e §12). Alan acrescentou ao escopo o residual de review do #1101 (comentários do #1103 listados no `proposal.md`, IDs R1–R36).

### O que a VM mostra hoje (inspeção de 2026-10-15)

Observado nesta conta, sem ler segredos (só nomes de variáveis e campos):

| Fato | Onde | Valor observado |
| --- | --- | --- |
| Cópia própria do Claude Code usada pelo app | `~/.claude/remote/ccd-cli/<versão>-<hash>` (binário único, ~255 MB) | `2.1.295-cdb4a4da2c4c` |
| Servidor do app na VM | `~/.claude/remote/srv/<hash>/server --serve --socket ~/.claude/remote/run/<id>/rpc.sock`, filho de `sshd` na porta 2200 | ativo |
| Terminal | `~/.local/bin/claude` (versões em `~/.local/share/claude/versions/`) | `2.1.300` |
| Superfície da sessão do app | `CLAUDE_CODE_ENTRYPOINT` do processo e campo `entrypoint` do transcript | `claude-desktop` (terminal: `cli`) |
| Outras marcas do app no ambiente | `CLAUDE_SSH_DAEMON_CHILD=1`, `CLAUDE_CODE_DESKTOP_APP_VERSION=2.37337.1`, `CLAUDE_AGENT_SDK_VERSION=0.3.295`, `CLAUDE_CODE_HOST_SESSION_ID`, `CLAUDE_CODE_ENABLE_ASK_USER_QUESTION_TOOL=true` | presentes |
| Lançamento da cópia | `--input-format/--output-format stream-json`, `--setting-sources=user,project,local`, `--permission-mode=auto`, `--model`/`--effort` escolhidos no app, `--plugin-dir ~/.claude/remote/plugins/...`, `--allowedTools` com ferramentas `mcp__ccd_*` (entre elas `mcp__ccd_session__spawn_task` e `mcp__ccd_session_mgmt__send_message`) | observado no `argv` |
| Transcript | mesmo lugar do terminal: `~/.claude/projects/<slug>/<sessão>.jsonl` e `<sessão>/subagents/agent-<id>.jsonl` + `.meta.json`, com `version`, `entrypoint`, `cwd`, `message.model`, `effort`, `toolUseResult.resolvedModel` | igual ao formato `claude-transcript-v1` |
| Primeira sessão real pelo app | a grelha do próprio #1103 (sessão `92c55543…`, cwd `/source`, 02:43–02:57) | pai e filho em `2.1.295`/`claude-desktop`; o filho `grill-card #1103` nasceu **sem `effort`** e rodou em `medium`; sem heartbeat do shim (o registro na conta foi instalado depois, ~02:59) |
| Git do próprio app | log do servidor: "this host's git works on Claude's own copy of a repository's settings (a shadow directory): a repository's own git config and hooks are not read" | só para o painel de git do app |
| Pasta própria do app | doc do Desktop: opção *worktree* cria `<raiz-do-projeto>/.claude/worktrees/<nome>` por padrão; no SSH vale a "Worktree folder" da conexão, senão `worktree.location` em `~/.claude/settings.json`; prefixo de branch configurável | nenhuma criada nesta VM até agora; `.claude/worktrees/` não está no `.gitignore` |

Consequências diretas no código atual: `claude_evidence.py` recusa a sessão do app (`QUALIFIED_ENTRYPOINTS = ("cli",)` → `unverified`); `model_selection.claude_detect_version` cai para `claude --version` quando falta `AI_AGENT`, e dentro do app isso leria o binário do terminal (`2.1.300`), não a cópia do app (`2.1.295`); o app abre em modo `auto`; e o app oferece um caminho de "abrir outra sessão" que não passa pelo `Agent`.

A sessão de grelha acima mostra o problema que o card quer fechar: sem o registro na conta ativo, um filho nasceu pelo app sem `effort` explícito e ninguém recusou.

## Goals / Non-Goals

**Goals:**

- O app desktop por SSH vale como superfície do cliente `claude`, com o mesmo processo do terminal: página, Guard por etapa, modelo por faixa, evidência por filho e recusa visível.
- Decidir e explicar o que acontece quando o app abre sessão numa pasta própria.
- Alan acompanha sessão e filhos pelo app; o Status segue no board.
- Fechar o residual do #1101 (R1–R36), com o grupo de digest antes de qualquer outra edição do adapter.
- Ensaio real: um card conduzido pelo app, com evidência.

**Non-Goals:**

- Mudar a FSM, os gates ou a seleção de modelos definidos no #1101 (Não entra). Nenhuma aresta, estado, ator ou par de modelos novo; nenhum cliente novo em `--client`.
- Rodar o Claude Code na nuvem ou em outra máquina; Desktop *local* no Windows continua falhando visivelmente (sem seleção, board nem worktree da VM).
- Outros clientes (Cursor, Codex, OpenCode, Grok Build, dsh) operados pelo app. O residual toca shim/instalador desses clientes só onde o #1101 já os colocou (R9, R10, R12, R18, R19), sem mudar a lei deles.
- Oficializar o Claude Code (`AGENTS.md`, linha "Cliente ativo", board): continua no card de seguimento do #1101.
- Controlar o painel de git do app (commit/PR por botão): é ação humana de Alan na interface, fora do agente.

## Decisions

### 1. Mesmo cliente, superfície nova: `claude-desktop`

O app é o cliente `claude` rodando na VM por outra porta de entrada. Não nasce `--client claude-desktop`, nem bloco novo na seleção, nem adapter novo: o shim da conta já é carregado pela cópia do app (`--setting-sources` inclui `user`), e o adapter pinado é o mesmo.

O que muda é a lista de superfícies conhecidas. `QUALIFIED_ENTRYPOINTS` passa a `("cli", "claude-desktop")`, mas o valor novo só entra junto com uma fixture **real** e sanitizada do transcript do app (pai e filho), tirada de uma sessão real do app (a da grelha do #1103 já serve de fonte de formato; task 4.4), como foi feito com `PRETOOL_AGENT_2_1_296` no #1101. Sem ela, `claude-desktop` continua `unverified`, e é isso que deve aparecer se alguém tentar seguir pelo app com o pin atual. O ensaio vivo (§11) confirma o resto: hooks, heartbeat e nascimentos na cópia do app.

A superfície é registrada em toda a cadeia: heartbeat do shim (`entrypoint`, `host_version`, mais `desktop_app_version` e `ssh` quando presentes no ambiente), receipt do `prepare`, evidência do `collect`, linha do `claude_proxy` e handoff. Uma sessão com mais de um `entrypoint` no transcript (por exemplo, aberta no app e retomada no terminal) continua recusada (`unverified`), como hoje: não se mistura prova de duas superfícies na mesma sessão.

Alternativa rejeitada: cliente `claude-desktop` próprio. Duplicaria seleção, captura e testes para o mesmo binário e mudaria `--client`, o que o "Não entra" fecha.

### 2. Versão e superfície vêm da sessão, nunca do binário do PATH

Dentro de uma sessão Claude Code (`CLAUDECODE=1`), versão do host = `AI_AGENT` da sessão, confirmada pelo `version` do transcript no `prepare`. O fallback `claude --version` só vale fora de sessão (operador rodando `resolve` num shell comum). Dentro do app, falta de `AI_AGENT` vira `capability_unavailable` visível, citando a superfície; nunca se mede o binário do terminal.

Pisos de capacidade continuam os do #1101: `effort` por invocação ≥ 2.1.292; hooks com `onFailure: "block"` ≥ 2.1.295. A cópia do app observada está exatamente em 2.1.295. R14 se resolve aqui: o código passa a aplicar também o piso 2.1.295 nas transições e nascimentos que dependem de hook, igualando código, doc e design; abaixo dele, `capability_unavailable`.

### 3. Quando o app abre a sessão numa pasta própria (decisão pedida pela grelha)

**Para Alan, em linguagem de operador:**

> Se o app abrir a sessão numa pasta que ele mesmo criou (a opção *worktree* do app, que cria uma cópia em `/source/.claude/worktrees/<nome>` num branch com nome do app), essa pasta **não é a pasta de trabalho de nenhum card**. O processo continua ligado ali, mas trata a pasta como "sem card": a primeira resposta diz "pasta criada pelo app, fora do worktree do card", nenhuma edição de produto nem de OpenSpec é aceita, nenhum filho de etapa nasce e nenhuma coluna anda. Para trabalhar no card, peça `#<id>` na mesma sessão: ela entra sozinha no worktree do card (`card-<id>-*`) com `EnterWorktree`, como já faz a partir de `/source`, e você não troca de pasta. A pasta do app não é apagada nem aproveitada; você a arquiva no próprio app quando quiser. O jeito recomendado é abrir as sessões no app em `/source`, com a opção *worktree* desligada.

**Como funciona:**

- O vínculo de card continua sendo só o branch `card-<id>-*` do worktree (`q_git`). O branch que o app cria não tem esse formato, então a pasta cai na regra existente "sem card": Guard nega escrita de produto (`fail_closed`), `prepare` recusa porque o cwd não é worktree de card, e `process_event` recusa. Nenhuma regra nova de Guard.
- O que é novo é só a **mensagem**: quando a raiz do worktree está sob um segmento `.claude/worktrees/` ou sob a "Worktree folder"/`worktree.location` configurada, a página e o motivo do deny dizem `pasta do app (sem card)` e a recuperação (`#<id>` → `EnterWorktree`). Em outra pasta sem card, a mensagem genérica de hoje.
- Pasta do app **fora** de repositório pinado (por exemplo a home): sem pin, o shim não faz nada (regra do #1101). Não há card para proteger ali; o runbook diz que sessão sem a linha de processo na primeira resposta está fora do processo.
- `.claude/worktrees/` entra no `.gitignore` do consumidor, para a pasta do app não sujar `git status` em `/source` (que o fecho de lote exige limpo).

Alternativas rejeitadas: **adotar** a pasta do app como worktree do card (criaria um segundo worktree por card, com branch fora do padrão, e quebraria `q_git`, review por diff e T14); **apagar** a pasta automaticamente (efeito destrutivo fora do pedido); **recusar a sessão inteira** (impediria justamente a saída por `EnterWorktree`).

### 4. Sessão nasce em `/source` e segue para o worktree do card

Mesmo desenho do #1101 §14, agora no app: o app abre em `/source`; o pedido `#<id>` leva a sessão ao worktree por `EnterWorktree`; o shim usa o adapter da nova raiz já no primeiro evento e reinjeta a página do card por `PostToolUse(EnterWorktree)`. O ensaio confirma esse `additionalContext` na cópia do app.

R34 (achado 41): o achado era de `/source` ainda no pin antigo. Com o T14 do #1101, `develop` tem o pin novo; a reavaliação é feita no Apply, com teste: sessão em `/source` no pin atual recebe a página de `develop` (`q_git=develop`, sem card) com a instrução de `EnterWorktree`; se faltar, o `SessionStart` passa a injetá-la ali. O ensaio só verifica a página em `/source`.

### 5. Filho de etapa nasce só pelo `Agent`

O app expõe ferramentas que abrem ou dirigem **outra sessão** (observadas no `argv`: `mcp__ccd_session__spawn_task`, `mcp__ccd_session_mgmt__send_message`, entre outras `mcp__ccd_*`). Uma sessão aberta assim não tem captura de modelo, receipt nem verificação de primeira escrita. Decisão: com card vinculado, o `PreToolUse` nega as ferramentas `mcp__ccd_*` que criam sessão, mandam mensagem para outra sessão ou abrem sessão em outra pasta, com o motivo "filho de etapa nasce só pelo `Agent`". As de leitura e layout (listar sessões, painéis, título, plano) ficam livres. Sem card vinculado, ficam livres (não há etapa a proteger).

A lista exata de nomes é P3 (sai do `argv`/schema da versão ensaiada); o contrato é: nada que crie trabalho fora do `Agent` passa com card vinculado. Ferramenta `mcp__ccd_*` nova, não classificada, é tratada como criadora de sessão (deny) até ser classificada.

### 6. Acompanhar pelo app

- **Sessão do card:** a sessão leva `#<id>` no título (o pai usa a ferramenta de título do app quando vincula o card). O Status continua no board, no navegador; o título não é fonte de Status.
- **Filhos lado a lado:** o painel de tarefas/subagentes do app lista os filhos do `Agent` pelo `description`, que já é `<papel> <id> <único>` (a etapa: `design-autor`, `design-critic`, `apply`, `diff-reviewer`, `code-reviewer`, `qa`), e mostra o estado de cada um (resultado). Nada é construído no app.
- **Handoff:** ao fim de cada filho, o pai escreve no chat e no comentário do card uma linha por filho com cliente, superfície, modelo/esforço observados e status, tirada do proxy (nunca do pedido). Em evidência ausente ou divergente, a mesma linha diz qual gate reprovou.
- **Perguntas e aprovações:** a grelha usa `AskUserQuestion` (ativo na cópia do app; a grelha do #1103 já foi respondida por clique). T1/T7/T15/T18 continuam só de Alan, no board.

### 7. Modo de permissão do app não é autorização

O app abre a cópia com `--permission-mode=auto`. O processo não depende do modo: o deny dos hooks vale em `auto`, `acceptEdits`, `default` e `bypassPermissions`, e a página não diz "modo Auto" em lugar nenhum. O ensaio prova o deny com o app no modo em que ele abre. Instrução de chat continua não sendo autorização (`implemente` ∉ δ).

### 8. Falha visível no app, sem fallback

| Falta no app | O que Alan vê no chat do app | Onde |
| --- | --- | --- |
| superfície `claude-desktop` não ensaiada, ou transcript com campo faltando | `unverified` / `unsupported_schema` com campo e versão | `prepare`, `collect`, `process_event` |
| registro na conta não carregado (sem heartbeat do shim) | `hooks_inactive` + recuperação (sessão nova) | `process_event`, `prepare` |
| versão sem `effort` por invocação ou sem hook bloqueante | `capability_unavailable` com versão e superfície | `resolve`, `prepare` |
| `AI_AGENT` ausente | `capability_unavailable` (versão não lida na sessão) | `resolve`, `prepare` |
| spawn sem `model`/`effort` ou com par diferente da captura | deny do hook com o motivo | `PreToolUse(Agent)` |
| sessão pela ferramenta do app | deny "filho de etapa só pelo `Agent`" | `PreToolUse(mcp__ccd_*)` |
| pasta própria do app | página e deny com "pasta do app (sem card)" | `SessionStart`, `PreToolUse` |
| filho em segundo plano com notificação em formato não reconhecido | `unsupported_schema` citando o campo | `collect`, `claude_proxy` |

Em nenhum caso o pai passa a etapa ao terminal, troca de modelo ou omite `effort`. Alan pode abrir uma sessão no terminal por decisão dele; o agente nunca o faz como saída de falha.

### 9. Evidência e gates

`claude_evidence.py prepare/collect`, `claude_proxy.py`, `claude_review.py verify-wave` e `observe-parent` aceitam `claude-desktop` depois da fixture real, e registram superfície e versões. `process_event --client claude` (detecção por `CLAUDECODE=1`, a provar na cópia do app) exige o mesmo preflight nos mesmos eventos. O gate que exige evidência reprova quando ela falta ou diverge, como no terminal.

**Decisão nova: retorno de filho em segundo plano.** O host real lança `Agent` em segundo plano: no 2.1.300 CLI, todo `Agent` do pai deste card voltou com `toolUseResult.status="async_launched"`, e a conclusão chegou ao transcript do pai como `queue-operation` (`operation: enqueue`) com `<task-notification>`. O coletor de hoje só conhece `<agent-message>` e devolveu `terminal_unavailable` para o Design-autor (`af0a1917b83c8aa19`) e o crítico (`aacea23e2dfb0ccf9`) deste card, ambos `completed` com turnos `claude-opus-5-5`/`high` iguais à captura. Por isso o contrato de evidência muda assim, no `extract`/`_handbacks`:

- Retorno de filho tem duas formas reconhecidas: `<agent-message from="{agentId}">` (como hoje) e `queue-operation` `enqueue` com `<task-notification>`.
- Na segunda, só vale a notificação com `<task-id>` == `agentId` **e** `<tool-use-id>` == `call.id` do spawn; qualquer divergência não é aceita como retorno deste filho.
- `<status>`: `completed` → `completed`, com payload = conteúdo de `<result>`; `failed` → `failed`; `killed` → `interrupted`.
- Spawn com `status="async_launched"` é aceito quando traz `resolvedModel` igual ao capturado; se o spawn não traz `resolvedModel`, a checagem do modelo passa ao retorno ou aos turnos do filho (par por turno = captura), nunca é pulada.
- Forma de retorno desconhecida (nem `<agent-message>` nem `<task-notification>` reconhecível, ou status fora da lista) → `unsupported_schema` visível citando o campo, nunca `terminal_unavailable` eterno. `terminal_unavailable` fica só para filho ainda sem notificação nenhuma.

### 10. Residual do #1101

**Digest A (prioridade; antes de qualquer outra edição do adapter).** R1 e R2: `route-landmarks.yaml` e `scripts/process-fsm/*_fixtures.py` saem de `CORE_TREES` (são dados e fixtures, não código executado pelo hook), com teste de que editar cada um não gera `adapter_divergent`. R3: o digest A inclui o bloco `entrypoints`/`modules` do manifesto do cliente, de modo que trocar só o argv exige nova revisão. R4: `enumerate_tree` desce em symlink de diretório e inclui o alvo no digest (symlink para fora do repo = falha no pin). R5: só `__pycache__/` e `*.pyc` dentro dele saem; `.pyc` solto entra. R6: arquivo listado com digest `None` falha no pin, com o caminho. R7: `detector/` do Impeccable entra, com teste de byte alterado.

**Shim e conta.** R8: só `SessionStart` com `source=startup` grava o `registration_digest`; `compact`/`clear`/`resume` preservam o original, e `hooks_changed` volta a disparar. R9: chamada estrangeira do Cursor decidida pelo cliente do registro que chamou o shim (argv), não por variável `CURSOR_*` herdada. R10: Cursor e OpenCode detectam o cliente nativamente para `hooks_inactive`, sem depender de `--client`/`COVENANT_CLIENT`. R11: `discover` sobe de um repo Git aninhado até achar o consumidor com overlay; aninhado sem overlay dentro de consumidor = o consumidor externo governa. R12: falha de `import()` no plugin OpenCode nunca bloqueia `read` (leitura não é bloqueada; escrita, shell e spawn continuam deny). R15: `trust --record` exige confirmação do operador fora da sessão do agente (TTY interativo, recusado quando `CLAUDECODE=1` ou equivalente de outro cliente), e `shim_verified()` deixa de aceitar `CF_SHIM_ACTIVE`/`CF_SHIM_ADAPTER_DIGEST` do ambiente como prova: o adapter confere contra o registro de confiança da conta. R16: a página avisa quando os worktrees abertos na sessão têm pins diferentes.

**Instalador da conta.** R18/R19: `--remove` só reescreve um arquivo se havia entrada do Covenant Flow; nunca cria `"hooks": {}` e nunca transforma `{}` em outra coisa (byte a byte igual quando não há entrada). R20: `--remove` remove o diretório versionado do shim e o link `current`, sem deixar alvo órfão. R21: o diff do `install.sh` do nucleus entra no `review_diff_path` da onda de review do consumidor.

**Adapter Claude Code.** R13: o último turno `<synthetic>` só classifica `failed` quando é erro da API; `<synthetic>` final sem erro fica fora da comparação e o status vem do último turno real. R26: a recusa de T16 com pai fora de `claude/execucao`, prometida na spec do #1101, passa a valer no próprio `process_event fechar_release` do cliente `claude` (chama `observe-parent` + `load_execucao_pair`), não só no runbook; é a mesma regra, aplicada onde o evento acontece, sem gate novo. R27: a verificação antes da primeira escrita do filho é provada com transcript real no ensaio pelo app. R35 (9.6): o fecho de lote pelo Claude Code só entra se Alan pedir; a task registra a resposta dele.

**Guard (R33).** O destino de escrita de `>`/`>>`/`tee` é resolvido para caminho absoluto: fora do repositório (scratchpad, `/tmp`) não é escrita de produto; `>>` dentro do corpo de um heredoc é texto, não redirecionamento. Redirecionamento para dentro do repo continua negado como hoje.

**Gate de Design (R28).** O guard de `submeter_design` (T5) roda o mesmo parser de `design_clone_gate.py` e exige as três linhas `UI impact`/`live_route`/`surface` parseáveis no `design.md`; ausência ou valor inválido recusa o T5 com o token faltante. Não é gate novo: é o checklist que o precommit já exige, antecipado para o evento onde o erro passou (achados 27/28).

**Textos e runbook.** R17: tabela de reinjeção da página por host em `host-mechanisms.md` do #1101. R22–R24: testes corrigidos como listados. R25 e R31: textos que citam `.codex/hooks.json`/`.cursor/hooks.json` do projeto passam a "registro na conta (`install.sh --account`) → shim → adapter pinado", no nucleus e no consumidor. R29: comandos para o operador sempre colados em bash comum, sem `!` e sem `cd … &&`. R30: depois da revisão da conta, sessão nova (o `prepare` dá `hooks_inactive` até lá). R32 e R36: notas de supersessão no OpenSpec do #1101 (3.2/7.1 "substituído por 11.4/11.5"; 6.5 sem a declaração do gate; 2.4 com a janela antiga; 9.3 com `implemente` em `Todo` sem prova viva) e `hook.mjs` citado na spec (R26), antes do archive do #1101.

### 11. Ensaio real pelo app

**Onde Alan executa:** no app desktop do Claude no Windows, conexão SSH para esta VM, pasta `/srv/apps/dev/criptofarol/source`, opção *worktree* do app desligada, no modo de permissão em que o app abre. O board fica no navegador. Alan não usa o terminal no ensaio; o que for comando de operador (revisão R/A, `install.sh --account`) é feito antes, em bash comum.

**Card de ensaio:** um card real pequeno, escolhido e priorizado por Alan (T1 dele), conduzido pelo app de Em Refinamento até QA verde: grelha, Design com crítico, T7, Apply, onda de review, QA. Ele precisa do adapter deste card, que só chega a `develop` no T14 do #1103; por isso o worktree dele nasce **empilhado** sobre o SHA com QA verde do #1103, com review só do próprio diff. O T14 do card de ensaio vem depois do T14 do #1103 e de rebase em `develop`, também pelo app, e a evidência dele fica no próprio card. Alternativas rejeitadas: ensaiar depois do T14 do #1103 (o Done técnico sairia sem a prova que o body exige); ensaiar no próprio #1103 (Em Refinamento e Design já passaram, e o objeto testado se misturaria ao teste).

**Negativos no app, antes do card:** `implemente` num card em `Todo` (nenhum arquivo muda; a resposta cita o Status); escrita de produto em `develop` por `Edit` e `Bash` negada; spawn sem `effort` e com modelo divergente negados; sessão na pasta do app recusada e saída por `EnterWorktree`; ferramenta de sessão do app negada com card vinculado; evidência apagada/divergente de um filho reprova o gate no chat do app; versão sem `AI_AGENT` simulada recusa sem ler o PATH.

**O que é evidência:** heartbeat do shim com `entrypoint=claude-desktop`, versões do host e do app; receipts e proxies por filho com superfície `claude-desktop` e par observado = captura; transcript real sanitizado gravado como fixture; saídas de `process_event`; os denies tirados do transcript (`tool_result` com o motivo); um comentário no #1103 por bloco com ids de sessão, filhos e SHA. Captura de tela é opcional, a critério de Alan.

## Riscos

- [Formato interno do app muda numa atualização automática da cópia `ccd-cli`] → aceitação por formato do #1101: `unsupported_schema` visível citando o campo; a versão nunca recusa sozinha.
- [Host lança todo `Agent` em segundo plano (observado no 2.1.300 CLI; confirmar no app 2.1.295)] → o coletor reconhece `async_launched` + `<task-notification>` (§9); forma desconhecida = `unsupported_schema`; o ensaio coleta pelo menos um filho em segundo plano no app.
- [App atualiza a cópia entre o ensaio e o uso] → a fixture prova o formato, não a versão; checagens cruzadas (`resolvedModel`, par por turno, filiação) reprovam semântica nova.
- [`EnterWorktree`, `PostToolUse(EnterWorktree)` ou `CLAUDECODE`/`AI_AGENT`/`CLAUDE_CODE_SESSION_ID` se comportam diferente na cópia do app] → cada um é linha do ensaio; o que não funcionar vira falha visível (§8) e lacuna registrada, sem mecanismo inventado.
- [Ferramentas `mcp__ccd_*` novas surgem numa atualização] → nome não classificado = tratado como criador de sessão (deny com card vinculado).
- [`--permission-mode=auto` e o classificador do app aprovam algo que o hook negaria] → o hook roda antes e nega; o classificador não é proteção do processo.
- [Painel de git do app commita sem hooks do repositório] → é ação humana na interface; o agente não usa esse caminho; o review por diff e o T14 continuam pelo processo.
- [Card de ensaio empilhado aumenta a coordenação (rebase, review só do próprio diff)] → card pequeno, escolhido por Alan; regra de empilhado que o runbook já tem.
- [Endurecer `trust --record` (R15) atrapalha o operador] → a confirmação é TTY em bash comum, o mesmo lugar onde Alan já registra R/A; mensagem diz o comando.
- [Trocar o shim (R8–R12) muda o digest R] → todas as sessões abertas ficam `hooks_changed`; a migração manda revisar R e abrir sessão nova antes do ensaio.

## P3 aceitos (detalhe de Apply)

- Nome exato dos campos novos do heartbeat (`desktop_app_version`, `ssh`) e se entram também no proxy.
- Padrão exato para reconhecer a pasta do app (segmento `.claude/worktrees/`, leitura de `worktree.location`) e texto da mensagem.
- Lista nominal das ferramentas `mcp__ccd_*` negadas e o matcher do registro na conta.
- Ferramenta usada para o título `#<id>` e momento em que o pai o atualiza.
- Formato da linha de handoff por filho (reaproveitar a do proxy).
- Forma da confirmação TTY de `trust --record` e como o shim marca a origem da revisão.
- Como `discover` limita a subida em repos aninhados (até a raiz do primeiro overlay encontrado).
- Sanitização da fixture real (sessão, caminhos, conteúdo de mensagens).
- Se o nucleus recebe as mudanças primeiro e o consumidor pelo pin (como no #1101) ou em par de commits.
- R26 é regra existente (`card-1101-claude-code-adapter/specs/claude-code-harness/spec.md:146`); o Apply aplica só ao cliente `claude`, reusando `observe-parent` + `load_execucao_pair`.
- R28 é regra existente; o predicado do `G_design` reusa `review_process_checklist._check_design_tokens` do precommit, para não divergir.
- A ferramenta de título `#<id>` (§6) entra classificada como permitida; senão a regra "não classificada = deny" de §5 bloquearia o próprio título.
- A fixture real do app inclui um filho com `effort` explícito (a grelha do #1103 teve filho sem `effort`).
- Local da evidência do ensaio: no #1103, um comentário por bloco; a do card de ensaio fica também no próprio card de ensaio. A spec "Live rehearsal", §11 e 8.5 dizem o mesmo.

## Migration Plan

1. Apply no nucleus (shim, instalador, regras) e no consumidor (adapter, coletor, Guard, gate T5, testes, docs); grupo de digest primeiro.
2. Commit; tag do nucleus e pin no consumidor, comparando overlay, política e adapters antes/depois.
3. Alan, em bash comum: `install.sh --account` com o shim novo, revisão R e A, sessão nova no app.
4. QA verde do #1103; ensaio no app (negativos + card de ensaio empilhado até QA verde); evidência no card.
5. T14 do #1103 pela regra geral; depois, rebase e T14 do card de ensaio pelo app.

Rollback: `install.sh --account` com o shim anterior e revisão R antiga; o pin anterior continua aceito pelo shim.

## Open Questions

Nenhuma de produto. Fica para Alan no T1 do card de ensaio: qual card real pequeno será conduzido pelo app.

## Design Critique

Teto sem-tela: 1 autor + 1 crítico + 1 rework (fechado). Snapshot: `.impeccable/critique/1103-card-1103-claude-desktop-ssh-design-critic.md`.

verdict (crítico c1): rework → aplicado no rework único.

- P1 | contrato | Retorno de filho em segundo plano (`queue-operation` com `<task-notification>`) não reconhecido pelo coletor; critério 3 reprovaria no caminho feliz. | resolvido no rework (§8, §9, Riscos, spec "Background child handback is recognized", tasks 5.5/5.6, 8.2/8.3)
- P2 | contrato | R34 como código depois do QA (8.1). | resolvido no rework (task 4.9; 8.1 só verifica)
- P2 | contrato | Critério 4 sem ensaio vivo dos negativos `AI_AGENT` ausente e `hooks_inactive`. | resolvido no rework (8.2)
- P3 | detalhe de Apply | R26 é regra existente (T16 com pai `claude/execucao`), não gate novo. | aceito P3
- P3 | detalhe de Apply | R28 é regra existente (`G_design` + `_check_design_tokens`), não gate novo. | aceito P3
- P3 | detalhe de Apply | Ferramenta de título `#<id>` classificada como permitida. | aceito P3
- P3 | detalhe de Apply | Fixture real do app com filho de `effort` explícito. | aceito P3
- P3 | detalhe de Apply | Local da evidência do ensaio (#1103 por bloco + card de ensaio). | aceito P3

Evidência de modelo dos filhos de Design (autor, crítico, rework): `claude_proxy.py` devolveu `terminal_unavailable` nos três, porque o host 2.1.300 lançou cada `Agent` em segundo plano e o coletor ainda não lê `<task-notification>`. Registro **reprovado/pendente**, sem observação manual; recoleta no Apply (task 5.6).
