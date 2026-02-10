# Tasks: Lab Trader-Driven Flow Refactor

**Change:** lab-trader-driven-flow  
**Estimated:** ~8h (desenvolvimento) + 2h (testes)  
**Priority:** high

---

## 📋 Ordem de Implementação

### Fase 1: Refatorar Graph (Core) — 4h

#### Task 1.1: Renomear e limpar graph
- [ ] Renomear `build_cp7_graph()` → `build_trader_dev_graph()`
- [ ] Atualizar docstring com nova arquitetura
- [ ] Remover referências a "CP7" no código

**Arquivos:**
- `backend/app/services/lab_graph.py`

**Estimativa:** 30min

---

#### Task 1.2: Criar nó `trader_validation_node`
- [ ] Implementar função `trader_validation_node(state)`
- [ ] Parse `verdict` do Trader (approved/needs_adjustment/rejected)
- [ ] Atualizar `state["status"]` e `state["phase"]`
- [ ] Adicionar trace events

**Arquivos:**
- `backend/app/services/lab_graph.py` (linha ~320, após `implementation_node`)

**Estimativa:** 1h

---

#### Task 1.3: Criar helper `_build_trader_validation_message`
- [ ] Montar mensagem com strategy_draft original + resultado do Dev
- [ ] Formatar métricas (all, in-sample, holdout)
- [ ] Incluir feedback anterior se for loop de ajuste

**Arquivos:**
- `backend/app/services/lab_graph.py` (helper function)

**Estimativa:** 30min

---

#### Task 1.4: Atualizar prompts
- [ ] Criar `TRADER_VALIDATION_PROMPT` (substitui VALIDATOR_PROMPT)
- [ ] Atualizar `DEV_SENIOR_PROMPT` (adicionar workflow de iteração)
- [ ] Simplificar `COORDINATOR_PROMPT` (Agile Coach, sem resumos)

**Arquivos:**
- `backend/app/services/lab_graph.py` (linhas ~458-520)

**Estimativa:** 1h

---

#### Task 1.5: Remover nó "validator"
- [ ] Remover bloco `if ok: ... persona="validator"` de `implementation_node`
- [ ] Atualizar `completed` check (sem validator_verdict)
- [ ] Limpar imports/refs a VALIDATOR_PROMPT

**Arquivos:**
- `backend/app/services/lab_graph.py` (linha ~306)

**Estimativa:** 30min

---

#### Task 1.6: Reconfigurar edges do graph
- [ ] Atualizar `graph.add_conditional_edges` para novo fluxo
- [ ] Upstream → Dev (se approved)
- [ ] Dev → Trader (se ready_for_trader)
- [ ] Trader → END ou Loop (se needs_adjustment)

**Arquivos:**
- `backend/app/services/lab_graph.py` (dentro de `build_trader_dev_graph`)

**Estimativa:** 30min

---

### Fase 2: Refatorar Routes (Integration) — 3h

#### Task 2.1: Criar `_create_template_from_strategy_draft`
- [ ] Implementar conversão de strategy_draft → template_data
- [ ] Normalizar indicadores (source/name → type/alias)
- [ ] Converter entry_idea → entry_logic
- [ ] Converter exit_idea → exit_logic
- [ ] Extrair stop_loss do risk_plan
- [ ] Salvar template no combo com metadata

**Arquivos:**
- `backend/app/routes/lab.py` (adicionar após `_choose_seed_template`)

**Estimativa:** 1h30

---

#### Task 2.2: Criar helpers de conversão
- [ ] `_convert_idea_to_logic(idea: str) -> str`
  - Normalizar operadores (E → AND, OU → OR)
  - Remover parênteses de indicadores (EMA(50) → ema)
  - Substituir "preço" → "close"
- [ ] `_extract_stop_loss_from_plan(plan: str) -> Optional[float]`
  - Regex para "stop-loss X%"
  - Converter para decimal (3% → 0.03)

**Arquivos:**
- `backend/app/routes/lab.py` (helper functions)

**Estimativa:** 45min

---

#### Task 2.3: Atualizar `_choose_seed_template`
- [ ] Adicionar parâmetros: `strategy_draft`, `symbol`, `timeframe`, `run_id`
- [ ] Prioridade 1: criar do strategy_draft (se presente)
- [ ] Prioridade 2: template preferido
- [ ] Prioridade 3: fallback alfabético (atual)
- [ ] Adicionar try/except com trace em caso de erro

**Arquivos:**
- `backend/app/routes/lab.py` (linha ~1514)

**Estimativa:** 30min

---

#### Task 2.4: Atualizar `_context_for_backtest`
- [ ] Carregar `strategy_draft` do run JSON
- [ ] Adicionar ao contexto retornado
- [ ] Validar que está presente quando esperado

