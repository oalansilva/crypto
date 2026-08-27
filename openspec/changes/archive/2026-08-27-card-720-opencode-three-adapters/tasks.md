## 1. Núcleo: terceiro dialeto

- [x] 1.1 Estender `normalize()` / `extract_path()` / `extract_paths()` em `scripts/process-fsm/guard.py` para o dialeto nativo OpenCode `{ tool, args }` (`filePath` / `patchText` / `command`); tools `write`/`edit`/`apply_patch`/`bash`; parse live `*** Add File:` / `*** Update File:` / `*** Delete File:` / `*** Move to:` (destino do Move); `decide()` trata qualquer path `product_globs` no patch como `write_produto`
- [x] 1.2 `write`/`edit`/`apply_patch` com path vazio ou `patchText` sem path extraível MUST deny (não early-return allow); tool desconhecida permanece allow (#611)
- [x] 1.3 Atualizar fallback bash para parsear `tool`/`args`/`filePath`/`patchText` (OpenCode `edit` + `filePath=backend/...` sem Python → dual deny)
- [x] 1.4 Usar skills de processo do repo (`.cursor/skills/alan-workflow`) e **não** editar `backend/` nem `frontend/src/`

## 2. Pele OpenCode Guard + paging

- [x] 2.1 Criar `.opencode/plugin/process-fsm-guard.js` (default export função): `tool.execute.before` serializa `{ tool, args }`, chama o mesmo `guard.py`/`decide()`, **throw** no deny; allow não throw
- [x] 2.2 Paging: no mesmo plugin ou módulo irmão, `experimental.chat.system.transform` injeta `page().additional_context` (≤20 linhas, sem release playbook); sem arquivo gitignored + MUST Read
- [x] 2.3 Não criar `opencode.json`; não versionar `.opencode/plugins/`; não criar `.opencode/command(s)/opsx-*`

## 3. Stubs e always-on

- [x] 3.1 Gerar stubs `.opencode/skills/<name>/SKILL.md` só para skills em `.cursor/skills/` (OpenCode 1.18.18 não descobre esse path); corpo ≤8 linhas, MUST Read canônico; não duplicar Impeccable/`design-critic` já em `.agents/skills/`
- [x] 3.2 `AGENTS.md`: nomear Cursor, Grok Build e OpenCode; Cursor Auto; Grok e OpenCode cooperativos até ensaio; ≤40 linhas não-vazias; sem Auto OpenCode/Grok; sem T0–T17
- [x] 3.3 `docs/decision-log.md`: revogar unicidade #562; **não** revogar morte do lock machine; registrar detector nos três clientes

## 4. Detector Impeccable nos três

- [x] 4.1 Grok: registrar `PostToolUse` + `Stop` em `.grok/hooks/` apontando ao mesmo adapter/`hook.mjs` (mapear `hook_event_name` como `.cursor/hooks/impeccable.sh`); fail-open; não relitigar Guard/paging #668
- [x] 4.2 OpenCode: `.opencode/plugin/impeccable-hook.js` com `tool.execute.after` + `session.idle` → o mesmo `hook.mjs`; mapear `args.filePath` → `file_path` e `session.idle` → `hook_event_name=Stop`; catch-all, **nunca throw**
- [x] 4.3 Cursor `afterFileEdit`/`stop` permanece; não segundo detector; não lock machine

## 5. Specs e config (Apply)

- [x] 5.1 Aplicar deltas `process-harness` (dois → três adapters), `cursor-harness`, `developer-tooling` (detector deixa de ser só Cursor), `process-fsm-guard`, `process-fsm-paging` nas specs main
- [x] 5.2 Editar `openspec/config.yaml`: remover “OpenCode is not an active harness” (não feito no turno Design)

## 6. Testes e verificação

- [x] 6.1 Golden `pytest scripts/process-fsm` (sem GitHub): G1–G12 e G17–G18 do `design.md` — G3 deny **e** `extract_paths()==["backend/app/main.py"]`; G17 `apply_patch` `*** Add File:` OpenSpec Design+`card-720-*` **allow** (path só de `patchText`); G18 `*** Move to: backend/app/moved.py` develop deny **e** dest em `extract_paths()`; G4/G5 empty-path deny; G8 `item-edit` com `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`/`bd47fbe8`
- [x] 6.2 Golden paging OpenCode: `page()` body injetável ≤20 linhas sem `release-guard`; G14 adapter detector (`tool.execute.after` mapeia `filePath`→`file_path` + `PostToolUse`; `session.idle`→`Stop`; exit 0); plugin throw no deny (não JSON permission); plugin ESM namespace is only `default` (1.18.18 named-export legacy loader)
- [x] 6.3 `test_agents_md_is_stub`: três clientes; não reivindica Auto OpenCode/Grok; ≤40 linhas; `.opencode/` sem T0–T17 e sem `opsx-*`
- [x] 6.4 `openspec validate` da change verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [ ] 6.5 Homologação humana (não bloqueia o apply; bloqueia Auto): plugin carregado em `.opencode/plugin/`; mesmo worktree `q_git=develop` `write`/`edit`/`apply_patch`/`bash` ilegal em `backend/` ou `frontend/src/` → deny/throw no OpenCode 1.18.18; editar UI nos três clientes dispara `hook.mjs` sem abortar o turno; residual #5894 (subagent `task`) observado se possível
