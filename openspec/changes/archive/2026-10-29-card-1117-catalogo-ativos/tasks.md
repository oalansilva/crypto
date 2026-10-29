## 1. Catálogo persistido

- [x] 1.1 Migração Alembic de `asset_catalog` (identidade estável, classe, símbolo, nome, ids Binance, estado e motivo, `first_seen_at`, `last_seen_at`, `removed_at`, resumo de histórico) e de `asset_catalog_refresh` (por classe: início, fim, ok ou erro com motivo, contagens de entrada, de excluídos por motivo e de resultado).
- [x] 1.2 Adaptador de cripto: `api/v3/exchangeInfo`, só `quoteAsset=USDT`; mapear `TRADING` para Negociável, `BREAK`/`HALT`/spot desligado para Suspenso, ausência para Removido; aplicar as exclusões explícitas de `excluded_symbols.json` e rever a regra de sufixo UP/DOWN (SYRUP/USDT).
- [x] 1.3 Adaptador de ações e ETFs: união por `ac` entre `get-symbols-static` e `get-exchange-info`; excluir RIGHT, warrants, rights, direitos de valor contingente e registro sem cadastro, com contagem por motivo; mapear `BUY_SELL`, `OFFMARKET`, `NONE`, ausência nas regras e remoção para os estados da decisão 11; guardar `dlt` como motivo informativo.
- [x] 1.4 Atualização agendada por classe e gatilho manual: falha em rede, 429, `code ≠ 000000`, schema inesperado ou queda brusca mantém a última lista válida e grava o erro; nunca lista vazia nem fixa.
- [x] 1.5 Backfill de removidos: símbolos com `/` usados em favoritos e resultados que não estão no catálogo entram como Removido; ticker sem `/` não é associado a ação.
- [x] 1.6 Resumo de histórico por ativo: cripto a partir de `market_ohlcv` (local desde/até ou sob demanda); ação e ETF como não coletado.

## 2. API

- [x] 2.1 `GET /assets/catalog` com pesquisa sem caixa nem acento (símbolo exato, prefixo, nome), filtro por classe, paginação, `total`, `eligible_total`, contagens por classe e `freshness` por classe.
- [x] 2.2 `POST /assets/catalog/resolve` devolve os ids negociáveis do filtro atual (para "Todos"), sem marcados.
- [x] 2.3 `GET /exchanges/binance/symbols` passa a ler os cripto negociáveis do catálogo, por compatibilidade.
- [x] 2.4 Trocar `_ensure_crypto_symbol(s)` pela recusa estruturada 422 (`asset_class_not_supported` com classe e ativos; `asset_not_selectable` com estado e motivo para ativo marcado em otimização e lote; `asset_not_in_catalog`) em backtest, otimização e lote; mensagem em português. Monitor, Favoritos e reabertura de resultados salvos não mudam.
- [x] 2.5 Preflight da Descoberta: motivo "análise ainda não disponível para ações e ETFs" por combinação de ação ou ETF em `exclusions`, e motivo da Binance (estado) por combinação de ativo marcado vindo de rascunho ou snapshot antigo; bloqueio quando não sobra combinação válida.
- [x] 2.6 `binance_symbol_universe.py`: universo da ingestão lido do catálogo; sem `FALLBACK_BINANCE_USDT_SYMBOLS` como universo; prioridade só de ordenação; limite por rodada não afeta o catálogo.

## 3. Seletor de ativos (frontend)

- [x] 3.1 Componente compartilhado conforme `index.html`: contagem por classe (com "N marcados ficam de fora"), frescor, aviso de falha, pesquisa, filtros com contagem, lista paginada com classe, negociação e histórico, linha do marcado sem caixa ativa e com motivo, "Selecionados" com chips (marcados primeiro, × com alvo de 44px) e nota de marcado; frescor e histórico com `--text-tertiary`.
- [x] 3.2 "Todos do filtro (N)" com confirmação inline (incluídos e marcados de fora), soma à seleção; Cancelar e Esc sem efeito, devolvendo o foco ao botão; marcados nunca entram.
- [x] 3.2a Seleção antiga (rascunho, snapshot, favorito, `?symbol=`) com ativo marcado: reidratar como está, mostrar "fica de fora" e deixar só o × para removê-lo; a pesquisa nunca o devolve à seleção.
- [x] 3.3 Estados de falha por classe: lista anterior com aviso e data; sem lista com um único erro e "Tentar de novo" em linha própria; pesquisa vazia durante a falha culpa a Binance, não o símbolo; sem paginador quando não há resultado; seleção preservada.
- [x] 3.4 Descoberta: eixo "Ativos" com o seletor, sem "Edição avançada" de símbolos; eixo Templates sem mudança; Preflight com o bloco "Fora desta varredura" (ações, ETFs e marcados, cada um com motivo); restore de rascunho e snapshot mantém a lista concreta.
- [x] 3.5 Combo: o seletor substitui o rádio Todos/Seleciona e a lista dupla; default BTC/USDT, Top 10 só com negociáveis, `Limpar (1 ativo)`; cópia sob Otimizar diz antes do clique o que roda e o que fica fora (só ação, ETF ou marcado → "Nada será executado nem salvo…"); aviso ao Otimizar; o lote recebe só os pares que rodam (1 par → caminho de 1 ativo).
- [x] 3.6 Otimização: o seletor completo (vários ativos, "Todos do filtro", Limpar) no lugar do texto livre; `?symbol=` só marca se existir no catálogo (marcado entra como "fica de fora"); 1 par roda `POST /combos/optimize` como hoje; N pares rodam o lote do Combo (`POST /combos/backtest/batch`, uma otimização por ativo, via `authFetch`) com o mesmo painel de progresso, Pausar/Encerrar e resumo com link para favoritos; cópia antes do clique e aviso com ação, ETF ou marcado; `/combos/optimize` valida o ativo contra o catálogo.

## 4. Verificação

- [x] 4.1 Testes de backend: reconciliação e contagem (união − excluídos = escolhíveis), exclusões por motivo, mapa de estados, removido preservado, falha sem esvaziar, ingestão sem fallback fixo, recusa 422 estruturada, Preflight com ação e ETF fora.
- [x] 4.2 Testes de frontend: pesquisa de BTC/USDT, NVDA, SPY e QQQ; "Todos" por filtro com confirmação e Esc; marcado sem caixa ativa e fora do Todos; seleção antiga com marcado; aviso nas três telas; lote da Otimização; falha por classe.
- [x] 4.3 Playwright contra o proto canônico `/prototypes/card-1117-catalogo-ativos/` (landmarks, seletor, Preflight) e extras `combo.html` e `optimize.html`.
- [x] 4.4 Evidência DEV com a Binance real: contagens por classe da atualização batem com a leitura pública do dia, descontados os excluídos registrados; BTC/USDT, NVDA, SPY e QQQ encontrados e selecionados.
- [x] 4.5 Regressão: fluxos de cripto atuais (Combo, lote, Descoberta, Otimização de 1 ativo), favoritos e resultados existentes continuam funcionando, inclusive os de ativos que a Binance pausou depois.
