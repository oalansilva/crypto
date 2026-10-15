## Why

O #1101 entregou o adapter Claude Code provado só no terminal da VM. O app desktop do Claude no Windows, ligado a esta VM por SSH, roda uma cópia própria do Claude Code (observada nesta VM: `~/.claude/remote/ccd-cli/2.1.295-…`, `entrypoint=claude-desktop`, enquanto o terminal está em `2.1.300`, `entrypoint=cli`), e o coletor de evidência hoje só aceita a superfície `cli`. Alan quer conduzir o trabalho pelo app com as mesmas garantias; e decidiu (2026-10-15) que o residual de review do #1101 entra neste card.

## Problema

Hoje Alan conduz o trabalho dos cards rodando o CLI no terminal da VM. O #1101 já prevê que o Claude Code roda sempre local, pelo CLI na VM, e que o desktop por SSH é uma das superfícies que dirigem essa sessão local. Mas o modo de trabalho do dia a dia continua sendo o terminal: abrir sessão, acompanhar filhos, ver o board e decidir gates ficam espalhados entre terminal, navegador e chat.

## História

Como Alan, quero me conectar a esta VM pelo aplicativo desktop do Claude no Windows, via SSH, e orquestrar meu trabalho por ali em vez de rodar no terminal: abrir sessões no repositório, acompanhar as sessões e filhos de cada card, ver o andamento e decidir os gates que são meus, com as mesmas garantias do processo que o #1101 entrega no CLI.

## Entra

