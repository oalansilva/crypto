## 1. Lib: dead-turn retry + wait loop helpers

- [x] 1.1 Em `scripts/process-fsm/dsh_plugin_lib.js`, exportar classificador `dsh_dead_turn` (EMPTY_RESPONSE / content vazio, limite de uso/quota, SESSION_NOT_FOUND / sessão em falta) e handler `agent/request-error` de **um** `{ kind: "retry" }` por agente (Set distinto de `dsh_reasoning_effort_none`); segunda ocorrência → `next()`. MUST NOT loop. MUST NOT `import` `@deepseek-ai/dsh*`
- [x] 1.2 Exportar helper de loop: dado `wait: true` e snapshot ainda `running`, repetir `jobs.wait` até terminal (`completed`/`killed`/`failed`) ou teto total 45 min; ler status do result `job_output` sem vendorar `dsh-tool-jobs`
- [x] 1.3 Instalar o handler `dsh_dead_turn` também em `attachAgentEffortGuards` (prepend no `agent.ctx`) sem lançar. **Não** editar `guard.py` `decide()` (fonte MUST NOT ganhar needles deste card); não vendorar runtime; não editar `backend/` nem `frontend/src/`; não editar `~/.dsh/settings.yaml`

## 2. Plugin Guard: rewrite wait, loop execute, steer turn-stopping

- [x] 2.1 `.dsh/plugin/process-fsm-guard.js` `tools/pre-execute`: se `job_output` e `wait === true` e `timeout_ms` ausente ou > cap, reescrever `timeout_ms` para 2400000. Ordem dos denies existentes (grill → effort spawn → cordis → `runGuard`) inalterada
- [x] 2.2 `tools/execute` para `job_output` com `wait`: após `next()`, se ainda `running`, loop 1.2 no **mesmo** execute até terminal ou 45 min. `inject` MAY incluir `"jobs"`; fail-open se `ctx.jobs` ausente (rewrite+cap ainda vale). MUST NOT poll/`sleep` genérico
- [x] 2.3 `ctx.on("agent/turn-stopping", handler, { global: true })`: se owner tem jobs `running`/`stopping` ou filho isolado vivo → `payload.agent.steer` com notice `{ kind: "plugin", plugin: "covenant-flow-process-fsm-guard", form: "notice", summary }` a pedir `job_output wait: true`. Sem pendentes → **não** steer. `inject()` MUST NOT ser o veículo. Listener sem `{ global: true }` MUST NOT ser o aceite
- [x] 2.4 Ligar o retry `dsh_dead_turn` no `apply` host (além do attach no `agent.ctx`)

## 3. Patch tool-jobs + Moore QA + skill

- [x] 3.1 `.dsh/cordis.patch.yml`: patch não-insert `- id: tool-jobs` / `config.maxWaitTimeoutMs: 2400000`. MUST NOT subir `maxConsecutiveWakes`. MUST NOT dual-write T0–T17. `dsh_boot.sh` continua a copiar linhas que não são os `name:` dos dois plugins nossos
- [x] 3.2 `.cursor/process-fsm.yaml` **só** stub `context_file[QA]`: Cursor/Grok filho QA lê checks / MUST NOT `process_event`; dsh root MUST NOT spawnar filho QA; espera `qa-gate` no turno (`job_output wait`, sem `continue`); pai T14 no mesmo turno do verde; pending / `no_pr` / `sync: dirty`. MUST NOT mexer transitions, Σ, `enabled_tools`. Paging `page()` QA ≤20 linhas
- [x] 3.3 `.cursor/skills/covenant-flow/SKILL.md` seção QA dsh: espera no turno / sem `continue` (já tem MUST NOT spawnar filho). Stubs `.dsh/skills/` `.grok/skills/` permanecem ≤8 linhas, sem 12 colunas. `AGENTS.md` MUST NOT crescer

## 4. Goldens pytest `import { apply }`

- [x] 4.1 W1: `job_output wait` ainda `running` após um wait host → `execute` não devolve até terminal ou teto 45 min; wait 30s/10 min que devolve `running` MUST falhar W1. `import { apply }` de `.dsh/plugin/process-fsm-guard.js`
- [x] 4.2 W2: `turn-stopping` `{ global: true }` com jobs running → `steer` + notice plugin; sem global MUST falhar; `inject()`-only MUST falhar. W3: sem jobs/filho → **sem** steer
- [x] 4.3 W4: `wait: true` sem `timeout_ms` → args com `timeout_ms === 2400000`; default 30000 MUST falhar W4. W5: segundo `dsh_dead_turn` → `next()`, sem terceiro retry. W6: primeira `EMPTY_RESPONSE` → `{ kind: "retry" }`
- [x] 4.4 W7: patch `tool-jobs` tem `maxWaitTimeoutMs` 2400000 e **não** sobe `maxConsecutiveWakes`; `.dsh/` sem T0–T17; `guard.py` sem needles novos deste card. W8: F*/E*/G1 regressão. Mock append-inner. `pytest scripts/process-fsm` sem GitHub

## 5. Produto covenant-flow (próximo patch após v1.1.9)

- [x] 5.1 Commit no repo `oalansilva/covenant-flow` (plugin + lib + patch + stub QA + skill + goldens W1–W8) após rebase no tip. Tag = próximo patch livre (`git ls-remote --tags`; origin neste Design = `v1.1.9` ocupado; esperado `v1.1.10` se livre; não major; não mover `v1.1.9`; não vendorar DeepSeek)
- [x] 5.2 `install.sh --pin` continua a copiar `.dsh/` sempre; `CLIENT_KEYS` três; `SCHEMA_MAJOR` 1; `clients.dsh.auto: false`

## 6. Pin Cripto

- [x] 6.1 `implantar --pin` da tag de 5.1 no worktree Cripto; overlay `pin:` = essa tag; `clients.dsh.auto: false` permanece
- [x] 6.2 Não ligar porta 3080 em `environments.dev.services`; não systemd; não dual-write T0–T17; não editar `backend/` / `frontend/src/`

## 7. Verificação

- [x] 7.1 `openspec validate card-858-dsh-idle-closeout --type change --strict` verde; UI impact none (zero diff `frontend/src/` / `backend/` de produto)
- [x] 7.2 Stubs `.dsh/skills/` ≤8; `.dsh/` sem T0–T17; `AGENTS.md` ≤40; sem Auto dsh

## 8. Homologação humana (Design especifica; Apply/homologação executa; **não** opcional)

- [ ] 8.1 Dump autenticado da GUI dsh web `http://127.0.0.1:3080` de um closeout de QA em que a sessão aguentou várias esperas seguidas **sem** prompt `continue`. Filho a devolver e reenvio após turno morto podem ser dumps à parte no mesmo card. Pytest W1–W8 **não** substitui o dump. Homologação ≠ `./restart`; 3080 ≠ systemd; cwd = `canonical_paths.dev`. Este checkbox é o DoD humano — MUST NOT ser residual opcional nem Done só com golden
