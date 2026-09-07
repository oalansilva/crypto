## Context

Card [#858](https://github.com/oalansilva/crypto/issues/858). Status observado: **Design**. Bound `q_git=card-858-dsh-idle-closeout`. Briefing = issue grelhado (Q1–Q4=A, 2026-09-07). Este Design **não** reabre as Qs.

Overlay Cripto `.covenant-flow/overlay.yaml`: `pin: v1.1.9`, `clients.dsh.auto: false`. Plugin live `.dsh/plugin/process-fsm-guard.js`: `inject = ["systemPrompt","skills"]`; settlement filho via `followup`/`steer` (#839). Moore `context_file[QA]` ainda diz «Filho QA lê checks»; a skill já diz que no dsh o root MUST NOT spawnar filho QA. Host `@deepseek-ai/dsh-tool-jobs` `0.1.2-rc.1`: `job_output wait` sem `timeout_ms` espera `waitTimeoutMs` **30s**; `maxWaitTimeoutMs` **10 min** (6e5); job done em pai idle → `followup` até `maxConsecutiveWakes` **3**, depois `inject` (não acorda); pai busy → `inject` no passo actual. `agent/turn-stopping` pode `steer` e manter o turno aberto.

Evidência: 852 T35 (~18:05 UTC) — watch do CI em fundo; turno fechado; UI idle; job ainda vivo. 853/854 — cadeia de `continue`; limite de uso; resposta vazia; sessão em falta no provedor. CI típico ~35 min > cap 10 min e >> default 30s.

UI impact: none
live_route: N/A — GUI dsh :3080 é dump de homologação vendor, não rota de catálogo Cripto
surface: N/A — harness dsh; sem tela de produto a clonar

## Goals / Non-Goals

**Goals:**

- Qualquer passo ainda do agente (espera de check, filho a devolver, integrar após verde): a GUI `:3080` **não** fica idle à espera de `continue`; sessão **ocupada** até decidir, check longo inclusive.
- Se parar, volta sozinha após várias esperas seguidas — sem `continue`.
- Turno morto no provedor: um reenvio; segundo falhanço visível; sem loop.
- Moore QA yaml nomeia closeout dsh no root. Pin = próximo patch livre após `v1.1.9` + `implantar --pin` no Cripto.
- Dump autenticado `:3080` de closeout QA com várias esperas seguidas sem prompt `continue`.

**Non-Goals:**

- Ligar Auto. Cruzar priorizar / aprovar design / homologar. Vendorar runtime DeepSeek. Mudar 12 colunas/eventos. Produto `backend/` / `frontend/src/`. Porta 3080 systemd. Cursor/Grok/OpenCode como alvo. Desligar isolamento Apply/review. Dual-write T0–T17. `guard.py` `decide()` com needles deste card. Subir `maxConsecutiveWakes` como remédio. Reabrir Q1–Q4.

## Decisions

1. **Remédio = espera no turno, não acordar o idle.**  
   Host: pai idle + job done → `followup` no máximo 3 vezes; depois `inject` sem acordar até prompt humano. `maxConsecutiveWakes` é **rede**, não remédio (Q3=A: sessão ocupada). Alternativa rejeitada: subir o teto de wakes. Alternativa rejeitada: ligar Auto.

2. **`job_output wait`: reescrever timeout + loop no mesmo `execute`.**  
   Live: `wait: true` sem `timeout_ms` espera 30s e devolve `[status: running]`; cap 10 min < CI ~35 min — o modelo fecha o turno (852 T35). Plugin Guard, `tools/pre-execute`: se `job_output` e `wait === true`, reescrever `timeout_ms` para o cap alinhado (**40 min**, 2_400_000 ms) se ausente ou maior que o cap. `tools/execute`: depois de `next()`, se `wait` e o job ainda `running`, loop `ctx.jobs.wait` no **mesmo** execute até estado terminal (`completed`/`killed`/`failed`) **ou** teto total **45 min** (alinhado ao watcher `qa-gate`). Sessão permanece ocupada (busy) — notices do host entram por `inject`, não gastam o orçamento de wake. Preferir `inject: [..., "jobs"]`; se o fiber não arrancar, Apply falha-aberto no rewrite+cap (P3). MUST NOT `import` `@deepseek-ai/dsh-tool-jobs`. Alternativa rejeitada: só texto Moore a pedir wait (o modelo já fechou o turno). Alternativa rejeitada: poll/`sleep`.

3. **`agent/turn-stopping` `{ global: true }`: steer se ainda há trabalho do agente.**  
   Se o owner tem jobs `running`/`stopping` **ou** filho isolado ainda vivo, `payload.agent.steer(...)` com notice plugin (`source.kind="plugin"`, `form="notice"`, `summary` ≤120) a mandar `job_output wait: true` — o turno **não** fecha. Sem jobs/filhos pendentes: **não** steer (gates humanos podem idle: Aprovação de Design, Em Refinamento sem Alan ter arrastado). `{ global: true }` — listener host sem global MUST NOT ser o aceite (mesmo furo de scope #817/#839). `inject()` MUST NOT ser o veículo de manter ocupado. Alternativa rejeitada: `completionDelivery: quiet` (piora o idle).

4. **Patch `tool-jobs`: cap alinhado; teto de wakes intacto.**  
   `.dsh/cordis.patch.yml` (overlay `--patch`, last-write do `config` da row):  
   `- id: tool-jobs` / `config.maxWaitTimeoutMs: 2400000`. **Não** alterar `maxConsecutiveWakes` (fica 3). `completionDelivery` permanece `wakeup`. `dsh_boot.sh` já copia linhas que não são `name:` dos dois plugins nossos — a row `tool-jobs` passa. Alternativa rejeitada: patch só do cap sem loop (CI >40 min ainda idle). Alternativa rejeitada: vendorar o pacote.

5. **Turno morto: um `{ kind: "retry" }`; segundo visível.**  
   `agent/request-error` (host **e** `attachAgentEffortGuards` no `agent.ctx`, prepend): classe `dsh_dead_turn` = resposta vazia (`EMPTY_RESPONSE` / content vazio), limite de uso (quota/usage-limit wording), sessão em falta no provedor (`SESSION_NOT_FOUND` / «session» missing). Set **distinto** do retry #817/#839. Primeira ocorrência → `{ kind: "retry" }`; segunda no mesmo agente → `next()` e o bloqueio é visível (notice ou erro de turno; não silêncio). MUST NOT loop. MUST NOT misturar com `dsh_reasoning_effort_none`. Alternativa rejeitada: retry ilimitado do `dsh-llm-retry`. Alternativa rejeitada: needles em `guard.py`.

6. **Moore QA + skill: um yaml, wording dsh no stub.**  
   `context_file[QA]` (núcleo, uma vez) passa a nomear os dois clientes numa linha curta, paging ≤20: Cursor/Grok filho QA lê checks / MUST NOT `process_event`; **dsh: root MUST NOT spawnar filho QA; espera `qa-gate` no turno (`job_output wait`, sem `continue`)**; pai T14 no mesmo turno do verde; primeiro reject ≠ fim. Skill `covenant-flow` seção QA dsh: acrescentar espera no turno / sem `continue` (já tem MUST NOT spawnar filho). Stubs `.dsh/skills/` ≤8, sem T0–T17. **Não** dual-write Σ. Alternativa rejeitada: segundo `context_file` só dsh.

7. **Goldens `import { apply }` do plugin; pin próximo após `v1.1.9`.**  
   W1: `job_output wait` ainda `running` após um wait host → `execute` **não** devolve até terminal ou teto 45 min. W2: `turn-stopping` com jobs running → `steer`. W3: sem jobs/filhos → **sem** steer. W4: `wait` sem `timeout_ms` → args reescritos com cap 40 min (30s default MUST falhar W4). W5: segundo `dsh_dead_turn` → `next()`, não terceiro retry. W6: `EMPTY_RESPONSE` primeira → `{ kind: "retry" }`. W7: `.dsh/` sem T0–T17; `guard.py` sem needles novos deste card; patch `tool-jobs` tem `maxWaitTimeoutMs` 2400000 e **não** sobe `maxConsecutiveWakes`. W8: F*/E*/G1 regressão. Mock append-inner + `{ global: true }`. Pin: `git ls-remote --tags`; próximo patch livre após `v1.1.9` (esperado `v1.1.10` se livre); rebase no tip; `implantar --pin`; `clients.dsh.auto: false`.

## Apply contract

- Ordem, só após `Status=Pronto para Dev` no **mesmo** chat `#858`, filho Apply (pai `iniciar_apply` antes do spawn). Zero produto UI. Design **não** aplica.
- (1) `dsh_plugin_lib.js`: classificador `dsh_dead_turn` + handler um-retry; helper de loop `jobs.wait` / leitura de status do result `job_output`; MUST NOT `import` `@deepseek-ai/dsh*`. (2) `.dsh/plugin/process-fsm-guard.js`: `tools/pre-execute` rewrite `job_output` `timeout_ms`; `tools/execute` loop no mesmo turno; `agent/turn-stopping` `{ global: true }` steer se jobs/filho pendentes; retry morto no host e no `agent.ctx`; `inject` MAY ganhar `"jobs"`. (3) `.dsh/cordis.patch.yml`: row `- id: tool-jobs` / `config.maxWaitTimeoutMs: 2400000` (não mexer `maxConsecutiveWakes`). (4) `.cursor/process-fsm.yaml` **só** stub `context_file[QA]` (não transitions/Σ/`enabled_tools`). (5) `.cursor/skills/covenant-flow/SKILL.md` QA dsh: espera no turno / sem `continue`. (6) goldens W1–W8 `import { apply }` do plugin + regressão; `pytest scripts/process-fsm` sem GitHub. (7) origin tags + rebase + tag livre após `v1.1.9` + `implantar --pin` Cripto.
- MUST NOT: `guard.py` `decide()` needles deste card; dual-write T0–T17; vendor DeepSeek; Auto; `backend/` / `frontend/src/`; Cursor/Grok/OpenCode; 3080 systemd; `AGENTS.md` a crescer; HTML / `DESIGN.md` de produto.
- Homologação (DoD humano, **não** substitui W*; bloqueia Auto): dump autenticado `http://127.0.0.1:3080` de um closeout de QA com várias esperas seguidas **sem** prompt `continue`. Filho a devolver e reenvio após turno morto podem ser dumps à parte. Homologação ≠ `./restart`; 3080 ≠ systemd; cwd = `canonical_paths.dev`.

## Risks / Trade-offs

- [`jobs` no `inject` do Guard atrasa/bloqueia o fiber] → fail-open no rewrite+cap 40 min; W1 ainda exige o loop quando `ctx.jobs` existe. P3 Apply.
- [Steer em todo `turn-stopping` prende gates humanos] → W3: só com jobs/filho pendentes. Em Refinamento / Aprovação de Design sem trabalho do agente continua idle.
- [Loop 45 min segura a GUI se o check nunca acaba] → teto 45 min; depois o result `running` chega ao modelo; Moore: pending espera e repete T14; sem loop infinito.
- [Host `maxConsecutiveWakes=3` ainda corta se o turno fechar] → aceite é W1+W2 ocupado; wakes são rede. MUST NOT subir o teto.
- [Patch `config` substitui o objecto inteiro da row] → só `maxWaitTimeoutMs`; zod do host preenche o resto. MUST NOT mandar `maxConsecutiveWakes: 99`.
- [Retry `dsh_dead_turn` vs quota terminal] → um reenvio (Q2=A); segundo visível. Não é `dsh-llm-retry` unbounded.
- [Homologação `:3080` ≠ worktree] → dump é Apply/homologação; goldens não substituem.

## Migration Plan

Aditivo sobre `v1.1.9`. Ordem Apply: lib + goldens W4/W5/W6 → plugin rewrite/loop/steer/retry + W1–W3 → patch `tool-jobs` + W7 → stub Moore QA + skill + paging ≤20 → regressão W8 → origin tags + pin Cripto. Rollback = pin `v1.1.9`. Sem banco. Sem rebuild frontend. Homologação = dump `:3080`.

## Open Questions

Nenhuma bloqueante (Q1–Q4 fechadas no issue). Residuais P3: inject `jobs`; envelope `summary` no steer; dump `:3080` ≠ worktree.

## UI impact

UI impact: none

## live_route

live_route: N/A — GUI dsh :3080 é dump de homologação vendor, não rota de catálogo Cripto

## surface

surface: N/A — harness dsh; sem tela de produto a clonar

## Prototype

N/A — `UI impact: none`. GUI dsh é vendor/homologação dump, não superfície Cripto. Sem rota de catálogo emprestada. Sem HTML. Sem `DESIGN.md` de produto. Sem pipeline Impeccable visual. Playwright desta coluna = N/A.

## Prototype Validation

N/A — sem superfície visual de produto. Aceite = dump dsh `:3080` + goldens W1–W8, não um protótipo HTML.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Snapshot Impeccable = N/A justificado (sem tela Cripto; crítico desta rodada verifica tokens, não um snapshot visual).

## Design Critique

- P0: nenhum
- P1: nenhum
- P3 (aceites, detalhe de Apply — não reabrir como P0/P1): hooks `tools/pre-execute` / `tools/execute` / `agent/turn-stopping` `{ global: true }` / `agent/request-error`; classificador `dsh_dead_turn`; `timeout_ms` cap 40 min + loop `jobs.wait` 45 min no mesmo execute; `inject` MAY `"jobs"` (fail-open se o fiber não arrancar); envelope steer notice `summary` ≤120 (`inject()` não ocupa); patch `tool-jobs` `maxWaitTimeoutMs: 2400000` sem subir `maxConsecutiveWakes`; goldens W1–W8 `import { apply }`; pin próximo após `v1.1.9`; dump `:3080` ≠ worktree
- Prototype: N/A — `UI impact: none` (GUI dsh vendor / dump `:3080`; sem HTML; sem `DESIGN.md` de produto)
- Snapshot: N/A
- Design Agent verdict: PASS
- Spawns: 2 (1 autor + 1 crítico; teto sem-tela 1+1+1; sem rework)
