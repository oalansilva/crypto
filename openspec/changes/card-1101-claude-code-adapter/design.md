UI impact: none
live_route: N/A — harness de processo, sem tela
surface: none

Ausência justificada: este card muda só o processo local (registro de hooks na conta, shim, pontes, hooks, seleção de modelos, evidência e mensagens de terminal/handoff) dos clientes do Covenant Flow. Não há tela, rota ou componente de produto. Prototype: N/A; nenhum HTML gerado ou copiado. Impeccable: N/A porque não existe superfície visual; crítica de Design e aprovação humana (T7) continuam obrigatórias.

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

Fontes: documentação oficial (`code.claude.com/docs/en/*`, para onde `docs.claude.com/en/docs/claude-code/*` redireciona) lida em 2026-10-13, e inspeção local desta conta (Claude Code `2.1.296`, `entrypoint=cli`) sobre a própria sessão deste Design. "Provado" aqui significa documentado ou observado localmente; nada disso substitui o ensaio do Apply (8.2, 15.2).

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
| Remote Control permite dirigir uma sessão local a partir do navegador (claude.ai/code); a sessão continua rodando na VM, com os arquivos da conta | docs `claude-code-on-the-web`, `settings` | provado (doc); sessão de nuvem fora do escopo (Non-Goals) |
| `AskUserQuestion` disponível para o pai | tool usado pelas skills OpenSpec do repo | limites (nº de opções, uso em filho) a provar |

### Rework de 2026-10-14: o que o piloto mostrou

