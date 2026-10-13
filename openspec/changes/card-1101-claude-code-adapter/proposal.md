## Why

Hoje o Claude Code não é cliente do Covenant Flow: lê o `AGENTS.md`, mas não encontra as skills canônicas, não tem Guard de escrita por etapa, não segue a seleção local de modelos por faixa e não registra evidência de runtime. Alan quer conduzir cards completos (e a parte do agente no fecho de lote) no Claude Code com as mesmas garantias de Cursor e Codex, sem segunda lei nem segundo mapa de modelos (#1101). Este card entrega o adapter **não oficial**, provado por um piloto empilhado e por um card real de troca de cliente; a oficialização é card de seguimento.


## Problema

Alan quer usar o Claude Code no método de trabalho com o mesmo fluxo completo que já roda no Cursor e no Codex, mas hoje o Claude Code não é cliente do Covenant Flow: não encontra as skills canônicas, não tem proteção de escrita por etapa, não segue a seleção de modelos por faixa e pode agir fora da coluna correta.

## História

Como Alan, quero usar o Claude Code com a mesma FSM, as mesmas skills canônicas e a mesma seleção local de modelos dos demais clientes, em todas as superfícies do Claude Code (terminal, web, desktop e IDE), para conduzir um card de Em Refinamento até Done técnico (e participar do fecho de lote) no Claude Code, com as mesmas garantias que tenho no Cursor e no Codex.

## Entra

- Uma sessão nova no Claude Code encontra as skills do repositório (sem cópia da lei), mostra a orientação correspondente ao Status do card vinculado e só permite as ações previstas para aquela etapa.
- Criação de card e grelha em Em Refinamento funcionam no Claude Code: o pai repassa as perguntas com todas as opções, e o filho de grelha escreve o body do issue.
- No Claude Code, tentativas de escrita de produto na branch de integração, em Todo ou sem card vinculado são negadas tanto por comando quanto por edição de arquivo. Em Design, os artefatos dessa etapa são permitidos; escrita de produto só no worktree do card depois de Pronto para Dev.
- Design, Apply, os dois reviewers e QA rodam como filhos isolados no próprio Claude Code, com prompt autocontido. Os dois reviewers nascem no mesmo turno, recebem o diff exato, só leem e entregam pareceres separados.
- Cada filho usa o modelo da sua faixa definido na seleção local compartilhada, com entrada própria para o Claude Code: juízo = Opus 5.5 com esforço alto; execução = Sonnet 5.5 com esforço alto. Alterar a escolha local afeta o próximo spawn da faixa; os valores dos outros clientes não mudam. Modelo ausente, proibido ou indisponível gera falha visível, sem troca silenciosa nem herança do modelo do pai.
- A evidência do modelo realmente usado por cada filho é coletada do runtime e registrada como nos demais clientes; ausência de evidência reprova o gate que a exige.
- Um card pode trocar de cliente entre etapas (por exemplo, Design no Cursor e Apply no Claude Code): segue a mesma FSM, e cada filho registra o cliente e o modelo realmente usados.
- O Status avança somente pelos eventos da FSM; gates humanos (priorização, aprovação de Design, homologar e não homologar) continuam só de Alan e pedido `implemente` não autoriza código fora de Pronto para Dev.
- O Claude Code conduz a parte do agente no fecho de lote com as mesmas regras dos outros clientes; o fecho só começa por pedido explícito de Alan, e homologar continua só dele.
- A orientação Impeccable dispara nas mesmas condições dos outros clientes.
- O fluxo vale nas superfícies terminal (CLI), web (claude.ai/code), desktop e IDE; onde alguma superfície não oferecer a proteção, a seleção de modelo ou a evidência exigida, a etapa falha de forma visível naquela superfície, sem fallback para outra.
- Um card piloto pequeno e real percorre no Claude Code Em Refinamento → Design → aprovação → Apply → dois reviews → QA → Done técnico sem pular etapas. O piloto roda empilhado sobre este card; o piloto concluído (QA verde no Claude Code, com filhos, eventos e evidência registrados) é condição para o Done técnico deste card. Durante o piloto, os demais cards ficam pausados nesta conta.
- Um segundo card pequeno e real prova a troca de cliente: Design no Cursor ou no Codex e Apply no Claude Code, até QA verde, com a evidência de cada cliente; também é condição para o Done técnico deste card.
- Este card entrega o adapter ainda **não oficial**: nem as instruções do repositório nem a descrição do board citam o Claude Code como cliente. A oficialização fica para um card de seguimento, aberto depois do piloto e da revisão de confiança no host.
- O instalador do pin reproduz o adapter no Cripto; specs e testes cobrem o novo cliente e os testes dos clientes existentes continuam verdes.
- Critérios observáveis:
  - Dado um card em Todo, quando Alan pede `implemente` no Claude Code, então nenhum arquivo de produto muda e a resposta cita o Status atual e que Apply só vem depois de Pronto para Dev.
  - Dado um card em Pronto para Dev, quando o fluxo segue no Claude Code, então Apply, review, QA e Done técnico acontecem com os filhos e eventos esperados e o handoff registra o cliente e o modelo observado de cada filho.
  - Dado modelo da faixa indisponível, quando o pai tenta abrir o filho, então a etapa para com erro visível.
  - Dado um card cujo Design foi feito no Cursor, quando o Apply segue no Claude Code, então o Status avança pelos mesmos eventos e o handoff mostra o cliente e o modelo de cada filho, inclusive os da etapa anterior.
  - Dado um lote pronto para fechar, quando o fecho é conduzido no Claude Code, então os passos do agente seguem as mesmas regras dos outros clientes e nada vai para produção sem pedido explícito de Alan e cards homologados por ele.
  - Dado este card em QA verde e o piloto ou o card de troca de cliente sem QA verde registrado, então este card não é integrado (não chega a Done técnico) e o Claude Code não aparece como cliente oficial.

## Não entra

- Oficializar o Claude Code nas instruções do repositório, no pin e na descrição do board (card de seguimento, com T1 de Alan, depois do piloto).

- Alterar T0–T18, estados, gates humanos ou regras de release.
- Duplicar a FSM, as skills ou a política de modelos em pastas do Claude Code; manter segundo mapa de modelos.
- Alterar o comportamento dos clientes atuais (Cursor, Codex, Grok, OpenCode, dsh) ou código de produto em `backend/` / `frontend/src/`.
- Reivindicar modo Auto para o Claude Code ou tratar instrução de chat como autorização.

## What Changes

- Novo adapter `claude`, espelhando o adapter Codex (#1042/#1095), ainda **não oficial**: ponte `CLAUDE.md` com import de `AGENTS.md`; pontes `.claude/skills/<nome>/SKILL.md` geradas com manifesto de hash e sem cópia da lei; `.claude/settings.json` com hooks `SessionStart`, `PreToolUse`, `PostToolUse`, `SubagentStop` e `Stop` apontando para `scripts/process-fsm/claude_adapter.py`; agentes `.claude/agents/diff-reviewer.md` e `.claude/agents/code-reviewer.md` só leitura.
- Seleção local: `.cursor/model-policy.yaml` ganha o contrato `clients.claude` (label/model/effort); `model_selection.py resolve --client claude` passa a resolver e capturar; a seleção da conta recebe `juizo.claude` = `claude-opus-5-5`/`high` e `execucao.claude` = `claude-sonnet-5-5`/`high` (decisão de Alan no body). `effort` explícito em todo spawn (o host roda filho sem `effort` em `medium`); sem fallback, sem herança.
- Guard de nascimento lê o esforço só de `tool_input.effort` do `Agent`; antes da primeira escrita de cada filho, o modelo/esforço do transcript do filho é comparado com a captura (`model_mismatch` = deny).
- Evidência de runtime do Claude Code: coletor a partir dos transcripts JSONL locais da sessão e dos subagentes (receipt antes do nascimento, coleta depois do retorno), com proxy e verificação de onda de review, como `codex_evidence`/`codex_proxy`/`codex_review`.
- `process_event --client claude` e detecção nativa do cliente, com preflight de disponibilidade antes das transições que dependem de filhos; T16 com captura do pai de execução do próprio cliente.
- Matriz de superfícies (terminal, web, desktop, IDE) com falha visível onde faltar proteção, seleção ou evidência, sem fallback.
- Instalador do pin no nucleus reproduz o adapter no Cripto; testes do novo cliente e dos clientes existentes.
- `review_process_checklist.py --phase postqa` ganha o item `pilot_evidence`, ativo só para changes que o declaram (este): exige piloto e card de troca com QA verde e proxies por filho.
- Piloto empilhado sobre a branch deste card até QA verde no Claude Code, mais um segundo card real de troca de cliente (Design no Cursor ou no Codex → Apply no Claude Code até QA verde); só então T14 deste card; depois T14 de cada card empilhado, rebaseado em `develop`.
- Fora deste diff: oficialização (`AGENTS.md` via renderer/pin, descrição do board) — card de seguimento com T1 de Alan.

## Capabilities

### New Capabilities

- `claude-code-harness`: adapter Claude Code do Covenant Flow — descoberta das skills canônicas, Guard por etapa, filhos isolados com seleção por faixa, evidência de runtime, eventos da FSM, fecho de lote, troca de cliente entre etapas, superfícies, piloto empilhado, card de troca e trava de não oficialização.

### Modified Capabilities

- `machine-model-selection`: o schema local e o roteamento explícito passam a distinguir seis clientes (inclui `claude`, com par modelo+esforço explícito).
- `process-harness`: o stub `AGENTS.md` continua nomeando só os cinco clientes oficiais; o Claude Code o lê via `CLAUDE.md` sem ser nomeado como cliente. Nomeá-lo é do card de seguimento.

## Impact

- Novos arquivos versionados: `CLAUDE.md`, `.claude/settings.json`, `.claude/skills/**` (pontes + manifesto), `.claude/agents/{diff-reviewer,code-reviewer}.md`, `scripts/process-fsm/claude_*.py` e testes, doc `docs/claude-runtime-evidence.md`, declaração do gate de piloto no change.
- Alterados: `.cursor/model-policy.yaml`, `scripts/process-fsm/{model_selection.py,model_proxy.py,process_event.py,paging.py,release_model_selection.py,review_process_checklist.py,guard.py (só normalização de nomes de ferramenta, se necessário)}`, `docs/model-selection.md`, skill `covenant-flow` (seção Claude Code, fora da linha "Cliente ativo"), `.gitignore` (se `.claude/settings.local.json` precisar ficar fora do git).
- Não alterados neste card: `AGENTS.md`, `scripts/process-fsm/overlay.py` (`render_agents`), testes `test_overlay.py`/`test_paging.py` de clientes oficiais e a descrição do Project 1 — ficam para o card de seguimento.
- Nucleus `oalansilva/covenant-flow`: `install.sh`/pin novo que copia e verifica o pacote Claude Code.
- Conta executora: entrada `claude` em `$HOME/.config/covenant-flow/model-selection.yaml` (edição local, sem commit, só no início do piloto) e registro local de revisão de confiança dos hooks.
- Operação: durante a janela do piloto os demais cards ficam pausados nesta conta (exceto o card de troca); o resolver antigo em `develop`/outros worktrees falha visivelmente até o T14 deste card.
- Sem mudança em `backend/`, `frontend/src/`, `.cursor/process-fsm.yaml`, estados, eventos, gates humanos, guard de T14 ou regras de release; sem mudança de comportamento em Cursor, Codex, Grok, OpenCode e dsh.
