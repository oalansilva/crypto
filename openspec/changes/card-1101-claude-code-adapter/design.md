UI impact: none
live_route: N/A — harness de processo, sem tela
surface: none

Ausência justificada: este card muda só o processo local (pontes, hooks, seleção de modelos, evidência e mensagens de terminal/handoff) do Claude Code. Não há tela, rota ou componente de produto. Prototype: N/A; nenhum HTML gerado ou copiado. Impeccable: N/A porque não existe superfície visual; crítica de Design e aprovação humana (T7) continuam obrigatórias.

## Context

O body grelhado do #1101 é a história; este pacote só define o *como*. O Claude Code lê `AGENTS.md`, mas não é cliente do fluxo: `model_selection.py` aceita só `cursor/codex/grok/opencode/dsh` (`CLIENTS`, linha 23), `process_event --client` tem as mesmas cinco opções, `paging.page()` só tem contexto específico para Codex e não há `CLAUDE.md`, `.claude/skills/`, `.claude/settings.json` nem `.claude/agents/` no repo. Este próprio Design-autor nasceu no Claude Code sem captura (exceção registrada no prompt do pai); fechar essa lacuna é o objeto do card.

Precedente a espelhar: o adapter Codex (#1042) e a evidência de runtime Codex (#1095):

- pontes `.agents/skills/<nome>/SKILL.md` que só mandam ler `.cursor/skills/<nome>/SKILL.md`, com manifesto `.agents/skills/.covenant-flow-bridges.json` (geradas por `codex_skills.py`);
- `.codex/hooks.json` → `codex_adapter.py` (`session-start` com a página Moore de `paging.page()`, `pre-tool-use` com `guard.decide()` e `validate_spawn()`, `post-tool-use`/`stop` com Impeccable), deny em qualquer exceção;
- `.codex/agents/{diff,code}-reviewer.toml` com `sandbox_mode = "read-only"`, sem par de modelo fixo;
- `model_selection.py resolve --client codex` → captura por nascimento → `validate_spawn` no hook;
- `codex_evidence.py prepare/collect` lendo o rollout local, `codex_proxy.py`, `codex_review.py verify-wave`;
- `process_event` detecta `CODEX_THREAD_ID` e exige `codex_evidence.preflight` antes de `iniciar_design`, `recriticar`, `submeter_design`, `iniciar_apply`, `pedir_review`, `aceitar_sha`, `integrar_develop`.

### Capacidades do Claude Code levantadas para este Design

Fontes: documentação oficial (`code.claude.com/docs/en/*`, para onde `docs.claude.com/en/docs/claude-code/*` redireciona) lida em 2026-10-13, e inspeção local desta conta (Claude Code `2.1.296`, `entrypoint=cli`) sobre a própria sessão deste Design. "Provado" aqui significa documentado ou observado localmente; nada disso substitui o ensaio do Apply nem o piloto.

| Capacidade | Fonte | Situação |
| --- | --- | --- |
| Lê `AGENTS.md` sem `CLAUDE.md`; com `CLAUDE.md`/`CLAUDE.local.md` presente lê só `CLAUDE.md`; `@path` importa arquivos (até 4 saltos); nada em `.agents/` é lido | docs `memory` (seções AGENTS.md e Import) | provado (doc); observado: esta sessão carregou `AGENTS.md` |
| Skills de projeto em `.claude/skills/<nome>/SKILL.md`, descobertas do cwd até a raiz do repo; em worktree sem `.claude/skills` cai para o checkout principal (v2.1.277+) | docs `skills` | provado (doc) |
| Hooks `SessionStart` (com `additionalContext`), `PreToolUse` (deny por `hookSpecificOutput.permissionDecision="deny"` + `permissionDecisionReason`), `PostToolUse` (`additionalContext`), `SubagentStart`, `SubagentStop` (com `agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message`), `Stop` | docs `hooks` | provado (doc) |
| Hooks de settings disparam também nas chamadas de ferramenta dos subagentes, com `agent_id`/`agent_type` no input | docs `hooks` ("Hooks from settings files … also run inside subagents") | provado (doc) |
| `PreToolUse` cobre `Agent` com `tool_input.model`; `Write`/`Edit` com `file_path` absoluto | docs `hooks` (schemas de tool_input) | provado (doc); `tool_input.effort` do Agent: a provar no ensaio do Apply, com payload real gravado por versão (§2) |
| Hook que expira ou sai com código ≠ 0/2 **não bloqueia** a ferramenta; `onFailure: "block"` (v2.1.295+) faz bloquear | docs `hooks` (Timeouts, Other exit codes) | provado (doc) |
| Confiança: sessão interativa segura os hooks de settings até o diálogo de confiança do workspace; `-p`/SDK trata a pasta como confiável e roda hooks commitados sem diálogo | docs `hooks` (Workspace trust), sem âncora estável registrada neste Design | **a provar** no ensaio 8.2/8.3; o desenho não depende disso (§9 exige registro de confiança próprio em qualquer modo) |
| Subagentes em `.claude/agents/*.md` com `tools`/`disallowedTools`, `model` (alias, id completo ou `inherit`), `effort`; ordem do modelo: parâmetro por invocação > frontmatter > `CLAUDE_CODE_SUBAGENT_MODEL` > modelo do pai; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` e allowlist `availableModels` da organização podem substituir; `effort` por invocação (v2.1.292+) sobrepõe o frontmatter e é sobreposto por `CLAUDE_CODE_EFFORT_LEVEL` | docs `sub-agents` | provado (doc) |
| Subagente pode criar subagentes até 3 níveis; remover `Agent` de `tools` impede | docs `sub-agents` | provado (doc) |
| No host local, o parâmetro `model` do tool Agent aceita só alias (`sonnet`, `opus`, `haiku`, `fable`) e há parâmetro `effort` (`low`…`max`) | schema do tool Agent exposto nesta sessão 2.1.296 | observado localmente |
| Transcript do pai em `~/.claude/projects/<slug>/<session_id>.jsonl`; filho em `<session_id>/subagents/agent-<agentId>.jsonl` + `.meta.json` (`agentType`, `description`, `model` alias, `toolUseId`); registros `assistant` trazem `message.model` (id completo), `effort`, `perTurnEffort`, `requestedModel`, `isSidechain`, `agentId`, `sessionId`, `version`, `cwd`, `entrypoint`; o `toolUseResult` do pai traz `agentId`, `status` e `resolvedModel` | inspeção local desta sessão (pai e dois filhos `grill-card 1101`/`design-autor 1101`, todos `claude-opus-5-5`, `effort=medium`) | observado localmente; formato interno, não documentado como contrato. Os filhos nasceram **sem** `effort` explícito e rodaram em `medium`: o host não herda `high` do pai nem da seleção, por isso o adapter exige `effort` explícito em todo spawn (§2, §4) |
| Ambiente dos comandos traz `CLAUDECODE=1`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_CODE_ENTRYPOINT`, `CLAUDE_EFFORT`, `AI_AGENT=claude-code_<versão>_agent`, `CLAUDE_CODE_CHILD_SESSION=1` dentro de filho | inspeção local (valores secretos não registrados) | observado localmente |
| Terminal, extensões VS Code/JetBrains e Desktop local leem os mesmos arquivos de settings; extensão e Desktop trazem cópia própria do Claude Code (versão pode diferir); Desktop tem sessões SSH que instalam o Claude Code no host remoto | docs `settings`, `vs-code`, `desktop` | provado (doc) |
| Sessão de nuvem (claude.ai/code, `--cloud`) roda em VM com clone novo; lê `.claude/settings.json` (um repo), não lê `~/.claude/settings.json` nem `.claude/settings.local.json`; credenciais GitHub ficam fora da VM via proxy; subagentes de `.claude/agents/` funcionam; Remote Control permite dirigir uma sessão local a partir do navegador | docs `claude-code-on-the-web`, `settings` | provado (doc) |
| `AskUserQuestion` disponível para o pai | tool usado pelas skills OpenSpec do repo | limites (nº de opções, uso em filho) a provar |

## Goals / Non-Goals

**Goals:**

- Tornar o Claude Code o sexto adapter, cooperativo, com a mesma FSM, as mesmas skills canônicas e a mesma seleção local (entrada `claude` própria).
- Guard de escrita e de nascimento no Claude Code equivalente ao Codex, fail-closed em erro, timeout e configuração ausente.
- Evidência de runtime coletada dos transcripts locais, vinculada a nascimento, com recusa quando ausente ou divergente.
- Falha visível por superfície, sem fallback.
- Piloto empilhado e card real de troca de cliente, ambos com QA verde no Claude Code, como condição do T14 deste card (decisões de Alan no Design).
- Entregar o adapter **não oficial**, travado por teste.

**Non-Goals:**

- Alterar T0–T18, estados, gates humanos, regras de release ou `.cursor/process-fsm.yaml`.
- Copiar FSM, runbook, skills ou política de modelos para `.claude/`; segundo mapa de modelos.
- Mudar o comportamento de Cursor, Codex, Grok, OpenCode ou dsh; código em `backend/` ou `frontend/src/`.
- Reivindicar modo Auto; tratar o modo de permissão `auto`/`bypassPermissions` do Claude Code como autorização de processo.
- Sessões de nuvem com seleção ou evidência próprias (não há `$HOME/.config/covenant-flow` nem transcripts locais lá): falham visivelmente neste card.
- Oficialização: `AGENTS.md` (renderer `scripts/process-fsm/overlay.py` `render_agents` + pin, testes `test_overlay.py`/`test_paging.py`), linha "Cliente ativo" da skill e descrição do board. Vai para card de seguimento, com T1 de Alan, depois do piloto e da revisão de confiança (decisão (d) de Alan).

## Decisions

### 1. Pontes: `CLAUDE.md` importa `AGENTS.md`; skills por pontes geradas com manifesto

`CLAUDE.md` na raiz contém só o import `@AGENTS.md` e uma linha dizendo que é ponte (sem lei, sem citar o Claude Code como cliente). Motivo: o Claude Code já lê `AGENTS.md` quando não há `CLAUDE.md`, mas (a) a doc registra sessões em que a leitura direta não está disponível e manda importar a partir de um `CLAUDE.md`; (b) um `CLAUDE.local.md` do operador desligaria a leitura de `AGENTS.md`, enquanto o import continua valendo. Alternativa rejeitada: depender só da leitura nativa (frágil) ou copiar o conteúdo (dual-write).

`.claude/skills/<nome>/SKILL.md` são pontes com o mesmo frontmatter `name`/`description` do canônico e corpo "leia `.cursor/skills/<nome>/SKILL.md` completo; esta ponte não autoriza nem define estado", mais manifesto `.claude/skills/.covenant-flow-bridges.json` com SHA-256 de cada ponte. O conjunto é o mesmo das pontes Codex (manifesto atual com 18 skills). `impeccable` e `playwright-cli`, que em `.agents/skills/` são conteúdo vendorado e não pontes, ganham ponte apontando para o caminho vendorado existente. Gerador: generalizar `codex_skills.py` com diretório-alvo e nome de manifesto parametrizados (ou módulo fino `claude_skills.py` que o reutiliza) — detalhe de Apply (P3). Instalação recusa ponte local divergente do manifesto em vez de sobrescrever, como no Codex.

### 2. Hooks: `.claude/settings.json` → `claude_adapter.py`, fail-closed

Bloco `hooks` em `.claude/settings.json` (compartilhado, commitado), comandos `python3 "$CLAUDE_PROJECT_DIR/scripts/process-fsm/claude_adapter.py" <evento>` com `timeout` explícito e `onFailure: "block"` nos eventos que gateiam (requer 2.1.295+; versão menor = capacidade ausente, ver §7).

- `SessionStart` (matcher `startup|resume|clear|compact`): injeta `paging.page(client="claude")` como `additionalContext` — Moore page com `q`, `bound_card`, `q_git`, `enabled_events`, `context_file[Status]` e um bloco `CLAUDE_CLIENT_CONTEXT` curto (análogo a `CODEX_CLIENT_CONTEXT`). Falha de Status = `Status unread. Write produto deny.` Também grava um *heartbeat* da sessão (`session_id`, `transcript_path`, versão, entrypoint, digest da definição de hooks em uso) num diretório privado da conta, consumido pelo preflight (§6).
- `PreToolUse`, matcher `Bash|Edit|Write|MultiEdit|NotebookEdit|Agent`: normaliza nomes (`NotebookEdit` → rota de notebook do Guard; `MultiEdit` se existir no host — a provar) e chama `guard.decide()` com o mesmo `status_provider` do Codex. Deny = JSON `permissionDecision: "deny"` com o motivo do Guard. Exceção ou input inválido = deny (nunca exit 1, que a doc define como não bloqueante). Product globs, design globs, branch de integração e binding vêm do overlay, como hoje: em `develop`, em `Todo` ou sem card vinculado o produto é negado por comando e por edição; em `Design` passam `openspec/changes/**` e protótipos; produto só no worktree `card-<id>-*` depois de T8.
  - Em chamada de **subagente** (`agent_id` presente): `Agent` é sempre negado (filhos não criam netos; isso também cobre "Apply não spawna reviewers"); para `agent_type` `diff-reviewer`/`code-reviewer`, qualquer ferramenta fora de `Read|Grep|Glob` é negada (defesa em profundidade além da allowlist do agente).
  - `Agent` do pai: `validate_spawn("claude", tool_input)` contra a captura citada no prompt (`model_selection_capture:`), mais checagem do receipt de evidência (`runtime_evidence_birth:`) e das variáveis que sobrepõem a escolha (`CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, `CLAUDE_CODE_EFFORT_LEVEL`): qualquer uma definida = deny visível. `Agent` sem `model` ou sem `effort` = deny (sem herança): o host roda filho sem `effort` em `medium` (observado), então `effort` explícito por spawn é obrigatório.
  - Origem do esforço no hook: o adapter lê o esforço pedido **só** de `tool_input.effort` do `Agent`. Nunca usa o campo comum de sessão do input do hook (esforço do pai), `CLAUDE_EFFORT` nem o frontmatter. O ensaio do Apply grava o payload real de `PreToolUse` do `Agent` na versão qualificada como fixture; se nessa versão o campo `tool_input.effort` não existir, o hook nega com `unsupported_schema` visível para aquela versão e **não** aceita spawn validado só por `model`. A checagem de `effort` por turno na coleta (§4 passo 4, §5) continua.
  - Verificação antes da primeira escrita do filho: no primeiro `Edit`/`Write`/`MultiEdit`/`NotebookEdit` ou `Bash` classificado como escrita pelo Guard vindo de um subagente (`PreToolUse` com `agent_id`), o adapter lê o último registro `assistant` do transcript desse filho (`message.model`, `effort`) e compara com a captura do receipt daquele nascimento. Divergente, ausente ou ilegível = deny + receipt marcado `model_mismatch`; o filho não escreve e o pai precisa de nascimento novo. Igual = marca o receipt como verificado e as escritas seguintes do mesmo filho não releem (a coleta final ainda confere todos os turnos).
- `PostToolUse`, matcher `Edit|Write|MultiEdit|NotebookEdit|Bash`: roda o mesmo `.agents/skills/impeccable/scripts/hook.mjs` (cujo cabeçalho já declara suporte a eventos Claude Code) com `IMPECCABLE_HOOK_HARNESS=claude`, nas mesmas condições dos outros clientes; advisory. Matcher `Agent`: confere `resolvedModel` do resultado contra a captura (§4) e anota divergência no receipt.
- `SubagentStop`: só evidência — registra `agent_id`, `agent_type`, `agent_transcript_path` e presença de `last_assistant_message` no receipt do nascimento. Nunca devolve `decision: "block"` (na doc isso mantém o filho rodando, não destapa o pai).
- `Stop`: deep pass Impeccable advisory, como no Codex.

Destape: no Claude Code o filho em primeiro plano devolve o resultado no próprio turno do pai, e o filho em background gera notificação de conclusão ao pai (comportamento observado nesta sessão; garantia formal a provar). Por isso o adapter não usa sidecar `awaiting-task.json` nem poke; o runbook ganha uma linha dizendo isso. Interrupção/erro do filho continua não sendo sucesso.

Alternativas rejeitadas: hooks em `~/.claude/settings.json` (não versionados, não vão para nuvem, não reproduzíveis pelo pin); hooks em frontmatter de agente (só valem no filho e têm regra de confiança mais estrita); `permissions.deny` como Guard (estático, não conhece Status).

### 3. Agentes de review: `.claude/agents/{diff-reviewer,code-reviewer}.md` só leitura

Frontmatter: `name`, `description`, `tools: Read, Grep, Glob` (sem `Bash`, `Edit`, `Write`, `Agent`), **sem** `model`/`effort` — o par vem por invocação da captura, igual à regra Codex de não fixar pares em `.codex/agents/*.toml`. O corpo reaproveita o contrato de `.cursor/agents/<nome>.md` (intervalo por `review_diff_path:`/`## Diff`, sem git, sem transcripts); gerar a partir do canônico com verificação de hash em vez de manter texto duplicado é detalhe de Apply (P3).

Onda: o pai materializa o diff com `materialize_review_diff.py` e o SHA-256, prepara as duas capturas `claude/execucao` (wave capture) e os dois receipts, e emite os dois `Agent` (`subagent_type` `diff-reviewer` e `code-reviewer`) **na mesma mensagem do assistente**. Diferente do Codex, não é preciso sessão dedicada read-only: a allowlist de ferramentas é por subagente (doc), e o pai continua gravável para registrar proxies. `claude_review.py verify-wave` exige: dois papéis, `agentId` distintos, as duas chamadas na mesma mensagem do pai, mesmo path+SHA nos prompts, nenhum `tool_use` fora de `Read|Grep|Glob` nos transcripts dos filhos, `completed` com payload e par observado igual à captura. Depois, `review_process_checklist.py` como hoje.

Design-autor, crítico, Assessment A/B, grill, Apply, QA e `fecho-lote` nascem como `general-purpose` com prompt autocontido (o runbook já admite `generalPurpose` com corpo colado); papel no `description` com o needle do classificador.

### 4. Seleção de modelos: contrato `claude-agent-pair-v1`

`.cursor/model-policy.yaml` ganha:

```yaml
  claude:
    contract: claude-agent-pair-v1
    fields: [label, model, effort]
    required: [label, model, effort]
```

e `model_selection.py` passa a aceitar `claude` em `CLIENTS`, no schema local e em `native_arguments`. Seleção da conta (edição local, sem commit; valores do body): `juizo: {label: "Opus 5.5", model: claude-opus-5-5, effort: high}`, `execucao: {label: "Sonnet 5.5", model: claude-sonnet-5-5, effort: high}`. Valores dos outros clientes não mudam; a migração existente (`preserve_existing`) não é reaplicada — o operador acrescenta o bloco `claude` e roda `model_selection.py validate`.

Rota nativa: parâmetros por invocação do tool `Agent` (`model` + `effort`), que a doc coloca no topo da precedência. O `model` do tool, neste host, aceita apenas alias de família; logo `native_arguments("claude")` traduz o id completo para o alias da família (`claude-opus-*` → `opus`, `claude-sonnet-*` → `sonnet`, …) a partir de uma tabela de **tradução de capacidade** versionada na política — não é segundo mapa de modelos, porque não escolhe modelo, só codifica o id selecionado no formato do host. O id completo continua na captura e é a referência de verificação: o alias pode resolver para outra versão, e `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` ou `availableModels` da organização podem substituir (doc). Por isso:

1. Antes do nascimento: resolver valida faixa/papel/proibidos, versão do host com `effort` por invocação (≥ 2.1.292) e ausência das variáveis de override; senão erro visível. O `Agent` sempre carrega `model` **e** `effort` explícitos (sem `effort` o host usa `medium`).
2. Logo após o spawn (`PostToolUse` em `Agent`): `resolvedModel` ≠ id capturado → receipt marcado `model_mismatch`, o pai não aceita o resultado e precisa de nascimento novo; nada é trocado em silêncio.
3. Antes da primeira escrita do filho: comparação do último registro `assistant` do transcript do filho com a captura (§2); divergente/ilegível = deny + `model_mismatch`.
4. Na coleta: cada registro `assistant` do transcript do filho precisa de `message.model` = id capturado e `effort` = esforço capturado (checagem por turno mantida).

Se o host não aceitar esforço por filho (versão antiga, superfície com cópia antiga, variável `CLAUDE_CODE_EFFORT_LEVEL` definida), a etapa falha visivelmente: não se omite `effort`, não se usa o esforço da sessão e não se troca de modelo. Um catálogo nativo local de modelos para validar o id antes do spawn não foi encontrado nesta inspeção; se existir, entra como validação extra (a provar no Apply). Alternativas rejeitadas: `model` no frontmatter dos agentes (fixa par em arquivo versionado); `--agents` JSON na abertura da sessão (congela a escolha durante a sessão, viola "próximo spawn usa a escolha nova"); `CLAUDE_CODE_SUBAGENT_MODEL` (uma só faixa por sessão).

Resume/continuação: `canContinueAgent` existe no resultado do spawn; continuação de filho usa a captura de nascimento e não aceita novos parâmetros, como `model_proxy.verify_continuation` já exige.

### 5. Evidência de runtime: driver `claude-transcript-v1`

`claude_evidence.py`, espelhando `codex_evidence.py`:

- **Localizador**: `CLAUDE_CODE_SESSION_ID` + `transcript_path` do heartbeat do `SessionStart` (o input de hook traz `transcript_path`). Fonte autoritativa candidata: o JSONL do pai e `subagents/agent-<agentId>.jsonl` + `.meta.json` sob `~/.claude/projects/`. Leitura só leitura, sem mutação, exigindo linhas JSON completas (arquivo truncado = `source_truncated`).
- **Qualificação por versão**: o driver declara as versões suportadas (`2.1.296` a qualificar no Apply com ensaio real). Outra versão = `unverified` e recusa nos gates, como no Codex; o formato não é contrato público, então mudança de schema vira `unsupported_schema` visível.
- **`prepare`** (antes de cada nascimento): valida sessão ativa, cwd = worktree, entrypoint/superfície, captura, e grava receipt privado (0400) com `task_name` = `description` única com needle, digest da captura e do diff quando houver.
- **`collect`** (após o retorno): acha no transcript do pai o `tool_use` `Agent` com aquela `description`, o `toolUseResult` (`agentId`, `resolvedModel`, `status`), o transcript do filho (`isSidechain`, `agentId`, `sessionId`), extrai modelo/esforço observados por turno, ferramentas usadas, término e payload retornado; sela com digests. `observed` nunca é copiado de `requested`; ausência = `unavailable` e reprova.
- **`claude_proxy.py`** registra a linha de proxy (`proxy modelo: <papel> → <rótulo> (<slug>)`, cliente `claude`, superfície, versão, status, payload) a partir do envelope; `model_proxy.evidence` ganha o cliente `claude`.
- Limpeza automática de transcripts (`cleanupPeriodDays`) pode apagar a fonte: coleta no mesmo turno do retorno; origem irrecuperável exige nascimento novo, nunca receipt retroativo.

### 6. `process_event --client claude` e preflight

`--client` aceita `claude`. Detecção nativa: `CLAUDECODE=1` → `claude`; coexistência com `CODEX_THREAD_ID` → precedência do processo mais interno (Codex aninhado no `Bash` do Claude Code continua `codex`, ver P3 aceitos), senão `reject ambiguous_client`; `--client`/`COVENANT_CLIENT` divergente do nativo → `reject ambiguous_client` (generalização do caso Codex). Para o mesmo conjunto de eventos que hoje exige preflight Codex, `claude` exige `claude_evidence.preflight`: transcript da sessão legível e versão qualificada, heartbeat presente e com digest de hooks igual ao registro de confiança (§9). Hooks ausentes, desligados (`disableAllHooks`) ou não confiados tornam-se assim visíveis na primeira transição dependente, sem nova transição nem permissão na FSM. Eventos humanos (T1, T7, T15, T18) continuam `reject actor`; T16 continua `fechar_release`. `implemente` em `Todo` não tem aresta: a página Moore e o Guard produzem a frase com Status atual e "Apply só depois de Pronto para Dev (T7 teu)".

### 7. Superfícies

| Superfície | Onde roda | Esperado |
| --- | --- | --- |
| Terminal (CLI) na VM | conta executora | caminho de referência; tudo disponível |
| IDE (VS Code/JetBrains) via Remote-SSH na VM | Claude Code embarcado na extensão, mesma conta | mesmos settings/hooks/skills (doc); versão própria da extensão checada pelo preflight; abaixo do mínimo = falha visível |
| Desktop, sessão SSH para a VM | Claude Code instalado pelo Desktop no host remoto | mesmos arquivos na VM (doc); a provar no piloto |
| Desktop **Local** no Windows | máquina Windows | sem seleção local, sem `gh`/worktree da VM: resolver e Status falham visivelmente; nenhuma etapa avança |
| Web claude.ai/code dirigindo sessão local por Remote Control | sessão CLI da VM | equivalente ao terminal (a provar no piloto) |
| Web/`--cloud`, sessão de nuvem | VM Anthropic, clone novo | lê `.claude/settings.json` (hooks rodam), mas não há `$HOME/.config/covenant-flow` nem acesso garantido ao board: resolver falha (`model-selection.yaml` ausente) e Status fica `unread` → Write produto deny, nenhum filho nasce; falha visível, sem fallback |

A superfície observada (`CLAUDE_CODE_ENTRYPOINT` e equivalentes de nuvem/remote, a provar) entra no heartbeat e no proxy.

### 8. Fecho de lote no Claude Code

Só por pedido explícito de Alan. Pré-requisito: o próprio pai é de execução do Claude Code — `release_model_selection.load_execucao_pair(root, "claude", capture)` e `check_runtime_model` comparam a captura `claude/execucao` (Sonnet 5.5, `high`) com o modelo/esforço observados do **pai** no transcript da sessão (último registro `assistant`: `message.model`, `effort`). Divergente/`unavailable` recusa T16 e pede sessão nova configurada (`/model` + `/effort`, ou flags equivalentes — a provar); não muda o pai vivo e não exige modelo de outro cliente. O filho `fecho-lote kaizen` nasce `general-purpose` com par capturado de `claude/execucao`, prompt autocontido do runbook, sem sidecar; o pai chama `process_event fechar_release` após `completed` e `release-guard post` PASS. Homologar continua só de Alan.

### 9. Revisão de confiança dos hooks

Pin e instalação não dão confiança. Em sessão interativa o Claude Code segura hooks até o diálogo de confiança do workspace; em `-p`/SDK roda hooks commitados sem diálogo (doc) — portanto o diálogo do host não é a revisão exigida. A revisão é um ato explícito do operador: ler `.claude/settings.json` e `claude_adapter.py` (e módulos importados) e registrar `claude_adapter.py trust --record` num arquivo da conta (`$HOME/.config/covenant-flow/claude-hook-trust.json`) com os digests revisados. O heartbeat compara o digest em uso com o registro; divergência = página com `hooks não revisados`, deny de Write de produto e de `Agent`, preflight recusado. Nunca usar bypass, nem tratar hook ausente/não confiado como proteção.

### 10. Troca de cliente entre etapas

Nada na FSM depende do cliente. Cada captura e cada proxy registram `client`; o handoff de cada etapa lista cliente e modelo observado por filho e repete os das etapas anteriores a partir dos comentários de handoff do card. Ex.: Design no Cursor (proxies `cursor`) e Apply no Claude Code (proxies `claude`) avançam pelos mesmos `iniciar_apply`/`pedir_review`/`aceitar_sha`/`integrar_develop`. Um filho nunca é transferido para outro cliente como fallback.

Prova viva (decisão (c) de Alan): um **segundo card real pequeno** ("card de troca"), não ensaio de contrato. Design (autor + crítico) no Cursor ou no Codex, com a evidência de runtime daquele cliente (proxies `cursor` com o mecanismo do Cursor, ou `codex` com receipt/rollout de #1095); T7 de Alan; Apply, onda de review e QA no Claude Code até QA verde, com proxies `claude` por filho. O handoff de QA lista cliente e modelo observado de cada filho das duas etapas. O card de troca também roda empilhado: seu worktree nasce do HEAD revisado do #1101, porque o Apply no Claude Code precisa do adapter que ainda não está em `develop`. QA verde do card de troca é condição do T14 do #1101 (§12).

### 11. Grelha em Em Refinamento

O pai spawna `grill-card` (juízo, Opus 5.5 alto) e só faz relaying. Perguntas fechadas vão por `AskUserQuestion` com **todas** as opções que o filho listou; se o host limitar o número de opções abaixo do que o filho trouxe, o pai divide em perguntas encadeadas ou lista as opções numeradas no texto da mesma pergunta — nunca colapsa para a recomendada. O limite exato e o comportamento em filho são a provar no Apply (detalhe de Apply, P3). O filho escreve o body do issue; `criar_card` continua fora de `process_event`.

### 12. Adapter não oficial, piloto empilhado e card de troca

**Não oficial (decisão (d) de Alan).** Neste card, `AGENTS.md`, a descrição do Project 1 e a linha "Cliente ativo" da skill/runbook não citam o Claude Code como cliente; `CLAUDE.md` e `.claude/` existem como pontes, sem afirmação de cliente. Um teste (tarefa 6.4) trava isso. Nada no diff do #1101 muda `AGENTS.md`, `scripts/process-fsm/overlay.py` (`render_agents`), o pin do `AGENTS.md`, `test_overlay.py`/`test_paging.py` na parte de clientes oficiais ou a descrição do board. Isso tudo é o card de seguimento, aberto depois do piloto e da revisão de confiança, com T1 de Alan; o handoff de Done do #1101 o cita.

**Piloto concluído** = um card piloto pequeno e real percorre no Claude Code Em Refinamento → Design → T7 → Apply → onda de dois reviewers → QA **verde**, com filhos, eventos e evidência (captura, receipt, proxy observado `claude` por filho) registrados. O T14 do piloto não faz parte da definição; ele vem depois do T14 do #1101.

**Ordem (decisão (a) de Alan).**

1. Pré: QA do #1101 verde no SHA revisado; **sem** `integrar_develop`. Revisão de confiança registrada; seleção `claude` validada; driver de evidência qualificado na versão em uso.
2. Bloco `claude` acrescentado à seleção da conta (início da janela, §Migration Plan).
3. Piloto e card de troca nascem em worktrees empilhados no HEAD revisado de `card-1101-claude-code-adapter` e vão até QA verde (piloto inteiro no Claude Code; card de troca com Design no Cursor/Codex e Apply no Claude Code).
4. `review_process_checklist.py --phase postqa` do #1101 passa, incluindo `pilot_evidence`; então o pai chama `integrar_develop` do #1101 (T14).
5. Piloto e card de troca são rebaseados em `develop` e fazem seus T14.

**Exceção local ao "T14 no mesmo turno do verde".** A skill manda o pai chamar `integrar_develop` no mesmo turno do filho QA verde. Para o #1101, e só para ele, essa regra fica suspensa entre o passo 1 e o passo 4: QA verde do #1101 não dispara T14; o pai registra no card "QA verde; T14 aguarda piloto e card de troca (decisão (a) de Alan)" e encerra o turno. O guard de T14 em `process_event` não muda: a espera é garantida pelo item `pilot_evidence` do checklist postqa e pela regra do pai, não por aresta nova. Para o piloto e o card de troca, a regra também fica suspensa entre o QA verde empilhado e o rebase (passo 5); depois do rebase volta a valer.

**Item `pilot_evidence`** em `review_process_checklist.py --phase postqa`. Ativo só quando o change ligado declara o gate (declaração versionada no próprio change, criada no Apply; changes sem declaração não mudam). Lê um JSON de evidência (`--pilot-evidence <path>`, não versionado) e só passa com:

- ids do card piloto e do card de troca, diferentes entre si e do #1101;
- para cada um, o SHA que teve `qa-gate` success na branch empilhada, conferido no GitHub como no QA;
- para cada filho de cada card, o proxy com cliente e modelo observado: todos `claude` no piloto; no card de troca, filhos de Design em `cursor` ou `codex` e filhos de Apply/review/QA em `claude`.

Qualquer campo ausente, SHA sem QA verde, proxy faltante ou com cliente errado = `ERROR: process-checklist failed: pilot_evidence` (bloqueio visível). O guard de T14 continua o mesmo.

**Review e rebase dos cards empilhados (P2-1).** A base do review do piloto é o HEAD revisado do #1101: o pai materializa só `<HEAD #1101>..<HEAD piloto>`, e os dois reviewers nunca recebem o diff do #1101. Depois do T14 do #1101, o piloto é rebaseado em `develop` (`rebase --onto develop <HEAD #1101>`). O pai prova que o diff do piloto é idêntico ao revisado (`git patch-id --stable` igual e digest do diff materializado igual) e só reexecuta o `qa-gate` no SHA novo, sem nova onda de review. Diff diferente ou conflito de rebase = causa visível para Alan no card, sem resolução silenciosa e **nunca** T13 forçado para destravar. O mesmo vale para o card de troca.

**Plano do piloto.**

1. Card piloto pequeno e real (escolhido por Alan em Em Refinamento; sem produto sensível), num chat Claude Code `#<id>` no terminal da VM: grelha → (Alan T1) → `iniciar_design` → Design-autor + crítico → `submeter_design` → (Alan T7) → `iniciar_apply` → Apply-coluna → `pedir_review` → onda de dois reviewers + `verify-wave` → commit/PR → `aceitar_sha` → QA verde. Cada filho com captura, receipt e proxy observado.
2. Negativos no mesmo ambiente: `implemente` em `Todo` (nada muda, frase com Status); Write de produto em `develop` e sem card (Edit e Bash negados, readback igual); seleção `claude/execucao` com modelo inexistente (spawn recusado visivelmente); hooks com digest alterado (preflight recusa).
3. Superfícies: o piloto registra, para IDE Remote-SSH, Desktop SSH, Remote Control pela web e sessão de nuvem, o resultado de SessionStart/deny/resolver/evidência; superfície sem capacidade fica como falha visível documentada.
4. Fecho de lote: se houver lote no período, a parte do agente é conduzida no Claude Code; senão, ensaio do pré-requisito de T16 (recusa com pai em juízo, aceitação com pai em execução) sem `fechar_release`.

## Risks / Trade-offs

- [Transcript JSONL é formato interno, pode mudar sem aviso] → driver versionado por versão do host; schema desconhecido = `unsupported_schema`/`unverified` e gate recusa; nunca inferir.
- [`tool_input.effort` do `Agent` ausente ou com outro nome numa versão] → payload real gravado no ensaio por versão; campo ausente = deny `unsupported_schema` naquela versão; nunca validar só `model` nem ler o esforço da sessão.
- [Filho sem `effort` explícito roda em `medium` (observado)] → deny de spawn sem `effort`; verificação antes da primeira escrita e por turno na coleta.
- [Alias de família resolve para versão diferente do id selecionado, ou a organização substitui o modelo] → verificação de `resolvedModel` logo após o spawn, do transcript do filho antes da primeira escrita e de `message.model` na coleta; divergência invalida o filho.
- [Hook que expira/erra não bloqueia por padrão] → `onFailure: "block"`, `timeout` explícito, adapter sempre emite JSON de deny em exceção.
- [`-p`/SDK pode rodar hooks sem diálogo (a provar); `.claude/settings.local.json` ou user settings podem `disableAllHooks`] → registro de confiança próprio + heartbeat + preflight em `process_event`; limite cooperativo documentado (como Codex: sem Auto).
- [Modo de permissão `auto`/`bypassPermissions` do Claude Code e Auto padrão na extensão VS Code] → o adapter não depende do modo de permissão; deny de hook vale em qualquer modo (comportamento em `bypassPermissions` a provar no Apply; se não valer, a superfície/modo é recusado pelo preflight).
- [Filho pode criar netos] → deny de `Agent` com `agent_id` no `PreToolUse`.
- [Rotas que não disparam `PreToolUse` (ferramentas MCP, LSP, Monitor etc.)] → ensaio lista rotas cobertas e não cobertas; não se afirma interceptação completa.
- [Worktree sem `.claude/skills` cai no checkout principal] → durante a janela, `develop` ainda não tem as pontes; piloto e card de troca rodam em worktrees empilhados que têm `.claude/` versionado; preflight compara manifesto do worktree.
- [Limpeza de transcripts] → coleta no mesmo turno; nascimento novo se a fonte sumir.
- [Sessão de nuvem sem seleção/board] → recusa visível; suporte de nuvem fica fora deste card.
- [Bloco `claude` na seleção compartilhada quebra o resolver antigo de `develop` e dos outros worktrees durante a janela] → aceito por Alan (decisão (b)): demais cards pausados nesta conta, falha visível do resolver antigo até o T14 do #1101; piloto interrompido = remover o bloco com backup.
- [#1101 parado em QA verde por mais tempo que o normal; `develop` pode andar (hotfix)] → janela curta com pausa; se `develop` andar, o #1101 é sincronizado pelo caminho existente e o QA reexecuta; os cards empilhados continuam com review só do próprio diff.
- [Rebase dos cards empilhados muda o diff ou conflita] → prova por `patch-id`/digest; divergência ou conflito = causa visível para Alan, nunca T13 forçado nem nova onda silenciosa.
- [`CLAUDECODE=1` herdado por processo aninhado (ex.: Codex rodando no `Bash` do Claude Code)] → precedência do sinal nativo mais interno (P3 abaixo), com teste que mantém o Codex como hoje.

## P3 aceitos

Detalhes de Apply aceitos na crítica, sem reabrir o Design:

- `AGENTS.md` só muda via renderer `render_agents` + pin, nunca à mão — e isso fica no card de seguimento; neste card o arquivo não muda.
- `.claude/agents/*.md` curtos, no padrão de `.codex/agents/*.toml`, ou ponte para `.cursor/agents/<nome>.md`; sem cópia do corpo canônico.
- `/opsx:*` no Claude Code via pontes `.claude/skills/openspec-*`; sem `.claude/commands`.
- Precedência de cliente: `CLAUDECODE=1` herdado por processo aninhado (Codex dentro do `Bash` do Claude Code) não pode transformar o Codex em `claude`; o sinal nativo do processo mais interno (`CODEX_THREAD_ID`) prevalece quando a herança é demonstrável, senão `ambiguous_client`. Teste mantém o comportamento atual do Codex.
- Specs base `cursor-harness` ("All five clients"), `covenant-flow` ("five client adapters") e `process-harness` ("five adapters"): aceito manter a redação neste card, porque os cinco continuam sendo os clientes **oficiais**; o requisito novo de `claude-code-harness` cobre o adapter não oficial e o instalador. A atualização da contagem fica para o card de seguimento.
- A afirmação "hooks rodam sem diálogo em `-p`/SDK" está marcada como **a provar** (tabela de capacidades); o desenho não depende dela.
- Também: generalizar `codex_skills.py`/`codex_hooks.py` ou módulos `claude_*`; nome/local do heartbeat, do registro de confiança e da declaração do gate de piloto; normalização de `NotebookEdit`/`MultiEdit` no Guard; forma de dividir perguntas do `AskUserQuestion`; nome do doc `docs/claude-runtime-evidence.md`.

## Migration Plan

1. Apply no worktree do card (consumidor) e no worktree do nucleus `covenant-flow` (pin novo), como no #1080/#1042.
2. Review, commit, PR e QA verde do #1101 com o Claude Code não oficial; **sem** `integrar_develop` (exceção §12).
3. Operador: revisão e registro de confiança dos hooks.
4. Início da janela do piloto (decisão (b) de Alan): os demais cards desta conta são pausados; backup da seleção da conta; bloco `claude` acrescentado + `model_selection.py validate` no worktree do #1101. Daqui até o T14 do #1101, o resolver antigo de `develop` e dos outros worktrees recusa o arquivo de forma visível — aceito.
5. Piloto e card de troca em worktrees empilhados no HEAD revisado do #1101 até QA verde. Exceção à pausa: o card de troca faz o Design no Cursor ou no Codex nesse worktree empilhado (o resolver de lá já é novo).
6. Checklist postqa do #1101 com `pilot_evidence` → T14 do #1101.
7. Piloto e card de troca rebaseados em `develop` com prova de diff idêntico → `qa-gate` → T14 de cada.
8. Fim da janela: os cards pausados rebaseiam em `develop` antes de retomar (para ganhar o validador novo). Handoff de Done cita o card de seguimento de oficialização.

Os passos 7–8 rodam depois do Done técnico do #1101 e ficam fora de `tasks.md`, porque o checklist postqa exige todas as tasks marcadas antes do T14; a task 10.2 os registra no card antes do T14.

Piloto interrompido (antes do passo 6): remover o bloco `claude` da seleção da conta restaurando o backup, para que `develop` e os outros worktrees voltem a resolver; os cards pausados retomam; o #1101 fica em QA verde sem T14 e a causa é registrada no card.

O Apply ensaia a migração com cópia temporária do arquivo de seleção (validador novo aceita o bloco; validador antigo recusa visivelmente), sem tocar o arquivo real.

Rollback: remover `CLAUDE.md`, `.claude/`, `scripts/process-fsm/claude_*.py`, o item `pilot_evidence` e o contrato `claude` da política, e o operador remover explicitamente o bloco `claude` da seleção local (com backup), porque o validador revertido o recusaria. Os demais clientes voltam ao estado anterior sem outra mudança.

## Open Questions

Nenhuma aberta. Ordem piloto × T14, janela e prova da troca de cliente foram decididas por Alan no Design (decisões (a)–(d), registradas no body). Suporte real de nuvem (seleção e evidência na VM de nuvem) fica para card futuro, se Alan quiser.

## Design Critique

- P1-1 — oficialização sem aresta legal com piloto empilhado: disposition: resolvido no único rework; oficialização movida para card de seguimento (decisão de Alan).
- P1-2 — trava "sem piloto não chega a Done" sem mecanismo: disposition: resolvido; cenário reescrito, exceção local ao T14 no mesmo turno e item `pilot_evidence` no checklist postqa.
- P2-1 — review/rebase dos cards empilhados: disposition: resolvido (§12 "Review e rebase dos cards empilhados").
- P2-2 — origem do esforço do filho: disposition: resolvido; só `tool_input.effort`, ausente = `unsupported_schema`.
- P2-3 — modelo do filho verificado tarde: disposition: resolvido; verificação antes da primeira escrita, `model_mismatch`.
- P3 — detalhes de Apply: disposition: aceitos em "P3 aceitos", sem reabrir como P0/P1.
- verdict: REWORK → resolvido no único rework; uma autoria, uma crítica sem tela, um rework. Snapshot: `.impeccable/critique/1101-card-1101-claude-code-adapter-design-critic.md`.
- Exceção de processo: filhos nascidos no Claude Code sem captura de modelo (cliente ainda não suportado), autorizado por Alan.
