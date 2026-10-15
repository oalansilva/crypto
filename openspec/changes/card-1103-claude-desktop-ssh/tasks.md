Nota: use as skills do projeto disponíveis aos clientes quando aplicável (`.cursor/skills/` canônico; pontes em `.agents/skills/` e `.claude/skills/`), em especial `covenant-flow`, `openspec-apply-change` e `implantar`. Gate antes do código: Design → Aprovação de Design (T7, só Alan) → Pronto para Dev; nenhuma task abaixo roda antes disso. IDs `R<n>` = residual do #1101 listado no `proposal.md`.

## 1. Digest A (prioridade: antes de qualquer outra edição do adapter)

- [ ] 1.1 Excluir `scripts/process-fsm/route-landmarks.yaml` (R1) e `scripts/process-fsm/*_fixtures.py` (R2) de `CORE_TREES`; teste: editar cada um não muda A nem gera `adapter_divergent`.
- [ ] 1.2 Incluir o bloco `entrypoints`/`modules` do cliente no digest A (R3); teste: mudar só o argv dá `hooks_unreviewed`.
- [ ] 1.3 `cf_shim.enumerate_tree` segue symlink de diretório e inclui o alvo; symlink para fora do repo falha no pin (R4); testes dos dois casos.
- [ ] 1.4 Excluir só `__pycache__/` e os `.pyc` dentro dele; `.pyc` solto entra em A; ajustar `_is_cache_file` e o teste que consagrava o contrário (R5).
- [ ] 1.5 `adapter_manifest.client_entry` falha no pin citando o arquivo quando o digest é `None` (R6); teste.
- [ ] 1.6 `detector/` do Impeccable dentro de A, com teste de um byte alterado (R7).

## 2. Shim e conta

- [ ] 2.1 `SessionStart` grava `registration_digest` só com `source=startup`; `compact`/`clear`/`resume` preservam (R8); teste de `hooks_changed` depois de compactar.
- [ ] 2.2 `_foreign_cursor_call` decide pelo cliente do registro que chamou o shim, não por `CURSOR_*` (R9); teste com Codex num processo que herdou `CURSOR_*`.
- [ ] 2.3 Detecção nativa de cliente no Cursor e no OpenCode para `hooks_inactive`, sem `--client`/`COVENANT_CLIENT` (R10); testes.
- [ ] 2.4 `cf_shim.discover` sobe de repo Git aninhado sem overlay até o consumidor pinado (R11); teste.
- [ ] 2.5 `cf_shim_opencode.js`: falha de `import()` não bloqueia `read`; escrita, shell e spawn continuam deny (R12); teste.
- [ ] 2.6 `trust --record` exige confirmação interativa e recusa dentro de sessão de agente; `claude_trust.shim_verified()` deixa de aceitar `CF_SHIM_ACTIVE`/`CF_SHIM_ADAPTER_DIGEST` do ambiente (R15); testes.
- [ ] 2.7 Aviso de pins mistos na página (R16); teste.

## 3. Instalador da conta (nucleus)

- [ ] 3.1 `--remove` em Claude Code e Codex só reescreve com entrada do Covenant Flow; nunca cria `"hooks": {}` nem altera `{}` (R18); `_merge_cursor` idem (R19); testes byte a byte.
- [ ] 3.2 `run_remove` remove o diretório versionado do shim e o link `current`, sem alvo órfão (R20); teste.
- [ ] 3.3 Diff do `install.sh` do nucleus incluído no `review_diff_path` da onda de review do consumidor (R21).

## 4. Superfície app desktop (design §1–§9)

