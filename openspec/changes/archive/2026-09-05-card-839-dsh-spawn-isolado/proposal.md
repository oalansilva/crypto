## Why

O spawn de filho isolado (`subagent` / `subagent_fork`) nesta sessão dsh nasce, entra em `turn/start` e morre no step 1 com 400 `INVALID_REQUEST` (`"reasoning.effort" does not support "none"`). O pai persiste `reasoningEffort: "high"` e completa; o filho persiste só `{provider, model}`. O driver mapeia o `kind` para `stopReason: "error"` sem copiar a mensagem, e o pai vê só `Error: subagent run failed` — sem `Diagnostic`. O #817 (Homologado, pin `v1.1.8`) sanitiza no `ctx` do plugin host depois de `next()`; no live do filho o header continua sem `high` e o retry não disparou. Enquanto o spawn não volta, Design/Apply/Review/QA ficam inoperantes (#837 parado com `ERROR` explícito). Card [#839](https://github.com/oalansilva/crypto/issues/839).

## What Changes

- Sonda mínima `PROBE_OK` em background e foreground MUST completar; `send_message` no filho retomado MUST devolver resultado ao pai (D2 no mesmo `agent.ctx` em **todo** turno — o `execute` de `send_message` sucede; o 400 live é o settlement, não um throw).
- O pedido do filho isolado MUST sair com esforço aceite (não `none` / campo ausente). Testemunha: o pai já envia `high`.
- Corrigir o residual live do #817 no caminho do **filho**: o sanitizer MUST ganhar no `agentCtx` isolado **depois** (e por fora) de `installModelSelection`, não só no mock waterfall do `apply()` host. `inject=["systemPrompt","skills"]` + `ctx.on("agent/request")` no host **não** basta — não repetir esse desenho.
- Falha real de run MUST subir `stopReason` + texto do provider (`Diagnostic`) ao pai no seam **live**: settlement `source.kind="subagent-settled"` (`followup`/`steer` após `turn/end`; `Background subagent … failed` / `It left no closing message.`). Classe 400 de esforço, se voltar, MUST ser nomeada (`dsh_reasoning_effort_none`) — não o genérico `subagent run failed` e **não** `Agent.inject()` como veículo. `session/event` MUST `{ global: true }` (presence-only ainda filtra).
- Canal = pele `covenant-flow` (plugin Guard + `dsh_plugin_lib.js`). Sem vendorar `@deepseek-ai/dsh*` / `pi-ai`. Sem perfil `~/.dsh/settings.yaml`. Sem trocar o modelo. Sem bypass de coluna. Sem o pai escrever artefato de filho.
- Pin produto = **próximo patch livre após `v1.1.8`** (Apply confere origin; Design não crava tag). Overlay `clients.dsh.auto: false`. Homologação: dump autenticado `:3080` de um spawn isolado (Design-autor **ou** sonda `PROBE_OK`) no mesmo tipo de modelo (testemunha `muse-spark-*`).

## Capabilities

### New Capabilities

- (nenhuma) — o spawn isolado e o sanitizer de esforço já são pele do quarto adapter em `process-harness`; este card fecha o furo live no filho e a opacidade do erro, não um quinto cliente nem spec de produto.

### Modified Capabilities

- `process-harness`: o Guard dsh instala o sanitizer de esforço **no `agentCtx` de cada agente** (incluindo filho isolado) de forma a ficar *outer* ao strip de `installModelSelection`; goldens MUST exercitar host vs `agentCtx` isolado (o mock E3–E8 do #817 permanece regressão, não o aceite deste furo). Falha real do filho MUST chegar ao pai no settlement `subagent-settled` com `stopReason` + `Diagnostic` (texto do `turn/end`); classe 400 nomeada; `session/event` `{ global: true }`. `guard.py` `decide()` **não** ganha esta regra.
- `covenant-flow`: pin **próximo patch livre após `v1.1.8`** (origin 2026-09-05: `v1.1.8` ocupado; Apply confere de novo) copia plugin/lib + goldens novos; `install.sh --pin` continua a copiar `.dsh/`; `SCHEMA_MAJOR` / `CLIENT_KEYS` inalterados; `clients.dsh.auto: false`. Sem reabrir #817 / #818 como trabalho. Sem linha nova no `AGENTS.md`.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` — `.dsh/plugin/process-fsm-guard.js`, `scripts/process-fsm/dsh_plugin_lib.js` (attach no `agentCtx` + store `turn/end` `{ global: true }` + `followup`/`steer` no pai + formatter `Diagnostic`/`stopReason`), goldens F1–F8 em `scripts/process-fsm` que **não** são o waterfall same-ctx do #817 nem throw-only, pin-tests para a tag que Apply cravar. Depois `implantar --pin` no Cripto.
- Não toca `backend/` / `frontend/src/` de produto, `process-fsm.yaml`, `guard.py` `decide()`, `.cursor/hooks.json`, `dsh_stubs.py`, `AGENTS.md` (substância/tamanho), perfil `~/.dsh/settings.yaml`, monorepo DeepSeek, Clara/Hermes, board/issue #837, #817/#818 como trabalho.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Clone gate isento (`surface: new` / `live_route: N/A`).
- Origem: issue #839. Homologação: dump autenticado `:3080` de um spawn isolado; goldens pytest **não** substituem o dump; 3080 ≠ systemd; homologação ≠ `./restart`.
