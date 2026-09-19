# Tasks — card-975-monitor-vazio-favoritos

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Primeira carga de opportunities

- [x] 1.1 — `GET /api/opportunities/` sem `refresh` do operador **não** serve cache miss/`[]`/stale `[]` como catálogo vazio quando o utilizador tem favoritos crypto; recomputa ou falha.
- [x] 1.2 — Payload não-vazio continua reutilizável no TTL (Favoritos `refresh=false` / signal_history). Chart/análise continua com velas e trades.
- [x] 1.3 — Subset analisável (ex. 11 de 18) é a resposta de sucesso; skip-all com favoritos **não** é 200 catálogo vazio.

## 2. Estados em `/monitor`

- [x] 2.1 — Primeira visita com favoritos crypto: o quadro mostra sinais ou o erro de carga actual — nunca «Nenhum ativo disponível no monitor». Sem segundo clique só para sair do vazio.
- [x] 2.2 — Recarregar a mesma sessão com os mesmos favoritos não prende o quadro no vazio falso.
- [x] 2.3 — 200 `[]` / análise sem linhas **havendo** favoritos crypto → «Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou. Isto não significa que não há estratégias.» + Tentar de novo; permanece em `/monitor`. Copy **não** muda.
- [x] 2.4 — «Nenhum ativo disponível no monitor» só quando a sessão não tem par crypto nos Favoritos.
- [x] 2.5 — Análise chegou e um filtro (Na carteira, busca, estrela, estratégia, tempo) esconde todos → «Não há resultado com estes filtros.» Default Na carteira vs Todos **não** muda.
- [x] 2.6 — Fetch HTTP falho continua no erro de carga (#970); `MonitorDashboardTab` permanece morto.

## 3. Favoritos sem regressão

- [x] 3.1 — `/favorites` continua a listar as estratégias crypto já salvas (lista magra #970 intacta). Sem extra `/favorites` no proto.

## 4. UI, testes e evidência

- [x] 4.1 — `/monitor` alinhado ao proto `index.html` (desktop + mobile): linhas visíveis; landmarks `table.signals` + Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia; ausente catálogo vazio no feliz.
- [x] 4.2 — Irmão `erro.html` coberto no Apply visível (copy actual; ausente catálogo vazio).
- [x] 4.3 — Testes da primeira carga (cache `[]`, skip-all, subset) e Playwright desktop+mobile. Fora: redesign da board, default de filtro, copy de erro, #970.
- [x] 4.4 — `openspec verify` desta change.