O adapter das seções 1–12 foi implementado (PR #1102, commits `bbb7c462`, `bb5a6c94`, `9dc6f043`) e chegou a QA. O piloto #703 expôs dois limites que Alan trouxe para este card (comentários `6167692629` e `6167788244`), e Alan devolveu o card a Design pelo board:

- **Registro preso ao projeto.** O Claude Code carrega `.claude/settings.json` só do diretório de lançamento; `EnterWorktree` não dispara `SessionStart` nem recarrega hooks. Uma sessão aberta em `/source` (develop, ainda sem `.claude/`) e levada ao worktree do card roda sem processo (`hooks_inactive`, achado 13). O mesmo vale, por construção, para `.cursor/hooks.json`, `.codex/hooks.json`, `.grok/hooks/process-fsm.json`, `.opencode/plugin/` e o patch de `.dsh/`: todo cliente depende de a pasta de lançamento ter o pin. Cada repo precisa do pin para ter hooks, e o registro depende da pasta, não do card (achado 15). Por decisão de Alan (2026-10-14, comentário `6169060530`), o rework trata só Claude Code, Cursor, Codex e OpenCode; Grok Build e dsh ficam como estão.
- **Versão fixa.** `claude_evidence.py` recusa qualquer host fora de `QUALIFIED_VERSIONS = ("2.1.296",)`; o host atualizou-se sozinho para 2.1.299 e todos os nascimentos pararam (`unverified`). `codex_evidence.py` tem a mesma trava: o driver é `codex_exec/0.162.1/rollout-v1` e qualquer outra `cli_version` é `unsupported_host`. Os coletores de Cursor, Grok, OpenCode e dsh não têm lista de versões (verificado no código: só `claude_evidence.py` e `codex_evidence.py`; o `host_min_version` da política é piso de capacidade, não lista).

O rework mantém tudo das seções 1–12 que não trata de **onde** os hooks são registrados nem de **como** a versão do host é aceita, e acrescenta as seções 13–18.

### Mecanismos globais de hook por host (para o rework)

"Global" = escopo da conta do operador, carregado em qualquer pasta. Nada aqui está provado nesta conta; o ensaio do Apply (task 11.1) confirma cada linha antes de o pin tirar o registro de projeto daquele host. Os quatro hosts estão instalados nesta VM (`claude`, `cursor-agent`, `codex`, `opencode`) e todos são ensaiados.

| Host | Registro de conta candidato | Registro de projeto que sai | Fonte | Situação |
| --- | --- | --- | --- | --- |
| Claude Code | bloco `hooks` em `~/.claude/settings.json` (escopo usuário; hooks de usuário e de projeto se somam) | bloco `hooks` de `.claude/settings.json` | doc `settings`/`hooks` | a ensaiar |
| Cursor | `~/.cursor/hooks.json` (hooks de usuário) | entradas do Covenant Flow em `.cursor/hooks.json` | doc de hooks do Cursor | a ensaiar |
| Codex CLI | `~/.codex/hooks.json` ou `[hooks]` em `~/.codex/config.toml` | `.codex/hooks.json` | camada de usuário do Codex; regra de confiança do host para hooks de usuário a provar | a ensaiar |
| OpenCode | plugin global em `~/.config/opencode/plugin/` | auto-load de `.opencode/plugin/` | doc de plugins do OpenCode (global e projeto) | a ensaiar na versão instalada |

Grok Build e dsh não entram na tabela: continuam com o registro de projeto atual (`.grok/hooks/process-fsm.json`, `.dsh/cordis.patch.yml` com `dsh_boot.sh`), sem shim, por decisão de Alan.

## Goals / Non-Goals

**Goals:**

- Tornar o Claude Code o sexto adapter, cooperativo, com a mesma FSM, as mesmas skills canônicas e a mesma seleção local (entrada `claude` própria).
- Guard de escrita e de nascimento no Claude Code equivalente ao Codex, fail-closed em erro, timeout e configuração ausente.
- Evidência de runtime coletada dos transcripts locais, vinculada a nascimento, com recusa quando ausente ou divergente.
- Falha visível por superfície, sem fallback.
- Entregar o adapter **não oficial**, travado por teste.
- (Rework) Registro dos hooks na conta do operador para Claude Code, Cursor, Codex e OpenCode, com shim que descobre o consumidor pelo cwd e chama o adapter pinado; processo ativo depois da troca de worktree, sem depender da pasta de lançamento.
- (Rework) Atualização do host não trava o processo: versão aceita pelo formato da fonte de evidência, nunca recusada só pelo número.

**Non-Goals:**

- Alterar T0–T18, estados, gates humanos, regras de release ou `.cursor/process-fsm.yaml`.
- Copiar FSM, runbook, skills ou política de modelos para `.claude/`; segundo mapa de modelos.
- Mudar o comportamento de Cursor, Codex ou OpenCode além do registro dos hooks na conta (com a revisão por digest que ele exige) e da aceitação de versão do coletor Codex; código em `backend/` ou `frontend/src/`.
- Grok Build e dsh (decisão de Alan, 2026-10-14): continuam exatamente como hoje, com o registro de projeto, os stubs e o comportamento atuais; sem registro na conta, sem shim, sem revisão por digest nova e sem a recusa por falta de shim. Levá-los para a conta é card de seguimento.
- Levar para a conta a FSM, adapters, skills ou política: só o registro sai do repositório.
- Travar a versão do host.
- Reivindicar modo Auto; tratar o modo de permissão `auto`/`bypassPermissions` do Claude Code como autorização de processo.
- Sessões de nuvem (claude.ai/code em ambiente de nuvem): não são suportadas por este card (decisão de Alan, 2026-10-14: o Claude Code roda sempre local, pelo CLI). Nenhum requisito, cenário ou ensaio as cobre.
- Oficialização: `AGENTS.md` (renderer `scripts/process-fsm/overlay.py` `render_agents` + pin, testes `test_overlay.py`/`test_paging.py`), linha "Cliente ativo" da skill e descrição do board. Vai para card de seguimento, com T1 de Alan, depois do Done técnico deste card e da revisão de confiança (decisão (d) de Alan; sem depender de piloto, cancelado em 2026-10-15, §12).
- Prova em outras harnesses e superfícies (decisão de Alan, 2026-10-15): piloto empilhado, card de troca de cliente, ensaio deny pelo registro da conta em Cursor/Codex/OpenCode e matriz de superfícies (IDE/Desktop SSH, Remote Control) ficam fora deste card; o app desktop é o #1103.

## Decisions

### 1. Pontes: `CLAUDE.md` importa `AGENTS.md`; skills por pontes geradas com manifesto

`CLAUDE.md` na raiz contém só o import `@AGENTS.md` e uma linha dizendo que é ponte (sem lei, sem citar o Claude Code como cliente). Motivo: o Claude Code já lê `AGENTS.md` quando não há `CLAUDE.md`, mas (a) a doc registra sessões em que a leitura direta não está disponível e manda importar a partir de um `CLAUDE.md`; (b) um `CLAUDE.local.md` do operador desligaria a leitura de `AGENTS.md`, enquanto o import continua valendo. Alternativa rejeitada: depender só da leitura nativa (frágil) ou copiar o conteúdo (dual-write).

`.claude/skills/<nome>/SKILL.md` são pontes com o mesmo frontmatter `name`/`description` do canônico e corpo "leia `.cursor/skills/<nome>/SKILL.md` completo; esta ponte não autoriza nem define estado", mais manifesto `.claude/skills/.covenant-flow-bridges.json` com SHA-256 de cada ponte. O conjunto é o mesmo das pontes Codex (manifesto atual com 18 skills). `impeccable` e `playwright-cli`, que em `.agents/skills/` são conteúdo vendorado e não pontes, ganham ponte apontando para o caminho vendorado existente. Gerador: generalizar `codex_skills.py` com diretório-alvo e nome de manifesto parametrizados (ou módulo fino `claude_skills.py` que o reutiliza) — detalhe de Apply (P3). Instalação recusa ponte local divergente do manifesto em vez de sobrescrever, como no Codex.

### 2. Hooks: registro → `claude_adapter.py`, fail-closed

Bloco `hooks` com `timeout` explícito e `onFailure: "block"` nos eventos que gateiam (requer 2.1.295+; versão menor = capacidade ausente, ver §7). Na primeira implementação ele ficou em `.claude/settings.json` (commitado) chamando `python3 "$CLAUDE_PROJECT_DIR/scripts/process-fsm/claude_adapter.py" <evento>`; o rework move o registro para `~/.claude/settings.json`, com comandos que chamam o shim, e o shim executa `claude_adapter.py <evento>` do worktree descoberto pelo cwd (§13). Eventos, matchers e comportamento abaixo não mudam.

- `SessionStart` (matcher `startup|resume|clear|compact`): injeta `paging.page(client="claude")` como `additionalContext` — Moore page com `q`, `bound_card`, `q_git`, `enabled_events`, `context_file[Status]` e um bloco `CLAUDE_CLIENT_CONTEXT` curto (análogo a `CODEX_CLIENT_CONTEXT`). Falha de Status = `Status unread. Write produto deny.` O *heartbeat* da sessão (`session_id`, `transcript_path`, versão, entrypoint, digest do registro), consumido pelo preflight (§6), passa a ser gravado pelo shim em qualquer pasta (§14).
- `PreToolUse`, matcher `Bash|Edit|Write|MultiEdit|NotebookEdit|Agent`: normaliza nomes (`NotebookEdit` → rota de notebook do Guard; `MultiEdit` se existir no host — a provar) e chama `guard.decide()` com o mesmo `status_provider` do Codex. Deny = JSON `permissionDecision: "deny"` com o motivo do Guard. Exceção ou input inválido = deny (nunca exit 1, que a doc define como não bloqueante). Product globs, design globs, branch de integração e binding vêm do overlay, como hoje: em `develop`, em `Todo` ou sem card vinculado o produto é negado por comando e por edição; em `Design` passam `openspec/changes/**` e protótipos; produto só no worktree `card-<id>-*` depois de T8.
  - Em chamada de **subagente** (`agent_id` presente): `Agent` é sempre negado (filhos não criam netos; isso também cobre "Apply não spawna reviewers"); para `agent_type` `diff-reviewer`/`code-reviewer`, qualquer ferramenta fora de `Read|Grep|Glob` é negada (defesa em profundidade além da allowlist do agente).
  - `Agent` do pai: `validate_spawn("claude", tool_input)` contra a captura citada no prompt (`model_selection_capture:`), mais checagem do receipt de evidência (`runtime_evidence_birth:`) e das variáveis que sobrepõem a escolha (`CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, `CLAUDE_CODE_EFFORT_LEVEL`): qualquer uma definida = deny visível. `Agent` sem `model` ou sem `effort` = deny (sem herança): o host roda filho sem `effort` em `medium` (observado), então `effort` explícito por spawn é obrigatório.
  - Origem do esforço no hook: o adapter lê o esforço pedido **só** de `tool_input.effort` do `Agent`. Nunca usa o campo comum de sessão do input do hook (esforço do pai), `CLAUDE_EFFORT` nem o frontmatter. O ensaio do Apply grava o payload real de `PreToolUse` do `Agent` na versão qualificada como fixture; se nessa versão o campo `tool_input.effort` não existir, o hook nega com `unsupported_schema` visível para aquela versão e **não** aceita spawn validado só por `model`. A checagem de `effort` por turno na coleta (§4 passo 4, §5) continua.
  - Verificação antes da primeira escrita do filho: no primeiro `Edit`/`Write`/`MultiEdit`/`NotebookEdit` ou `Bash` classificado como escrita pelo Guard vindo de um subagente (`PreToolUse` com `agent_id`), o adapter lê o último registro `assistant` do transcript desse filho (`message.model`, `effort`) e compara com a captura do receipt daquele nascimento. Divergente, ausente ou ilegível = deny + receipt marcado `model_mismatch`; o filho não escreve e o pai precisa de nascimento novo. Igual = marca o receipt como verificado e as escritas seguintes do mesmo filho não releem (a coleta final ainda confere todos os turnos).
- `PostToolUse`, matcher `Edit|Write|MultiEdit|NotebookEdit|Bash`: roda o mesmo `.agents/skills/impeccable/scripts/hook.mjs` (cujo cabeçalho já declara suporte a eventos Claude Code) com `IMPECCABLE_HOOK_HARNESS=claude`, nas mesmas condições dos outros clientes; advisory. Matcher `Agent`: confere `resolvedModel` do resultado contra a captura (§4) e anota divergência no receipt.
- `SubagentStop`: só evidência — registra `agent_id`, `agent_type`, `agent_transcript_path` e presença de `last_assistant_message` no receipt do nascimento. Nunca devolve `decision: "block"` (na doc isso mantém o filho rodando, não destapa o pai).
- `Stop`: deep pass Impeccable advisory, como no Codex.

Destape: no Claude Code o filho em primeiro plano devolve o resultado no próprio turno do pai, e o filho em background gera notificação de conclusão ao pai (comportamento observado nesta sessão; garantia formal a provar). Por isso o adapter não usa sidecar `awaiting-task.json` nem poke; o runbook ganha uma linha dizendo isso. Interrupção/erro do filho continua não sendo sucesso.

Alternativas rejeitadas no primeiro Design: hooks em `~/.claude/settings.json` (não versionados, não reproduzíveis pelo pin). O rework inverte essa escolha só para o registro, por decisão de Alan (§13): a lógica continua versionada pelo pin. Continuam rejeitados hooks em frontmatter de agente (só valem no filho e têm regra de confiança mais estrita); `permissions.deny` como Guard (estático, não conhece Status).

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
- **Aceitação por formato** (rework, §17): a primeira implementação qualificava versão a versão (`QUALIFIED_VERSIONS`); agora o driver aceita qualquer versão cujos registros usados validem o schema `claude-transcript-v1`. O formato não é contrato público, então mudança real de schema vira `unsupported_schema` visível, citando o campo.
- **`prepare`** (antes de cada nascimento): valida sessão ativa, cwd = worktree, entrypoint/superfície, captura, e grava receipt privado (0400) com `task_name` = `description` única com needle, digest da captura e do diff quando houver.
- **`collect`** (após o retorno): acha no transcript do pai o `tool_use` `Agent` com aquela `description`, o `toolUseResult` (`agentId`, `resolvedModel`, `status`), o transcript do filho (`isSidechain`, `agentId`, `sessionId`), extrai modelo/esforço observados por turno, ferramentas usadas, término e payload retornado; sela com digests. `observed` nunca é copiado de `requested`; ausência = `unavailable` e reprova.
- **`claude_proxy.py`** registra a linha de proxy (`proxy modelo: <papel> → <rótulo> (<slug>)`, cliente `claude`, superfície, versão, status, payload) a partir do envelope; `model_proxy.evidence` ganha o cliente `claude`.
- Limpeza automática de transcripts (`cleanupPeriodDays`) pode apagar a fonte: coleta no mesmo turno do retorno; origem irrecuperável exige nascimento novo, nunca receipt retroativo.

### 6. `process_event --client claude` e preflight

`--client` aceita `claude`. Detecção nativa: `CLAUDECODE=1` → `claude`; coexistência com `CODEX_THREAD_ID` → precedência do processo mais interno (Codex aninhado no `Bash` do Claude Code continua `codex`, ver P3 aceitos), senão `reject ambiguous_client`; `--client`/`COVENANT_CLIENT` divergente do nativo → `reject ambiguous_client` (generalização do caso Codex). Para o mesmo conjunto de eventos que hoje exige preflight Codex, `claude` exige `claude_evidence.preflight`: transcript da sessão legível e com schema válido (§17), heartbeat do shim presente, digest do registro igual ao do heartbeat e digests de registro e adapter revisados (§15). Hooks ausentes, desligados (`disableAllHooks`) ou não confiados tornam-se assim visíveis na primeira transição dependente, sem nova transição nem permissão na FSM. Eventos humanos (T1, T7, T15, T18) continuam `reject actor`; T16 continua `fechar_release`. `implemente` em `Todo` não tem aresta: a página Moore e o Guard produzem a frase com Status atual e "Apply só depois de Pronto para Dev (T7 teu)".

### 7. Superfícies

| Superfície | Onde roda | Esperado |
| --- | --- | --- |
| Terminal (CLI) na VM | conta executora | caminho de referência; tudo disponível |
| IDE (VS Code/JetBrains) via Remote-SSH na VM | Claude Code embarcado na extensão, mesma conta | mesmos settings/hooks/skills (doc); versão própria da extensão checada pelo preflight; abaixo do mínimo = falha visível |
| Desktop, sessão SSH para a VM | Claude Code instalado pelo Desktop no host remoto | mesmos arquivos na VM (doc); fora deste card (ver #1103) |
| Desktop **Local** no Windows | máquina Windows | sem seleção local, sem `gh`/worktree da VM: resolver e Status falham visivelmente; nenhuma etapa avança |
| Web claude.ai/code dirigindo sessão local por Remote Control | sessão CLI da VM | equivalente ao terminal (doc); fora deste card (ver #1103) |

O Claude Code roda sempre local, pelo CLI na VM (decisão de Alan, 2026-10-14); sessão de nuvem está fora do escopo e não entra na matriz. Este card prova só o terminal (8.2, 15.2); as demais linhas não são reivindicadas como provadas aqui (decisão de Alan, 2026-10-15) e, em qualquer uma, capacidade ausente continua falha visível. A superfície observada (`CLAUDE_CODE_ENTRYPOINT` e equivalentes de remote, a provar) entra no heartbeat e no proxy.

### 8. Fecho de lote no Claude Code

Só por pedido explícito de Alan. Pré-requisito: o próprio pai é de execução do Claude Code — `release_model_selection.load_execucao_pair(root, "claude", capture)` e `check_runtime_model` comparam a captura `claude/execucao` (Sonnet 5.5, `high`) com o modelo/esforço observados do **pai** no transcript da sessão (último registro `assistant`: `message.model`, `effort`). Divergente/`unavailable` recusa T16 e pede sessão nova configurada (`/model` + `/effort`, ou flags equivalentes — a provar); não muda o pai vivo e não exige modelo de outro cliente. O filho `fecho-lote kaizen` nasce `general-purpose` com par capturado de `claude/execucao`, prompt autocontido do runbook, sem sidecar; o pai chama `process_event fechar_release` após `completed` e `release-guard post` PASS. Homologar continua só de Alan.

### 9. Revisão de confiança dos hooks

Pin e instalação não dão confiança. Em sessão interativa o Claude Code segura hooks até o diálogo de confiança do workspace; em `-p`/SDK roda hooks commitados sem diálogo (doc) — portanto o diálogo do host não é a revisão exigida. A revisão é um ato explícito do operador. Na primeira implementação: ler `.claude/settings.json` e `claude_adapter.py` (e módulos importados) e registrar `claude_adapter.py trust --record` em `$HOME/.config/covenant-flow/claude-hook-trust.json`. No rework ela vira revisão em duas partes (registro e adapter), comum a Claude Code, Cursor, Codex e OpenCode e conferida pelo shim antes de executar o adapter (§15). Digest não revisado = página com `hooks não revisados`, deny de Write de produto e de `Agent`, preflight recusado. Nunca usar bypass, nem tratar hook ausente/não confiado como proteção.

### 10. Troca de cliente entre etapas

Nada na FSM depende do cliente. Cada captura e cada proxy registram `client`; o handoff de cada etapa lista cliente e modelo observado por filho e repete os das etapas anteriores a partir dos comentários de handoff do card. Ex.: Design no Cursor (proxies `cursor`) e Apply no Claude Code (proxies `claude`) avançam pelos mesmos `iniciar_apply`/`pedir_review`/`aceitar_sha`/`integrar_develop`. Um filho nunca é transferido para outro cliente como fallback.

A prova viva por card real de troca (decisão (c) de Alan) foi cancelada por Alan em 2026-10-15 (§12): o contrato acima fica coberto pelos testes de captura/proxy por cliente, sem card de troca neste card.

### 11. Grelha em Em Refinamento

O pai spawna `grill-card` (juízo, Opus 5.5 alto) e só faz relaying. Perguntas fechadas vão por `AskUserQuestion` com **todas** as opções que o filho listou; se o host limitar o número de opções abaixo do que o filho trouxe, o pai divide em perguntas encadeadas ou lista as opções numeradas no texto da mesma pergunta — nunca colapsa para a recomendada. O limite exato e o comportamento em filho são a provar no Apply (detalhe de Apply, P3). O filho escreve o body do issue; `criar_card` continua fora de `process_event`.

### 12. Adapter não oficial; piloto e card de troca cancelados

**Não oficial (decisão (d) de Alan).** Neste card, `AGENTS.md`, a descrição do Project 1 e a linha "Cliente ativo" da skill/runbook não citam o Claude Code como cliente; `CLAUDE.md` e `.claude/` existem como pontes, sem afirmação de cliente. Um teste (tarefa 6.4) trava isso. Nada no diff do #1101 muda `AGENTS.md`, `scripts/process-fsm/overlay.py` (`render_agents`), o pin do `AGENTS.md`, `test_overlay.py`/`test_paging.py` na parte de clientes oficiais ou a descrição do board. Isso tudo é o card de seguimento, aberto depois do Done técnico do #1101, com T1 de Alan; o handoff de Done do #1101 o cita.

**Cancelado (decisão de Alan, 2026-10-15: "quanto aos ensaios em outra harness fora daqui nao vamos fazer agora"; "o 15.3 e o card piloto vamos cancelar siga sem eles").** Saem deste card, sem substituto:

- o piloto empilhado (card real percorrendo o fluxo no Claude Code sobre o HEAD revisado do #1101) e o card real de troca de cliente (decisões (a) e (c) do Design de 2026-10-13), com a ordem empilhada, o review por diff empilhado e o rebase com prova por `patch-id`;
- o gate `pilot_evidence` deste change: a declaração `pilot-evidence-gate.json` sai do change, e por isso `review_process_checklist.py --phase postqa` não avalia o item (ele só roda quando o change declara o gate; o código da task 6.5 fica, inativo, disponível para outro change que o declare);
- a exceção local ao "T14 no mesmo turno do verde": o T14 do #1101 segue a regra geral — depois do QA verde e do checklist `postqa` (sem `pilot_evidence`), o pai chama `integrar_develop` no mesmo turno;
- a matriz de superfícies (IDE Remote-SSH, Desktop SSH, Remote Control) e o ensaio deny pelo registro da conta em Cursor, Codex e OpenCode (15.3): prova de outras harnesses e superfícies fica fora deste card (o app desktop é o #1103).

Não muda: FSM, guard de T14 em `process_event`, gates humanos, seleção de modelos, caráter não oficial e o card de seguimento de oficialização (que deixa de depender do piloto). O que o ensaio real já provou no terminal da VM fica como prova deste card (8.2, 8.3, 15.2). Textos fora deste change que ainda citam o piloto (linha de superfícies da skill `covenant-flow`, `docs/claude-runtime-evidence.md` e a janela de `docs/model-selection.md`, todos vindos do pin `v1.1.20`) são alinhados no card de seguimento de oficialização, que já muda a skill e o pin.

### 13. Registro dos hooks na conta, para Claude Code, Cursor, Codex e OpenCode (rework; decisões de Alan)

Três camadas, cada uma com um dono:

1. **Registro** (conta, um por host): o mesmo conjunto de eventos, matchers, `timeout` e flags de bloqueio (`onFailure: "block"`, `failClosed`) que o registro de projeto tem hoje, mas cada comando chama o shim com o cliente e o evento (por exemplo `python3 "$HOME/.config/covenant-flow/shim/current/cf_shim.py" claude pre-tool-use`). No OpenCode, que carrega plugin JS em processo, o registro é um plugin global fino que encaminha ao mesmo contrato do shim (P3: subprocesso ou import do plugin pinado).
2. **Shim** (conta, distribuído pelo `covenant-flow`): descobre o consumidor, confere compatibilidade e digest, executa o adapter pinado e traduz as próprias falhas para o formato de deny de cada host. Não tem FSM, Guard, paginação nem seleção de modelos.
3. **Adapter** (consumidor, versionado pelo pin): o que existe hoje — `claude_adapter.py`, `codex_adapter.py`, `.cursor/hooks/*.sh`, plugins do OpenCode, `hook.mjs` do Impeccable — sem mudança de lei.

Grok Build e dsh ficam fora das três camadas: o pin continua gravando o registro de projeto deles como hoje e o shim não é registrado nesses hosts. No manifesto, `registration` é por cliente: `account` para os quatro do escopo com mecanismo provado, `project` para Grok Build e dsh.

Descoberta, a cada evento: cwd do payload do hook (`cwd` no Claude Code e no Codex; `workspace_roots` no Cursor; diretório do contexto no OpenCode), senão a raiz do workspace, senão o cwd do processo → `git rev-parse --show-toplevel` → `.covenant-flow/overlay.yaml`. Decisão por caso:

| Situação | Comportamento |
| --- | --- |
| sem overlay, ou overlay sem `pin` | nada: sem página, sem deny, sem executar código do repo |
| pin anterior ao registro na conta (sem manifesto de adapters) | nada para aquele host: o registro de projeto do pin antigo é o único que roda (sem execução dupla) |
| manifesto com `registration: account` e tudo confere | executa o adapter do cliente com o payload original e devolve a resposta dele |
| arquivo do manifesto ausente | `adapter_missing` visível |
| arquivo diferente do manifesto | `adapter_divergent` visível |
| digest do adapter não revisado | `hooks_unreviewed` visível, sem executar o adapter |
| `shim_protocol` do manifesto não suportado | `shim_incompatible` visível, com o comando de atualização da conta |
| raízes de workspace em consumidores diferentes | `consumer_ambiguous` visível |

"Visível" segue o fail-closed de hoje: nos eventos que gateiam (pre-tool de escrita, shell e spawn) deny no formato nativo do host com motivo e recuperação; no início de sessão, o motivo vai na página; leitura não é bloqueada. Exceção ou timeout do adapter continua deny, como hoje.

Por que manifesto: o shim precisa distinguir "pin antigo, registro no projeto" de "pin novo, adapter sumiu", que Alan quer como falha visível. O pin grava `.covenant-flow/adapters.json` (nome P3) com `registration`, `shim_protocol` e, por cliente, o ponto de entrada e a lista de arquivos do adapter.

Claude Code: registro em `~/.claude/settings.json`, e não plugin. O plugin exige marketplace e habilitação por escopo; as user settings se fundem com o mesmo merger de `claude_hooks.py`/`codex_hooks.py`. A decisão de Alan permite marketplace só para o registro, então o plugin fica como alternativa se o ensaio mostrar limite das user settings. Em todos os hosts os registros de usuário e de projeto se somam; por isso o pin novo tira o registro do projeto e o shim não age em pins antigos (§16).

Alternativas rejeitadas: manter o registro no projeto e exigir sessão por pasta (contraria o uso pedido por Alan); symlink de `.claude/` para a conta em cada repo (continua por pasta); copiar a lógica para a conta (segunda lei, fora da decisão).

### 14. O processo segue a sessão para o worktree do card

- **Heartbeat do shim.** No `SessionStart` de qualquer pasta, o shim grava na conta (`~/.config/covenant-flow/sessions/<cliente>/<sessão>.json`, 0600) a identidade da sessão, o localizador do transcript/rollout, a versão do host, a superfície, o digest do registro (§15) e o cwd de lançamento. Numa pasta sem pin esse registro privado é o único efeito: não há página, deny nem saída para a sessão. Ele é a âncora do "registro que o host carregou", e por isso não pode nascer depois. O heartbeat do Claude, que hoje `claude_trust.py` grava só quando o adapter roda, passa a ser este; `hooks_inactive` = sessão sem heartbeat do shim.
- **Troca de worktree.** O shim guarda por sessão a última raiz de consumidor. No primeiro evento com raiz diferente, (a) o adapter da nova raiz é usado já nesse evento (Guard e spawn), e (b) a página Moore do card recém-vinculado é injetada. No Claude Code, (b) usa `additionalContext` de `PostToolUse` com matcher `EnterWorktree` e, se o host oferecer evento de mudança de cwd, esse evento (a provar). Nos outros hosts, (b) usa o mecanismo de contexto que cada um tiver; onde não houver, a página aparece no próximo início de sessão, e os gates já valem desde o primeiro evento. A troca continua seguindo só `transcript_path` e `cwd` (`9dc6f043`) e preserva o digest do registro.
- **`$CLAUDE_PROJECT_DIR`** deixa de importar: o shim resolve o consumidor pelo cwd do payload, não pela pasta de lançamento. Isso fecha a dúvida aberta da onda `1101-fixwt-w2`.
- Uma sessão `#<id>` aberta em `/source` continua entrando no worktree `card-<id>-*` por `EnterWorktree`, como manda o runbook; a diferença é que o processo fica ativo sem relançar a sessão.

### 15. Revisão de confiança em duas partes (achado 6 e residual P2)

Registro de confiança único na conta, comum aos clientes (`~/.config/covenant-flow/hook-trust.json`, versão 2), com entradas `{digest, part, client, files, recorded_at}`:

- **Parte registro (R):** bloco de hooks da conta daquele host (JSON canônico) mais os arquivos do shim. O heartbeat guarda o R do início da sessão. R atual ≠ R do heartbeat → `hooks_changed` (o host ainda roda o registro antigo; exige sessão nova). R não revisado → `hooks_unreviewed`.
- **Parte adapter (A):** todos os arquivos que o adapter do cliente pode executar, pela lista do manifesto: `scripts/process-fsm/` (sem testes), o diretório de handlers do cliente e a árvore inteira `.agents/skills/impeccable/scripts/**`. A árvore inteira fecha o P2 do `hook-lib.mjs` (cerca de 20 módulos de `detector/` e `lib/impeccable-config.mjs` por `import()` dinâmico), sem tentar seguir imports dinâmicos. A é conferido **pelo shim antes de executar**, não pelo próprio adapter; hoje o adapter confere o próprio digest, o que não protege contra um adapter alterado. A revisado vale no próximo evento sem reabrir a sessão; trocar entre worktrees com A diferentes e ambos revisados funciona.
- `claude_adapter.py trust --record|--status` passa a delegar ao shim (`cf_shim.py trust`), que mostra R e A da pasta atual e grava os dois. As revisões v1 (`claude-hook-trust.json`) não são migradas: os digests mudam de qualquer forma, e o operador registra de novo.
- Cursor e OpenCode passam a ter revisão por digest, porque o shim executa código do repo a partir de um hook da conta. Sem isso, qualquer repo clonado com overlay e pin teria código executado em toda chamada de ferramenta. Esse é o custo da decisão de Alan ("a revisão de confiança continua por digest") e aparece na migração (§16, passo 3). Grok Build e dsh não ganham revisão nova: não passam pelo shim.
- O limite aceito continua: o agente pode tentar gravar a revisão; nesta conta o classificador de permissão do host negou a tentativa (achado 7). O endurecimento fica no card de seguimento.

### 16. Pin, `implantar` e migração do registro

- **`install.sh --pin` (tag nova):** continua "copiar e commitar" para núcleo, adapters, pontes, helpers e política. Deixa de gravar registro de hooks de Claude Code, Cursor, Codex e OpenCode no consumidor; remove dos registros de projeto desses quatro só as entradas do Covenant Flow, preservando as alheias (mesmo merger, recusa visível em JSON inválido ou conflito, sem escrita parcial); grava o manifesto de adapters. No OpenCode, os plugins do adapter saem do diretório que o host auto-carrega para um caminho que o plugin global importa (P3). Os registros de Grok Build (`.grok/hooks/process-fsm.json`) e dsh (`.dsh/cordis.patch.yml`, `dsh_boot.sh`) continuam gravados pelo pin como hoje.
- **`install.sh --account` (novo, na conta, nada vai para git):** instala o shim versionado em `~/.config/covenant-flow/shim/<versão>/` com `current`; funde uma entrada por host do escopo instalado na máquina (Claude Code, Cursor, Codex, OpenCode; todos presentes nesta VM); `--check` mostra, por host do escopo, `registration=account|unproven|not_installed` (e `project` para pin antigo), shim ou registro faltando, a versão do shim e R/A revisados; `--remove` tira só as entradas do Covenant Flow. Idempotente, preserva o que é alheio, não lê nem grava a seleção de modelos e não grava confiança.
- **Compatibilidade:** pins antigos continuam funcionando com o registro de projeto (o shim não age neles). O pin novo exige o shim instalado. Sem ele, a sessão fica sem hooks, e hoje só Claude Code e Codex têm preflight em `process_event`. Por isso o rework estende a recusa aos quatro clientes do escopo (spec `account-hook-shim`, "Account registration without the shim is refused visibly in every account-registered client"): num consumidor com o pin novo, para cada um desses clientes, as transições que hoje exigem o preflight Codex recusam com `hooks_inactive` quando falta o heartbeat do shim daquela sessão, quando falta o shim ou o registro na conta daquele cliente, ou quando o cliente está `registration=unproven`. A recusa cita o cliente e a recuperação (`install.sh --account` e sessão nova), e o `--check` mostra o host sem registro. É precondição de eventos que já existem, como o preflight Codex: não cria aresta e não muda Guard, paginação nem seleção. Está dentro do "Não entra", porque é a visibilidade do próprio registro na conta. Onde checar e como casar a sessão com o heartbeat em cada cliente é P3; um cliente que não exponha a sessão a `process_event` exige, no mínimo, shim e registro do cliente instalados e revisados.
- **Cliente do escopo sem mecanismo global provado no ensaio** (decisão de Alan, 2026-10-14): fica só com a falha visível. O `--check` mostra `registration=unproven`, o manifesto não o declara `registration: account`, a lacuna vai para o card e nenhuma página, checagem ou handoff o apresenta como protegido. Ele fica sem registro do processo: não se mantém registro de projeto para ele nem se inventa outro mecanismo, e o `process_event` dependente dele recusa visivelmente com `hooks_inactive` citando `registration=unproven`. Grok Build e dsh não são casos de `unproven`: estão fora do escopo e mantêm o registro de projeto.
- Neste repo: `.claude/settings.json` perde o bloco `hooks` e deixa de existir, pois não tem outras chaves. `CLAUDE.md`, `.claude/skills/` e `.claude/agents/` ficam: são descoberta, não registro.

### 17. Versão do host aceita pelo formato (rework; decisão de Alan)

- **Claude Code.** `QUALIFIED_VERSIONS` sai. O driver `claude-transcript-v1` declara, por tipo de registro usado, os campos obrigatórios e os tipos: `assistant` (`type`, `sessionId`, `version`, `entrypoint`, `cwd`, `message.id`, `message.model`, `effort`); `tool_use` do `Agent` no pai (`input.description`, `input.model`, `input.effort`, `input.subagent_type`); `toolUseResult` (`agentId`, `status`, `resolvedModel`); `.meta.json` do filho (`toolUseId`, `description`, `agentType`, `model`); registros do filho (`isSidechain`, `agentId`, `sessionId`); payload de `PreToolUse(Agent)` (`tool_input.effort`, como já é). Campos extras e tipos de registro não usados são ignorados. A validação roda onde o coletor lê: `prepare` valida o último `assistant` do pai, como sonda, antes do nascimento; `collect` valida todos os registros usados. Falta ou tipo diferente → `unsupported_schema` com tipo, campo e versão observada.
- A versão observada vai para heartbeat, receipt, evidência e proxy, e nunca recusa sozinha. Um transcript com mais de uma versão (sessão retomada depois de atualização) é aceito se cada registro valida; a evidência guarda o conjunto. A identidade filho×pai usa os valores do pai no receipt (§18).
- **Pisos de capacidade ficam:** `host_min_version` 2.1.292 (`effort` por invocação) e 2.1.295 (`onFailure: "block"`) recusam só hosts mais antigos, com `capability_unavailable`. `QUALIFIED_ENTRYPOINTS` também fica: é superfície, não versão, e segue a tabela de §7 (só `cli` provado neste card).
- **Codex.** O driver passa a `codex_exec/rollout-v1`. A checagem de `originator == codex_exec` fica (tipo de host); `cli_version` é registrada. O schema valida `session_meta`, `turn_context`, chamada/retorno nativos, `task_started`, `task_complete` e `agent_message`. A qualificação privada (`qualification.json`) vale por schema do driver, não por versão: a prova existente continua válida (aceitar o id antigo do driver como o mesmo schema é P3).
- **Risco aceito:** formato igual com semântica nova. A mitigação são as checagens cruzadas que já existem: `resolvedModel` contra a captura, modelo e esforço por turno, filiação e payload. Divergência reprova em qualquer versão.
- Alternativas rejeitadas: travar a versão do binário (impede atualização de segurança e não atende "nas próximas"); janela de qualificação por versão (ainda trava até o ensaio); aceitar qualquer versão sem schema (troca "trava" por "aceita errado").

### 18. Achados do piloto: o que entra e o que fica fora

Entram, porque tocam registro, sessão ou evidência:

- **6 (digest em duas partes)** → §15.
- **13 e 15 (sessão de `/source` sem hooks; registro preso ao projeto)** → §13, §14.
- **10 (turno `<synthetic>`)**: o último `assistant` com `message.model == "<synthetic>"` (erro da API gravado pelo host) classifica o filho como `failed`, e o proxy registra a tentativa sem sucesso; não é `model_mismatch`. Um `<synthetic>` intermediário seguido de turnos reais é excluído da comparação de modelo e contado na evidência.
- **11 (filho coletado após troca de worktree)**: a coleta compara cwd e versão do filho com os do pai **gravados no receipt** do nascimento, não com o cwd atual da sessão.
- **1 (grelha com o card errado)**: com sessões nascendo em `/source`, a grelha roda sem vínculo de git. O receipt grava o card do `--task-name` (`grill-card <id> …`) quando o git não vincula card. Quando o git vincula outro card, `prepare` recusa com `card_mismatch`. Vale para todo papel: o id do `--task-name` precisa bater com o `bound_card` quando houver.
- **P2 do `hook-lib.mjs` fora do digest** → §15, árvore inteira.
- **P3 do texto do requisito de confiança** (só "hook definition and adapter") → corrigido no spec delta deste rework.
- **9 e 14 (isolamento do host após `EnterWorktree`)**: só uma nota de uso no runbook (corpo por `--body-file` com path literal; comandos compostos com variável de shell podem ser recusados pelo host).

Ficam fora, com seguimento:

- **2 (Guard trata `>` entre aspas como redirecionamento)**: é o Guard compartilhado de todos os clientes, fora dos dois blocos do rework. Vai para card de seguimento.
- **12 (protótipo 404 em card novo)**: é o serviço de protótipos do DEV (lista de worktrees montada no início), um problema de ambiente do consumidor, não do processo. Vai para card de seguimento, como o body já decide. Um passo de restart no runbook fica só como sugestão para esse card.
- **7 (autoaprovação do `trust --record`)**: o limite já foi aceito por Alan; o endurecimento fica no card de seguimento.
- **P2 de 3.7 (verificação antes da primeira escrita provada só com sintéticos)** e **P3 de 6.2 (`check_claude_parent` sem ponto de entrada)**: são residuais de review que este desenho não muda; diziam "continuam no piloto" (9.2/9.3/9.6) e, com o piloto cancelado (§12), passam a residual registrado no #1103.
- **P3 do `recorded_at` do heartbeat**: resolvido de passagem, porque o heartbeat do shim separa `recorded_at` (início da sessão) dos campos de troca.

## Risks / Trade-offs

- [Transcript JSONL é formato interno, pode mudar sem aviso] → schema declarado por driver e validado onde se lê (§17); formato mudado = `unsupported_schema` citando o campo, e o gate recusa; nunca inferir. Versão nova com formato igual segue.
- [`tool_input.effort` do `Agent` ausente ou com outro nome numa versão] → payload real gravado no ensaio por versão; campo ausente = deny `unsupported_schema` naquela versão; nunca validar só `model` nem ler o esforço da sessão.
- [Filho sem `effort` explícito roda em `medium` (observado)] → deny de spawn sem `effort`; verificação antes da primeira escrita e por turno na coleta.
- [Alias de família resolve para versão diferente do id selecionado, ou a organização substitui o modelo] → verificação de `resolvedModel` logo após o spawn, do transcript do filho antes da primeira escrita e de `message.model` na coleta; divergência invalida o filho.
- [Hook que expira/erra não bloqueia por padrão] → `onFailure: "block"`, `timeout` explícito, adapter sempre emite JSON de deny em exceção.
- [`-p`/SDK pode rodar hooks sem diálogo (a provar); `.claude/settings.local.json` ou user settings podem `disableAllHooks`] → registro de confiança próprio + heartbeat + preflight em `process_event`; limite cooperativo documentado (como Codex: sem Auto).
- [Modo de permissão `auto`/`bypassPermissions` do Claude Code e Auto padrão na extensão VS Code] → o adapter não depende do modo de permissão; deny de hook vale em qualquer modo (comportamento em `bypassPermissions` a provar no Apply; se não valer, a superfície/modo é recusado pelo preflight).
- [Filho pode criar netos] → deny de `Agent` com `agent_id` no `PreToolUse`.
- [Rotas que não disparam `PreToolUse` (ferramentas MCP, LSP, Monitor etc.)] → ensaio lista rotas cobertas e não cobertas; não se afirma interceptação completa.
- [Shim na conta executa código de qualquer repo com overlay e pin] → só executa adapter cujo digest A o operador revisou; repo sem pin não executa nada (§13, §15).
- [Registro de usuário e de projeto se somam e o hook roda duas vezes] → o pin novo tira o registro do projeto; em pin antigo o shim não age (§16); teste de "uma execução por evento".
- [Host do escopo sem mecanismo global, ou mecanismo diferente do previsto] → ensaio por host antes de o pin tirar o registro daquele host; sem prova, o host aparece como `registration=unproven` e fica só com a falha visível (§16).
- [Mesmo formato com semântica nova numa versão futura] → checagens cruzadas de `resolvedModel`, modelo e esforço por turno, filiação e payload; divergência reprova (§17).
- [Hash das árvores do adapter em toda chamada pesa] → cache por (path, tamanho, mtime, inode) na conta (P3); a árvore inteira é o preço de cobrir imports dinâmicos.
- [Revisão por digest nova para Cursor e OpenCode trava sessões até o operador registrar] → passo explícito na migração, `--check` mostra o que falta; pins antigos não são afetados.
- [Página não reinjetada no meio da sessão em host sem mecanismo de contexto] → os gates seguem o novo worktree desde o primeiro evento; a página aparece no próximo início de sessão; lacuna registrada por host.
- [Worktree sem `.claude/skills` cai no checkout principal] → até o T14 do #1101, `develop` ainda não tem as pontes; só o worktree do #1101 tem `.claude/` versionado; preflight compara manifesto do worktree.
- [Limpeza de transcripts] → coleta no mesmo turno; nascimento novo se a fonte sumir.
- [Pin novo numa conta sem o shim (máquina nova, `--remove`, outro operador)] → recusa `hooks_inactive` em cada cliente do escopo nas transições dependentes e `--check` com o host sem registro (§16).
- [Bloco `claude` na seleção compartilhada quebra o resolver antigo de `develop` e dos outros worktrees até o T14 do #1101] → aceito por Alan (decisão (b)): demais cards pausados nesta conta, falha visível do resolver antigo até o T14; sem piloto, o intervalo é só QA verde → T14 no mesmo turno; T14 que não acontecer = restaurar o backup.
- [`CLAUDECODE=1` herdado por processo aninhado (ex.: Codex rodando no `Bash` do Claude Code)] → precedência do sinal nativo mais interno (P3 abaixo), com teste que mantém o Codex como hoje.

## P3 aceitos

Detalhes de Apply aceitos na crítica, sem reabrir o Design:

- `AGENTS.md` só muda via renderer `render_agents` + pin, nunca à mão — e isso fica no card de seguimento; neste card o arquivo não muda.
- `.claude/agents/*.md` curtos, no padrão de `.codex/agents/*.toml`, ou ponte para `.cursor/agents/<nome>.md`; sem cópia do corpo canônico.
- `/opsx:*` no Claude Code via pontes `.claude/skills/openspec-*`; sem `.claude/commands`.
- Precedência de cliente: `CLAUDECODE=1` herdado por processo aninhado (Codex dentro do `Bash` do Claude Code) não pode transformar o Codex em `claude`; o sinal nativo do processo mais interno (`CODEX_THREAD_ID`) prevalece quando a herança é demonstrável, senão `ambiguous_client`. Teste mantém o comportamento atual do Codex.
- Specs base `cursor-harness` ("All five clients"), `covenant-flow` ("five client adapters") e `process-harness` ("five adapters"): aceito manter a redação neste card, porque os cinco continuam sendo os clientes **oficiais**; o requisito novo de `claude-code-harness` cobre o adapter não oficial e o instalador. A atualização da contagem fica para o card de seguimento.
- A afirmação "hooks rodam sem diálogo em `-p`/SDK" está marcada como **a provar** (tabela de capacidades); o desenho não depende dela.
- (Rework) Nome e formato do manifesto de adapters (`.covenant-flow/adapters.json`), do diretório do shim e do heartbeat; linguagem do shim (Python, com plugin JS fino para o OpenCode) e se esse plugin encaminha por subprocesso ou importa o plugin pinado.
- (Rework) Caminho não auto-carregado para os plugins do adapter OpenCode.
- (Rework) Lista exata de arquivos de A por cliente; cache do hash; aceitar o id antigo do driver Codex na qualificação existente como o mesmo schema.
- (Rework) Texto de requisitos base que ainda citam registro de projeto (`codex-harness` "project `PreToolUse` hook", `cursor-harness` Impeccable e `subagentStop`, `covenant-flow` "Five adapters ship"): vale o requisito `account-hook-shim` ("the same entries apply to the account registration"); a reescrita literal fica para o Apply ou para o arquivamento.
- (Rework) O requisito "Unsupported host qualification" de #1095 (change ainda não arquivado) passa a ler-se como qualificação por schema do driver (§17); reconciliar o texto no arquivamento do lote.
- (Rework) Formato exato do deny de cada host para as falhas do próprio shim e campo de cwd por host.
- (Rework, crítica de 2026-10-14) Sessão de pins mistos: o Claude Code carrega o registro de projeto da pasta de **lançamento**. Testes nos dois sentidos ("lançada em pin antigo, entra em pin novo" e o inverso); o heartbeat registra o registro carregado no lançamento e a página avisa quando ele difere do pin do cwd.
- (Rework, crítica de 2026-10-14) `QUALIFIED_ENTRYPOINTS`: valor de `entrypoint` desconhecido recusa citando o valor observado como mudança de formato ou superfície, nunca como versão.
- (Rework, crítica de 2026-10-14) Pisos 2.1.292/2.1.295: de preferência detectados pela presença da capacidade (`tool_input.effort`, `onFailure`), com o número só como referência.
- (Rework, crítica de 2026-10-14) Frase de §15 sobre o achado 7 reescrita como "classificador de permissão do host", sem citar modo Auto.
- (Rework, crítica de 2026-10-14) Heartbeat privado gravado pelo shim em pasta sem pin: aceito, porque não tem efeito na sessão e é a âncora de `/source` → worktree (§14).
- Também: generalizar `codex_skills.py`/`codex_hooks.py` ou módulos `claude_*`; nome/local do heartbeat, do registro de confiança e da declaração do gate de piloto; normalização de `NotebookEdit`/`MultiEdit` no Guard; forma de dividir perguntas do `AskUserQuestion`; nome do doc `docs/claude-runtime-evidence.md`.

## Migration Plan

1. Apply no worktree do card (consumidor) e no worktree do nucleus `covenant-flow` (shim, `install.sh --account`, manifesto, pin novo), como no #1080/#1042. Ensaio por host do mecanismo global (task 11.1) antes de tirar o registro de projeto de cada host.
2. Operador: `install.sh --account` (o shim não age em pins antigos: develop e os outros worktrees seguem como hoje) e revisão de confiança R e A por `cf_shim.py trust --record`, lendo o que vai ser executado. A partir daqui, o worktree do #1101 (pin novo, sem registro de projeto) roda pelo shim, e uma sessão lançada em `/source` que entra nele fica com o processo ativo. (Feito: 8.3, 15.2.)
3. Bloco `claude` na seleção da conta (decisão (b) de Alan), com backup da seleção e os demais cards desta conta pausados; até o T14 do #1101, o resolver antigo de `develop` e dos outros worktrees recusa o arquivo de forma visível — aceito.
4. Review, commit, PR e QA verde do #1101 com o Claude Code não oficial; checklist `postqa` (sem `pilot_evidence`, §12) → T14 do #1101 no mesmo turno do verde (regra geral). O develop recebe o pin novo: os registros de projeto de Claude Code, Cursor, Codex e OpenCode saem (Grok Build e dsh mantêm os seus) e o shim passa a agir em `/source`.
5. Depois do T14: os cards pausados rebaseiam em `develop` antes de retomar (para ganhar o validador novo e o pin novo). Handoff de Done cita o card de seguimento de oficialização.

O passo 5 roda depois do Done técnico do #1101 e fica fora de `tasks.md`, porque o checklist postqa exige todas as tasks marcadas antes do T14; a task 10.2 o registra no card antes do T14. Piloto empilhado e card de troca (antigos passos 4–7) foram cancelados por Alan em 2026-10-15 (§12).

Se o #1101 não chegar ao T14 (QA vermelho sem conserto, rollback): restaurar o backup da seleção da conta, para que `develop` e os outros worktrees voltem a resolver; os cards pausados retomam; a causa é registrada no card. O shim pode ficar instalado: em pins antigos ele não age.

O Apply ensaia a migração com cópia temporária do arquivo de seleção (validador novo aceita o bloco; validador antigo recusa visivelmente), sem tocar o arquivo real.

Rollback: remover `CLAUDE.md`, `.claude/`, `scripts/process-fsm/claude_*.py`, o item `pilot_evidence` (inativo neste change) e o contrato `claude` da política, e o operador remover explicitamente o bloco `claude` da seleção local (com backup), porque o validador revertido o recusaria. Rollback do registro: `install.sh --account --remove` e voltar ao pin anterior, que traz os registros de projeto de volta; o shim removido não deixa entradas alheias alteradas. Os demais clientes voltam ao estado anterior sem outra mudança.

## Open Questions

Nenhuma. As decisões de Alan de 2026-10-15 (piloto, card de troca, `pilot_evidence` e 15.3 cancelados; outras harnesses e superfícies fora deste card, §12), as de 2026-10-13 (a)–(d) — (a) e (c) cancelados em 2026-10-15 — e as de 2026-10-14, incluindo as respostas às três Open Questions do rework (comentário `6169060530`: Grok Build e dsh fora; nuvem fora; a pergunta sobre hosts não instalados caiu), estão no body ou no card e não reabrem.

## Design Critique

Rodada de 2026-10-14 (crítica do rework, sem tela, teto 1+1+1). Snapshot: `.impeccable/critique/1101-card-1101-claude-code-adapter-design-critic-rework.md`.

- P1-1 (contrato): a nuvem perdeu o Guard e o cenário ainda prometia negação. Disposition: resolvido no rework. O cenário e o requisito de superfícies (`claude-code-harness`) agora descrevem a nuvem como cooperativa sem Guard, com falha visível no resolver e no `process_event`, e a tabela de §7 diz o mesmo. A escolha entre aceitar a nuvem assim ou usar outro mecanismo foi para a Open Question 2 de Alan; o registro de projeto não foi reintroduzido.
- P1-2 (contrato): sem shim, só Claude e Codex recusavam. Disposition: resolvido no rework. Requisito novo "Account registration without the shim is refused visibly in every client" (`account-hook-shim`) com cenários, §16 e task 11.8. Onde checar fica P3.
- P1-3 (contrato/escopo): o spec fixava o default da OQ1. Disposition: resolvido no rework. `account-hook-shim`, `cursor-harness` e `process-harness` exigem só `registration=unproven` visível e remetem o tratamento à Open Question 1, que diz explicitamente que manter o registro de projeto conflita com o critério "não há nenhum".
- P2-1 (escopo): a OQ3 reabria o protótipo 404. Disposition: resolvido no rework. A OQ3 foi removida e o achado 12 ficou só como seguimento (§18).
- P3-1 a P3-5 (pins mistos, `QUALIFIED_ENTRYPOINTS`, pisos por capacidade, frase de §15, heartbeat em pasta sem pin): disposition: P3 aceitos, registrados em "P3 aceitos" para o Apply. A frase de §15 já foi reescrita.
- Verdict: REWORK → resolvido no único rework (sem tela, 1 autor + 1 crítico + 1 rework). Open Questions 1–3 ficam para Alan antes do T7.
- Decisões de Alan pós-T6 (2026-10-14): OQ1 → Grok/dsh fora; OQ2 → nuvem fora; OQ3 → caiu. Aplicadas no body, em `proposal.md`, neste design (§7, §13, §15, §16, Non-Goals) e nos specs `account-hook-shim`, `claude-code-harness`, `cursor-harness`, `process-harness` e `covenant-flow`; o cliente do escopo sem mecanismo global provado fica só com a falha visível (`registration=unproven`).
