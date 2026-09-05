Skills canónicas deste repo (`.cursor/skills/`, `.agents/skills/`): `covenant-flow`, `implantar`, `openspec-apply-change`. Apply só com `Status=Pronto para Dev` (gate Design → Aprovação de Design → Pronto para Dev; `UI impact: none` não pula colunas). Não editar `backend/` nem `frontend/src/`. Não editar `guard.py`. Não reabrir #786 / #790. Não reverter #817 (`dsh_reasoning_effort_spawn`, `agent/request`). Não trocar o texto do comentário canónico T1. Não ensinar o modelo a omitir o ritual no briefing. Não alargar a lista de marcadores.

## 1. Goldens TDD (falham no matcher live)

- [x] 1.1 Em `scripts/process-fsm/test_dsh_grill_spawn.py`, acrescentar G12 via `apply` + `tools/pre-execute`: `subagent` description `design-autor 818` (sem `grill-card`) e prompt contendo `grill-card fronteira vazia` → `nextCalled === true` e reason **não** contém `dsh_grill_spawn`
- [x] 1.2 G12b/G12c: description `apply 818` com prompt `grill-card dod` / `dod grelhado`; description `diff-reviewer 818` com prompt `closed grill` + `grill-card` → idem allow via `apply`
- [x] 1.3 G12d: description `design-autor 818` + nested campo que **não** é `description`/`prompt` contendo `grill-card` → allow; G10 nested `inner.prompt` `x grill-card y` permanece `isGrillShapedSpawn === true`
- [x] 1.4 Confirmar que G1 (`grill-card 701`), G2 (`Please run Grill-Card`), G6 (JSON string description) e G10 negativos `grill_card` / `grill card` continuam exactos; G5/G11 inalterados

## 2. Helper JS (papel vs citação)

- [x] 2.1 Em `scripts/process-fsm/dsh_plugin_lib.js`, reescrever haystacks de `isGrillShapedSpawn`: só chaves `description`/`prompt` (recursivo em objectos); `arguments` string → `JSON.parse` ou string crua como prompt; MUST NOT `JSON.stringify` o objecto inteiro
- [x] 2.2 Aplicar D1: description com `grill-card` → true; prompt com `grill-card` e algum marcador pinado (`fronteira vazia`, `do not re-interview`, `não reentrevistar`, `do not invoke grill-card`, `não invocar grill-card`, `closed grill`, `grill-card dod`, `dod grelhado`, `grilled dod`) → false; prompt com `grill-card` sem marcador → true; tools exactas `subagent` / `subagent_fork`; `includes` após `toLowerCase()`, **não** regex
- [x] 2.3 **Não** editar `guard.py` (fonte MUST NOT conter `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`). «Listener inalterado» = `isGrillShapedSpawn` **primeiro** entre denys de spawn, **antes** de `runGuard`, reason `dsh_grill_spawn`, sem `next()` — **não** ficheiro byte-identical a `v1.1.6`. MUST NOT reverter `dsh_reasoning_effort_spawn` nem `agent/request` / `agent/request-error` se #817 já os tiver; o gate #817 MAY ficar depois do grill e antes de cordis

## 3. Pytest

- [x] 3.1 `pytest scripts/process-fsm/test_dsh_grill_spawn.py` verde: G1–G11 + G12/G12b/G12c/G12d
- [x] 3.2 Pin-tests (`test_dsh_adapter.py` e needle em `test_grill_card.py`) sobem o esperado de `v1.1.6` para **a tag deste card após rebase** (não hardcode `v1.1.7` no vácuo); N3 `guard.py` sem needle; `pytest scripts/process-fsm` sem GitHub verde

## 4. Tag produto (após rebase no sibling)

