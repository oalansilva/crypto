## Why

Os seis portões do Alan só passam arrastando o card no board, e o agente usa o mesmo login do GitHub que o Alan, então um movimento do agente e um arrasto do Alan são iguais para o GitHub. Este card leva os portões para um comando exato no chat e tira do agente a escrita no Project: todo movimento passa por um executor que confere a regra da FSM.

Briefing copiado do issue #1135 (REST, 2026-10-28). As quatro seções abaixo são cópia literal do body.

## Problema

Hoje os portões que só o Alan pode passar (priorizar, aprovar design, devolver design, homologar, não homologar e cancelar) exigem abrir o board e arrastar o card. O Alan já está no chat com o agente quando decide, então trocar de tela para arrastar é atrito, e pelo celular é pior ainda.

Também não dá simplesmente para o agente entender "pode seguir" no chat e mover o card: aí quem decide que o Alan aprovou passa a ser o modelo, e o processo proíbe isso (chat é wording, NLU ≠ δ).

E há um buraco que vale até para o board de hoje: o agente usa o mesmo login do GitHub que o Alan (`oalansilva`, com permissão de escrita no Project). Para o GitHub, um arrasto do Alan e uma mudança feita pelo agente são indistinguíveis. O que segura o agente hoje é ele cooperar e o guard bloquear `item-edit` por regex.

## História

Como Alan, quero passar os meus portões digitando um comando exato no chat, para decidir sem sair da conversa, com a garantia de que só um comando digitado por mim move o card e de que o agente não consegue fazer isso no meu lugar.

## Entra

- [ ] Seis comandos, com texto exato. Qualquer variação ("aprova aí", "pode seguir") não tem efeito nenhum:

  | Comando | Transição | De → Para |
  |---|---|---|
  | `/priorizar <card>` | T1, e em seguida T3 | Em Refinamento → Todo → Design |
  | `/aprovar-design <card>` | T7 | Aprovação de Design → Pronto para Dev |
  | `/devolver-design <card> "motivo"` | T6 | Aprovação de Design → Design |
  | `/homologar <card>` | T15 | Done → Homologado |
  | `/nao-homologar <card> "motivo"` | T18 | Done → Em desenvolvimento |
  | `/cancelar <card> "motivo"` | T2 | coluna viva → Cancelado |

- [ ] `/priorizar` encadeia: move o card para Todo e, no mesmo passo, o fluxo inicia o Design dele (iniciar o Design já é passo do agente). Todo vira só passagem: depois de priorizar, o Alan não precisa pedir o início do Design. Se o Design não puder começar, o card fica em Todo e a resposta diz por quê.
- [ ] O comando só vale digitado pelo Alan no chat com o agente. Quem reconhece o comando é um código fixo que lê o texto do Alan antes do agente, e não o agente. Texto colado, comentário de issue (inclusive do próprio Alan) e resposta de ferramenta nunca disparam um comando.
- [ ] Antes de mover, o comando confere se o card está mesmo na coluna de origem. Se não estiver, recusa e diz por quê.
- [ ] `/aprovar-design` não leva código do design. O executor recusa a aprovação se o design (texto ou protótipo) mudou desde o envio para aprovação, e diz por quê.
- [ ] Devolver design, não homologar e cancelar exigem motivo. O motivo vira o comentário visível na issue (por exemplo, `Não homologar: <motivo>`).
- [ ] Cancelar é sem volta, então só o `/cancelar` pede confirmação: o executor responde com o título do card e só cancela depois de um segundo comando exato de confirmação. Sem a confirmação, o card não muda.
- [ ] Todo comando executado deixa um recibo na issue: comando, data e hora, e de qual cliente veio.
- [ ] O agente passa a ter um login próprio no GitHub que só lê o board (sem permissão de escrita no Project). Todo movimento de coluna passa por um executor: os comandos do Alan e também as transições que já são do agente. Nas do agente, o agente pede, o executor confere a regra da coluna e move. Pedido do agente que fere a regra (coluna errada ou portão do Alan) é recusado e o card não muda. O jeito exato do executor (outro usuário na máquina ou outro) fica com o Design.
- [ ] Arrastar no board continua funcionando como hoje. Arrastar para Todo só move para Todo, sem iniciar o Design: o encadeamento é só do `/priorizar`.
- [ ] Verificação:
  - para cada comando, um teste com o comando certo (move) e outro com o texto aproximado ou vindo de outra fonte, inclusive comentário na issue (não move);
  - `/priorizar` certo deixa o card em Design sem nenhum outro pedido do Alan; arrastar o card para Todo no board deixa o card em Todo;
  - `/aprovar-design` com o design alterado depois do envio para aprovação é recusado;
  - `/cancelar` sem a confirmação não move;
  - uma transição do agente pedida ao executor move, e um portão do Alan pedido pelo agente ao executor é recusado;
  - o agente, com o login dele, não consegue mudar o Status direto no board.

## Não entra

