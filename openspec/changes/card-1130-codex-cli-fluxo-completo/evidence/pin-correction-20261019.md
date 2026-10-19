# #1130 — correção reconciliada do pin v1.1.23, 19/10/2026

Implementação e testes em árvore descartável, com delta aplicável ao núcleo. Não é uma publicação, novo pin, trust, Review/QA de produto ou aceite nativo. As sete tasks de aceitação permanecem abertas (19/26), conforme `phase-resolution.md`.

## Base e causa

Base publicada: `v1.1.23` = `c10fb7cf50bb09c87f7da8734f92688df8b1b789`, árvore `740ca48994b452c642807cc87eb166261ba688e1`. Comparação com o consumidor pré-pin `cfaa6d949614b8d9b43b906e6b758530a5ef1287` mostrou que a publicação carregou versões anteriores de módulos compartilhados. O pin substituiu hardening/Claude existente, enquanto acrescentava o suporte terminal #1130. Não foi revertido o pin: as funções genéricas foram reconciliadas sobre a tag, preservando os módulos modernos e a autoridade externa.

O candidato fica em `.cursor/tmp/card-1130-pin-correction/candidate`; base imutável extraída por `git archive` e aplicação de conferência ficam nas pastas irmãs `base` e `applied-check`. Nenhum checkout do núcleo foi editado. O checkout dirty #1098 não foi usado. O diretório histórico `implementation/nucleus/` permanece intacto.

## Os 13 achados corrigidos

| Achado original | Correção no núcleo candidato | Cobertura |
| --- | --- | --- |
| P1: agente podia gravar trust | `cf_shim.py`: recusa por identidade/env/process tree de agente e confirmação digitada em terminal | `test_cf_shim`, `test_account_install`, `test_claude_account_trust` |
| P1: entrypoints/modules fora do digest | Digest A inclui bytes e configuração executada | `test_cf_shim`, `test_account_install` |
| P1: claims CF_SHIM viravam revisão | `claude_trust.py` reabre registro, shim, manifesto e digest atual; env é apenas claim | `test_claude_account_trust` |
| P1: Claude no terminal Cursor ficava sem hooks | Identidade Claude prevalece sobre CURSOR_* herdado | `test_cf_shim` |
| P1: dependências executáveis sem cobertura | Walker acompanha symlinks internos, recusa escape/loop, inclui node_modules e bytecode solto; manifesto falha se não puder digerir arquivo listado | `test_cf_shim`, `test_account_install` |
| P1: resume/compact apagava âncora R | Heartbeat preserva digest/recorded_at inicial; acompanha roots/pins sem reancorar | `test_cf_shim`, `test_claude_desktop_surface` |
| P1: retorno background perdido | `claude_evidence.py` coleta task-notification vinculada a agentId/tool-use-id, resultados e falha/interrupção; par vem dos turnos reais | `test_claude_desktop_surface`, `test_claude_evidence` |
| P1: mcp__ccd_* fora da interceptação | Matcher ancorado de conta e classificação de ferramentas desktop; sessão/rota não classificada recusa com card | `test_claude_desktop_surface`, `test_account_install` |
| P1: superfície claude-desktop removida | Driver/receipt/proxy/handoff preservam superfície, versão da sessão/app e SSH; sem fallback para binário do PATH | `test_claude_desktop_surface`, `test_claude_proxy` |
| P1: piso de hooks bloqueantes removido | `claude_hook_check` exige ≥ 2.1.295; piso de esforço continua 2.1.292 | `test_claude_desktop_surface`, `test_model_selection`, `test_claude_process_event` |
| P2: instalador desapareceu do diff | `materialize_review_diff.py` restaura --nucleus/--nucleus-base e composição de install.sh | `test_residual_1101` |
| P2: route-landmarks virou código do adapter | `adapter_manifest.py` restaura exclusão de dado e fixtures; catálogo continua consumer-owned | `test_account_install`, `test_codex_installer` |
| P2: harness apontava hooks do projeto | `.cursor/rules/harness.mdc` descreve conta → shim → adapter pinado | `test_rules_and_runbook_text` |

