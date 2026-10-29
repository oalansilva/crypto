# #1098 — correção CI e reconciliação factual da CLI, 18/10/2026

Entrada Em desenvolvimento informada pelo pai após T13 `falha_codigo`, sem novo T8. Base `c0328af5872c2b75ceb787423a28f4c1e443d527`, PR #1129. Filho único desta entrada: `apply_coluna_1098_ci_fix`, thread `01a14f64-7148-79f1-a3f1-0b4a2aca5447`, captura `fb0104d1-83bf-47da-815c-54935a99bc6e`. Este filho não executou transições, commit/push, novos agentes, instalação, trust ou alteração de conta/permissões.

## Correção determinística

- `test_paging.py` passa a exigir o contrato vigente: principal gravável, coordenador dedicado automático read-only desde o nascimento, cadeia autoritativa, dois papéis/perfis no mesmo turno, mesmo diff/SHA, seleção capturada, deny/readback, ambos payloads e coleta/gates posteriores. Conserva a ordem e a página Cursor; recusa regressão para `/permissions` manual.
- O runbook substitui somente a frase ambígua de hook de projeto pela cadeia registro na conta → shim → adapter pinado, preservando pins antigos e as duas revisões de confiança. `test_rules_and_runbook_text.py` permanece intacto.
- `python3 -m pytest -q scripts/process-fsm/test_paging.py scripts/process-fsm/test_rules_and_runbook_text.py`: **37 passed, 4 warnings, 1.00s**. Os avisos são opções pytest indisponíveis no ambiente. Não se repetiram a suíte inteira nem os 148 testes anteriores. A primeira execução focada encontrou uma string incorreta no novo assert (`não pedir` versus `nem pedir`), corrigida antes do resultado final.

Nenhum executável do adapter mudou. Manifesto SHA-256 `3a90add2ddffa07963d28196b495e3ff435356a2d6a980c7e1a33d63dc28e0cb`; `adapter_manifest.py check` PASS. Adapter Codex A `41dddd4aa190e08307cd92f71139447bd342bcddf8f6b3d7466a1431f09d3f3a`, missing/divergent vazios, reviewed=true em leitura. Os dois arquivos corrigidos estão fora do manifesto; não requerem novo registro de trust.

## Procedência e patch pendente do nucleus

O nucleus está fora do binding autorizado deste filho. Sua cópia dos dois arquivos ainda coincide byte a byte com a base consumidora anterior à correção. Não se tentou escrever fora do binding ou usar rota alternativa. O patch revisável [ci-contract-nucleus-20261018.patch](ci-contract-nucleus-20261018.patch), SHA-256 `b11760dcba3f447a0089a705935e87c1af80a23c2c92fa7b47db3ab6848672d9`, contém somente as duas correções. Sua aplicação no contexto autorizado do nucleus e a conferência de redistribuição permanecem pendentes; esta entrada não alega procedência nucleus → consumidor concluída para esses bytes novos.

| Arquivo | Nucleus/base consumidor | Consumidor corrigido |
|---|---|---|
| `.cursor/skills/covenant-flow/SKILL.md` | `4e17711d1b1621ff278d0aeb320cf0a55bdb1b0f849588ce600b32797916bba4` | `9f4a33da3265bf72ba5b9ce36724d2eb8e8fbcab70eb6749d8fec109496f09be` |
| `scripts/process-fsm/test_paging.py` | `cbc099cb4c0cf1d3b57da4872a1a357a37e2c0117997c1b4825ebd46c1d974f7` | `fe64b74260b901082ad5f1f4535a9e0d7bcc6be4ff4b1053324f127f10eff6e0` |

## Aceites 5.2 e 5.4

**5.2 — recusa real atual:** a qualificação `dedicated-route-1490b149f6c8155e486a13dadec2ccaca0b6b4c756bebf0abc647ecc870ca97f.json` referencia `refusal_source` ordinal zero-based 8124 (linha 8125), raw SHA-256 `1e03f350402eeb66d5860886bc7fc6d27633b565a684af7d26e33adcc20bfd86`. Este filho revalidou o hash da linha nativa exata. `CommandExecution` `exec-7951e1bd-685c-4035-b567-133dfb3a9505`: failed/exit1, worktree #1098, `blocked/review_route_unqualified`; faltava diagnóstico nativo completo dos papéis nomeados e da rota principal→exec antes de liberar a onda. A recuperação preservava artefatos e exigia qualificação diagnóstica sem produto/alternância de permissões. Diagnóstico posterior não transforma essa tentativa em etapa concluída; não houve substituição por sessão externa nessa recusa.

**5.4 — onda real final:** pacote `60cd4f791012e6671a56dcf9`, selo `9cfc4798266158c4330fee7ea3c5a450764e08df830f33765c9ece9fdb4678d2`; principal TUI `01a14a14-8ad0-78b2-8278-c14aec2b4bf8` → coordenador exec `01a14f45-de41-7df3-8d8e-819f6c5a3fa0` → dois filhos distintos no turno `01a14f4f-c150-79b1-99cd-4e1efe5b30c3`. Diff completo de 809505 bytes, 60 páginas 0–59, SHA-256 `7115a1abb2a2439ac047582f8bdbd9cca9b1e1198f2a5dd2374ea38d7a3c791e`; fechamento informado idêntico pelo pai. Não houve alternância manual.

