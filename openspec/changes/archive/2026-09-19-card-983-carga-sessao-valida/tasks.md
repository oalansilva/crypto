# Tasks — card-983-carga-sessao-valida

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Sessão: 200 ganha de abort / 401 transitório

- [x] 1.1 — Um único caminho de renovação no cliente: `authFetch` / `authStore` axios / `HomePage.fetchJson` deixam de pintar falha falsa enquanto o refresh ainda recupera o acesso. Sem alongar TTL do login.
- [x] 1.2 — Um 200 que chegou ou vai chegar ganha de abort e de 401 transitório. «Tentar de novo» e um pedido a meio do caminho não deixam a tela no erro se a lista chegou ou está a chegar.
- [x] 1.3 — Sessão morta de verdade (refresh esgotado) → login. Não permanece no erro do #970 com «a sessão continua válida».

## 2. Favoritos

- [x] 2.1 — Janela de renovação + catálogo crypto no servidor + Todos → `/favorites` lista os pares; ausente o erro do #970; ausente «Nenhuma estratégia favorita encontrada».
- [x] 2.2 — Falha real de rede ou corpo inválido continua «Não foi possível carregar as estratégias favoritas.» + «Tentar de novo»; não volta a fingir catálogo vazio. Distinção vazio vs filtro vs erro do #970 intacta.
- [x] 2.3 — Abrir gráfico/análise de um favorito continua a mostrar velas e trades. Lista magra do #970 intacta.

## 3. Início, Monitor e Carteira

- [x] 3.1 — `/home`: na renovação o KPI «Melhor estratégia (7d)» mostra a estratégia; ausente «Não foi possível carregar `/api/favorites`.». Falha real do KPI continua essa copy. Sem redesign.
- [x] 3.2 — `/monitor`: na renovação `table.signals` lista os pares; ausente a falha falsa da lista. Falha real continua o erro de carga do Monitor. `MonitorDashboardTab` permanece morto.
- [x] 3.3 — `/external/balances`: na renovação mostra os saldos; ausente «Erro ao carregar» / «Falha ao carregar saldos». Falha real continua esse erro. Sem redesign. Credenciais da exchange fora.

## 4. UI, testes e evidência

- [x] 4.1 — Grade `/favorites` alinhada ao proto `index.html` (desktop + mobile): pares visíveis; landmarks intactos.
- [x] 4.2 — Irmão `erro.html` e extras `monitor.html` / `inicio.html` / `carteira.html` / `carteira-erro.html` cobertos no Apply visível.
- [x] 4.3 — Testes da query/sessão e Playwright desktop+mobile. Fora: redesign da grade, Discovery, alongar sessão, apagar favoritos.
- [x] 4.4 — `openspec verify` desta change.