- [x] 4.1 `gh api repos/oalansilva/covenant-flow/tags` **e** rebase o produto na tag/tip que já existir (incl. #817 / `card-817-dsh-reasoning-effort` se tiver publicado o nucleus). MUST NOT partir de `v1.1.6` a ignorar o sibling. Número: se `v1.1.7` livre no tip `v1.1.6`, MAY usá-la; se #817 já a ocupou, próximo patch livre (nunca major). `SCHEMA_MAJOR` permanece 1
- [x] 4.2 Commit no produto (helper + goldens **em cima** do tip rebaseado) e tag = a deste card; `install.sh --pin` continua a copiar nucleus/adapters; MUST NOT vendorar `deepseek-harness`; MUST NOT editar `process-fsm.yaml` / `AGENTS.md` / texto T1 / skills Cursor-Grok de grill spawn; MUST NOT reverter listeners #817

## 5. Pin Cripto

- [x] 5.1 `implantar --pin` da **tag deste card** (pós-rebase) no worktree Cripto; overlay `pin:` = essa tag; `clients.dsh.auto: false` permanece
- [x] 5.2 Não reabrir #786/#790; não clobber #817; zero diff `backend/` / `frontend/src/` de produto; peles grill-card continuam thin; Cursor/Grok continuam a poder spawnar grill

## 6. Verificação

- [x] 6.1 `openspec validate card-818-dsh-grill-spawn-cite --type change --strict` verde; UI impact none; Prototype N/A
- [x] 6.2 G12 allow e G1 deny no mesmo ficheiro de testes; fonte de `guard.py` sem matcher; overlay pin = tag deste card; plugin ainda tem grill primeiro e, se o tip as tiver, as linhas `dsh_reasoning_effort_spawn` / `agent/request`


## 1. Goldens TDD (falham no matcher live)

- [x] 1.1 Em `scripts/process-fsm/test_dsh_grill_spawn.py`, acrescentar G12 via `apply` + `tools/pre-execute`: `subagent` description `design-autor 818` (sem `grill-card`) e prompt contendo `grill-card fronteira vazia` → `nextCalled === true` e reason **não** contém `dsh_grill_spawn`
- [x] 1.2 G12b/G12c: description `apply 818` com prompt `grill-card dod` / `dod grelhado`; description `diff-reviewer 818` com prompt `closed grill` + `grill-card` → idem allow via `apply`
- [x] 1.3 G12d: description `design-autor 818` + nested campo que **não** é `description`/`prompt` contendo `grill-card` → allow; G10 nested `inner.prompt` `x grill-card y` permanece `isGrillShapedSpawn === true`
- [x] 1.4 Confirmar que G1 (`grill-card 701`), G2 (`Please run Grill-Card`), G6 (JSON string description) e G10 negativos `grill_card` / `grill card` continuam exactos; G5/G11 inalterados

## 2. Helper JS (papel vs citação)

- [x] 2.1 Em `scripts/process-fsm/dsh_plugin_lib.js`, reescrever haystacks de `isGrillShapedSpawn`: só chaves `description`/`prompt` (recursivo em objectos); `arguments` string → `JSON.parse` ou string crua como prompt; MUST NOT `JSON.stringify` o objecto inteiro
- [x] 2.2 Aplicar D1: description com `grill-card` → true; prompt com `grill-card` e algum marcador pinado (`fronteira vazia`, `do not re-interview`, `não reentrevistar`, `do not invoke grill-card`, `não invocar grill-card`, `closed grill`, `grill-card dod`, `dod grelhado`, `grilled dod`) → false; prompt com `grill-card` sem marcador → true; tools exactas `subagent` / `subagent_fork`; `includes` após `toLowerCase()`, **não** regex
- [x] 2.3 **Não** editar `guard.py` (fonte MUST NOT conter `grill-card` / `dsh_grill_spawn` / `isGrillShapedSpawn`); **não** mover o matcher para o listener; `.dsh/plugin/process-fsm-guard.js` permanece `isGrillShapedSpawn` antes de `runGuard`, reason `dsh_grill_spawn`, sem `next()` no deny

## 3. Pytest

- [x] 3.1 `pytest scripts/process-fsm/test_dsh_grill_spawn.py` verde: G1–G11 + G12/G12b/G12c/G12d
- [x] 3.2 Pin-tests (`test_dsh_adapter.py` e needle em `test_grill_card.py`) sobem o esperado de `v1.1.6` para a tag deste card; N3 `guard.py` sem needle; `pytest scripts/process-fsm` sem GitHub verde

## 4. Tag produto

- [x] 4.1 Confirmar `gh api repos/oalansilva/covenant-flow/tags`; se `v1.1.7` livre, usá-la; senão o próximo patch livre (nunca major); `SCHEMA_MAJOR` permanece 1
- [x] 4.2 Commit no produto (helper + goldens) e tag patch; `install.sh --pin` continua a copiar nucleus/adapters; MUST NOT vendorar `deepseek-harness`; MUST NOT editar `process-fsm.yaml` / `AGENTS.md` / texto T1 / skills Cursor-Grok de grill spawn

## 5. Pin Cripto

- [x] 5.1 `implantar --pin` da tag deste card no worktree Cripto; overlay `pin:` = essa tag; `clients.dsh.auto: false` permanece
- [x] 5.2 Não reabrir #786/#790; zero diff `backend/` / `frontend/src/` de produto; peles grill-card continuam thin; Cursor/Grok continuam a poder spawnar grill

## 6. Verificação

- [x] 6.1 `openspec validate card-818-dsh-grill-spawn-cite --type change --strict` verde; UI impact none; Prototype N/A
- [x] 6.2 G12 allow e G1 deny no mesmo ficheiro de testes; fonte de `guard.py` sem matcher; overlay pin = tag deste card
