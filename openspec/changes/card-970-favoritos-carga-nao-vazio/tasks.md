# Tasks — card-970-favoritos-carga-nao-vazio

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Lista GET é resumo

- [x] 1.1 — `GET /api/favorites/` deixa de embutir `metrics.analysis_candles` (e séries históricas equivalentes) em cada linha; a grade recebe identidade + métricas de grelha.
- [x] 1.2 — Abrir gráfico/análise de um favorito continua a mostrar velas e trades via `GET /api/favorites/{id}/trades` e market candles.

## 2. Estados em `/favorites`

- [x] 2.1 — «Carregando estratégias...» só enquanto a lista corre; no fim, lista ou erro explícito — nunca o texto de catálogo vazio após falha.
- [x] 2.2 — Sessão válida + pares crypto + Todos + busca vazia → a grade lista esses pares; ausente «Nenhuma estratégia favorita encontrada» e ausente «0 estratégias carregadas» como único resultado.
- [x] 2.3 — Erro de rede / 401 com sessão ainda válida / corpo inválido: «Não foi possível carregar as estratégias favoritas.» + «Tentar de novo»; permanece em Favoritos; não vai ao login.
- [x] 2.4 — Filtro/busca esconde todos os pares crypto → «Não há resultado com estes filtros.»; não usa o texto de catálogo vazio.
- [x] 2.5 — Catálogo crypto realmente vazio (Todos, busca vazia) → «Nenhuma estratégia favorita encontrada».
- [x] 2.6 — Sessão morta → login. Favoritos sem `/` continuam de fora da grade.

## 3. Início e Monitor (Q3=B)

- [x] 3.1 — `/home`: falha de `/api/favorites` continua «Não foi possível carregar `/api/favorites`.»; não regride para «Nenhuma estratégia favoritada». Sem redesign.
- [x] 3.2 — `/monitor`: falha ao carregar a lista derivada de favoritos não pinta «Nenhum ativo disponível no monitor». `MonitorDashboardTab` permanece morto.

## 4. UI, testes e evidência

- [x] 4.1 — Grade `/favorites` alinhada ao proto `index.html` (desktop = mobile): pares visíveis; landmarks intactos.
- [x] 4.2 — Irmãos `erro.html` e `filtro.html` e extra `monitor.html` cobertos no Apply visível.
- [x] 4.3 — Testes da query/payload e Playwright desktop+mobile. Fora: redesign da grade, Discovery #897/#948/#935, login novo.
- [x] 4.4 — `openspec verify` desta change.
