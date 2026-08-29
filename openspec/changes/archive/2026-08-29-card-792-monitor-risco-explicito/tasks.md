# Tasks: Card do Monitor — risco explícito (card #792)

> Fonte: proposal + design § Apply contract. Skills: `covenant-flow` (runbook), `design-critic` (gate), `github-project-board` (Status). Só após `Status=Pronto para Dev` (T7).

## 1) Frontend — bloco de risco explícito em HOLD

- [x] **T1 — `OpportunityCard.tsx`: estender `<dl class="kv">` para HOLD com hierarquia risco**
  - `resolveOpportunitySignal` → badge `Compra/Venda`; quando `is_holding=true` e `stop_price`/`entry_price`/`distance_to_stop_pct` top-level presentes, renderizar na ordem `distância até saída` (`distance_to_next_status`), `distância até stop` (`distance_to_stop_pct`), `stop` (`stop_price`), `alvo` (derivado quando confiável), `entrada` (`entry_price`), `preço atual` (`last_price`). Formatar USD com `priceString` (2–8 casas) e % com `toDisplayValue(…,2)` → 2 casas. Quando qualquer campo for null/undefined/stale renderizar literal `indisponível — dado não confiável` (nunca `-`, `N/A` ou backfill de outra timeframe). Adicionar `data-testid="monitor-risk-block-<symbolKey>"`.
  - Critério: Given HOLD com stop/alvo no payload, When vê card, Then distância+stop+alvo visíveis sem abrir gráfico (critério #1).

- [x] **T2 — Frase de cenário condicionada**
  - Renderizar "se o preço cruzar $X, a leitura de posição deixa de valer" só quando houver dado comprovado (`stop_price` do payload ou invalidação de `signal_history[].explanation.summary`). Usar `stop_price` como âncora numérica. Não renderizar quando dado ausente/não confiável.
  - Critério: #5.

## 2) Frontend — EXIT sem ressuscitar Entry/Stop

- [x] **T3 — EXIT: esconder Entry/Stop operáveis e mostrar risco residual**
  - Gate existente `showEntryStopRows = section !== 'exit' && !hasExitedOpportunity(opportunity)` mantém-se; em EXIT não renderizar `entry_price`/`stop_price` como operáveis. Mostrar bloco "Risco residual" com mensagem `posição encerrada segundo a estratégia — sem risco residual mapeado` quando `signal_history` vazio (len 0), senão mostrar risco residual derivado do histórico (último EXIT/ENTRY). Copy exata do issue.
  - Critério: #3.

- [x] **T4 — Coerência com modal do gráfico**
  - Espelhar mesma hierarquia/copy no `ChartModal.tsx` para o mesmo payload: badge `Compra/Venda`, distância relevante, stop/alvo ou indisponível, frase de cenário só com dado, EXIT sem Entry/Stop operáveis. Não reintroduzir Entry/Stop em EXIT.
  - Critério: coerência card↔modal.

## 3) Frontend — proteção de segredo e formatação

- [x] **T5 — `is_strategy_protected=true` não vaza segredo**
  - Risco continua lendo apenas top-level `stop_price`/`entry_price`/`distance_to_stop_pct`; não tocar `opportunity.parameters`/`indicator_values` quando protegido. Comum e admin ambos respeitam.
  - Critério: #6. Validar `strategy_secret_visibility.py` já preserva top-level.

## 4) Validação

- [x] **T6 — Playwright + unit: 5 cenários do issue**
  - HOLD com dados → risco visível; HOLD sem dados → `indisponível — dado não confiável`; EXIT vazio → mensagem sem risco + sem Entry/Stop; EXIT com histórico → risco residual; protegido não vaza `parameters`. Cobrir #1–#6 e roteiro #75 (tester aponta onde dói sem operador).

## Notas de implementação

- Backend sem mudança de contrato: `opportunity_service.py` já entrega top-level; `strategy_secret_visibility.py` já filtra.
- Não entra: Kelly, colocar stop na Binance, Sharpe/SQN, Telegram #747, trailing, backfill placeholder.
- Rollback: reverter `OpportunityCard.tsx` ao `<dl>` anterior.

> `UI impact: affected` — aguardar crítica PASS + `process_event submeter_design` antes de Apply. TAREFA só fecha com código + evidência vs protótipo (#530).
