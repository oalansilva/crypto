## Why

Hoje o Claude Code não é cliente do Covenant Flow: lê o `AGENTS.md`, mas não encontra as skills canônicas, não tem Guard de escrita por etapa, não segue a seleção local de modelos por faixa e não registra evidência de runtime. Alan quer conduzir cards completos (e a parte do agente no fecho de lote) no Claude Code com as mesmas garantias de Cursor e Codex, sem segunda lei nem segundo mapa de modelos (#1101). O piloto mostrou que isso não basta: com o registro dos hooks dentro do repositório, uma sessão aberta em `/source` e levada ao worktree do card fica sem processo, e uma atualização automática do host (2.1.299) travou todos os nascimentos. As decisões de Alan de 2026-10-14 trazem para este card o registro dos hooks na conta, para Claude Code, Cursor, Codex e OpenCode (Grok Build e dsh ficam como estão; nuvem fora), e a aceitação de versão do host pelo formato. Este card entrega o adapter **não oficial**, provado por um piloto empilhado e por um card real de troca de cliente; a oficialização é card de seguimento.

## Problema

Alan quer usar o Claude Code no método de trabalho com o mesmo fluxo completo que já roda no Cursor e no Codex, mas hoje o Claude Code não é cliente do Covenant Flow: não encontra as skills canônicas, não tem proteção de escrita por etapa, não segue a seleção de modelos por faixa e pode agir fora da coluna correta.

O piloto mostrou mais dois problemas, que valem para todos os clientes. Primeiro, o registro dos hooks fica dentro de cada repositório e depende da pasta onde a sessão foi aberta: uma sessão aberta em `/source` e levada para o worktree do card roda sem processo (`hooks_inactive`). Segundo, uma atualização automática do host travou todos os nascimentos, porque o coletor de evidência só aceita versões listadas uma a uma.

## História

Como Alan, quero usar o Claude Code com a mesma FSM, as mesmas skills canônicas e a mesma seleção local de modelos dos demais clientes, com o Claude Code sempre local, pelo CLI na VM (no terminal, ou dirigido pelo IDE, pelo desktop ou pela web via Remote Control), para conduzir um card de Em Refinamento até Done técnico (e participar do fecho de lote) no Claude Code, com as mesmas garantias que tenho no Cursor e no Codex. Quero também que, no Claude Code, no Cursor, no Codex e no OpenCode, os hooks e o processo rodem a partir da minha conta, independentes do projeto e da pasta em que abri a sessão, e que não travem quando o host se atualiza.

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
- O Claude Code roda sempre local, pelo CLI na VM (decisão de Alan, 2026-10-14). O fluxo vale no terminal (CLI) e nas superfícies que dirigem essa sessão local: IDE e desktop por SSH na VM e web por Remote Control. Onde alguma delas não oferecer a proteção, a seleção de modelo ou a evidência exigida, a etapa falha de forma visível naquela superfície, sem fallback para outra.
- **Hooks e processo independentes do projeto, para Claude Code, Cursor, Codex e OpenCode (decisões de Alan, 2026-10-14):**
  - O registro dos hooks sai do repositório consumidor e vai para a conta do operador, distribuído pelo `covenant-flow`. Vale para Claude Code, Cursor, Codex e OpenCode, cada um pelo mecanismo nativo de hook ou plugin global do host. Os quatro estão instalados nesta VM e são ensaiados.
  - Um cliente do escopo cujo mecanismo global não ficar provado no ensaio fica só com a falha visível (`registration=unproven`): não é apresentado como protegido, e o processo recusa de forma visível as transições que dependem dos hooks. Não se inventa outro registro para ele.
  - Um shim fino descobre o consumidor pela pasta atual da sessão (`.covenant-flow/overlay.yaml` com pin) e chama o adapter pinado daquele repo ou worktree. Repo sem pin: nada acontece. Repo pinado com adapter ausente ou divergente: falha visível.
  - A revisão de confiança continua por digest: o shim não executa adapter que o operador não revisou, e instalar ou pinar não conta como revisão.
  - Uma sessão aberta em `/source` e levada para o worktree do card (`EnterWorktree` ou o equivalente de cada cliente) fica com o processo ativo, sem depender da pasta de lançamento.
  - A lógica do processo (FSM, adapters, skills e política) continua versionada no repositório pelo pin; só o registro dos hooks sai do repositório.
- **O processo não trava quando o host atualiza (decisão de Alan, 2026-10-14):**
  - O adapter funciona na versão atual do Claude Code e nas seguintes. Uma atualização automática do host não bloqueia nascimentos nem transições.
  - Versão nova é aceita quando o formato do transcript bate com o esperado; a recusa (`unsupported_schema`) só acontece quando o formato realmente muda e cita o que mudou.
  - A evidência real (modelo e esforço observados) continua obrigatória. Falha visível só quando a evidência falta ou diverge, nunca só pelo número da versão.
  - Vale também para os outros clientes que hoje têm lista fixa de versões no coletor de evidência (Codex).
- Achados do piloto que entram, porque tocam este desenho: o turno de erro da API do host marca o filho como falho, e não como modelo divergente; um filho nascido antes de uma troca de worktree continua coletável; a grelha feita fora do worktree registra o card do pedido; o digest de confiança cobre todo o código do Impeccable que o hook executa; e trocar para um adapter já revisado não exige reabrir a sessão.
- Um card piloto pequeno e real percorre no Claude Code Em Refinamento → Design → aprovação → Apply → dois reviews → QA → Done técnico sem pular etapas. O piloto roda empilhado sobre este card; o piloto concluído (QA verde no Claude Code, com filhos, eventos e evidência registrados) é condição para o Done técnico deste card. Durante o piloto, os demais cards ficam pausados nesta conta.
- Um segundo card pequeno e real prova a troca de cliente: Design no Cursor ou no Codex e Apply no Claude Code, até QA verde, com a evidência de cada cliente; também é condição para o Done técnico deste card.
- Este card entrega o adapter ainda **não oficial**: nem as instruções do repositório nem a descrição do board citam o Claude Code como cliente. A oficialização fica para um card de seguimento, aberto depois do piloto e da revisão de confiança no host.
- O instalador do pin reproduz o adapter no Cripto e o instalador da conta registra o shim no Claude Code, no Cursor, no Codex e no OpenCode; specs e testes cobrem o novo cliente e o shim, e os testes dos clientes existentes (inclusive Grok Build e dsh, sem mudança) continuam verdes.
- Critérios observáveis:
  - Dado um card em Todo, quando Alan pede `implemente` no Claude Code, então nenhum arquivo de produto muda e a resposta cita o Status atual e que Apply só vem depois de Pronto para Dev.
  - Dado um card em Pronto para Dev, quando o fluxo segue no Claude Code, então Apply, review, QA e Done técnico acontecem com os filhos e eventos esperados e o handoff registra o cliente e o modelo observado de cada filho.
  - Dado modelo da faixa indisponível, quando o pai tenta abrir o filho, então a etapa para com erro visível.
  - Dado um card cujo Design foi feito no Cursor, quando o Apply segue no Claude Code, então o Status avança pelos mesmos eventos e o handoff mostra o cliente e o modelo de cada filho, inclusive os da etapa anterior.
  - Dado um lote pronto para fechar, quando o fecho é conduzido no Claude Code, então os passos do agente seguem as mesmas regras dos outros clientes e nada vai para produção sem pedido explícito de Alan e cards homologados por ele.
  - Dado este card em QA verde e o piloto ou o card de troca de cliente sem QA verde registrado, então este card não é integrado (não chega a Done técnico) e o Claude Code não aparece como cliente oficial.
  - Dada uma sessão Claude Code aberta em `/source` com título `#<id>`, quando ela entra no worktree do card, então a página mostra o card, as transições não são recusadas por hooks inativos e escrita de produto fora da etapa continua negada.
  - Dada uma pasta sem pin, quando Claude Code, Cursor, Codex ou OpenCode abre sessão nela, então nenhum hook do processo age: não aparece página nem negação.
  - Dado um repo pinado cujo adapter falta, foi alterado sem revisão ou não confere com o pin, quando a sessão tenta escrever produto ou abrir filho, então a ação é negada com o motivo visível.
  - Dado um repo com o pin novo, quando se procura registro de hooks do processo dentro do repositório, então não há nenhum do Claude Code, do Cursor, do Codex nem do OpenCode (Grok Build e dsh mantêm o registro atual); em cada um desses quatro clientes com mecanismo global provado, a negação de produto na branch de integração vem do registro na conta, e o cliente sem mecanismo provado aparece como `registration=unproven`, sem ser apresentado como protegido.
  - Dado o Claude Code atualizado sozinho para uma versão nunca vista e com o mesmo formato de transcript, quando o pai prepara um filho, então o nascimento segue e a evidência registra a versão observada.
  - Dada uma versão do host cujo transcript perdeu o modelo ou o esforço, quando o pai prepara um filho ou coleta a evidência, então a etapa para com `unsupported_schema` citando o campo.
  - Dado evidência ausente ou modelo/esforço divergente, em qualquer versão do host, então o gate que exige a evidência reprova.

## Não entra

- Oficializar o Claude Code nas instruções do repositório, no pin e na descrição do board (card de seguimento, com T1 de Alan, depois do piloto).
- Alterar T0–T18, estados, gates humanos ou regras de release.
- Duplicar a FSM, as skills ou a política de modelos em pastas do Claude Code ou na conta; manter segundo mapa de modelos.
- Tirar do repositório a lógica do processo (FSM, adapters, skills, política): só o registro dos hooks vai para a conta. Fora do registro dos hooks, o canal v1 do pin continua "copiar e commitar", sem submodule nem marketplace.
- Grok Build e dsh (decisão de Alan, 2026-10-14: "Nao vamos mexer em Grok buil e dsh nesse momento"): continuam exatamente como hoje, com o registro de hooks no repositório, os stubs atuais e o mesmo comportamento; sem registro na conta, sem shim, sem revisão por digest nova e sem recusa por falta de shim. Levá-los para a conta fica para card de seguimento.
- Sessões de nuvem (claude.ai/code em ambiente de nuvem) não são suportadas por este card (decisão de Alan, 2026-10-14: "nao vamos usar na nuvem sempre local via cli"). O Claude Code roda sempre local, pelo CLI.
- Alterar o comportamento dos clientes atuais (Cursor, Codex, OpenCode) além do registro dos hooks na conta, da revisão de confiança por digest que ele exige e da aceitação de versão por formato; Guard, paginação, seleção de modelos e demais regras desses clientes não mudam. Também não muda código de produto em `backend/` / `frontend/src/`.
- Travar a versão do host ou exigir card/Apply para cada versão nova.
- Endurecer a revisão de confiança contra o próprio agente (confirmação interativa/TTY): card de seguimento, limite aceito por Alan.
- Achados do piloto fora deste card (seguimento): falso positivo do Guard com `>` dentro de aspas (Guard compartilhado de todos os clientes); protótipo de card novo com 404 no DEV (serviço de protótipos do ambiente); atrito do isolamento do host após `EnterWorktree` fica só como nota de uso no runbook.
- Reivindicar modo Auto para o Claude Code ou para qualquer cliente, ou tratar instrução de chat como autorização.

## What Changes

- Novo adapter `claude`, espelhando o adapter Codex (#1042/#1095), ainda **não oficial**: ponte `CLAUDE.md` com import de `AGENTS.md`; pontes `.claude/skills/<nome>/SKILL.md` geradas com manifesto de hash e sem cópia da lei; `scripts/process-fsm/claude_adapter.py` com os eventos `SessionStart`, `PreToolUse`, `PostToolUse`, `SubagentStop` e `Stop`; agentes `.claude/agents/diff-reviewer.md` e `.claude/agents/code-reviewer.md` só leitura. (Já implementado; o rework muda onde os hooks são registrados.)
- Seleção local: `.cursor/model-policy.yaml` ganha o contrato `clients.claude` (label/model/effort); `model_selection.py resolve --client claude` passa a resolver e capturar; a seleção da conta recebe `juizo.claude` = `claude-opus-5-5`/`high` e `execucao.claude` = `claude-sonnet-5-5`/`high` (decisão de Alan no body). `effort` explícito em todo spawn; sem fallback, sem herança.
- Guard de nascimento lê o esforço só de `tool_input.effort` do `Agent`; antes da primeira escrita de cada filho, o modelo/esforço do transcript do filho é comparado com a captura (`model_mismatch` = deny).
- Evidência de runtime do Claude Code: coletor a partir dos transcripts JSONL locais da sessão e dos subagentes (receipt antes do nascimento, coleta depois do retorno), com proxy e verificação de onda de review.
- `process_event --client claude` e detecção nativa do cliente, com preflight de disponibilidade antes das transições que dependem de filhos; T16 com captura do pai de execução do próprio cliente.
- **Rework 2026-10-14 — registro dos hooks na conta, para Claude Code, Cursor, Codex e OpenCode:** um shim fino do `covenant-flow`, instalado na conta do operador e registrado pelo mecanismo global de hook/plugin de cada um desses hosts, descobre o consumidor pelo cwd (`.covenant-flow/overlay.yaml` + `pin` + manifesto de adapters do pin) e chama o adapter pinado do repo/worktree. Sem pin: nada acontece. Adapter ausente, divergente do manifesto, não revisado ou com protocolo incompatível: falha visível. Pins antigos, que ainda registram hooks no projeto, continuam com o registro de projeto, sem execução dupla. Cliente do escopo sem mecanismo global provado no ensaio fica só com a falha visível (`registration=unproven`). Grok Build e dsh ficam fora: o pin continua gravando o registro de projeto deles como hoje, sem shim nem digest novo.
- Instalador de conta novo (`install.sh --account`, com `--check` e `--remove`) e pin novo que deixa de gravar registro de hooks no consumidor e remove do consumidor só as entradas do Covenant Flow dos quatro clientes do escopo, preservando as alheias e os registros de Grok Build e dsh. Fora do registro, o canal v1 continua "copiar e commitar".
- Revisão de confiança por digest em duas partes, comum aos quatro clientes do escopo: registro (bloco de hooks da conta + shim) e adapter (árvores executadas, incluindo todo `.agents/skills/impeccable/scripts/**`). O shim nunca executa adapter não revisado; trocar para um adapter já revisado não exige reabrir a sessão; mudança no registro exige.
- Página reinjetada quando a sessão troca de worktree (`EnterWorktree` ou equivalente), com heartbeat de sessão gravado pelo shim na conta; sessão aberta em `/source` fica com o processo ativo no worktree do card.
- **Rework 2026-10-14 — versão do host aceita pelo formato:** `claude_evidence.py` troca a lista `QUALIFIED_VERSIONS` por validação do schema `claude-transcript-v1` nos registros usados; `codex_evidence.py` troca a versão fixa `0.162.1` do driver pela validação do schema do rollout. Versão nova com formato igual é aceita e registrada; formato mudado = `unsupported_schema` citando o campo. Mínimos de capacidade (por exemplo `effort` por invocação ≥ 2.1.292) continuam, só para versões antigas.
- Achados do piloto: turno `<synthetic>` final = filho `failed`, não `model_mismatch`; coleta de filho compara com o cwd/versão do pai no nascimento (receipt); `grill-card` em branch sem card registra o card do `--task-name`, e card divergente é recusado.
- Matriz de superfícies locais (terminal na VM; IDE e desktop por SSH; web por Remote Control dirigindo a sessão local) com falha visível onde faltar proteção, seleção ou evidência, sem fallback. Sessão de nuvem fora do escopo.
- `review_process_checklist.py --phase postqa` com o item `pilot_evidence`, ativo só para changes que o declaram (este).
- Piloto empilhado e segundo card real de troca de cliente até QA verde; só então T14 deste card.
- Fora deste diff: oficialização (`AGENTS.md` via renderer/pin, descrição do board) — card de seguimento com T1 de Alan.

## Capabilities

### New Capabilities

- `claude-code-harness`: adapter Claude Code do Covenant Flow — descoberta das skills canônicas, Guard por etapa, filhos isolados com seleção por faixa, evidência de runtime, eventos da FSM, fecho de lote, troca de cliente entre etapas, superfícies, piloto empilhado, card de troca e trava de não oficialização.
- `account-hook-shim`: registro dos hooks do processo na conta do operador para Claude Code, Cursor, Codex e OpenCode (Grok Build e dsh inalterados), shim de descoberta pelo cwd, compatibilidade com pins antigos, instalador de conta, revisão de confiança em duas partes e processo ativo após troca de worktree.
- `host-version-acceptance`: coletores de evidência aceitam versões do host pelo formato da fonte, não por lista de versões; recusa só por formato mudado, evidência ausente ou divergente.

### Modified Capabilities

- `machine-model-selection`: o schema local e o roteamento explícito passam a distinguir seis clientes (inclui `claude`, com par modelo+esforço explícito).
- `process-harness`: o stub `AGENTS.md` continua nomeando só os cinco clientes oficiais e o Claude Code o lê via `CLAUDE.md` sem ser nomeado; o núcleo deixa de incluir arquivos de registro de hooks nos adapters do consumidor (registro na conta).
- `cursor-harness`: o Guard compilado do Cursor passa a ser registrado no `hooks.json` da conta, pelo shim, com os mesmos eventos, matchers e `failClosed`.
- `covenant-flow`: `implantar` mantém o canal v1 "copiar e commitar" para a lógica e ganha o canal de conta só para o registro dos hooks.

## Impact

- Já no PR #1102: `CLAUDE.md`, `.claude/skills/**`, `.claude/agents/*.md`, `scripts/process-fsm/claude_*.py` e testes, `docs/claude-runtime-evidence.md`, `.cursor/model-policy.yaml`, `scripts/process-fsm/{model_selection.py,model_proxy.py,process_event.py,paging.py,release_model_selection.py,review_process_checklist.py,guard.py}`, `docs/model-selection.md`, skill `covenant-flow`, declaração `pilot-evidence-gate.json`.
- Rework neste consumidor: sai do repositório o registro de hooks do processo (`.claude/settings.json` bloco `hooks`; entradas do Covenant Flow em `.cursor/hooks.json` e `.codex/hooks.json`; auto-load de `.opencode/plugin/`), aplicado pelo pin; `.grok/hooks/process-fsm.json` e `.dsh/` ficam como estão; scripts e handlers continuam no repo. Alterados: `claude_trust.py`/`claude_adapter.py` (digest em duas partes, heartbeat do shim), `claude_evidence.py`, `codex_evidence.py`, `claude_proxy.py`, docs de evidência, skills `covenant-flow` e `implantar`.
- Nucleus `oalansilva/covenant-flow`: shim, manifesto de adapters gerado pelo pin, `install.sh --account`, pin novo.
- Conta executora: shim em `$HOME/.config/covenant-flow/`, registro nos arquivos globais dos quatro hosts do escopo (por exemplo `~/.claude/settings.json`, `~/.cursor/hooks.json`, `~/.codex/`, plugin global do OpenCode), registro de confiança comum e heartbeats de sessão; entrada `claude` na seleção local (já prevista).
- Operação: pins antigos (develop e worktrees de outros cards até o T14 e o bump) continuam com registro de projeto; o shim não age neles. Os demais cards seguem pausados durante o piloto.
- Sem mudança em `backend/`, `frontend/src/`, `.cursor/process-fsm.yaml`, estados, eventos, gates humanos, guard de T14 ou regras de release; em Cursor, Codex e OpenCode muda só o registro dos hooks (com a revisão por digest) e, no Codex, a aceitação de versão do coletor; Grok Build e dsh não mudam.
