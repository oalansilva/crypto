# Snapshot Design Critique — #1086

Data: 2026-10-13. Papel: design-critic. Rodada: 1 crítico, sem tela; nenhum rework solicitado.
Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1086-donchian-rompimento`.
Branch observada: `card-1086-donchian-rompimento`. Status Design informado pelo orquestrador; este filho não consultou nem alterou o board.

## Metadata de execução

- model_selection_capture: `/tmp/card-1086-design-critic-birth.json`
- attempt_id: `a7cee64e-d258-4431-935e-5c1cd3254ed2`
- requested_model: `gpt-6-astra`
- requested_reasoning_effort: `medium`
- requested_label: `GPT-6 Astra`
- observed_model: `unavailable`
- observed_reasoning_effort: `unavailable`
- host: Codex Agent, conforme contexto disponibilizado; versão: `unavailable`.
- runtime_verification: `unavailable`; a captura prova somente a seleção solicitada. O parecer de produto abaixo não comprova aprovação de gate que exija identidade runtime observada.
- Payload: parecer registrado neste snapshot e retornado ao pai. Status final do host deve ser coletado pelo pai; não inferido aqui.

## Fontes e limites

Leitura REST ao vivo de `repos/oalansilva/crypto/issues/1086`, incluindo Problema, História, Entra e Não entra. Leitura integral de proposal.md, design.md, tasks.md e specs/discovery-catalog-selection/spec.md da change. Conferidos os pontos pertinentes em `backend/app/strategies/combos/combo_strategy.py`, `backend/app/services/combo_optimizer.py`, `backend/app/startup_seed.py`, `backend/config/combo_templates_export.json`, `backend/tests/unit/test_card_1074_combo_templates.py` e `backend/tests/unit/test_combo_strategy_logic_parser.py`.

Este parecer avalia Design; não executou backtest, seed, escrita em banco ou teste de produto. `validate --strict PASS 4/4` foi informado pelo autor, não repetido pelo crítico. Nenhuma alteração em OpenSpec, código ou estado; escrita limitada a este snapshot.

## Rubrica do contrato

| Critério | Avaliação |
| --- | --- |
| Briefing preservado | PASS: proposal copia Problema, História, Entra e Não entra do issue, incluindo compra real, negativos e limites de escopo. |
| Canal anterior | PASS: dc_upper.shift(1) corresponde a N máximas imediatamente anteriores; evita mudar as bandas compartilhadas e a saída. |
| Volume existente | PASS: preserva SMA, multiplicador 1,2 e volume atual; exemplo 19×100 + 200 em janela 20 produz média multiplicada 126. Igualdade é negativa pela comparação estrita. |
| Compra efetiva | PASS: exige ComboStrategy e extrator real, operação long/Comprar com tempo e preço na abertura t+1, saída posterior controlada e caminhos fast/legacy. |
| Negativos | PASS: fechamento igual/abaixo, máxima isolada acima, volume insuficiente/igualdade e warmup estão cobertos. Refinamento de asserções é P3 abaixo. |
| Causalidade | PASS: exclui máxima atual, altera futuro e compara decisões/sinais até t+1; preço só comparado com abertura t+1 fixa, sem exigir igualdade artificial dos lucros futuros. |
| Timeframes | PASS: 4h, 1h e 15m parametrizados para positivos/negativos e causalidade; outro N exigido, sem fixar timeframe no template. |
| Preservação | PASS: bandas, saída, stop loss, optimization_schema e demais templates explicitamente preservados; thresholds, taxas, slippage e promoção fora do delta. |
| Catálogo existente | PASS: startup_seed já chama upsert para donchian_volume_breakout em catálogo populado; carga inicial e atualização idempotente previstas. Estratégias salvas e resultados históricos não são reescritos. |
| Parser de superfície | PASS: `UI impact: none`, `live_route: N/A` com justificativa e `surface: none` em linhas próprias; não empresta rota do catálogo. |

Nielsen, personas, browser, clone e protótipo: N/A; nenhum contrato de tela/copy/interação foi alterado. HTML gerado/copied: N/A. A mudança observável é a entrada do backtest, devidamente especificada.

## Achados

- P0: nenhum.
- P1: nenhum.
- P2: nenhum.
- P3: detalhe de Apply — nas fixtures negativas, verificar ausência do sinal de compra em t+1 além de ausência de trade encerrado, ou garantir fechamento posterior de qualquer entrada indevida. O extrator só retorna posições encerradas; lista vazia isolada poderia esconder uma compra ainda aberta. O contrato já exige ausência de entrada, portanto isto apenas concretiza a asserção, sem mudar produto ou pedir rework.
- disposition: aceitar P3 como detalhe de Apply na seção de crítica do design; nenhuma nova rodada necessária.
- verdict: PASS para conteúdo do Design; zero P0/P1 abertos. Verificação de modelo runtime permanece unavailable e não deve ser promovida a PASS pelo parecer de produto.

## Complemento de evidência do orquestrador — 2026-10-13

A indicação anterior de unavailable descreve a informação disponível no retorno do agente. A inspeção posterior dos traces locais recuperou a comprovação, sem alterar o parecer de conteúdo.

- design-autor: `gpt-6-astra/medium`; Codex `0.162.1`; completed com payload; proxy successful=true.
  - child_id: `01a132f8-fd75-7c72-97e9-ac8ce44b129e`; turn_id: `01a132f8-fd9c-7490-aac8-ce218b6edd25`.
  - trace: `/home/ubuntu/.codex/sessions/2026/10/13/rollout-2026-10-13T01-55-41-01a132f8-fd75-7c72-97e9-ac8ce44b129e.jsonl`.
  - SHA-256: `52a68f6d0192761d39c503b4e120790384d46f3b65c9b1207160a7ab4ea5e02a`.

- design-critic: `gpt-6-astra/medium`; Codex `0.162.1`; completed com payload; proxy successful=true.
  - child_id: `01a132fe-31cb-7e80-b4b7-ec198775ee3e`; turn_id: `01a132fe-31f4-7683-b0a6-48d175368c1b`.
  - trace: `/home/ubuntu/.codex/sessions/2026/10/13/rollout-2026-10-13T02-01-22-01a132fe-31cb-7e80-b4b7-ec198775ee3e.jsonl`.
  - SHA-256: `bbddb311d2bb754c4a36499347bf44d946762b8895dbacb49b43c96bdfa6fcf5`.
