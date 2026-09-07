## Why

Na GUI dsh (`http://127.0.0.1:3080`) o fluxo pára no meio do caminho e Alan precisa escrever `continue` / `nada ainda?` / `concluiu?` quando o próximo passo ainda era do agente — espera de check, filho a devolver, integrar após verde. Evidência: sessão 852 turno 35 (watch do CI em fundo, turno fechado, UI idle, job vivo); 853/854 (cadeia de `continue`, limite de uso, resposta vazia, sessão em falta no provedor). Auto continua desligado; gates humanos não entram.

## What Changes

- Qualquer momento em que o próximo passo ainda é do agente: a GUI **não** fica idle à espera de `continue`; a sessão permanece **ocupada** até esse passo decidir (check longo inclusive).
- Se mesmo assim parar, a sessão volta sozinha mesmo depois de várias esperas seguidas — sem `continue`.
- Turno morto no provedor (limite de uso / resposta vazia / sessão em falta): um reenvio automático; segundo falhanço visível; sem loop.
- Moore `context_file[QA]` deixa de falar só em «filho QA lê checks»: no dsh o root **MUST NOT** spawnar filho QA; closeout no mesmo turno do verde.
- Auto permanece desligado. Isolamento Apply/review permanece. Gates humanos (priorizar, aprovar design, homologar) continuam a exigir Alan.
- Pin produto = próximo patch livre após o pin live `v1.1.9`, depois `implantar --pin` no Cripto. Sem vendorar o runtime DeepSeek. Sem mudar as 12 colunas/eventos. Sem produto `backend/` / `frontend/src/`. Sem Cursor/Grok/OpenCode como alvo.

## Capabilities

### New Capabilities

- (nenhuma) — o quarto adapter dsh e o closeout de QA já existem em `process-harness` / `process-fsm` / `covenant-flow`; este card fecha o idle visível na GUI `:3080` e o stub Moore que ainda descreve filho QA.

### Modified Capabilities

- `process-harness`: no dsh, enquanto o próximo passo ainda é do agente (espera de check, filho a devolver, integrar após verde), a sessão MUST permanecer ocupada (espera no turno); `maxConsecutiveWakes` do host é rede, não remédio; turno morto no provedor = um reenvio, segundo falhanço visível, sem loop; `guard.py` `decide()` MUST NOT ganhar needles deste card.
- `process-fsm`: `context_file[QA]` MUST nomear o closeout dsh no root (MUST NOT spawnar filho QA; espera `qa-gate` no turno) sem adicionar estado, evento ou `enabled_tools`; paging continua ≤20 linhas.
- `covenant-flow`: pin = próximo patch livre após `v1.1.9`; skill QA dsh MUST dizer espera no turno (sem `continue`); `clients.dsh.auto: false`; dual-write T0–T17 em `.dsh/` continua proibido.

## Impact

- Apply (após Pronto para Dev, mesmo chat `#858`): `.dsh/plugin/process-fsm-guard.js`, `scripts/process-fsm/dsh_plugin_lib.js` se preciso, `.dsh/cordis.patch.yml` (config `tool-jobs`), `.cursor/process-fsm.yaml` só o stub Moore `QA` (não Σ/T0–T17), `.cursor/skills/covenant-flow/SKILL.md` seção QA dsh se o stub yaml não bastar, goldens pytest `import { apply }` do plugin, pin `oalansilva/covenant-flow` + `implantar --pin` no Cripto.
- Não toca `backend/` / `frontend/src/`, `guard.py` `decide()`, colunas/eventos, Auto, runtime DeepSeek, Cursor/Grok/OpenCode, porta 3080 em systemd.
- `UI impact: none`. Prototype N/A. Snapshot Impeccable N/A. Homologação: dump autenticado `:3080` de um closeout de QA com várias esperas seguidas **sem** prompt `continue`; filho a devolver e reenvio após turno morto podem ser dumps à parte. Pytest não substitui o dump.
- Origem: issue #858 (Q1–Q4=A, 2026-09-07). Este Design não reabre as Qs.
