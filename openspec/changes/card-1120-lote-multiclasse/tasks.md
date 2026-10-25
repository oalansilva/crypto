> Lembrete: use as skills do projeto disponíveis no Cursor e no Claude Code quando couberem (`.cursor/skills/` — `covenant-flow`, `openspec-apply-change`, `openspec-verify-change`, `playwright-cli`; `.agents/skills/` — `impeccable`, `design-critic`).
>
> Gate de Design (UI impact: affected): Design → Aprovação de Design → Pronto para Dev, com a skill `design-critic` e a aprovação humana de Alan. Nada aqui roda antes de `Status=Pronto para Dev`. O protótipo `frontend/public/prototypes/card-1120-lote-multiclasse/` é a spec de UI.
>
> Dependência de aceite: #1122 (identidade, atualização e alertas de favoritos de ação/ETF). Contrato na decisão 12 do `design.md`.

## 1. Estado durável do lote

- [x] 1.1 Migração com as tabelas do lote e dos itens (lote: id, usuário, payload, plano, status, pedidos de pausa/encerramento, tempos; item: símbolo, classe, moeda, ordem, estado, motivo, progresso, `favorite_id`, `execution`, `snapshot_id`, tempos)
- [x] 1.2 `batch_backtest_store.py` lê e grava no PostgreSQL (sem prazo enquanto pausado); Redis só como fila do Celery; lote antigo no Redis termina no caminho antigo
- [x] 1.3 `GET /api/combos/backtest/batch/{id}` devolve `items` e os totais por estado; `GET /api/combos/backtest/batch/active` devolve o lote não final mais recente do usuário

## 2. Aceite por classe e plano do lote

- [x] 2.1 `refusal_for_symbols` com escopo de lote: ação e ETF passam; marcado e fora do catálogo seguem recusados; teste de contrato
- [x] 2.2 `POST /api/combos/backtest/batch` sem `_ensure_crypto_data_source`; fonte por ativo; 422 só quando nada roda, com o motivo por ativo
- [x] 2.3 `POST /api/combos/backtest/batch/preview`: plano por ativo (roda/fora e motivo), `needs_collection` e `collect_kind` pelo que a Binance tem na janela e ainda não está guardado (decisão 4), sem coletar, totais por classe e moeda; regras de fora (tempo de ação/ETF, janela fixa da Otimização sem 5m em 15m/1h/4h, marcado)
- [x] 2.5 Lote pausado bloqueia lote novo: `POST /backtest/batch` e `/preview` devolvem 409 `batch_paused` com o id do pausado (decisão 16); teste de contrato
- [x] 2.4 Descoberta: porquê novo da recusa (decisão 13) no servidor e no front; teste de que a Descoberta segue recusando

## 3. Execução por ativo

