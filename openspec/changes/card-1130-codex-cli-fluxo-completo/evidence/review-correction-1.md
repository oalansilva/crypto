# #1130 — primeira correção após T10

Pai confirmou retorno oficial T10 → Em desenvolvimento, mantendo o único Apply e sua captura/birth originais. A onda `7bf356e19cca59aa59b4ae63` produziu um P1 verificado do code-reviewer: o controller solicitava `route-check` antes do lançamento bootstrap; `binding()` precisava desse lançamento e recusava `review_launch_source_unavailable`, que não era a recusa `review_route_unqualified` necessária. O avanço seguinte não alcançava a preparação automática. O outro reviewer falhou com `Selected model is at capacity`, sem payload: onda incompleta, não segundo achado nem evidência de contexto excedido.

## Correção no candidato inativo

`implementation/nucleus/scripts/process-fsm/codex_terminal_review.py` agora retorna primeiro o comando de lançamento bootstrap. Com eventos disponíveis, exige `binding(..., complete=True)` antes de solicitar/aceitar o comando nativo de recusa de rota. Só a resposta `blocked/review_route_unqualified` permite avançar a contexto/probes/qualificação. Ausência/saída parcial de lançamento continua em recuperação finita e não vira recusa válida ou relançamento automático.

`test_codex_terminal_review.py` acrescenta regressão parametrizada TUI/exec a partir de checkpoint vazio. Ela usa os helpers reais `verify_route`, `binding`, contexto/probe/qualificação e verify-wave sobre fontes controladas: antes do lançamento, observa `review_launch_source_unavailable`; completa a fonte de lançamento; observa a recusa correta; registra esse retorno calculado pelo helper e percorre contexto/probe/review até verificação final. A preparação do pacote que o controller já criou é reutilizada pelo construtor da fixture, sem substituir as funções sob teste. O teste antigo de eventos parciais deixa de inventar uma recusa para poder alcançar essa falha. São fixtures de contrato, não qualificação viva do candidato ou de principal exec.

Nenhum arquivo ativo, source ou nucleus foi alterado por este filho. O worktree nucleus limpo preparado pelo pai, HEAD `14aa9d6`, e o bundle combinado são responsabilidades do pai; a base dirty #1098 de procedência permanece preservada. Este filho regenera apenas o pacote inativo e seus patches, sem aplicar nenhum deles.

## Gates preservados

Tasks 3.4/3.5/4.3/4.4/5.5 continuam abertas em after-pin; 6.1 after-commit e 6.2 after-qa. O faseamento não muda com essa correção. A nova onda de Review sobre os bytes corrigidos, dois payloads, verify-wave e checklist pré-commit continuam obrigação real do pai. Nenhum resultado de teste substitui o reviewer que não retornou payload.

Os 639 PASS e a suite posterior 16 PASS do relatório são históricos, anteriores a estes bytes. A verificação desta correção está registrada separadamente abaixo; não são reutilizados como execução dos arquivos novos.

## Verificação dos bytes corrigidos

- Suite focada `python3 -m pytest -q .cursor/tmp/card-1130-candidate-test/scripts/process-fsm/test_codex_terminal_review.py`: **7 PASS, 4 avisos, 120,84s**, exit0. Inclui as duas regressões novas e o teste de eventos parciais atualizado.
- Regressão ampliada dos arquivos `test_codex_qualification_index`, `test_codex_terminal`, `test_codex_terminal_install`, `test_codex_refinement_binding`, `test_codex_evidence`, `test_codex_context`, `test_codex_review`, `test_codex_review_probe`, `test_codex_review_session` e `test_review_process_checklist`: **439 PASS, 4 avisos, 236,92s**, exit0. Não inclui novamente o arquivo da suite focada. Log privado `.cursor/tmp/card-1130-correction-1-regression.txt`, SHA `623c958982023bc97d60276c7c5c2236d985ace2c1f20a31942e2700ffd15d5f`.
- Quatro avisos conhecidos de opções de configuração pytest não instaladas; nenhuma falha ou skip nessas execuções. Os testes exercitam cópias descartáveis; não ativam hooks/trust ou constituem QA de produto.
- `openspec validate card-1130-codex-cli-fluxo-completo --strict`: PASS. `git diff --check`: PASS nos arquivos rastreados; Python alterado parse PASS. Candidato novo também foi verificado pelos patches com `git apply --check --whitespace=error` na origem e consumidor reais, ambos PASS sem aplicar patch.
- A barreira real de tasks permanece precommit `None`; postcommit bloqueia 6.1, postpin/postqa bloqueiam 3.4 e strict bloqueia tasks pendentes. Isso não é checklist completo/verify-wave.

Uma tentativa opcional de gravar projeção adicional de metadados dos comandos foi recusada antes da execução pelo hook: `evaluation_error / unsupported_targets: dynamic mutation or changed shell directory cannot be verified`. Nenhuma projeção foi criada ou alegada; não se contornou a recusa. O log já existente foi conferido por leitura suportada (`sha256sum`), e os retornos nativos originais dos testes permanecem as fontes. Essa recusa de coleta auxiliar não é falha dos testes ou bloqueio do controller.

## Artefatos finais do candidato

| Artefato | SHA-256 / tamanho |
| --- | --- |
| `implementation/package.json` | `de599a368b2b2d8214906af0ec1d28690cff4701d576ac449db2c02fe6d7e5af` |
| `.cursor/tmp/card-1130-delivery/nucleus.patch` | `2e7047ed3346704dc5af394346ca7f7bb7e35c2aabf22651846784028a82efd3`, 110308 bytes |
| `.cursor/tmp/card-1130-delivery/consumer.patch` | `c6ae9c2bc30234701d602cd3b21d66b837d38a8ec9cdcad7eabf354571b1e8b4`, 114434 bytes |
| `scripts/process-fsm/codex_terminal_review.py` candidato | `8f6eaaee1caae21a5ecc4ebc32dbf8e97283e6a4c9b23d29ed14e41dbccbaf67`, 9394 bytes |
| `scripts/process-fsm/test_codex_terminal_review.py` candidato | `1bd891dd190abc7dde4c0e01d75dcfa0b5104b222ee73aec86e6c64eef57ccea`, 7201 bytes |

Build repetido após os testes confirmou os mesmos digests e ambos apply-check PASS. Pacote continua com 16 arquivos distribuíveis; todos os 16 arquivos do candidato e da árvore efetivamente testada coincidem com o inventário do pacote. Links/whitespace e manifesto ativo PASS na conferência final. Manifesto ativo conserva SHA `3a90add2ddffa07963d28196b495e3ff435356a2d6a980c7e1a33d63dc28e0cb`; `codex_evidence.py` ativo conserva SHA `79fc746a254f64987c7aa3686584921a2df083f446e6376410075042a42d375e`. Não há nova revisão/tag/pin, instalação, trust, evento, spawn ou mutação Git por este filho.