Também foram preservadas funções compartilhadas pré-pin: sinks/heredocs do Guard, pasta desktop sem card, avisos de pins mistos, remoção idempotente dos registros da conta e falha de import do OpenCode sem bloquear leitura. O provider `github_status_provider` atual com autoridade explícita foi mantido dentro do Guard reconciliado; `process_event.py` e `process_authority.py` permanecem byte a byte da tag. As adições #1130 não foram substituídas por versões pré-pin.

Os testes desktop/residuais/runbook já presentes na árvore da tag, mas removidos do consumidor pelo pin anterior, foram exercitados. O teste de instalação limpa exige que a distribuição entregue esses arquivos e o teste novo. O instalador passa a distribuir também a documentação Claude e recusa colisão desse destino com `overlay_doc`. Não foi necessária uma nova árvore paralela de adapters.

## Dois residuais prévios

1. `codex_review_session.binding(complete=True)` exige um preflight nativo bem-sucedido em **context, probe e review**, antes de todos os nascimentos da fase, no mesmo turno. Confere ready/phase/work_release/coordinator, ordinais, metadata nativa dos spawns e fontes; conserva essas referências na cadeia. A projeção dos spawns usa o formato canônico das fontes do coletor, evitando colisões de snapshot. Preflight posterior, ausente, falho, em outro turno ou com release divergente recusa. A onda real anterior não é reinterpretada.
2. `codex_binding.mutation_paths` identifica executáveis e operadores em segmentos reais, preservando aspas até a classificação. `rg "cp.*" scripts` e exemplos citados não viram mutação. Alvos de cp/mv/install/tee/touch/mkdir/rm/truncate, edições in-place e redirecionamentos reais continuam vinculados a roots/card. Mutação dinâmica, wrappers com código mutante, shell cwd alterado, symlinks de escape e targets de outro card continuam recusados. O Guard compartilhado permanece ativo.

## Condução de leitura

As ondas históricas falharam por reconstrução manual do path de leitura, com `../..` nos chunks 18 e 17. O verificador estava correto ao recusá-las. O candidato mantém argv literal e fornece a cada resposta `next_read_command`, com helper/plano relativos ao cwd nativo e comando mais curto. O prompt manda copiar literalmente o retorno anterior, passar o workdir exato e validar índices consecutivos; `null` só termina a última parte. O template fica informativo. O probe continua primeiro/único, sem escrita nos comandos de leitura.

O coletor agora exige também ordem consecutiva dos chunks. Não aceita paths equivalentes, repetição do probe, comandos combinados, manifesto/resumo em lugar do diff, saída truncada ou leitura fora do turno/cwd. Mantém SHA, bytes integrais em CommandExecution **e** no retorno entregue ao modelo, deny/readback, isolamento/read-only, TTL de 120 segundos, seleção, autoridade externa e verify-wave no principal. Não houve aumento de budgets.

Fixtures positivas: exatamente **900.641 bytes / 67 partes**, e **940.641 bytes / mais de 67 partes**, com verificação posterior das fontes. Negativas adicionais: path equivalente desviado, cwd errado, chunks fora de ordem, truncamento e next-command adulterado. Fixtures continuam diagnósticas, sem substituir a aceitação nativa do suporte após distribuição.

## Pacote e validação

Inventário completo, hashes SHA-256 base/destino e árvore Git equivalente: `../implementation/correction-v1.1.23/manifest.json`. Patch: `nucleus.patch`; reprodução: `README.md` e `package.py`; comandos, resultados e logs: `validation.json`/`validation-logs/`. O pacote não contém overlay nem manifesto ativo. `package.py` verifica a identidade de todos os blobs base, aplica `git apply --check` fora da descoberta Git ancestral, aplica realmente numa cópia limpa e compara toda a árvore resultante com a candidata testada.

| Identidade final | Valor |
| --- | --- |
| Arquivos do delta | 34 (23 restaurações exatas pré-pin; 11 reconciliações/adições) |
| Patch / tamanho | `d0d2b61213c8b7d585e7e72c147d64e94feb684649297cf6a847d5468de1ce38` / 240731 bytes |
| Árvore Git equivalente testada/aplicada | `45ac0dbd0333c1b453f06f397a41c156a03e7567` |
| apply-check / aplicação real / comparação integral | PASS / PASS / idêntica |

