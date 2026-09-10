UI impact: affected
live_route: /combo/discovery
surface: existing

# Design — card 876: amostra insuficiente antes do grid

## Context

Hoje `run_combination` chama `ComboOptimizer.run_optimization` de imediato. O fetch de OHLCV e o split 70/30 só acontecem **dentro** do grid (~16 mil parâmetros). Pares com listagem curta (ex.: BLZ/USDT ~27 diárias) gastam 1–2 min e saem como `low_sample` / sucesso. A fórmula visível é `N processadas = X sucesso + Y falha + Z ignoradas`. Reconcile com `succeeded=0` e `failed=0` e só skipped marca falha operacional.

Operador: administrador da Descoberta em `/combo/discovery` (modos Montar / Acompanhar / Decidir já vivos, #852).

## Goals / Non-Goals

**Goals:**

- Cortar o grid quando a listagem no timeframe da combinação não pode alguma vez gerar 30 negócios de ranking.
- Quarto saco persistido e visível; linha no Decidir com selo `Amostra insuficiente`, rank «—», métricas N/A, sem promover.
- Varredura só com esse desfecho conclui; «1 por sweep» inalterado.

**Non-Goals:**

- Concorrência / Celery / mais processos nesta VPS.
- Redesign dos 3 modos ou das parciais top-5 (#852).
- Operar a run `#c243f729`, mudar o universo 694, Calmar de par com histórico cheio, ou poupar tempo em par com anos de candles e poucos negócios.

## Recorte

- **Audience:** administrador da Descoberta, varredura grande em curso, VPS saturada.
- **Outcome:** ver quais pares não tinham histórico, sem esperar minutos de grid, sem poluir o top-5.
- **Direction:** clone+delta da rota viva; Operate; mesmo chrome e selo-amber de `Baixa amostra`, palavras distintas.
- **Scope:** Acompanhar (fórmula) + Decidir (linha). Montar intacto.

## Decisions

### 1. Onde medir — claim-time, antes do grid

Em `run_combination`, depois do recheck `sweep.state == running` e **antes** de `ComboOptimizer.run_optimization` / `generate_stages`. Mesmo `provider.fetch_ohlcv` (símbolo × timeframe da combinação × datas do snapshot, incl. «todo o histórico»). Não medir no preflight (694 fetches atrasariam o start).

Alternativa rejeitada: calendário esperado da janela pedida — listagem curta pode ter cobertura ~100% da janela **devolvida**.

### 2. «Não dá para 30 negócios» = barras de treino < 30

Descoberta já usa `split_train_holdout(df, 0.7)` (`DISCOVERY_SPLIT_TRAIN_RATIO`). Teto teórico de negócios fechados no ranking ≤ barras do treino (1 round-trip por barra). Corte:

- listagem vazia ou `< 2` barras (split recusa); ou
- `len(train) < MIN_ELIGIBLE_TRADES` (30).

Ex.: 27 diárias → treino `int(27*0.7)=18` → corta. ~43 diárias → treino 30 → segue o grid (pode ainda sair `Baixa amostra` depois). Timeframe da combinação, sem converter 1d↔4h.

### 3. Quarto desfecho, não reusar sacos

- Combinação: estado `insufficient_sample` (não `succeeded` / `skipped` / `failed`).
- Sweep: coluna/contador `insufficient_sample` (default 0).
- **BREAKING** invariante: `processed = succeeded + failed + skipped + insufficient_sample`.
- Persistência: `DiscoveryResult` com `eligibility=insufficient_sample` (distinto de `low_sample`) para a linha existir no Decidir; métricas ranking nulas.
- Reconcile: `failed=0` e `insufficient_sample>0` e `succeeded=0` → `completed` (não `operational_failure` do ramo skipped-only). `Baixa amostra` pós-grid continua `succeeded` + `low_sample`.

### 4. UI — mesmo padrão de leitura, selo distinto, sem CTA promover

Acompanhar: `N processadas = X sucesso + Y falha + Z ignoradas + W amostra insuficiente` (`data-testid=counter-invariant`). Parciais top-5 **não** incluem `insufficient_sample`.

Decidir: linha visível; rank «—»; selo visível `Amostra insuficiente` (não `Baixa amostra`); Calmar / Max DD / Trades/cobertura = `N/A`; **sem** controlo Promover (não basta desabilitar com o rótulo da baixa amostra). Chip vs texto do selo = detalhe Apply, desde que as palavras sejam as do progresso. Excluir permanece (inspectável, como hoje).

## Apply contract

- Apply (pós `Pronto para Dev`) lê este `design.md` + `frontend/public/prototypes/card-876-discovery-amostra-insuficiente/index.html` como spec de UI; API é fonte de dados, não de layout.
- Fidelidade bloqueante: landmarks `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`; tokens `DESIGN.md` (não reescrever).
- Worker: gate de listagem em `run_combination` antes do grid; helper de contagem reusa `fetch_ohlcv` + `split_train_holdout`; não instanciar estágios do otimizador no corte.
- Persistência + reconcile + payload do sweep com `insufficient_sample`; migração default 0; leitura antiga sem o campo trata 0.
- Frontend: só a fórmula e a linha do Decidir/parciais; sem redesenhar modos.
- Desvio do proto: path + elemento + motivo no PR; sem registro = bloqueio.
- Proibido: contar amostra insuficiente como sucesso ou ignorada; selo `Baixa amostra` nesta linha; Promover visível nesta linha; `completed` recusado quando só há amostra insuficiente; subir «1 por sweep».

## Risks / Trade-offs

- [Fetch extra por combinação] → um `fetch_ohlcv` barato vs 16k backtests; cache do provider se já existir.
- [Teto 1-trade-por-barra é conservador] → pares com treino ≥30 ainda podem ser `Baixa amostra` depois (fora deste card, grelha).
- [Invariante BREAKING] → testes de reconcile/UI da fórmula de 3 termos; coluna nova default 0.
- [Leaderboard lista não-sucesso] → query do Decidir inclui `eligibility=insufficient_sample`; top-5 filtra fora.

## Migration Plan

Alembic: `discovery_sweeps.insufficient_sample INTEGER NOT NULL DEFAULT 0`. Sweeps em curso na deploy não recortam o já-gridado; só claims novos. Rollback: coluna ignorada; worker antigo volta a gastar minutos.

## Open Questions

Nenhuma de produto (grelha fechada). Chip vs texto do selo = Apply.

## Prototype

- **URL:** https://dev.criptofarol.com.br/prototypes/card-876-discovery-amostra-insuficiente/
- **Caminho:** `frontend/public/prototypes/card-876-discovery-amostra-insuficiente/index.html`
- **Digest (sha256):** `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722` · 33203 bytes · servido == local
- **Copiados vs gerados:** 8 pares `COPIED:start/end` · 6831 bytes copiados · 26372 bytes gerados/delta
- **Base:** rota viva `/combo/discovery` (shell autenticado 224px + heading + 3 modos + Acompanhar + Decidir). Delta só: quarto termo na fórmula; linha Decidir selo `Amostra insuficiente`, rank —, N/A, sem Promover.
- **Fluxos:** default Acompanhar (18/24, parciais top-5 sem amostra insuficiente); Montar com landmarks Preflight/Rascunho; Decidir com elegível + `Baixa amostra` + `Amostra insuficiente`.
- **Viewports:** 1440×900 e 390×844.

## Prototype Validation

- **URL:** https://dev.criptofarol.com.br/prototypes/card-876-discovery-amostra-insuficiente/ (sha256 `a128a598…`, 33203 bytes, servido == local)
- **Viewports:** desktop 1440×900 + mobile 390×844 (Playwright Chromium; PNGs em `/tmp/card876-gate/*-{montar,acomp,decidir}.png`)
- **Asserts:** landmarks 3/3 (h1 + Preflight + Rascunho via tab Montar); Acompanhar `18 processadas = 12 sucesso + 1 falha + 1 ignoradas + 4 amostra insuficiente`; top-5 sem o selo; Decidir linha `data-testid=row-insufficient` com selo `Amostra insuficiente` (não `Baixa amostra`), rank —, 3× N/A, 0 Promover, Excluir presente; vizinho `Baixa amostra` intacto.
- **Resultado:** 17/17 PASS por viewport; 0 erros de console; 0 pageerrors; 0 recursos ≥400. Detector Impeccable `[]`. Veredito do autor (não final da coluna): **PASS**. O pai dispara A/B; este filho não emite `Design Agent verdict`.

## Design Critique

Onda A/B isolada (inherit, sem transcript). Zero P0/P1. P3 aceitos no Apply.

- **P0** — nenhum. Index = clone+delta (não galeria / ANTES-DEPOIS); landmarks 3/3; digest servido == local `a128a598…`; 8 pares COPIED; linha delta sem Promover.
- **P1** — nenhum. Detector `[]`; 15–17/17 asserts desktop+mobile; 0 console/pageerror; fórmula com quarto termo; Decidir `Amostra insuficiente` ≠ `Baixa amostra`; rank —; 3× N/A.
- **P3** (aceitos, Apply) — Montar condensado vs vivo; Decidir sem filtros/modais; Promover elegível outline vs fill `DESIGN.md`; mock 16/16 vs 4 linhas; overflow ~4 px thead mobile; jargão `#PF-` no chrome copiado; chip vs texto do selo.
- **Disposition:** P3 no Apply; não reabrir grelha.
- **Riscos não bloqueantes:** sem sessão nas rotas vivas; `/login` não foi evidência de clone (A avaliou proto + fonte × landmarks).
- **Proto:** https://dev.criptofarol.com.br/prototypes/card-876-discovery-amostra-insuficiente/ · digest `a128a59851d8cc23dc5ee5ca798a99fa5c6387f525f2b4d2189f722a94339722`
- **Snapshots:** `.impeccable/critique/876-card-876-discovery-amostra-insuficiente-2026-09-08T2357Z.md` (autor); `…-assessment-A-2026-09-09T0005Z.md`; `…-assessment-B-2026-09-09T0005Z.md`

Design Agent verdict: PASS