- [ ] 4.1 Heartbeat do shim grava `entrypoint`, `host_version` e, quando presentes, versão do app desktop e marca SSH; receipt, evidência, proxy e handoff registram superfície e versões.
- [ ] 4.2 Versão do host só da sessão: `claude_detect_version` usa `claude --version` só fora de sessão (`CLAUDECODE` ausente); dentro de sessão sem `AI_AGENT` = `capability_unavailable` com a superfície; teste com PATH apontando para outra versão.
- [ ] 4.3 Piso 2.1.295 aplicado no código para nascimentos e transições que dependem de hook, igual à doc e ao design (R14); teste em 2.1.294 e 2.1.295.
- [ ] 4.4 Fixture real e sanitizada do transcript do app (pai e filho, `entrypoint=claude-desktop`, versão observada), tirada de uma sessão real do app, em `claude_fixtures.py`; `claude_evidence.py` ganha `claude-desktop` em `QUALIFIED_ENTRYPOINTS` só junto dela; testes de `prepare`/`collect` com a fixture e de transcript com `cli` e `claude-desktop` misturados = `unverified`.
- [ ] 4.5 Pasta própria do app: página e motivo de deny dizem "pasta do app (sem card)" com a recuperação `#<id>` → `EnterWorktree` quando a raiz está sob `.claude/worktrees/` ou na pasta de worktree configurada; testes (deny de produto e de OpenSpec, `prepare` e `process_event` recusados, nada apagado).
- [ ] 4.6 `.claude/worktrees/` no `.gitignore` do consumidor.
- [ ] 4.7 `PreToolUse` com card vinculado nega as ferramentas `mcp__ccd_*` que criam sessão, mandam mensagem a outra sessão ou abrem sessão em outra pasta, e trata `mcp__ccd_*` não classificada como criadora; leitura e layout livres; registro da conta ganha o matcher; testes.
- [ ] 4.8 Runbook do pai: título `#<id>` na sessão do app, `description` `<papel> <id> <único>` e linha de handoff por filho com cliente, superfície, modelo/esforço observados e status, tirada do proxy.
- [ ] 4.9 R34 no Apply: teste de que sessão em `/source` no pin atual recebe a página com `q_git=develop` e a instrução `EnterWorktree`; se faltar, implementar no `SessionStart` até o teste passar.

## 5. Adapter Claude Code e Guard

- [ ] 5.1 `<synthetic>` final só é `failed` com erro da API; sem erro fica fora da comparação e vale o último turno real (R13); testes dos dois casos.
- [ ] 5.2 `process_event fechar_release` com cliente `claude` confere o pai observado contra `claude/execucao` (`observe-parent` + `load_execucao_pair`) e recusa divergente/`unavailable` (R26); teste.
- [ ] 5.3 Guard: destino de redirecionamento resolvido; fora do repo não é escrita de produto; `>>` dentro de heredoc é texto; dentro do repo continua negado (R33); testes dos três cenários.
- [ ] 5.4 `submeter_design` (T5) exige `UI impact`/`live_route`/`surface` parseáveis pelo parser de `design_clone_gate.py`, citando o token faltante (R28); testes.
- [ ] 5.5 `claude_evidence` (`extract`/`_handbacks`) reconhece o retorno em segundo plano (design §9): `queue-operation` `enqueue` com `<task-notification>` aceito só com `<task-id>`==`agentId` e `<tool-use-id>`==`call.id`; `<status>` completed→`completed` com payload de `<result>`, failed→`failed`, killed→`interrupted`; spawn `async_launched` aceito com `resolvedModel` igual à captura, ou checado no retorno/turnos do filho quando o spawn não traz `resolvedModel`; forma desconhecida = `unsupported_schema` citando o campo. Fixtures reais sanitizadas em `claude_fixtures.py`: do 2.1.300 CLI (este card, agentIds `af0a1917b83c8aa19` e `aacea23e2dfb0ccf9`) e do app; testes dos cenários de "Background child handback is recognized" (completed com payload, failed, `tool-use-id` divergente não aceito, forma desconhecida = `unsupported_schema`).
- [ ] 5.6 Depois da 5.5, recoletar no Apply os proxies do Design-autor, do crítico e do rework do Design do #1103 (receipts em `.cursor/tmp/claude-evidence/` do worktree) e registrar no card o resultado de cada um (status e par observado = captura, ou o motivo).

## 6. Testes, regras, docs e notas do #1101