| Grupo verificado | Resultado sem somar reexecuções |
| --- | --- |
| Compartilhados, Guard, conta, Claude, autoridade, controller/índice e instalação | 762 PASS + uma falha documental inicial; rechecagem 54 PASS/3 skips cobre a correção (763 casos únicos verdes e 3 skips) |
| Sessão dedicada | 154 PASS antes de uma asserção com código esperado antigo; rechecagem 15 PASS cobre a falha e os dois últimos casos (157 casos únicos verdes) |
| Entrega/probes/controller Review | 74 PASS |
| Regressões novas | 44 PASS na execução inicial; positivos grandes e parser final rechecados: 47 casos únicos verdes no inventário final |
| Compatibilidade adicional | 178 PASS |
| Distribuição | 15 PASS; após o último ajuste do parser, adapters/instalação 42 PASS (sobrepostos, sem soma) |
| Sintaxe install.sh / OpenSpec strict | PASS / PASS |

As execuções iniciais e rechecagens não são somadas: a suíte compartilhada inicialmente teve uma falha documental, corrigida e revalidada; a suíte do coordenador inicialmente teve uma asserção esperando o erro antigo em origem falsa, atualizada para a recusa antecipada. Os comandos e resultados individuais permanecem no registro, inclusive essas falhas. Warnings do pytest referem-se a opções de plugins não instalados herdadas do consumidor; três skips são asserts específicos de consumidor no checkout genérico do núcleo.

## Fontes históricas preservadas

| Fonte em `.cursor/tmp/card-1130-delivery/` | SHA-256 |
| --- | --- |
| consumer-pin-reviewer-payloads.json | e077efd26a769c995297808380d085fdba0902483cb31e21accc0fb3d305dc21 |
| consumer-closing-reviewer-payloads.json | 2ef533735c4e9c7ff04ecf7ca0afb199196af5bcf847248dbbc904bc7dd10d82 |
| consumer-closing-retry-payloads.json | 41fa5b7d962d42d7f1ad4454b69c96dbccee829b1b9540789fbd8bd8ba20cfde |
| consumer-finalization-handoff.json | bd62ccfd24b40d046d9b21246b98ddc4aa446c5404a0ca145642e97b1e40058a |

Nenhuma captura, trace, payload ou fonte de onda falhada foi alterada ou promovida. Os 10 P1 + 3 P2 continuam registrados com a severidade original, agora com correção candidata rastreável.

Os hashes ativos foram conferidos antes/depois e permaneceram idênticos: manifesto `5f5adce1df4840723e1d87537e91b1caa48e14aaa0d15d24f2e9af783654d1cc`; codex_review_probe.py `413d37b8bf5d49132320ee4304d3b8e9a5f74af5dec986bfb8b5581be1cc836d`; codex_review_session.py `e5dd7bf77578c64fc94a3d21e0e2d093741ece8f80efd3987411cf0a168c26d9`; codex_binding.py `13115941c4a23ae9b4a0aecfcfe8e65d1645218deba2624a26463eb08d9db4d5`. Status Git final contém apenas o pacote e este relatório novos. Núcleo continua limpo.

## Handoff e pendências reais

O pai ainda precisa aplicar no núcleo sob binding nativo próprio, conduzir os gates de distribuição/review, publicar revisão real, pinar no consumidor e obter a revisão humana pertinente. Só então pode ensaiar nativamente a nova condução e concluir os aceites de fases/raízes/rotas que faltam. Não existe nova tag, commit ou trust gravado por este filho. O código ativo do consumidor permanece no HEAD local informado `c3a89e3bb904da21e3ca1d0dd5fa1bd6f9cc292b`; publicação não é bloqueio de implementação deste pacote.

Nascimento Apply informado pelo pai: captura `.cursor/tmp/card-1130-delivery/correction-apply-20261019.capture.json`, receipt `.cursor/tmp/codex-evidence/0d8b36ec-af55-4800-9760-9f12141c546b.birth.json`. Requested: gpt-6.1-sol/high. Observed não foi inferido; coleta/runtime/proxy pertencem ao pai após o retorno. Nenhum agente adicional foi criado neste Apply.

proxy modelo: apply-coluna → GPT-6.1 Sol (gpt-6.1-sol), esforço solicitado high; observado aguarda coleta nativa do pai. Proxies desta correção: zero spawns adicionais; HTML gerado/copiado N/A (UI impact none); design.md não foi alterado.