- Comandos do Alan para transições que já são do agente (iniciar design, apply, review, QA, integrar, `fechar_release`). Para essas, um pedido no chat continua sendo só um pedido. Elas não ganham comando do Alan, mas passam a ser movidas pelo executor a pedido do agente (ver Entra).
- Interpretar linguagem natural como aprovação.
- Tirar o arrasto no board.
- Cobrir todos os clientes de uma vez: o Design decide por qual cliente (ou caminho independente de cliente) começar. Clientes sem o mecanismo continuam só com o board.
- Priorizar junto com o pedido de refino (por exemplo, `/refinar <card> --priorizar`, ou entender "refine" como priorização). O `/priorizar` continua sendo um comando exato que o Alan digita depois do refinamento.
- Um comando para só priorizar sem iniciar o Design (Todo como fila). Se um dia precisar, vira outro card.

## What Changes

- Executor de movimentos fora da VM (GitHub Actions num repositório próprio do executor), único dono do token que escreve no Project 1. Ele confere coluna de origem, evento e ator contra a FSM fixada, move, deixa recibo na issue e responde.
- Login próprio do agente no GitHub, sem papel no Project 1 (o Project é público, então o agente só lê). O token do agente passa a ser o único token GitHub na VM. **BREAKING** para o fluxo: o agente deixa de conseguir `gh project item-edit` / `item-add`.
- `process_event` continua sendo o caminho do agente, mas move pedindo ao executor (T0, T3, T5, T8–T14, T16, T17). Eventos do Alan pedidos pelo agente continuam recusados (`reason=actor`) e o executor também os recusa.
- Hook de prompt do Claude Code (`UserPromptSubmit`), instalado pelo registro na conta: reconhece os seis comandos exatos (e a confirmação do `/cancelar`) antes do agente e manda ao executor. Os demais clientes continuam só com o board.
- `/priorizar` encadeia T1 e T3; `/aprovar-design` recusa design mudado desde o T5; motivo obrigatório em T6/T18/T2; `/cancelar` exige `/confirmar-cancelar`.
- Regras escritas: AGENTS.md (gerado por `overlay.py`), página do processo, `covenant-flow/SKILL.md`, `github-project-board`, `process-fsm.yaml` (I2 e ações de T5/T7) e `ALAN_GATES` passam a citar os seis portões e a nova frase sobre wording.
- Nível de garantia declarado: em todos os clientes a captura do comando é **cooperativa**, porque o agente roda no mesmo usuário do sistema que o hook, e esse usuário tem root. Run e recibo são registro, não prova: o agente tem `write` nos dois repos e pode apagá-los, e o recibo sai como `oalansilva`, então não avisa o Alan. O que fica fora do alcance do agente é o token que escreve no Project 1.
- A História pede que só um comando digitado pelo Alan mova o card e que o agente não consiga fazer isso no lugar dele; este card entrega um agente sem escrita no Project 1, que só move por aresta da FSM via executor, e uma captura do comando do Alan cooperativa, que um agente decidido forja com um `dispatches` (`tipo=capturar`, `ator=Alan`), segurada só pela regex da Guard e sem rastro fora do alcance dele; a diferença fica para o card de separação de usuário (futuro, não criado).
- Antes de qualquer código ou passo do Alan no GitHub, um ensaio com hook descartável confere se o `UserPromptSubmit` dispara no cli e no app desktop e recebe `/priorizar …` cru. Se falhar, o Apply para e volta ao Alan (só cli, outro texto de comando ou parar).

## Capabilities

### New Capabilities

- `board-executor`: executor fora da VM que move o Status do Project 1, confere a FSM fixada, deixa recibo e é o único com escrita no Project.
- `alan-gate-commands`: os seis comandos exatos do Alan no chat (e a confirmação do cancelamento), a captura antes do agente, o encadeamento do `/priorizar`, a conferência do design no `/aprovar-design`, o motivo e o recibo.

### Modified Capabilities

- `process-fsm-event`: `process_event` passa a mover pelo executor (inclusive `criar_card`), não mais com `gh project item-edit`.
- `account-hook-shim`: o registro na conta do Claude Code ganha a entrada de prompt (`UserPromptSubmit`), que chama o adapter pinado.
- `process-fsm-guard`: a Guard nega a chamada direta ao caminho de captura do Alan e o disparo do executor fora do `process_event`.

## Impact

- Código: `scripts/process-fsm/` (`process_event.py`, `fsm.py`, `guard.py`, `board_status.py`, `overlay.py`, `paging.py`, `claude_adapter.py`/`claude_hooks.py`, `cf_shim.py`, novo `portao/`), `.cursor/process-fsm.yaml`, `.cursor/hooks/process-fsm-session-start.sh`, `.covenant-flow/adapters.json` e overlay, `install.sh` do nucleus (entra no diff via `--nucleus`, como no #1101/#1103/#1098).
- Regras: `AGENTS.md`, `.cursor/skills/covenant-flow/SKILL.md`, `.cursor/skills/github-project-board/` (SKILL e `references/project-board-commands.md`).
- GitHub (operador): conta do agente, repositório do executor com ruleset e environment, PAT clássico do Alan como secret do environment, troca do login do `gh` na VM.
- Fora: telas do produto, backend e frontend.
