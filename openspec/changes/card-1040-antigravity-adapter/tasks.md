# Tasks — card-1040-antigravity-adapter (Harness Antigravity CLI)

> **AVISO OBRIGATÓRIO:** Execução SOMENTE após `Status=Pronto para Dev` (T8).
> Este filho de Design NÃO implementa código de produto nem altera scripts de produção.
> `UI impact: none` nesta entrega: harness de processo puro (sem tela, rota, HTML ou banco de produto).
> Zero Dual-Write: runbooks canônicos continuam exclusivamente sob `.cursor/skills/`.

## 1. Stubs do Antigravity CLI (`scripts/process-fsm/antigravity_stubs.py` e `.agents/skills/*`)

- [ ] 1.1 — Criar `scripts/process-fsm/antigravity_stubs.py` com `canonical_skills()`, `stub_sources()`, `expected_stubs()`, `write_stubs()` e `stub_errors()`, preservando as skills canônicas locais (`impeccable`, `playwright-cli`).
- [ ] 1.2 — Executar `antigravity_stubs.py` para gerar os stubs leves em `.agents/skills/*` apontando para `.cursor/skills/*` (`covenant-flow`, `covenant-flow-environments`, `github-project-board`, `grill-card`, `grilling`, `implantar`, `kaizen`, `openspec-*` e atualizar `design-critic` para stub apontando para o canônico).
- [ ] 1.3 — Validar que `stub_errors()` retorna lista vazia.

## 2. Write Guard e Normalização (`scripts/process-fsm/guard.py`)

- [ ] 2.1 — Em `scripts/process-fsm/guard.py`, adicionar `"write_to_file"` e `"replace_file_content"` ao conjunto `WRITE_TOOLS`.
- [ ] 2.2 — Em `scripts/process-fsm/guard.py`, adicionar `"run_command"` ao conjunto `SHELL_TOOLS`.
- [ ] 2.3 — Em `scripts/process-fsm/guard.py`, adicionar `"TargetFile"` e `"targetFile"` à tupla `PATH_KEYS`.
- [ ] 2.4 — Em `scripts/process-fsm/guard.py`, atualizar `normalize()` para extrair `CommandLine` do dicionário de argumentos de ferramentas shell.

## 3. Adapter de Hooks (`scripts/process-fsm/antigravity_guard.py` e `.agents/hooks.json`)

- [ ] 3.1 — Criar `scripts/process-fsm/antigravity_guard.py` para receber payload JSON no stdin (`toolCall`), normalizar argumentos, delegar a `decide()` de `guard.py` e emitir `{"decision": "...", "reason": "..."}` no stdout com exit code 0 e fail-closed em erros.
- [ ] 3.2 — Criar `.agents/hooks.json` configurando o hook `fsm-guard` no evento `PreToolUse` com matcher `"write_to_file|replace_file_content|run_command"` apontando para `antigravity_guard.py`.

## 4. Catálogo de Clientes (`AGENTS.md`)

- [ ] 4.1 — Atualizar `AGENTS.md` para incluir `Antigravity CLI (agy)` na lista de clientes cooperativos.
- [ ] 4.2 — Atualizar `AGENTS.md` para proibir reivindicação de modo Auto no `agy`.

## 5. Suíte de Testes do Adapter (`scripts/process-fsm/test_antigravity_adapter.py`)

- [ ] 5.1 — Criar `scripts/process-fsm/test_antigravity_adapter.py` com testes para:
  - Sincronização e integridade dos stubs em `.agents/skills/` (`stub_errors`).
  - Bloqueio de escrita em produto em `Todo` e `Design` via payload do Antigravity.
  - Bloqueio de redirecionamentos e mutações perigosas via `run_command`.
  - Permissão de escrita após `Pronto para Dev`.
  - Permissão de escrita em `openspec/changes/` durante `Design`.
  - Execução CLI de `antigravity_guard.py` via subprocess (stdin/stdout e fail-closed).
- [ ] 5.2 — Rodar `pytest scripts/process-fsm/test_antigravity_adapter.py` e garantir 100% de aprovação.
- [ ] 5.3 — Rodar suíte completa `pytest scripts/process-fsm` garantindo zero regressões.

## 6. Validação e Handoff

- [ ] 6.1 — Validar o pacote OpenSpec com `openspec validate card-1040-antigravity-adapter --strict`.
- [ ] 6.2 — Verificar `git status` e preparar handoff para revisão e fechamento.