**Arquivos:**
- `backend/app/routes/lab.py` (linha ~1700)

**Estimativa:** 15min

---

#### Task 2.5: Atualizar chamadas em `_run_lab_autonomous`
- [ ] Carregar `upstream` e `strategy_draft` do run
- [ ] Passar para `_choose_seed_template(...)`
- [ ] Atualizar trace `seed_chosen` com `from_strategy_draft`
- [ ] Trocar `build_cp7_graph` → `build_trader_dev_graph`

**Arquivos:**
- `backend/app/routes/lab.py` (linhas ~1879, ~1890)

**Estimativa:** 30min

---

### Fase 3: Testes & Validação — 2h

#### Task 3.1: Testes unitários
- [ ] `test_create_template_from_strategy_draft()`
- [ ] `test_convert_idea_to_logic()`
- [ ] `test_extract_stop_loss_from_plan()`
- [ ] `test_choose_seed_template_with_draft()`
- [ ] `test_choose_seed_template_fallback()`

**Arquivos:**
- `backend/tests/test_lab_refactor.py` (criar novo)

**Estimativa:** 1h

---

#### Task 3.2: Teste de integração (run manual)
- [ ] Criar run com strategy_draft válido (BTC/USDT 4h, RSI+EMA)
- [ ] Verificar template criado corretamente
- [ ] Verificar fluxo: Trader → Dev → Trader
- [ ] Validar trace events (template_created_from_draft, trader_validation_done)

**Arquivos:**
- N/A (teste manual via API ou UI)

**Estimativa:** 45min

---

#### Task 3.3: Regressão
- [ ] Testar run SEM strategy_draft (deve usar fallback)
- [ ] Testar run com strategy_draft inválido (deve fallback + log erro)
- [ ] Verificar backward compatibility com runs antigos

**Estimativa:** 15min

---

### Fase 4: Deploy & Monitoramento — 1h

#### Task 4.1: Deploy na VPS
- [ ] Stop backend
- [ ] Git pull da branch `feature/long-change`
- [ ] Start backend
- [ ] Verificar logs de inicialização

**Estimativa:** 15min

---

#### Task 4.2: Validação end-to-end na UI
- [ ] Iniciar novo run do Lab
- [ ] Trader propõe estratégia (RSI+EMA)
- [ ] User aprova
- [ ] Verificar template criado (não Bollinger_Breakout!)
- [ ] Verificar métricas de backtest
- [ ] Trader valida resultado

**Estimativa:** 30min

---

#### Task 4.3: Monitoramento pós-deploy
- [ ] Acompanhar primeiros 3 runs
- [ ] Verificar tokens/tempo por run (esperado: ~50k, ~60s)
- [ ] Ajustar prompts se necessário

**Estimativa:** 15min

---

## ✅ Critérios de Aceite Geral

1. **Template criado do strategy_draft** ✅
   - Nome: `lab_{run_id[:8]}_draft_{symbol}_{timeframe}`
   - Indicators alinhados com proposta
   - Entry/exit logic traduzidos corretamente

2. **Dev recebe contexto completo** ✅
   - `context["strategy_draft"]` presente
   - Dev pode iterar N vezes

3. **Trader valida resultado** ✅
   - Não existe mais "Validator" separado
   - Trader decide: approved/needs_adjustment/rejected

4. **Coordinator é opcional** ✅
   - Não gera resumos automáticos
   - Só intervém sob demanda

5. **Fluxo end-to-end funciona** ✅
   - Run 9a13692200ed não se repete
   - Template alinhado com proposta 100% das vezes

---

## 🚧 Riscos & Dependências

| Risco | Mitigação |
|-------|-----------|
| Regex de conversão falha em casos edge | Testar com 10+ exemplos reais |
| Dev itera infinitamente | Limite hard-coded (5 max) |
| Breaking change em runs antigos | Manter fallback alfabético |
| Trader aprova strategy_draft ruim | User aprova antes (gate duplo) |

---

## 📊 Estimativa Final

| Fase | Tempo |
|------|-------|
| 1. Refatorar Graph | 4h |
| 2. Refatorar Routes | 3h |
| 3. Testes & Validação | 2h |
| 4. Deploy & Monitoramento | 1h |
| **Total** | **10h** |

**Buffer:** +20% = **12h total**

---

## 🔗 Próximos Passos

Após aprovação deste Change Proposal:
1. Alan revisar via viewer: `http://31.97.92.212:5173/openspec/lab-trader-driven-flow/`
2. Alan aprovar: "Go/implementar"
3. Executar via `./scripts/openspec_codex_task.sh lab-trader-driven-flow`
4. Testar na UI
5. Arquivar change: `openspec archive lab-trader-driven-flow`