- A conexão do app desktop no Windows com esta VM por SSH já funciona hoje, e as sessões abertas por ela rodam localmente na VM (mesma regra do #1101: sem nuvem). O que falta é o processo valer nessa superfície. O app usa uma cópia própria do Claude Code na VM, numa versão diferente da do terminal, por isso o que passa no terminal não conta como provado no app.
- Alan conduz o card inteiro pelo app (decisão de Alan, 2026-10-15): abre a sessão de cada card, vê os filhos (Design, Apply, reviewers, QA) lado a lado, com a etapa e o resultado de cada um, e responde às perguntas da grelha e às aprovações pelo app. O Status dos cards continua sendo visto no board, no navegador.
- A sessão aberta pelo app nasce em `/source` e passa para o worktree do card sem perder o processo (hooks ativos, Status do card vinculado e ações permitidas por etapa iguais às do CLI).
- Este card prova as proteções no app (decisão de Alan, 2026-10-15): a proteção de escrita por etapa, o modelo por faixa e a evidência do modelo usado por cada filho são ensaiados no próprio app. O #1101 fica responsável por provar o terminal.
- Os gates humanos (T1, T7, T15, T18) continuam só de Alan, no board; o agente não arrasta essas colunas.
- Onde o app não oferecer a proteção, a seleção de modelo ou a evidência que o processo exige, a etapa falha de forma visível no app, sem fallback silencioso para outra superfície (mesma regra do #1101).
- O que acontece quando o app abre uma sessão numa pasta própria criada por ele, fora da pasta de trabalho do card, fica para o Design decidir e explicar a Alan em linguagem de operador. Não é decisão tomada nesta grelha.
- Este card só anda depois que o #1101 chegar a Done técnico (decisão de Alan, 2026-10-15). Até lá fica em Em Refinamento ou Todo, sem Design nem Apply.
- Ensaio real: um card conduzido do início ao fim pelo app no Windows via SSH, com evidência registrada.
- Critérios observáveis:
  - Dado um card em Todo e a sessão aberta pelo app, quando Alan pede `implemente`, então nenhum arquivo de produto muda e a resposta cita o Status atual, como no terminal.
  - Dado um card em andamento, quando Alan abre o app, então vê a sessão do card e os filhos lado a lado, com a etapa e o resultado de cada um, sem precisar do terminal.
  - Dado um filho aberto pelo app, quando ele termina, então o handoff registra o cliente, a superfície e o modelo observado. Se a evidência faltar ou divergir, o gate que a exige reprova, de forma visível no app.
  - Dada uma etapa cuja proteção, modelo ou evidência não funciona no app, quando Alan tenta seguir por ele, então a etapa para com o motivo visível, sem passar sozinha para o terminal.

## Não entra

- Rodar o Claude Code na nuvem ou em outra máquina (decisão de Alan no #1101, 2026-10-14).
- Mudar a FSM, os gates ou a seleção de modelos definidos no #1101.
- Outros clientes (Cursor, Codex, OpenCode, Grok, dsh) operados pelo app.

Relacionados: #1101 (adapter Claude Code — este card é o seguimento dele), #703 (piloto).

UI impact: none. Prototype: N/A. Entrada: Em Refinamento. Este card registra a mudança de processo; não autoriza implementação nem avanço de coluna.

## What Changes

O *como*, resumido (detalhes em `design.md`):

- **Mesma lei, superfície nova.** O app desktop por SSH continua sendo o cliente `claude` (sem cliente novo na FSM, sem `--client` novo). O que muda é a **superfície** observada: `claude-desktop` passa a ser uma superfície conhecida do coletor (`QUALIFIED_ENTRYPOINTS`), só junto com uma fixture real e sanitizada de transcript dessa cópia (tirada de uma sessão real do app); o ensaio vivo confirma. Heartbeat do shim, página, `process_event --client claude`, receipts, proxies e handoff registram a superfície, a versão da cópia do app e a versão do app.
- **Versão lida da sessão, nunca do binário do PATH.** Dentro de uma sessão Claude Code, a versão do host vem só da própria sessão (`AI_AGENT` / transcript). O fallback `claude --version` mediria o binário do terminal (`2.1.300`), não a cópia do app (`2.1.295`); fica proibido dentro de sessão, e a falta da versão vira `capability_unavailable` visível.
- **Pasta própria do app = pasta sem card.** Sessão aberta numa pasta que o app criou (opção *worktree* do app, por padrão `<repo>/.claude/worktrees/<nome>`, num branch do app) não é worktree de card: a página diz isso em uma linha, escrita de produto e de OpenSpec é negada, nenhum filho de etapa nasce e `process_event` recusa. A recuperação é a mesma de `/source`: a própria sessão entra no worktree `card-<id>-*` com `EnterWorktree`. Nada é apagado, nada é adotado como worktree de card.
- **Filho de etapa só por `Agent`.** As ferramentas de sessão do app que abrem outra sessão (por exemplo `mcp__ccd_session__spawn_task`) não podem servir para nascer filho de etapa sem captura e receipt: o hook nega quando há card vinculado.
- **Acompanhar pelo app.** Os filhos aparecem no painel de tarefas/subagentes do app pelo `description` `<papel> <id> <único>` (etapa) e pelo estado de retorno (resultado); a sessão do card leva `#<id>` no título; o handoff de cada etapa lista cliente, superfície e modelo observado por filho. O Status continua no board.
- **Falha visível no app.** Onde a cópia do app não oferecer hook, `effort` por invocação, sessão identificável ou transcript no formato, a etapa para com o motivo no próprio chat do app (deny do hook, recusa do `prepare`/`process_event`), sem passar ao terminal. O modo de permissão do app (abre em `auto`) não autoriza processo.
- **Residual do #1101** (decisão de Alan, 2026-10-15): correções no adapter, no shim, no instalador, nos testes, nas regras e no runbook, listadas abaixo com origem; o grupo de digest vem antes de qualquer outra edição do adapter.
- **Ensaio real no app:** um card conduzido do início ao fim pelo app no Windows via SSH, mais os negativos dos quatro critérios, com evidência registrada.

### Residual do #1101 que entra (origem → item)

Origens: **A** = comentário `6183698630` (que cita os comentários do #1101 `6170767412`, `6174258031`, `6177245185`, `6183680647`); **B** = `6183722826` (`1101-close-r3`); **C** = `6183874513` (ensaio 15.2, achado 39); **D** = `6184024579` (achado 41); **E** = `6184214645` (onda `1101-cancel-w1`).

| ID | Item | Origem |
| --- | --- | --- |
| R1 | `route-landmarks.yaml` fora do digest A (`CORE_TREES`), com teste (P2, prioridade) | A |
| R2 | `scripts/process-fsm/*_fixtures.py` fora do digest A (P3, junto de R1) | B |
| R3 | digest A cobre `entrypoints`/`modules` do manifesto (P2 / P1 de juízo da w1) | A |
| R4 | `cf_shim.enumerate_tree` e symlink de diretório (P2) | A |
| R5 | `.pyc` solto, `node_modules`, `.git`: excluir `.pyc` só dentro de `__pycache__/` | A |
| R6 | `adapter_manifest.client_entry` com digest `None` falha no pin | A |
| R7 | `detector/` do Impeccable dentro do digest | A |
| R8 | `SessionStart` `compact`/`clear`/`resume` não regrava `registration_digest` | A |
| R9 | `_foreign_cursor_call` não decide pelo ambiente `CURSOR_*` | A |
| R10 | recusa `hooks_inactive` no Cursor e no OpenCode sem depender de `--client`/`COVENANT_CLIENT` | A |
| R11 | `cf_shim.discover` com repo Git aninhado | A |
| R12 | `cf_shim_opencode.js` não bloqueia `read` quando o `import()` falha | A |
| R13 | `<synthetic>` final que não é erro não vira `failed` | A |
| R14 | piso de hook 2.1.295 alinhado entre doc, design e código | A |
| R15 | endurecimento de `trust --record` pelo agente; `shim_verified()` não aceita ambiente como prova | A, B |
| R16 | aviso de pins mistos na página | A |
| R17 | reinjeção da página por host em `host-mechanisms.md` | A |
| R18 | `--remove` em Claude e Codex sem `"hooks": {}` e sem reescrever settings sem entradas | A |
| R19 | `_merge_cursor` sem `hooks` vazio no `--remove` | A |
| R20 | `run_remove` remove o alvo, não só o symlink | A |
| R21 | `install.sh` do nucleus na onda de review do consumidor | A |
| R22 | `test_guard` do Impeccable pelo shim prova que o `impeccable.sh` rodou | A |
| R23 | `test_design_clone_gate` exige `/combo/results` no catálogo do Cripto | A |
| R24 | `test_release_closeout` com `pytest.skip` explícito sem `docs/crypto-overlay.md` | A |
| R25 | skill `covenant-flow` linha 70 (`.codex/hooks.json`) atualizada | A |
| R26 | spec do #1101 cita `hook.mjs`; a recusa de T16 da 6.2 vale no evento, não só no runbook | A |
| R27 | primeira escrita de um filho real (3.7) provada com transcript real | A |
| R28 | `G_design` (T5) valida os tokens `UI impact`/`live_route`/`surface` (achados 27/28) | A |
| R29 | comandos para o operador sem `!` e sem `cd … &&` (achado 34) | A |
| R30 | runbook: depois da revisão da conta, `hooks_inactive` até sessão nova (achado 37) | A |
| R31 | `.cursor/rules/harness.mdc:8` e `rules.md:52` sem `.cursor/hooks.json` do projeto (nucleus e consumidor) | B |
| R32 | tasks 3.2 e 7.1 do OpenSpec do #1101 anotadas "substituído por 11.4/11.5" | B |
| R33 | falso positivo do Guard: redirecionamento para fora do repo e `>>` dentro de heredoc (achado 39) | C |
| R34 | sessão em `/source` com `#<id>` recebe a página (achado 41), reavaliado depois do T14 do #1101 | D |
| R35 | 9.6 do #1101 (fecho de lote no Claude Code) só se Alan pedir | E |
| R36 | notas de supersessão no OpenSpec do #1101 (6.5, 2.4, 9.3) antes do archive | E |

Ficam no #1101, por decisão de Alan no comentário A: 7.3 (tag), 8.3, 15.2, 15.3, 9.x e 10.x.

## Capabilities

### New Capabilities

- `claude-desktop-surface`: o app desktop do Claude no Windows, por SSH, como superfície do cliente `claude` nesta VM — reconhecimento da cópia própria do app, pasta própria do app, acompanhamento pelo app, falha visível sem fallback e ensaio real.

### Modified Capabilities

- `account-hook-shim` (introduzida pelo #1101, ainda não arquivada; delta só com requisitos adicionados): residual do shim, do digest e do instalador da conta (R1–R12, R15, R16, R18–R21).
- `claude-code-harness` (introduzida pelo #1101, ainda não arquivada; delta só com requisitos adicionados): residual do adapter Claude Code (R13, R14, R26, R27, R35).
- `process-fsm-guard`: falso positivo de destino de escrita (R33).
- `process-harness`: tokens do Design no T5, textos de regra, runbook e notas de supersessão (R17, R22–R26, R28–R32, R34, R36).

## Impact

- Consumidor (`oalansilva/crypto`): `scripts/process-fsm/` (`claude_evidence.py`, `claude_adapter.py`, `claude_trust.py`, `model_selection.py`, `cf_shim.py`, `cf_shim_opencode.js`, `adapter_manifest.py`, `account_install.py`, `guard.py`, `process_event.py`, `design_clone_gate.py`/gate de T5, testes e fixtures), `.cursor/rules/harness.mdc`, `.cursor/skills/covenant-flow/SKILL.md` (+ pontes), `docs/claude-runtime-evidence.md`, `.gitignore` (`.claude/worktrees/`), notas no OpenSpec do #1101.
- Nucleus (`oalansilva/covenant-flow`): shim, `install.sh` (`--account`/`--remove`/`--pin`), `rules.md`, tag nova e pin no consumidor.
- Conta do operador: shim novo instalado por `install.sh --account`, revisão R/A pelo operador; seleção de modelos inalterada.
- Sem mudança em FSM, gates, seleção de modelos, `AGENTS.md`, `backend/` ou `frontend/src/`.
