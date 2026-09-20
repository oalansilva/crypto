# Tasks — card-995-monitor-retry-rede

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Reabsorção da falha transitória

- [x] 1.1 — Com sessão válida, um corte `Failed to fetch` / reset na carga autenticada de `/monitor` **não** pinta o #975 à primeira; o quadro espera dezenas de segundos em «Carregando sinais...». Sem mudar Caddy/backend/TTL.
- [x] 1.2 — Se a lista chega na mesma abertura, `table.signals` lista os pares; ausente o quadro de erro; ausente o toast «Não foi possível carregar preferências do monitor.».
- [x] 1.3 — Sessão morta de verdade → login. Não permanece no quadro de erro.

## 2. Estados visíveis no Monitor

- [x] 2.1 — Enquanto espera, KPIs **não** pintam `0` como contagem concluída. Labels da faixa intactos (sem redesign).
- [x] 2.2 — Falha persistente após a espera → copy #975 + «Tentar de novo»; permanece em `/monitor`; ausente catálogo vazio.
- [x] 2.3 — «Tentar de novo» relê a lista já calculada (sem `refresh=true`). «Atualizar» continua a recomputar.
- [x] 2.4 — `MonitorDashboardTab` permanece morto. Copy #970/#975, filtros e board intactos.

## 3. Fora deste card

- [x] 3.1 — Favoritos, Início e Carteira continuam o contrato do #983. Sem extra dessas rotas no proto.

## 4. UI, testes e evidência

- [x] 4.1 — `/monitor` alinhado ao proto `index.html` (desktop + mobile): linhas visíveis; landmarks `table.signals` + Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia; ausente #975 e toast de preferências no feliz.
- [x] 4.2 — Irmãos `carga.html` / `erro.html` / `sessao.html` cobertos no Apply visível.
- [x] 4.3 — Testes da espera/retry/reread e Playwright desktop+mobile. Fora: Caddy, Zscaler, TTL, redesign, Favoritos/Início/Carteira.
- [x] 4.4 — `openspec verify` desta change.
