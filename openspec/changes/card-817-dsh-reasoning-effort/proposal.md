## Why

Na sessão dsh `session-679a762b` o pedido ao modelo enviou esforço de raciocínio `none`; o modelo do chat recusou (400 `"reasoning.effort" does not support "none"`). O turno 9 do root (`implemente`) acabou em `INVALID_REQUEST`; Apply e o par reviewer nasceram e fecharam no step 1 sem ferramenta nem mensagem de fecho. O perfil local já mapeia `off: null` e o default do agente é `high` — mesmo assim filhos e o turno 9 enviaram `none`. P0: parte o contrato dsh (filho isolado) **e** o turno do root (Q1=A). #518 cobre o relato do spawn vazio, não a causa. Card [#817](https://github.com/oalansilva/crypto/issues/817).

## What Changes

- Pedido ao modelo: **não** enviar o valor de esforço de raciocínio que o modelo do chat recusa (Q2=A: qualquer modelo desta sessão dsh que recuse esforço desligado — testemunha `muse-spark-*`, não o recorte). Mapeamento na **pele** `covenant-flow` (plugin Guard + `dsh_plugin_lib.js`), **não** no perfil `~/.dsh/settings.yaml` (já insuficiente) e **não** vendorando o runtime.
- Forçar um valor aceite (`high`, o default do agente e o testemunho do turno 10). Omitir o campo **não** é o conserto: `installModelSelection` do runtime **apaga** esforço herdado quando o filho só traz `agentProvider`+`agentModel`; o default do fornecedor volta a `none`. Filhos MUST herdar o esforço aceite do root; se o root não tiver um aceite, mapear para `high`.
- **Q1=A:** a mesma recusa **não** mata o turno do root. `agent/request-error` desta classe faz **um** retry do **mesmo** pedido do agente (já sanitizado), não um spawn novo.
- Depois do **primeiro** 400 desta classe no turno: **não** spawnar mais filhos com o mesmo preset; registar `ERROR: subagent spawn failed/empty` e continuar no root com residual explícito. O retry 1/1 do #518 **não** se aplica a esta classe (repetiu o mesmo 400 e ainda nasceu o par reviewer cadáver).
- Caminho feliz: spawn Apply isolado e o par reviewer isolado entram em `turn/start`, correm ≥1 ferramenta e deixam mensagem de fecho. Fallback no root **não** é o caminho feliz.
- **Q3=A:** dump autenticado `:3080` de **um** spawn Apply ou reviewer isolado no mesmo tipo de modelo (filho trabalha; zero recusa desta classe nesse spawn). Golden pytest MAY e **também** entra no Apply; **não** substitui o dump.
- Fonte no produto `oalansilva/covenant-flow` tag **`v1.1.7`**; Cripto pin depois. Overlay live `pin: v1.1.6`. Sem vendorar `deepseek-harness`. Sem reabrir #790 / #782 / #784 / #786 / #518 / #569. Sem `process-fsm.yaml` / Σ / colunas. Sem produto UI. Sem Auto dsh. Sem deny global de todo `subagent`. Sem recortar só `muse-spark-*`. Sem deixar o 400 do root fora.

## Capabilities

### New Capabilities

- (nenhuma) — sanitizar esforço de raciocínio no pedido dsh é pele do quarto adapter já descrito em `process-harness`; este card fecha o 400 desta classe, não um quinto cliente nem spec de produto.

### Modified Capabilities

- `process-harness`: plugin dsh sanitiza `reasoningEffort` / `reasoning.effort` em `agent/request` (depois de `await next()`, para ganhar ao strip de herança do runtime) e recupera o turno do root em `agent/request-error` desta classe com um retry do mesmo pedido. Depois do primeiro 400 desta classe no turno, `tools/pre-execute` deny de `subagent` / `subagent_fork` adicionais (mesmo preset). Write deny e grill-shaped deny #786 não regridem. `guard.py` `decide()` **não** ganha esta regra.
- `covenant-flow`: pin **`v1.1.7`** (patch após `v1.1.6`) copia plugin/lib + goldens; `install.sh --pin` continua a copiar `.dsh/`; `SCHEMA_MAJOR` / `CLIENT_KEYS` inalterados; `clients.dsh.auto: false`. Uma linha no runbook dsh: após 400 desta classe, não spawnar mais o mesmo preset; residual #518 no root.
- `cursor-code-review`: no dsh, 400 desta classe **não** consome o retry de spawn do #518; o par reviewer não nasce depois do primeiro cadáver. Cursor/Grok 1 retry de spawn vazio permanece.

## Impact

- Altera (Apply, após Pronto para Dev): produto `oalansilva/covenant-flow` (tag `v1.1.7`) — `.dsh/plugin/process-fsm-guard.js`, `scripts/process-fsm/dsh_plugin_lib.js` (helper de sanitizar + classificar 400), goldens `test_dsh_adapter.py` / novo ficheiro se o Apply fatiar, uma linha em `.cursor/skills/covenant-flow` no ramo dsh. Depois `implantar --pin v1.1.7` no Cripto.
- Não toca `backend/` / `frontend/src/` de produto, `process-fsm.yaml`, `guard.py` `decide()`, `.cursor/hooks.json`, `dsh_stubs.py`, `AGENTS.md` (substância/tamanho), perfil `~/.dsh/settings.yaml` como canal de pin, monorepo DeepSeek, Clara/Hermes.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A.
- Origem: issue #817. Homologação: dump autenticado `:3080` (Q3=A); goldens pytest **não** substituem o dump; 3080 ≠ systemd; homologação ≠ `./restart`.
