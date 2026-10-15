# Ensaio por host do registro na conta (task 11.1)

Ensaio de 2026-10-14 na VM, sem produto nem transição. Todo ensaio de execução rodou com `HOME` (e `CODEX_HOME`) temporário em `scratchpad/apply-home-<host>`; nenhum arquivo de configuração real (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.config/opencode`, `~/.config/covenant-flow`) foi escrito. Leitura da configuração real foi só para conferir estado. Versões: Claude Code 2.1.299, Cursor Agent 2026.10.01-e373342, Codex CLI 0.162.1, OpenCode 1.18.32. Grok Build e dsh não foram ensaiados e ficam como estão.

## Tabela por host

| Host | Registro | Mecanismo de conta | Eventos / matchers | Campo de cwd | Conta + projeto se somam | Regra de confiança do host | Nível de prova |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Code | `account` | bloco `hooks` de `~/.claude/settings.json` (escopo usuário) | `SessionStart` (`startup\|resume\|clear\|compact`), `PreToolUse` (`Bash\|Edit\|Write\|MultiEdit\|NotebookEdit\|Agent`, `onFailure: "block"`), `PostToolUse`, `SubagentStop`, `Stop`; `CwdChanged` existe (sem matcher; entrada `old_cwd`/`new_cwd`; saída só `watchPaths`, sem `additionalContext`) | `cwd` no topo do payload; vira a raiz do worktree depois de `EnterWorktree` (doc) | sim: hook de usuário e de projeto dispararam no mesmo evento (`ProjectSessionStart` e `SessionStart` no log); handler idêntico em dois arquivos roda uma vez (doc) | hooks de settings de usuário não passam pelo diálogo de confiança da pasta; `claude -p` roda hooks sem diálogo (doc "What runs before you trust a folder", confirmado) | executado: `claude -p` em `HOME` temporário (login ausente; os hooks rodam antes da chamada de modelo) |
| Cursor | `account` | `~/.cursor/hooks.json` (hooks de usuário) | `sessionStart`, `preToolUse` (`Write\|StrReplace\|Delete\|EditNotebook`, `Task\|Agent`, `failClosed`), `beforeShellExecution`, `afterFileEdit`, `stop`, `subagentStop` | `workspace_roots` (comum); `cwd` só em eventos de ferramenta/shell | sim: "todos os hooks de todas as fontes rodam" (doc); o carregador do CLI instalado lê enterprise, team, user, project em sequência e funde | hooks de projeto exigem workspace confiável; hooks de usuário não têm essa regra; hook de usuário roda com cwd `~/.cursor/` | doc oficial + carregador do CLI instalado (`userConfigPath = ~/.cursor/hooks.json`). Execução real não ensaiada: o `cursor-agent` exige login antes de iniciar o agente (HOME temporário e chave fictícia recusados). A negação real seria a task 15.3, cancelada por Alan em 2026-10-15 (fora deste card) |
| Codex CLI | `account` | `~/.codex/hooks.json` (também `[hooks]` em `~/.codex/config.toml`) | `SessionStart`, `PreToolUse` (`Bash\|exec_command\|apply_patch\|Edit\|Write\|Agent`), `PostToolUse`, `Stop`; `PreToolUse` nega por `hookSpecificOutput.permissionDecision` | `cwd` no topo do payload (com `session_id`, `transcript_path`, `model`) | sim: "todas as fontes são carregadas"; `hooks/list` do app-server mostra `source: user` | hook não gerenciado só roda depois da revisão do host (`/hooks`, grava `trusted_hash` em `config.toml [hooks.state]`): sem ela `trustStatus: untrusted` e o hook não dispara; o ensaio gravou o hash só no `CODEX_HOME` temporário e o `SessionStart` de usuário rodou com `cwd`. A camada de projeto só carrega se o projeto for confiável | executado: `hooks/list` e `codex exec` em `CODEX_HOME` temporário |
| OpenCode | `account` | plugin global em `~/.config/opencode/plugin/*.js` | `tool.execute.before` (`input.tool`, `output.args`), `experimental.chat.system.transform`, `event` (`session.created`, `session.idle`...) | só no `init` do plugin (`directory`, `worktree`); as chamadas não trazem cwd | sim: o plugin global e o de projeto (`.opencode/plugin/`) carregaram na mesma execução | sem diálogo: plugin de usuário é código da própria conta | executado: `opencode run` real em `HOME` temporário (modelo gratuito) |

## Reinjeção da página por host (nota do #1103, R17)

A página do processo (`paging.page`) chega à sessão por um canal próprio de cada host; o shim a produz a partir do adapter pinado do cwd do evento e nunca a guarda.

| Host | Canal da página | Quando reaparece | Troca de worktree na mesma sessão |
| --- | --- | --- | --- |
| Claude Code | `SessionStart` (`startup\|resume\|clear\|compact`) com `hookSpecificOutput.additionalContext` | a cada início, `clear`, retomada e compactação (o `compact` reinjeta a página sem regravar o digest R do heartbeat, R8) | `PostToolUse` com matcher `EnterWorktree` reinjeta a página do card novo (`SessionStart` não dispara); sessão em `/source` recebe a página de `develop` (`bound_card=⊥`) com a instrução de `EnterWorktree` |
| Cursor | `sessionStart` com `additional_context` | no início de cada conversa; sem prova de reinjeção depois de compactar | sem evento de troca: a página vale pela raiz do workspace |
| Codex CLI | `SessionStart` com `hookSpecificOutput.additionalContext` | no início e na retomada; sem prova de reinjeção depois de compactar | sem evento de troca: o shim resolve o consumidor a cada evento pelo `cwd`, mas a página não é reinjetada |
| OpenCode | `experimental.chat.system.transform` empurra a página em `output.system` | a cada chamada ao modelo (o plugin pergunta ao shim pelo diretório da sessão) | o diretório do contexto não muda: vale a pasta de lançamento |

O que não foi ensaiado fica como "sem prova": nenhum host é dado como reinjetando a página só porque o canal existe.

## Achados que mudam a implementação

1. **Claude Code, troca de worktree.** O host não recarrega settings de projeto no `EnterWorktree`, mas os hooks de usuário já estão carregados e recebem o `cwd` novo em todo evento. A página do card novo é reinjetada por `PostToolUse` com matcher `EnterWorktree` (saída `additionalContext` válida no schema do host); `CwdChanged` não aceita `additionalContext` e só ajuda como sinal. Sem prova de execução do `EnterWorktree` nesta VM em 2026-10-14 (sem login); confirmado depois no ensaio 15.2 (host 2.1.300).
2. **Cursor carrega os hooks de `~/.claude/settings.json`** (campo `claudeUserHooks` no carregador do CLI). A entrada do Covenant Flow no Claude Code pode então rodar também dentro do Cursor, com payload convertido e `CURSOR_VERSION`/`CURSOR_PROJECT_DIR` no ambiente. O shim ignora a entrada `claude` quando o ambiente é do Cursor, para não executar duas vezes.
3. **Codex exige revisão do host além da nossa.** Depois de `install.sh --account`, o operador precisa abrir `/hooks` no Codex e confiar nas entradas do shim; sem isso não há heartbeat e o `process_event` recusa com `hooks_inactive` citando o Codex. O instalador nunca grava `trusted_hash`.
4. **OpenCode sem identidade por chamada.** O cwd só existe no `init`; o plugin global guarda `directory` do contexto e encaminha cada chamada ao shim com esse valor.
5. **Cursor sem identidade de sessão no `process_event`.** Vale a regra do design: `registration=account` exige pelo menos o shim e o registro do cliente instalados e com R/A revisados.

## Decisão por host

- Claude Code, Codex e OpenCode: `registration=account`, mecanismo executado.
- Cursor: `registration=account` por documentação oficial e pelo carregador do CLI instalado, sem execução ponta a ponta nesta VM por falta de login. A task 15.3 (negação real em Cursor, Codex e OpenCode) foi cancelada por Alan em 2026-10-15: a prova de outras harnesses fica fora deste card. Se uma prova posterior falhar, a única mudança é a linha daquele host na tabela do instalador de conta passar a `unproven` (o shim, o manifesto e o `--check` já tratam esse estado).
- Nenhum host do escopo ficou `unproven` no ensaio.
