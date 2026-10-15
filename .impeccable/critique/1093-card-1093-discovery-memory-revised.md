# Snapshot Design Critique revisado — #1093

Data: 2026-10-13. Nova entrada em Design por mudança explícita de escopo de Alan: incluir a correção da estratégia original e completar a busca. Rodada desta revisão: 1 autor + 1 crítico; nenhuma nova rodada solicitada. Este snapshot substitui o parecer anterior somente quanto à avaliação do escopo ampliado e não certifica a implementação parcial.

## Estado, autorização e evidências

Issue https://github.com/oalansilva/crypto/issues/1093 relido via REST, com escopo atualizado. GraphQL pontual confirmou Project 1, Status=Design. Branch/worktree: `card-1093-discovery-memory`, `/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory`.

Skills aplicadas: `.cursor/skills/design-critic/SKILL.md` e `.cursor/skills/covenant-flow/SKILL.md`, canônicas já lidas nesta sessão. Ownership desta continuação: somente este snapshot. Nenhuma alteração em código, OpenSpec, serviços, banco ou Status; nenhum spawn, teste ou nova consulta ao DEV.

Pacote relido: proposal, design, tasks, deltas combo-optimizer/discovery-sweep/discovery-resource-budget e `.openspec.yaml`. Fatos técnicos consultados: `apply-evidence.md`, fixture `backend/tests/fixtures/discovery_memory/original_template.json` e trecho de `backend/app/strategies/combos/combo_strategy.py::_evaluate_logic_vectorized`. O strict PASS da revisão foi informado pelo pai; não foi reexecutado pelo crítico.

O worktree contém alterações parciais de Apply, preservadas integralmente. O documento de evidência registra 3/22 tasks anteriores completas, unit nova apenas versionada, worker DEV antigo parado, reprodução integral ainda pendente e teste de filho perdido acima do prazo. Nenhuma dessas evidências anteriores equivale à validação do novo binding.

## Análise do contrato revisado

1. Escopo: a exceção à equivalência estrita está explícita no proposal, design e delta normativo. A política alcança somente `long_ma_pullback_rsi_adx`, condicionada à declaração original de uma instância RSI e uma ADX sem alias, ambas originalmente de período 14. Não altera templates persistidos nem amplia a heurística global. Thresholds, MA/pullback, stops, direção, fórmulas, custos, grid e normalização continuam preservados.
2. Defeito factual: a fixture original usa RSI_14 nas expressões de entrada e saída e ADX_14 na entrada, enquanto o schema admite períodos 10..20. No avaliador atual, a validação de identificadores desconhecidos ocorre antes da compatibilidade de períodos; logo a análise de ordenamento descrita no Design corresponde ao código lido. O ensaio anterior 10/10 inválido e 14/14 válido foi documentado pelo Apply; esta crítica não o repetiu.
3. Resolução: vincular símbolos inteiros à identidade original do produtor antes dos overrides e antes da validação evita inferência por nome de coluna ou primeira instância. A política especifica séries físicas preservadas, mesmo binding RSI em entrada/saída, colisões e ausência/ambiguidade como erros determinísticos. RSI_140/ADX_99 não recebem remapeamento por semelhança. Aliases estáveis, referências literais não abrangidas e outros templates mantêm semântica.
4. Compatibilidade: cálculo final, holdout, Deep/fallback e demais consumidores do template recebem a mesma política. O transporte de identidade original e inclusão de política/binding/parâmetros efetivos na chave de cache evitam que a correção exista somente no caminho de otimização ou reutilize máscaras de períodos diferentes. O contrato cobre explicitamente A→B→A e eviction.
5. Efeito observável: candidatos antes inválidos agora podem gerar sinais/trades/métricas; vencedor e GO/NO-GO podem mudar pela busca completa. Isso é informado como efeito sujeito à aprovação do Design, sem alegar equivalência com resultado anterior incompleto nem reescrever histórico. O cálculo TA-Lib de cada período não muda; muda a série à qual o símbolo da expressão se refere.
6. Baseline: 14/14 e outros casos válidos exigem igualdade histórica exata; candidatos restaurados usam oracle independente TA-Lib que não chama o resolver novo. Todos os pares do grid, períodos mistos, thresholds, warm-up, entrada/saída, holdout e cache estão previstos. A busca completa compara ranking contra a referência corrigida integral. 492.480 é R1, seguida das rodadas restantes, não um atalho de aceite.
7. Contenção: permanecem cgroup DEV 5/6 GiB, swap 512 MiB, um worker, LRU agregado 64 MiB compatível com #1091, spool limitado, três tentativas duráveis, reconciler externo, fencing e contadores. Erro de referência é calculation_error determinístico e não consome retries operacionais adicionais nem produz vencedor parcial. Nenhum teto foi ampliado para acomodar o defeito de cleanup observado.
8. UI: `UI impact: none`, `live_route: N/A`, `surface: none` continuam em linhas próprias. A mudança é computacional e altera dados resultantes, sem redesenho de tela/copy/componente. A mensagem de intervenção permanece no canal operacional previamente definido; não foi prometida nova superfície visual.

