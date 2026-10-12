# Verification Report: card-1080-modelos-locais

Verificação pela skill canônica `openspec-verify-change`, em 2026-10-09. Change explícita, schema `spec-driven`; proposal, design, nove delta specs e tasks lidos. Consumer funcional `697247bd63377db84c3a5bc4baf9a2859683825a`; nucleus `d807a4965a7fe7b3dca9d820ec46cbbb14c6f19c`, confirmado pela PR. Este fechamento altera apenas tasks/evidência, sem código, sync, archive ou transição.

## Summary

| Dimension | Status |
| --- | --- |
| Completeness | 16/16 tasks; 23 requisitos mapeados; task4.4 fechada no escopo explicitamente autorizado |
| Correctness | 23 requisitos / 31 cenários com anchors de implementação e cobertura de contrato; limites runtime abaixo |
| Coherence | Arquivo por conta/máquina, política versionada, capturas e falha fechada seguem o Design; gates preservados |

`verification-mapping.json` lista cada requisito/cenário, path/linha da spec e anchors existentes de implementação/testes. `qa-closeout.json` registra a matriz runtime, fontes e manifesto SHA-256 dos artefatos duráveis em `qa-runtime/`. Cobertura de contrato não é execução nativa positiva. Testes anteriores foram consultados como evidência, não repetidos neste fechamento documental.

## Checks executados

- `openspec status --change card-1080-modelos-locais --json`: contexto repo-local e artefatos completos.
- `openspec instructions apply --change card-1080-modelos-locais --json`: 16/16 e `all_done`. Advertência preexistente de configuração: rules de tasks devem ser array de strings; não invalida o resultado e não foi corrigida fora do escopo.
- `openspec validate card-1080-modelos-locais --strict`: PASS.
- `openspec validate --all`: 208 passed, 0 failed. Nenhuma divergência legada encontrada pelo validador.
- `review_process_checklist.py` no root absoluto do consumer, com `--wave-same-turn yes --phase postqa`: PASS, exit0. Same-turn é sustentado pela onda nativa existente; nenhuma nova revisão foi criada neste fechamento.
- `validate_capture` e `model_proxy.evidence` revalidaram Cursor, Grok e os dois reviewers Codex: quatro provas positivas com successful=true.
- `stub_errors()` de Grok/dsh/OpenCode: listas vazias.
- SQLite OpenCode consultada via `mode=ro`: zero sessões identificadas por directory/title/slug card1080 e descendentes; nenhum todo pendente associado. Sessões não identificáveis por esses campos não são abrangidas pela consulta.
- CI original consumer: 14 PASS / deploy-staging skipped no SHA697247bd, incluindo qa-gate e Playwright. CI do próximo commit documental deve ser conferida pelo pai; não é atestada antecipadamente.

## Runtime e limites

| Cliente | Resultado | Prova / limite |
| --- | --- | --- |
| Cursor CLI 2026.10.01-e373342 | PASS generalPurpose + deny nativo | Filho composer-2.5 observado em providerOptions.cursor.modelName da própria resposta/DB; completed e payload. Captura ausente recusada antes de nascimento. CLI/generalPurpose observado; named Task/Desktop+SSH não foram observados nesta QA. |
| Codex CLI 0.162.0 | PASS onda existente | Dois filhos gpt-6.1-sol/high, metadata própria, sandbox read-only, completed/payload e mesmo diff SHA. Review não repetido. |
| Grok Build 1.0.25 | PASS | Filho01a11e0f-7ca0-71f0-85ee-266fcbb553e1: own current_model_id=grok-4.6; own usage backend=grok-4.6-build; 1 modelCall; completed/exit0/payload LOCAL_SELECTION_PROBE_OK. Identificador selecionado e backend de usage são dados distintos preservados. Esforço separado not_applicable no spawn; high do host não vira argumento configurável. Permissão pontual, sem auto/bypass/confiança persistente. |
| dsh 0.1.5-rc.2 | waived_by_user, NÃO PASS | [Dispensa explícita de Alan](https://github.com/oalansilva/crypto/issues/1080#issuecomment-6071728818). Resultado anterior QUOTA antes do spawn; observed unavailable, payload=false; adapter/testes mantidos. |
| OpenCode 1.18.32 | DENY residual, NÃO PASS positivo | Schema task sem provider/model/variant explícitos preservando lifecycle/permissões/retorno. Recusa antes de criação prevista no Design/spec; cobertura positiva permanece pendente, não simulada. |

Fonte QA final: `/tmp/card1080-qa/qa-report.md` e `qa-summary.json`; digest da summary e metadata filtrada estão no pacote durável. Nenhum transcript/thinking copiado. Settings dsh e seleção local preservados, conforme `qa-runtime/account-preservation.json`. Capturas conservam source_sha256 `6167e38fd93f8f00577de4adab6f73ab0c0f6942d72f610e85e989d78eabe9c4`.

## Coherence e gates

`design.md` declara UI impact:none, live_route:N/A, surface:none e Design Agent verdict:PASS. Não há task UI/protótipo entregue a comparar; comparação visual é N/A por escopo, não skip silencioso. Snapshot Impeccable não foi lido.

As PRs [crypto1081](https://github.com/oalansilva/crypto/pull/1081) e [covenant-flow6](https://github.com/oalansilva/covenant-flow/pull/6) foram conferidas read-only após atualização do pai: ambas listam change, design.md/verdict PASS, UI impact:none e T8. [Design/crítica](https://github.com/oalansilva/crypto/issues/1080#issuecomment-6068828360) e `design-gate-evidence.json` sustentam o gate. Trace autoritativo registra T8 Pronto para Dev→Em desenvolvimento em 2026-10-08T21:03:50.521Z; prova do estado, sem inferir ator a partir do evento.

Captura por nascimento, releitura por filho/onda, proibições versionadas, ausência de fallback e pin sem escolhas locais seguem o Design. Os seis testes reais de installer no nucleus estão em `apply-resume-checks.json`; skips consumer não são contados como execução do installer. A correção provider/variant e variant opcional foi validada na rodada mecânica consumer58/nucleus36; não alterada aqui.

Histórico preservado: `apply-resume-checks.json` e os parágrafos históricos de tasks descrevem tentativas iniciais sem login/filho. A matriz final QA supersede somente esse estado de cobertura. Specs/Design não foram relaxados. Dispensa dsh altera apenas o ensaio deste card, sem remover requisito/adapter e sem declarar sucesso runtime.

## Issues by priority

CRITICAL: 0. Nenhuma task pendente ou requisito de implementação ausente identificado neste escopo; descrições das PRs incluem evidência de gate.

WARNING: 2 limites de cobertura positiva preservados:

- Cursor: execução nativa comprovada apenas CLI/generalPurpose. Antes de declarar named Task/Desktop+SSH positivos, executar esses caminhos e registrar metadata/payload próprios; os testes de contrato atuais não substituem essa prova.
- OpenCode: cobertura positiva pendente na versão1.18.32. Antes de declará-la, versão/API deve preservar semântica task e passar ensaio nativo explícito; a recusa atual satisfaz o ramo fail-closed aprovado.

dsh: ensaio positivo dispensado explicitamente neste card, portanto não é task pendente nem PASS; trace ausente permanece unavailable. SUGGESTION: 0.

## Final assessment

Nenhum issue crítico. Implementação/tarefas verificadas no escopo autorizado, com os dois limites de cobertura e a dispensa dsh acima. Evidência pronta para o pai conduzir os gates restantes. Não houve archive; disponibilidade técnica não concede autorização de FSM, integração, release ou homologação.