- [ ] 6.1 `test_guard` do Impeccable pelo shim com stub que grava log e `stderr == ""` (R22); `test_design_clone_gate` exige `/combo/results` no catálogo do Cripto (R23); `test_release_closeout` com `pytest.skip` explícito sem `docs/crypto-overlay.md` (R24).
- [ ] 6.2 `.cursor/rules/harness.mdc:8` e `rules.md:52` (nucleus e consumidor) e a linha 70 da skill `covenant-flow` descrevem "registro na conta (`install.sh --account`) → shim → adapter pinado" (R25, R31); teste de texto.
- [ ] 6.3 Skill `covenant-flow` (seção Claude Code): superfície app desktop (abrir em `/source` com a opção *worktree* desligada, pasta do app = sem card, `#<id>` → `EnterWorktree`, filho só por `Agent`, modo `auto` não autoriza), comandos de operador sem `!` e sem `cd … &&` (R29), sessão nova depois da revisão da conta (R30); regenerar pontes e manifestos.
- [ ] 6.4 `docs/claude-runtime-evidence.md`: tabela de superfícies com a linha do app desktop, versão lida da sessão, pisos 2.1.292/2.1.295.
- [ ] 6.5 OpenSpec do #1101: tabela de reinjeção da página por host em `host-mechanisms.md` (R17); notas de supersessão em 3.2/7.1 "substituído por 11.4/11.5" (R32), 6.5, 2.4 e 9.3 (R36); `hook.mjs` citado no requisito Impeccable da spec (R26).

## 7. Integração e verificação local

- [ ] 7.1 `python3 -m pytest scripts/process-fsm` e testes do nucleus verdes; testes de Cursor, Codex, OpenCode, Grok Build e dsh inalterados e verdes; `openspec validate card-1103-claude-desktop-ssh --strict` verde.
- [ ] 7.2 Tag do nucleus e pin no consumidor, comparando overlay, política e adapters antes/depois; Alan instala o shim novo com `install.sh --account`, revisa R e A em bash comum e abre sessão nova. <!-- covenant-flow:after-commit -->

## 8. Ensaio real pelo app (Alan opera no Windows; design §11)

- [ ] 8.1 Sessão aberta pelo app em `/source` (opção *worktree* desligada): heartbeat com `entrypoint=claude-desktop` e versões; verificar a página em `/source` (R34; implementada e testada na 4.9); `#<id>` → `EnterWorktree` com `bound_card=<id>`; `CLAUDECODE`, `AI_AGENT` e `CLAUDE_CODE_SESSION_ID` presentes no `Bash` do app; `process_event --client claude --dry-run` sem `hooks_inactive`. <!-- covenant-flow:after-qa -->
- [ ] 8.2 Negativos no app, no modo de permissão em que ele abre: `implemente` em `Todo` sem arquivo alterado e com o Status citado; `Edit` e `Bash` de produto em `develop` negados; spawn sem `effort` e com modelo divergente negados; sessão na pasta do app recusada e saída por `EnterWorktree`; ferramenta de sessão do app negada com card vinculado; evidência apagada ou divergente de um filho reprova o gate com o motivo no chat do app; `AI_AGENT` ausente simulado → `capability_unavailable` sem consultar PATH; registro na conta não carregado → `hooks_inactive` com recuperação visível no chat do app; pelo menos um filho de etapa lançado em segundo plano no app coletado `completed` pela notificação. <!-- covenant-flow:after-qa -->
- [ ] 8.3 Card de ensaio (escolhido e priorizado por Alan), empilhado sobre o SHA com QA verde deste card, conduzido pelo app de Em Refinamento até QA verde: grelha, Design com crítico, T7, Apply, onda de review e QA; filhos lado a lado no app com etapa e resultado; primeira escrita de um filho real verificada contra a captura (R27); pelo menos um filho de etapa lançado em segundo plano no app coletado `completed` pela notificação; handoff com cliente, superfície e modelo observado por filho. <!-- covenant-flow:after-qa -->
- [ ] 8.4 Perguntar a Alan se quer o ensaio do fecho de lote no Claude Code (9.6 do #1101); se sim, rodar pelo app com pai em `claude/execucao`; se não, registrar a resposta dele no card (R35). <!-- covenant-flow:after-qa -->
- [ ] 8.5 Registrar no #1103 a evidência por bloco: ids de sessão e filhos, superfície, versões, pares observados = capturas, saídas de `process_event`, motivos de deny tirados do transcript e lacunas que ficaram como falha visível. <!-- covenant-flow:after-qa -->
