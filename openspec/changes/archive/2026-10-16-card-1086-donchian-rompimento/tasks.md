## 1. Regressão do rompimento

- [x] 1.1 Criar fixtures OHLCV determinísticas usando o template real do export e parametrizar 4h, 1h e 15min; demonstrar que o caso positivo falha antes da correção. Evidência: teste `valid_breakout` antes da alteração: 6 failed (fast/legacy × três timeframes), por `len(trades) == 0`; log `/tmp/card-1086-red.log`.
- [x] 1.2 Exigir operação real pelo caminho ComboStrategy + extrator de trades da Descoberta, com saída posterior controlada, type long, Comprar, horário t+1 e preço de abertura; cobrir fast e legacy sem mockar sinais ou extrator.
- [x] 1.3 Cobrir fechamento igual/abaixo, máxima isolada acima e confirmação de volume ausente ou no limite de igualdade, sem compras indevidas nos três timeframes.

## 2. Correção restrita ao template

- [x] 2.1 Alterar somente a referência de entrada do template donchian_volume_breakout para dc_upper.shift(1), preservando confirmação de volume, indicadores, saída, stop loss e optimization_schema.
- [x] 2.2 Validar histórico insuficiente, primeiro candle elegível e período N diferente do padrão; comprovar ausência de execução sem candle seguinte.
- [x] 2.3 Validar independência da máxima do candle avaliado e invariância das decisões/sinais diante de alterações futuras nos três timeframes; manter a abertura de execução fixa quando comparar preços.

## 3. Integração e preservação

- [x] 3.1 Verificar seed inicial e atualização idempotente do catálogo existente com o export corrigido, usando PostgreSQL isolado se houver persistência; preservar definições dos outros templates e não introduzir DDL.
- [x] 3.2 Comparar bandas Donchian e condição de saída com baseline; comprovar preservação de indicadores/sinais de bollinger_squeeze, long_ma_pullback_rsi_adx e Bollinger_Breakout.
- [x] 3.3 Executar a suíte focal do #1086, os testes do #1074, parser de lógica e regressões fast/legacy afetadas; registrar comandos e resultados, sem alterar thresholds, custos ou promoção de favoritos.

## Evidência Apply

- `test_card_1086_donchian_breakout.py`: OHLCV determinístico e export real, parametrizados em 4h/1h/15min e fast/legacy; positivos exigem trade long/Comprar, abertura t+1=101.25 e saída por lógica em t+3. Negativos exigem ausência de sinal de compra t+1 e em toda a série, além de lista de trades vazia (P3 aceito resolvido).
- Histórico: N=20/25, primeiro candle elegível, N=10 sem média de volume disponível; máxima antiga entra/sai exatamente na janela configurada; decisão no último candle não executa sem candle seguinte.
- Causalidade: máxima atual alterada de 102 para 1000 mantém entrada; OHLCV futuro alterado conserva máscaras até t e sinais até t+1; abertura de t+1 fixa conserva preço; prefixo truncado mantém sinal.
- Preservação: fixture `backend/tests/fixtures/card_1086/templates_before.json` capturada do export antes da correção. Igualdade integral do template Donchian exceto entrada; bandas/saída e indicadores/sinais dos outros três templates iguais ao baseline nos seis cenários.
- `test_card_1086_donchian_seed.py`: seed inicial e refresh de catálogo anterior usando SessionLocal real; duas repetições preservam IDs/definições e estratégia salva. PostgreSQL 16 próprio em `/tmp/card-1086-postgres`, porta 25486, banco `card_1086_app_test`; nenhuma escrita em banco compartilhado nem mudança de DDL do produto.
- Primeira rodada verde focal: 117 passed em 6.23s (46 avisos existentes de depreciação Pydantic/datetime).
- Design e snapshot congelados preservados; UI impact none, protótipo N/A.

### Comandos e resultados finais

Interpreter usado: `/srv/apps/dev/criptofarol/source/backend/.venv/bin/python`; comandos no worktree `card-1086-donchian-rompimento`.

```bash
/srv/apps/dev/criptofarol/source/backend/.venv/bin/python -m pytest -q backend/tests/unit/test_card_1086_donchian_breakout.py -k valid_breakout --tb=short
# Antes da correção: 6 failed, 109 deselected; falha por ausência de trade real.

DATABASE_URL=postgresql+psycopg2://postgres@127.0.0.1:25486/card_1086_app_test WORKFLOW_DATABASE_URL=postgresql+psycopg2://postgres@127.0.0.1:25486/card_1086_app_test /srv/apps/dev/criptofarol/source/backend/.venv/bin/python -m pytest -q backend/tests/unit/test_card_1086_donchian_breakout.py backend/tests/unit/test_card_1086_donchian_seed.py backend/tests/unit/test_card_1074_combo_templates.py backend/tests/unit/test_vwap_indicator_schemas.py backend/tests/unit/test_backtest_execution_costs.py backend/tests/unit/test_combo_strategy_logic_parser.py backend/tests/unit/test_card_945_fastpath.py backend/tests/unit/test_card_945_goldens.py backend/tests/contract/test_backend_unit_harness.py --tb=short
# 266 passed, 47 warnings em 359.58s; log /tmp/card-1086-green.log.

/srv/apps/dev/criptofarol/source/backend/.venv/bin/python -m pytest -q backend/tests/unit/test_card_1086_donchian_breakout.py -k new_breakout --tb=short
# 6 passed, 115 deselected em 1.46s: rompimento adicional com long aberta não duplica compra.

/srv/apps/dev/criptofarol/source/backend/.venv/bin/python -m black --check backend/tests/unit/test_card_1086_donchian_breakout.py backend/tests/unit/test_card_1086_donchian_seed.py backend/tests/contract/test_backend_unit_harness.py
/srv/apps/dev/criptofarol/source/backend/.venv/bin/python scripts/validate_backend_unit_inventory.py
openspec validate card-1086-donchian-rompimento --strict
git diff --check
# Todos PASS; inventário 83 entradas / 83 arquivos.
```

Os avisos vêm de Pydantic, datetime.utcnow e cálculo de CAGR em teste de custos existente. Nenhuma mudança em thresholds, custos, favoritos, serviços ou bancos compartilhados. Cluster temporário encerrado após os testes; arquivos de evidência e `/tmp/card-1086-postgres` preservados para auditoria.

Progresso: 9/9 tasks feitas. Handoff ao pai para git + pedir_review; sem archive, process_event, commit/push ou reviewers no filho.