| Papel | Thread | Selo da evidência sanitizada |
|---|---|---|
| diff-reviewer | `01a14f50-6c3a-7b42-abde-ae58d56101a6` | `359403dc5e2814f6cc4b2c0c9a456d1f7987e45508ff344149282448c4d92cfe` |
| code-reviewer | `01a14f50-b20a-7292-805d-9d3c02697ba4` | `9e3e95ba9111ccb5f5c7f3fac3835b7ac8d8501818bbb2ebcbd21dc4cf6884d7` |

Ambos registros finais: validation=verified, completed/payload, codex_exec/0.163.0, gpt-6.1-sol/high solicitado/observado, fork_turns=none, read-only contínuo, diff_read e write_denial_readback verificados. QA conferiu essas projeções; o pai informou `verify-wave` e checklist precommit PASS, também registrados no comentário do card. Este filho confirmou os arquivos/selos e não repetiu coletores/probes. O aceite desta onda não atribui seus bytes revisados ao delta CI posterior; os gates do delta cabem ao pai.

## Matriz de 5.7: positivo atual e negativos com origem explícita

O positivo repetido após adaptação é a onda final acima, sobre a versão final dos executáveis. O delta desta entrada afeta teste/runbook, não esses executáveis. Atestação interna completa permanece unavailable. A matriz não afirma que todos os negativos sejam novas execuções reais atuais.

| Caso | Classe | Evidência / resultado |
|---|---|---|
| Rota ainda não qualificada | Real atual | Fonte nativa 8124 acima: `review_route_unqualified` antes da onda. |
| Contexto operacional ausente | Real histórico | [preflight-stage.json](preflight-stage.json), SHA `b1e11bb76272a0e5c34118bde0dbbe828814056cf0af48133bd049c159818f1e`: `stage_capability_missing`, context_isolation e barreira diagnóstica unavailable; nenhum filho de etapa. Contrato histórico preservado, não requisito atual de atestação interna. |
| Contexto de revisão gravável | Real histórico | [preflight-review.json](preflight-review.json), SHA `cfb86f797cfa04ed6efe2bd17695ff4cbf9459f6b3bf8cb0bb21a91d9dbf53b0`: `parent_sandbox_mismatch`. A receita antiga não substitui o coordenador atual. |
| Vínculo incorreto por workdir/root | Real histórico | [shell-workdir-is-not-rebind.json](shell-workdir-is-not-rebind.json), SHA `ac93565e092180d1c86cf81706ecc6688fdaf9c51a3411f66e7c2dc9dabbfdfa`: `worktree_mismatch`, sem rebind nativo. |
| Origem/evidência ausente | Fixture de contrato | `test_codex_evidence.py::test_refusal_preserves_work_and_status` (fonte/call/terminal/payload ausentes), `test_codex_review_session.py::test_native_launch_source_missing_is_explicitly_unavailable`, `test_codex_review_probe.py::test_probe_requires_native_origin_and_all_bindings`. Não é telemetria viva. |
| Binding/card/turno incorretos | Fixture de contrato | `test_codex_evidence.py::test_preflight_host_schema_and_worktree` e `test_codex_review_probe.py::test_probe_requires_native_origin_and_all_bindings` (cwd/thread/turno/path/diff). |
| Modelo/esforço divergentes | Fixture de contrato | `test_codex_evidence.py::test_refusal_preserves_work_and_status` (requested/observed) e `test_divergent_continuation_cannot_reuse_old_proof_or_last_good_turn`; a continuação final correta não apaga a divergência. |
| Contexto insuficiente/divergente | Fixture de contrato | `test_codex_context.py::test_missing_divergent_contaminated_inputs_never_qualify`: controle ausente/incorreto, payload incompleto, sentinel devolvida/contaminação e fork divergente não qualificam. Nenhum marcador real é publicado. |

Os testes de contrato acima pertencem à suíte do job process-fsm auditado pelo QA: 1616 passaram e somente os dois contratos textuais reparados falharam. Não foram repetidos nem promovidos a ensaios vivos nesta reconciliação. Interrupção continua distinta de completed/payload. O QA nativo `01a14f5f-fa4f-7472-9f5a-addd96cf85f6` foi coletado pelo pai: lifecycle completed/payload, gpt-6.1-sol/high observado, evidence SHA `c7662fe2f403eca07da3f95d0d00f26f6abf980d28c1ddde8bc0d44274c7e186`; seu parecer reprova o CI da base, não é QA verde.

## 5.3 — fixture e alcance do ensaio observado

Fixture exclusiva e descartável: `backend/.pytest_cache/card-1098-guard-fb0104d1.txt`. Diretório/arquivo estavam ausentes; este filho criou somente o cache e `.gitignore` próprio (`*`) antes do arquivo. `git check-ignore -v` confirmou a exclusão. Não houve sobrescrita de trabalho alheio nem escrita em outro card/produto. O caminho pertence aos product_globs backend; o filho mantém contexto nativo #1098/Em desenvolvimento.