- [x] 3.1 `run_batch_backtest` por item: coleta (`prepare_equity_history` para ação/ETF), otimização sem nova coleta, gravação; estados e motivos da decisão 8 (insuficiente, rejeitado, falha, pulado, fora, não rodou)
- [x] 3.2 `HistoryService.ensure` com retorno de progresso por página; o lote grava "série · página N de M" no item
- [x] 3.3 Mesma amostra: cripto e ação/ETF congelam a amostra no começo de cada ativo; teste de que o provedor é lido uma vez por ativo e todas as tentativas usam o mesmo `snapshot_id`
- [x] 3.4 Pausa e encerramento ao fim da etapa em curso; `POST /api/combos/backtest/batch/{id}/resume` continua o mesmo lote do próximo passo, sem refazer itens finais nem coleta guardada
- [x] 3.5 Favorito de qualquer classe (ação/ETF sem nível de estrela até o #1122) com `data_source`, `asset`, `execution`, `conventions`, `data_provenance` e `batch_id`; checagem de "já nos favoritos" e `lock_and_find_duplicate` recebem `data_source` e `asset` (contrato com o #1122); a recusa de favoritar ação/ETF pela tela do resultado continua
- [x] 3.6 Testes: lote misto 1d (BTC/USDT, NVDA, SPY) grava 3 favoritos com precisão e janela; mesmo lote em 5m roda só BTC/USDT e marca NVDA e SPY "Fora"; NVDA no lote igual ao backtest de 1 ativo; regressão do lote só cripto na mesma amostra; insuficiente, rejeitado e falha não gravam favorito e não param o lote

## 4. Combo e Otimização (UI, seguindo `configure.html` e `optimize.html`)

- [x] 4.1 `assetSelection.ts`: plano de lote por classe e tempo; seleção com mais de 1 ativo sempre lote; textos da decisão 6 (nota da classe, sob demanda, antes de rodar, fora antes de começar); sem "o lote vem depois" no Combo e na Otimização
- [x] 4.2 Tempos "(só cripto)" na seleção mista (Combo 1m/5m; Otimização 1m/5m/30m), escolhíveis
- [x] 4.3 Confirmar lote no fluxo (sem modal) com o preview: vão rodar, precisam de coleta, ficam fora, configuração, favoritos; foco no título; Voltar devolve o foco
- [x] 4.4 Painel do lote no lugar do `BatchProgressPanel`: selo, tempo, linha viva `role=status`, barra, nota de precisão diária, filtro por estado, lista por ativo com classe e moeda, "Mostrar mais 50", cartões abaixo de 620 px de largura do painel
- [x] 4.5 Pausar → Pausando… (`aria-disabled`, foco fica) → Pausado → Retomar; Encerrar (foco no título); resumo e link `/favorites?lote=<id8>` (singular com 1); painel do lote ativo ao reabrir a página (`useBatchJob`)
- [x] 4.7 Lote pausado: rodar mostra "Retome ou encerre o lote <id8> antes de começar outro." com Retomar, Encerrar e Voltar (decisão 16)
- [x] 4.8 Combo: Market Data por ativo na seleção mista; Configuração do Confirmar com tempo e período escolhidos. Otimização: Confirmar e painel na coluna larga no lugar de "Ready to Optimize"; fora por cobertura em 15m/1h/4h
- [x] 4.6 E2E Playwright com a API simulada (desktop 1440 e celular 390): lote misto, 5m, lote grande, pausa/retomada, encerrar, problemas; comparação com o protótipo registrada

## 5. Favoritos (UI, seguindo `index.html`)

- [x] 5.1 `GET /api/favorites/` com `asset` (de `metrics.asset` ou do catálogo)
- [x] 5.2 `FavoritesDashboard.tsx` sem `matchesCryptoOnly`; filtro Classe com contagens; grade de 6 filtros a partir de 1100 px
- [x] 5.3 Linha e cartão: chip da classe e moeda; bloco da estratégia com precisão, convenções curtas e período efetivo à vista e "Limitações e origem" num `<details>`; células sem o `aria-label` vivo; favorito antigo sem `execution`; ATR na moeda; "Atualização diária, Monitor, Telegram e Revalidar: ainda não para ações e ETFs" até o #1122
- [x] 5.6 Ação/ETF: estrelas, Telegram e Revalidar `aria-disabled` com `aria-describedby`; resumo e filtro por estrelas só com cripto e a nota; `:focus-visible` nos selects de filtro
- [x] 5.4 Faixa do lote com `?lote=<id8>` e "Mostrar todos os favoritos"; contagem e rodapé com os filtros
- [x] 5.5 Atualizar os specs `favorites-asset-type-filter` e `crypto-only-mvp` (delta deste change) e o E2E de Favoritos (desktop e celular), comparando com o protótipo

## 6. Verificação e demonstração

- [ ] 6.1 Demonstração no card: lote BTC/USDT + NVDA + SPY em 1d (favoritos consultáveis com período efetivo, precisão e limitações) e o mesmo em 5m (NVDA e SPY fora, BTC/USDT roda), em DEV <!-- covenant-flow:after-qa -->
- [ ] 6.2 Regressão do lote de cripto em DEV (mesma amostra, antes/depois) registrada na evidência <!-- covenant-flow:after-qa -->
- [ ] 6.3 `/opsx:verify`: tasks × implementação × protótipo; aceite só depois do #1122 em `develop` <!-- covenant-flow:after-qa -->

## 7. Worker do lote (pós-homologação, decisão de Alan 25/10/2026)

- [x] 7.1 Templates `ops/systemd/criptofarol-dev-batch-worker.service` e `criptofarol-prod-batch-worker.service`: só `-Q batch_backtest`, `--pool=solo --concurrency=1 --prefetch-multiplier=1`, hostname `batch-<env>@%h`, `.env`, perfil de recursos e spool próprios, tetos de memória iguais aos da Descoberta (DEV 3/4 GiB, PROD 4/5 GiB), `KillMode=mixed` e `TimeoutStopSec=300s` para um lote em curso terminar; `systemd-analyze verify` limpo
- [x] 7.2 `install-discovery-workers-systemd.sh`: valida e instala as duas units (DEV e PROD) no instalador completo, para um worker ativo antes de gravar a unit, e ganha `--batch-only` (PROD sem tocar na Descoberta); valida fila, pool, hostname, perfil e `KillMode` do template do lote e que o template da Descoberta consome só `discovery`; `./restart` do DEV instala, liga e confere o worker do lote
- [x] 7.3 Testes do instalador e do restart cobrindo as units novas: `scripts/test_install_discovery_workers.sh`, `backend/tests/unit/test_prod_discovery_installer.py` e `backend/tests/unit/test_dev_restart_contract.py`
- [x] 7.4 Overlay (`environments.dev.services` e `environments.prod.services`) e docs (`docs/crypto-overlay.md`, `docs/runtime-architecture.md`, `docs/prod-migration-runbook.md`, `docs/discovery-memory-operations.md`): inventário de serviços, janela do publish, instalação do worker no T16 e evidência `services=`
- [x] 7.5 Teste de contrato `backend/tests/unit/test_celery_queue_consumers.py`: falha se uma fila de `celery_app.task_routes` (ou uma task `app.*` sem rota) não tiver um template de worker em `ops/systemd` com `-Q` para DEV e PROD, instalado pelo instalador e listado no overlay

## 8. Combinação com erro e template bollinger_rsi_adx (pós-homologação, decisões de Alan 25/10/2026)

- [x] 8.1 `execute_stream` ganha o parâmetro explícito `failures` (`FailureLog`): sem ele segue estrito (a Descoberta, #1093, aborta na primeira combinação com erro); com ele a combinação com erro é pulada, contada e agrupada por motivo (sem a regra inteira nem a lista de colunas), com um aviso agrupado no log por etapa
- [x] 8.2 `ComboOptimizer.run_optimization(tolerate_combination_errors=False)`: o motivo real da combinação sai do `CalculationFailure` genérico (`_failure_text`); o resultado traz `combination_errors` (`failed`, `executed`, `reasons`, `message`); o ativo só falha (`NoValidCombination`, "nenhuma combinação válida; N com erro: <motivo>") se nenhuma combinação funcionou na otimização inteira; etapa de refino só com combinações quebradas mantém o melhor já achado
- [x] 8.3 Lote e `POST /api/combos/optimize` (Combo e Otimização) ligam a tolerância; o detalhe do item gravado mostra "N combinações com erro: <motivo>" (`reason` do item) e vai ao log do worker; `ComboOptimizationResponse.combination_errors` e o aviso "Combinações puladas" no bloco "Dados e execução" das telas de resultado e de Otimização (sem layout novo); falha sem combinação válida é "Falha" com o motivo real
- [x] 8.4 Template `bollinger_rsi_adx`: as regras leem os aliases `rsi` e `adx` e a coluna `adx_threshold` (`threshold` do ADX), então `rsi_length`, `adx_length` e `adx_threshold` otimizados valem; seed atualizado (`prebuilt_strategies()`) e migração Alembic de dados `20261025_0001` (idempotente, reversível, só o registro `bollinger_rsi_adx` com as regras antigas; outros templates e cópias de usuário ficam como estão)
- [x] 8.5 Testes: toda a faixa padrão do template avalia (e o limite do ADX age); `execute_stream` tolerante × estrito; otimização e lote com combinações quebradas gravam o favorito com as válidas e mostram a contagem; sem nenhuma válida falha com o motivo; Descoberta segue estrita; migração em schema privado do PostgreSQL; `card-1120-lote.test.mjs` cobre o texto no item e na tela
