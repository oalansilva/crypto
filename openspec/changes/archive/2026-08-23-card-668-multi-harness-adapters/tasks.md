## 1. Núcleo: normalize + emit

- [x] 1.1 Extraír `normalize(payload)` (Cursor `tool_name`/`tool_input`/`cwd` e Grok `toolName`/`toolInput`/`workspaceRoot`; write: `Write|StrReplace|Delete|EditNotebook|write|search_replace|Edit|MultiEdit`; shell: `Shell|Bash|run_terminal_command|run_terminal_cmd`; paths `path|file_path|file|target_file|target_notebook`)
- [x] 1.2 Extraír `emit(allow|deny, message)` dual `{permission, decision, agent_message, user_message, reason}` e passar `decide()` a devolver esse objeto
- [x] 1.3 Atualizar fallback bash para dual-emit **e** parsear `toolName`/`toolInput` (Grok `write` + `file_path=backend/...` sem Python → dual deny, não allow por path vazio)
- [x] 1.4 Usar skills de processo do repo (`.cursor/skills/alan-workflow`, `alan-workflow-ambientes`) e **não** editar `backend/` nem `frontend/src/`

## 2. Pele Grok

- [x] 2.1 Versionar `.grok/hooks/` nativo (JSON aninhado, `timeout` ≥ 30s): matcher write `Write|StrReplace|Delete|EditNotebook|write|search_replace|Edit|MultiEdit` e shell `Bash|Shell|run_terminal_command|run_terminal_cmd`
- [x] 2.2 Adapter Grok `SessionStart`: gravar `.grok/rules/process-fsm-page.md` a partir de `page()` (não depender de stdout)
- [x] 2.3 Commitar `.grok/rules/00-harness.md` (δ = `AGENTS.md`; MUST Read `process-fsm-page.md` se existir; sem T0–T17); gitignore a página gerada (não é auto-rule)
- [x] 2.4 Gerador/check de stubs para **todo** `.cursor/skills/*/SKILL.md` (mesmo `name`, description do canônico, corpo ≤8 linhas: Read canônico; cliente Grok; mapear Task inherit → `spawn_subagent` inherit)

## 3. Always-on e specs

- [x] 3.1 Subir δ curto para `AGENTS.md` (≤40 linhas; clientes Cursor e Grok; Alan-only T1/T7/T15; Cursor Auto; Grok cooperativo até ensaio; header deixa de dizer “não always-on”; overlay on-demand)
- [x] 3.2 Afinar `.cursor/rules/harness.mdc` para identidade Cursor (4–12 linhas; hooks + inherit; sem T1/T7/T15, sem “Auto permitido” herdável pelo Grok)
- [x] 3.3 Aplicar deltas das specs `process-harness` (nova), `cursor-harness` (inclui MODIFIED Pronto closeout), `process-fsm-guard`, `process-fsm-paging` no apply (não neste turno de Design)

## 4. Testes e verificação

- [x] 4.1 Golden `pytest scripts/process-fsm`: Cursor Write develop deny; Grok `write`/`search_replace` develop deny; Grok tee deny; Grok OpenSpec Design+`card-*` allow; dual keys; fallback bash com envelope Grok `toolName=write` → `permission`+`decision` deny
- [x] 4.2 Teste de paging Grok: `page()` → arquivo com stub `Todo`, ≤20 linhas, sem `release-guard`; `00-harness.md` contém MUST Read; gerador de stub stale falha
- [x] 4.3 Retarget `test_harness_mdc_body_budget` (4–12 identidade, sem δ no mdc) e `test_agents_md_is_stub` (δ + Alan-only + não reivindica Grok Auto; ≤40 linhas)
- [x] 4.4 `openspec validate` da change verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [ ] 4.5 Homologação humana (não bloqueia o apply): `/hooks-trust` no worktree; mesmo Write ilegal `q_git=develop` deny em Cursor **e** Grok; paging Grok via Read de `process-fsm-page.md` (não auto-inject); até lá Grok permanece cooperativo, não Auto