## Design Critique

- P0/P1/P2: nenhum achado de produto, escopo ou contrato visível na revisão.
- P3 — Detalhe de Apply: concretizar o transporte da identidade original/política por todos os consumidores e sua participação nas chaves de cache; os testes de 6.3 devem provar aliases, colisões e A→B→A, além de final/holdout. Disposition: aceito, já coberto pelo contrato e pelas tasks 6.2–6.3.
- P3 — Detalhe de Apply: manter separado o oracle corrigido independente do resolver e a baseline histórica 14/14; provar pares do grid e busca completa sem reutilizar saída antiga incompleta. Disposition: aceito, já coberto por 6.1/6.4 e 5.1/5.4.
- P3 — Defeito conhecido de Apply: filho perdido levou cerca de 30 s, acima do teto contratual de 20 s. Disposition: pendente em 3.2/5.3/6.5; aceito como trabalho de Apply, sem bloquear o Design nem relaxar o aceite de implementação. Cleanup de spool/órfãos e goldens de LRU/ordenação anteriores continuam pendentes conforme tasks.
- Disposition: aprovado com P3 aceitos para Apply; nenhuma correção obrigatória de Design ou nova rodada. Aprovação humana do escopo revisado e transição autorizada continuam necessárias antes da implementação.
- Verdict: APPROVED_WITH_ACCEPTED_P3.

## Metadata e limites de confiança

Papel: design-critic; faixa: juízo. Captura original mantida nesta continuação: `/tmp/card-1093-design-critic-birth-20261013.json`; attempt_id `158ef54a-d7ca-4ec4-8d21-9c834e9bc4dc`; capture_sha256 `2d6f234bcb266bcd76f65cb3ad0645eda69e69104fb811ca93c966c3623a9468`. Requested: GPT-6 Astra (`gpt-6-astra`), effort `medium`.

Observed anterior informado pelo pai a partir do trace real: `gpt-6-astra`, effort `medium`, Codex CLI `0.162.1`, session id `01a132e1-3267-7060-aa5b-05ee59863071`, agent_path `/root/design_1093_critic`, sandbox `danger-full-access`. Trace: `/home/ubuntu/.codex/sessions/2026/10/13/rollout-2026-10-13T01-29-41-01a132e1-3267-7060-aa5b-05ee59863071.jsonl`. O pai informou `verify_continuation` PASS sobre essa evidência e retorno anterior completed com payload. A verificação do retorno/runtime desta continuação pertence ao pai; o crítico não infere metadados observados da configuração.

proxy modelo: design-critic → GPT-6 Astra (gpt-6-astra)

Spawns pelo crítico: 0. HTML generated/copied: N/A. Sem novos testes. Este parecer aprova o contrato para submissão à aprovação humana, não declara Apply concluído, homologação, instalação da unit ou publicação.