Fonte privada: `/home/ubuntu/.codex/sessions/2026/10/18/rollout-2026-10-18T14-22-25-01a14f64-7148-79f1-a3f1-0b4a2aca5447.jsonl`, turno `01a14f64-7170-7801-8cea-c9d3454da199`. Ordinais desta tabela são zero-based; hashes são da linha sem newline. Só metadados pontuais foram lidos, sem dump de transcript/C/S.

| Evento nativo | Ordinal | SHA-256 da linha | Observação |
|---|---|---|---|
| FileChange apply_patch | 118 | `7d6342b7f67900d4b9c9ce5d08e84a18b7d233920a716c85b910ee3b15e2c853` | completed; arquivo criado, readback inicial SHA `9868ab899a43f831ccb6efde4fca25cb02ee3155fdcc9748a48c59733ccc40e3`. |
| exec_command no worktree | 213 | `d3454bcb8b43d9308237da6c3380da42657e4b3791ec7bedd661e905ee5887b3` | completed/exit0; escrita estática somente na fixture, readback 218 SHA `59eca63019f7de1a9425999c52f524a08ca9dc9afd954e15a62ebd7e443e852c`. |
| exec_command workdir=/tmp | 223 | `a23469d435648c46f705243c89a2765a784a2dda843b4ae4744bc227e5cd29d7` | completed/exit0; alvo absoluto ainda era somente a fixture deste card autorizado, na mesma etapa. Readback 230 mostrou SHA `b2c6cc195fbe136479c01f1469fe2444eacface57d31cbd9b784ec21f7bdd7ba`. Isso não é tentativa de escrita fora do card/etapa. |
| Restauração da própria fixture no worktree | 235 | `57ae073f3cb55357ee644f77f7ffede64ba91b531ccec77809954df63a157861` | completed/exit0; readback final devolveu SHA `59eca63019f7de1a9425999c52f524a08ca9dc9afd954e15a62ebd7e443e852c`. |

Essas são chamadas reais do filho por `functions.exec` → `tools.exec_command`, não invocações sintéticas de adapter. O contrato não exige evento explícito `allow`; comportamento, contexto e deny/readback da mesma rota poderiam comprovar o Guard. O Design/spec separam identidade autorizada, workdir e alvos: neste caso, mudar somente o workdir não mudou o alvo absoluto nem a autorização do card/etapa. Portanto, essa execução não constitui o negativo fora do card/etapa exigido por 5.3 e seu exit0 não demonstra ausência de hook, falta de cobertura ou bug do Guard.

A leitura do código acrescenta uma expectativa condicional, não uma observação de runtime: `codex_binding.py::validate_context` recusaria um workdir resolvido fora da raiz com `worktree_mismatch` **se** recebesse esse `workdir` no payload normalizado do hook. `codex_adapter.py::pre_tool_use` chama essa validação antes das decisões Guard. O ensaio não capturou o payload entregue ao hook nem sua decisão; o CommandExecution isolado não permite concluir qual caminho do adapter foi executado ou a causa do resultado. O sucesso da escrita também não prova autorização pelo Guard. **5.3 permanece pendente** até positivo e negativos reais adequados fora do card e da etapa, com contexto e readback pela rota suportada/interceptada. Alterar adapter/conta/trust não está no escopo deste filho.

Receita segura para o próximo QA, somente após sua entrada real na etapa: registrar hash/readback e executar pela rota nativa cuja interceptação for comprovada `printf 'card=1098\nfixture=guard-stage-deny-fb0104d1\n' > /srv/apps/dev/criptofarol/crypto-worktrees/card-1098-codex-agentes-nativos/backend/.pytest_cache/card-1098-guard-fb0104d1.txt`. Exigir recusa real por etapa e readback/hash inalterados; se a rota executar, registrar falha de cobertura em vez de converter a execução em deny. Não forjar Status, alterar etapa para ensaio, tentar outro card real ou usar adapter sintético como observado. A fixture permanece ignorada para esse readback.

## Pendências e limites

5.1 aguarda observação real de Alan dos controles/lista/estado/inspeção/interação/retorno. 5.3 aguarda os negativos reais adequados: fora da etapa na entrada real de QA e fora do card em fixture segura autorizada. O ensaio workdir=/tmp não os substitui nem comprova defeito. 5.2/5.4/5.7 ficam reconciliadas com origens separadas, sem aprovação global de QA/Done. O pai conduz os gates/checks do delta e a coerência documental com o nucleus. Preservados os dois P2 residuais do comentário 6250926701 e o teto já consumido, sem reabertura. App/IDE/refinamento/matriz integral/principal exec independente seguem #1128.

Spawns deste filho: 0. HTML gerado/copiado: N/A. Proxy modelo solicitado: apply-coluna → GPT-6.1 Sol (`gpt-6.1-sol`, high), captura de nascimento preservada; observado/terminal deste filho cabem à coleta do pai após retorno. Nenhuma alegação Auto.
