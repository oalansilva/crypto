# Validação da Proposta: short-backtest-support

**Data:** 2026-01-31  
**Objetivo:** Validar a proposta (não a implementação) quanto a coerência, viabilidade e alinhamento com o código atual.

---

## 1. Resumo

| Critério        | Resultado |
|-----------------|-----------|
| Coerência       | ✅ Aprovado |
| Viabilidade     | ✅ Aprovado |
| Alinhamento     | ✅ Aprovado (com 1 correção pontual) |
| Completude      | ✅ Aprovado |

**Conclusão:** A proposta está **válida** e pronta para design/specs/tasks e implementação.

---

## 2. Coerência interna

- **Why:** Problema descrito de forma clara (apenas long hoje; necessidade de testar short com a mesma lógica).
- **What Changes:** 
  - Modo long permanece inalterado e como default → consistente.
  - Short = mesma lógica de sinais, interpretação invertida (entrada 1 = abrir short, saída -1 = fechar short) → correto e sem ambiguidade.
  - PnL/stop/take-profit ajustados para short → coerente com o modelo.
- **Capabilities:** Nova capability `backtest-direction` e modificação em `backtest-config` estão alinhadas com o escopo.
- **Impact:** Backend, frontend, API e templates descritos de forma consistente; explicitado que o template `multi_ma_crossover` não muda (apenas interpretação na execução).

Nenhuma contradição interna identificada.

---

## 3. Viabilidade técnica

Verificação no código atual:

| Ponto da proposta | Evidência no código |
|-------------------|---------------------|
| Sinais 1 = entrada, -1 = saída | `combo_optimizer.py` linhas 139 e 149: `row['signal'] == 1` (entrada), `row['signal'] == -1` (saída). `deep_backtest.py` 67–70: `signal == 1` (entry), `signal == -1` (exit). |
| Tipo de posição hoje fixo em long | `combo_optimizer.py` linha 146: `'type': 'long'`. `deep_backtest.py` linha 178: `'type': 'long'`. |
| PnL long (entry/exit, fees) | `combo_optimizer.py` 159: PnL long com fees. `deep_backtest.py` 164–167: mesmo modelo. |
| Engine só long | `src/engine/backtester.py`: apenas `position > 0`, compra em signal 1 e venda em -1. Proposta prevê extensão ou camada de tradução → viável. |

Conclusão: a proposta é **viável**; os pontos de extensão (parâmetro `direction`, tratamento de short em `extract_trades_from_signals`, `simulate_execution_with_15m`, e opcionalmente no engine) estão bem delimitados.

---

## 4. Alinhamento com o código (Impact)

- **Backend**
  - `BacktestService`: existe em `backend/app/services/backtest_service.py`; recebe `config` → adicionar `direction` é factível.
  - `ComboOptimizer`, `extract_trades_from_signals`, `simulate_execution_with_15m` (deep_backtest): existem e são os pontos corretos para interpretar `direction` e tratar short (sinal 1 = abrir short, -1 = fechar; stop acima da entrada; PnL short).
  - `src/engine/backtester.py`: hoje só long; proposta já considera extensão ou camada de tradução → alinhado.

- **Frontend**
  - Proposta cita “tela Configure Backtest (ex.: ComboOptimizePage.tsx ou equivalente)”.
  - **Correção:** A tela **Configure Backtest** corresponde a **`ComboConfigurePage.tsx`** (rota `/combo/configure`), título “Configure Backtest”. `ComboOptimizePage.tsx` é a tela de **otimização** (`/combo/optimize`). Ambas podem precisar do controle de direção (configurar e otimizar em long/short); recomenda-se citar ambas na spec/design: `ComboConfigurePage.tsx` para configuração do backtest e `ComboOptimizePage.tsx` para otimização.

- **API**
  - Payloads de backtest/otimização/batch: novo campo opcional `direction: "long" | "short"` com default `"long"` está coerente com o uso atual de `config` e payloads de batch.

- **Templates**
  - `multi_ma_crossover` em `backend/app/migrations/seed_prebuilt_strategies.py` com `entry_logic` / `exit_logic`; proposta não altera template, apenas interpretação na execução → correto.

---

## 5. Completude

- **Batch:** Proposta menciona “requisições de backtest/otimização”; o batch em `ComboConfigurePage.tsx` chama `/api/combos/backtest/batch` com payload análogo → incluir `direction` no payload de batch está coberto pelo escopo “requisições de backtest/otimização”.
- **Deep backtest:** `simulate_execution_with_15m` usa entry/exit por sinal 1/-1 e stop; para short será necessário stop acima do preço de entrada e PnL invertido; proposta já cita `deep_backtest` no Impact → completo.
- **Métricas:** “Calcular métricas/PnL/stop/take-profit corretos para short” cobre win rate, return %, etc., desde que calculados a partir dos trades já com PnL e tipo (short) corretos → suficiente na proposta.

Nenhum impacto relevante faltando para a fase de proposta.

---

## 6. Sugestões para design/specs

1. **UI:** Especificar em qual(is) tela(s) o controle de direção aparece: pelo menos **ComboConfigurePage** (Configure Backtest) e, se a otimização suportar short, **ComboOptimizePage** (Optimize).
2. **Stop/take-profit short:** Em short, stop acima da entrada, take-profit abaixo; deixar explícito na spec (e no deep backtest) a verificação de High para stop e Low para take-profit na vela de preço.
3. **Campo `type` nos trades:** Já existe `'type': 'long'` nos trades; para short, usar `'type': 'short'` e garantir que relatórios e métricas tratem ambos os tipos.
4. **BacktestService / engine:** Decidir na design se o `BacktestService` (e o engine em `src/engine/backtester.py`) ganham suporte nativo a short ou se toda a lógica short fica na camada combo (extract_trades + deep_backtest), sem alterar o engine legado.

---

## 7. Conclusão

A proposta **short-backtest-support** está **válida**: é coerente, viável, alinhada com o código e completa para seguir para design, specs e tasks. A única correção pontual é precisar na documentação que a tela “Configure Backtest” é **ComboConfigurePage.tsx** (e, se aplicável, incluir ComboOptimizePage na spec de direção).
