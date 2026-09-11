UI impact: affected
live_route: /combo/discovery
surface: existing

# Design — card 896: Calmar de calendário e NO-GO na linha

## Context

Card [#896](https://github.com/oalansilva/crypto/issues/896). Briefing = issue grelhado. Q1 aceite — este Design não a reabre.

Incidente PROD 2026-09-11: operador em `/combo/discovery`, varredura `#862f31de`, parcial top-1 `ALPHA/USDT · 1d · Long` (`RS-B109ED2C80`) com Calmar `1.195.206.471.012.770.100.000.000.000,00`, Max DD `−16,5%`, `30 · 100%`. Walk-forward já era **NO-GO** (Sharpe IS 0,31). Operador promoveu como «melhor agora».

Causa: a curva de equity da Descoberta no `combo_optimizer` é uma lista por negócio, sem `DatetimeIndex`. `calculate_cagr` cai no ramo «cada ponto = 1 dia» (`len(equity)/365`). 30 negócios + capital inicial ≈ 31/365 de ano; retorno composto +16.951% vira CAGR `1.97e26` e Calmar `1.195e27`. `fmtNum` formata qualquer finito como `pt-BR` com 2 casas — 27 dígitos. `oos_verdict` já vai gravado em `metrics`; Acompanhar e Decidir não o pintam.

Com calendário da janela (treino 2020-10-10 → 2024-02-01, ~3,3 anos) o Calmar honesto cai para ~22 — ainda alto frente ao típico 1–3. Por isso Q1 (todo GO acima de todo NO-GO) é load-bearing, não só o conserto do `1e27`.

Operador: administrador da Descoberta em `/combo/discovery` (modos Montar / Acompanhar / Decidir já vivos, #852).

Regiões clonadas (só estas): shell AppNav + heading + 3 modos + Acompanhar parciais + Decidir linhas. Montar (Preflight / Rascunho) entra no clone para landmarks; sem delta visual.

## Goals / Non-Goals

**Goals:**

- CAGR/Calmar da Descoberta com denominador de calendário da janela.
- Célula absurda ou não finita = `N/A`; não disputa 1º lugar.
- Selo `GO` / `NO-GO` visível nas parciais (Acompanhar) e no Decidir, sem abrir gráfico nem promover.
- Todo `GO` acima de todo `NO-GO`; `NO-GO` permanece na lista com selo.
- Copy da coluna: Calmar ≠ retorno; `30 · 100%` = negócios / cobertura.

**Non-Goals:**

- Amostra insuficiente (#876).
- Achatar métricas no favorito (#897).
- Redesign dos 3 modos (#852).
- Trocar universo de símbolos ou split 70/30.
- Backfill da varredura `#862f31de`.
- Ensinar Calmar na landing / Ajuda.
- Travar o clique Promover.

## Recorte

- **Audience:** administrador da Descoberta, varredura em curso ou recém-terminada, a ler parciais/Decidir para promover.
- **Outcome:** não promover um NO-GO só porque a coluna Calmar parece um jackpot.
- **Direction:** clone+delta da rota viva `/combo/discovery`; Operate; refinement (não new-work). Tokens `DESIGN.md` Binance, sem reescrever.
- **Scope:** Acompanhar parciais + Decidir linhas (selo, ordem, célula, copy). Montar intacto.

## Decisions

### 1. Anos = calendário da janela de evidência

No caminho da Descoberta, CAGR usa `years = (end_at − start_at).days / 365` da janela in-sample persistida (`[start_at, end_at)`), ou os timestamps da mesma curva/velas. Não `n_trades/365` nem `len(equity_curve)/365`. Calmar continua CAGR ÷ |Max DD| com Max DD fração 0–1.

O sítio barato: ao persistir ranking em `discovery_tasks` / ao calcular métricas pesadas no otimizador da Descoberta, passar o span de calendário (já conhecido no resultado) em vez de indexar a lista de negócios como dias. Helper partilhado MAY corrigir `calculate_cagr` quando o índice não é datetime — detalhe de Apply, desde que a Descoberta deixe de anualizar por negócio.

Rejeitado: backfill de `#862f31de`. Rejeitado: mudar o split 70/30.

### 2. Teto antes de gravar e antes de formatar

Antes de persistir `calmar_ratio`/`cagr` e antes de `fmtNum` `pt-BR`: não finito (`NaN`, `±Inf`) **ou** `|Calmar| > 1000` → null / célula `N/A`. `|CAGR| > 100` (10.000% ao ano) → null na coluna de ranking. O honesto ~22 do incidente **permanece visível** com 2 casas (`22,00`). Calmar `1,20` continua `1,20`, nunca `N/A`.

A UI sanitiza também valores já gravados (ALPHA `1e27` legado → `N/A` sem recalcular a varredura). N/A não disputa 1º lugar (ordena com os outros N/A da mesma classe de veredito, depois de todo finito).

Teto 1000: típico 1–3; honesto do incidente ~22; `1e27`/`1e38` caem. Alternativa rejeitada: teto 100 (cortaria pouco e não muda o incidente). Alternativa rejeitada: só o conserto de calendário, sem teto — a coluna ainda formataria qualquer finito restante como dinheiro.

### 3. Classe GO acima de não-GO; entre iguais, Calmar já corrigido

`rank_eligible` (parciais top-5 e Decidir) ordena elegíveis assim:

1. Classe walk-forward: `GO` acima de todo não-`GO` (`NO-GO`, `ERROR`, veredito ausente).
2. Dentro da classe: métrica selecionada (Calmar default, pós-calendário e teto) descendente, depois negócios descendente, depois `result_id` ascendente.

Só um `GO` ocupa o 1º lugar quando existe algum `GO`. `NO-GO` permanece na lista, com rank global abaixo de todo `GO`. Entre `NO-GO`s, Calmar (já corrigido) → negócios → id. Elegibilidade 30/90% **não** muda: um `NO-GO` com 30 negócios continua elegível e promovível.

Veredito ausente não inventa `GO` e não compete com `GO` pelo 1º.

### 4. Selo na linha; Promover continua

Acompanhar parciais e Decidir pintam `oos_verdict.status` quando for `GO` ou `NO-GO`, no próprio candidato — chip, não tooltip-only. Sem abrir gráfico, sem «+ detalhes», sem o diálogo Promover.

- `GO`: chip informativo azul (`#3b82f6` / `#93c5fd`), distinto do verde Long.
- `NO-GO`: chip danger (`#f6465d` / `#ff8294`), distinto do âmbar `Baixa amostra` / `Amostra insuficiente`.

Promover num `NO-GO` elegível **permanece** (Descoberta já é só admin; Combo já tem override). Este card não trava o clique.

Payload do leaderboard/parciais expõe `oos_verdict.status` no nível da linha (hoje só dentro de `metrics`). Detalhe de Apply: campo top-level vs leitura de `metrics.oos_verdict.status`.

### 5. Copy mínima da coluna

Cabeçalho Calmar: texto visível `Calmar` + hint `CAGR ÷ Max DD`; `aria-label` = `Calmar (CAGR anual do calendário ÷ Max DD)`. Cabeçalho `Trades/cobertura`: hint `negócios · velas`; `aria-label` = `negócios / cobertura`. Nota sob o Decidir: «Calmar não é retorno… `30 · 100%` = negócios e cobertura, não taxa de acerto.» Win rate fica em «+ detalhes». Sem página de Ajuda, sem landing.

## Apply contract

- Apply (pós `Pronto para Dev`) lê este `design.md` + `frontend/public/prototypes/card-896-discovery-calmar-nogo/index.html` como spec de UI; API é fonte de dados, não de layout.
- Fidelidade bloqueante: landmarks `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`; tokens `DESIGN.md` (não reescrever); 8 pares `COPIED:start/end` no proto.
- Worker/métricas: denominador de anos = calendário da janela in-sample; teto `|Calmar|>1000` ou não finito → null antes de gravar.
- `rank_eligible`: classe `GO` antes de não-`GO`; N/A não toma 1º; entre iguais, Calmar → negócios → id.
- Frontend: `fmtNum` sanitiza absurdo legado → `N/A`; selo GO/NO-GO nas parciais e no Decidir; copy/aria das colunas; Promover intacto no NO-GO elegível.
- Sem backfill `#862f31de`. Sem redesenhar os 3 modos. Sem travar Promover. Sem #876/#897/#852.
- Desvio do proto: path + elemento + motivo no PR; sem registro = bloqueio.

## Risks / Trade-offs

- [Calmar honesto ~22 ainda parece «melhor» que 1,20] → Q1 (GO acima de NO-GO) é a carga; o teto sozinho não basta.
- [Valores legados `1e27` nas varreduras antigas] → UI sanitiza display; sem backfill. Ranking de sweeps antigos ganha selo + classe se `oos_verdict` já estiver em `metrics`.
- [Veredito ausente] → sem selo, não compete com GO pelo 1º; não inventar GO.
- [Verde/vermelho] → GO usa azul informativo, não `trading-up`; NO-GO usa danger de rejeição, não o âmbar da amostra.

## Migration Plan

Sem Alembic. Sweeps novos gravam Calmar de calendário + teto. Leituras antigas: UI `N/A` para absurdo; ordem GO-first aplica-se a qualquer sweep cujo `metrics` já traga `oos_verdict`. Rollback: worker antigo volta a anualizar por negócio; UI antiga volta a formatar 27 dígitos — por isso o teto no formatador é o cinto.

## Open Questions

Nenhuma de produto (Q1 aceite; fronteira vazia). Campo top-level vs `metrics.oos_verdict` = Apply.

## Prototype

- **URL:** https://dev.criptofarol.com.br/prototypes/card-896-discovery-calmar-nogo/
- **Caminho:** `frontend/public/prototypes/card-896-discovery-calmar-nogo/index.html`
- **Digest (sha256):** `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` · 37328 bytes · servido == local (`cmp` clean)
- **Copiados vs gerados:** 8 pares `COPIED:start/end` · 7180 bytes copiados · 30148 bytes gerados/delta
- **Base:** rota viva `/combo/discovery` (shell autenticado 224px + heading + 3 modos + Acompanhar + Decidir). Delta só: célula Calmar honesta/`N/A`; selo GO/NO-GO; ordem (todo GO acima de todo NO-GO); copy da coluna.
- **Fluxos:** default Acompanhar (parciais: GO `1,20` no 1º, ALPHA NO-GO `22,00` no 4º com `30 · 100%`, N/A no 5º); Montar com landmarks Preflight/Rascunho; Decidir com GO acima de NO-GO, Promover no NO-GO, `Baixa amostra` intacta.
- **Viewports:** 1440×900 e 390×844.

## Prototype Validation

- **URL:** https://dev.criptofarol.com.br/prototypes/card-896-discovery-calmar-nogo/ — HTTP 200, 37328 bytes, sha256 `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08`, disco == HTTPS (`cmp` clean).
- **Comando:** `playwright-cli` 0.1.19 headed sob `xvfb-run -a` (`PLAYWRIGHT_MCP_SANDBOX=false`, Chromium 1243). Um `run-code` por viewport com `page.goto` + asserts + `page.screenshot` na mesma sessão. Wrapper `playwright-cli-headed` ausente neste host (`/usr/local/bin/playwright-cli-headed` não existe).
- **Viewports:** 1440×900 (20/20 PASS) e 390×844 (18/18 PASS). 0 console error, 0 pageerror, 0 ≥400.
- **Asserts (todos PASS):** landmarks visíveis `Descoberta de estratégias swing` / `Preflight` / `Rascunho de varredura` (Preflight+Rascunho após tab Montar, igual ao vivo com sweep); Acompanhar default GO 1º Calmar `1,20`; ALPHA NO-GO selo `NO-GO` + Calmar `22,00` (não `1e27` nem 27 dígitos); célula absurda `N/A`; todo GO acima de todo NO-GO nas parciais e no Decidir; selo visível sem gráfico/promover (mobile: selo no viewport); `30 · 100%` + aria/copy `negócios / cobertura` (não win rate); Promover enabled no NO-GO elegível; sem painel ANTES/DEPOIS; sem erros bloqueantes.
- **Re-gate (1×):** CSS mobile wrap do chip (flex row ≤720px escondia o selo no crop). Re-gate verde. PNGs: `.impeccable/critique/896-autor-desktop-1440x900.png`, `.impeccable/critique/896-autor-mobile-390x844.png`.
- **Detector Impeccable:** `[]`.

## Impeccable

Operate; refinement (não new-work). Pipeline: context → shape → prototype → critique (autor) → detector → browser gate. Assessment A/B **não** spawnados neste filho — o pai spawna a dupla. `DESIGN.md` não reescrito. Surface brief: not-found (rota existente).

### Shape

- Job: administrador da Descoberta a comparar candidatos para promover.
- Outcome: veredito e Calmar honesto na linha; GO no topo.
- Direction: clone+delta; chips de selo no candidato; hints no `<th>`.
- Untouched: Montar, 3 modos, CTA Promover, amostra insuficiente, favoritos.
- Assumptions (sem AskUser): teto `|Calmar|>1000`; GO azul / NO-GO danger; veredito ausente ≠ GO.

## Design Critique

Dupla A/B (com-tela) PASS. Sem P0/P1 de produto. Sem rework (teto 1+1+1: autor + dupla + 1 rework só com P0 novo). P3 aceitos aqui, resolvidos no Apply.

- **P0** — nenhum. Tokens parseáveis `UI impact: affected` / `live_route: /combo/discovery` / `surface: existing`. Index = clone+delta (não galeria / ANTES-DEPOIS). Landmarks 3/3. 8 pares COPIED. Digest disco == HTTPS `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` · 37328 bytes. Rota viva sem sessão → `/login` (não conta).
- **P1** — nenhum. A e B: GO 1º Calmar `1,20`; ALPHA NO-GO selo + `22,00` (não `1e27`); célula absurda `N/A`; todo GO acima de todo NO-GO; selo visível sem gráfico; `30 · 100%` = negócios/cobertura; Promover enabled no NO-GO elegível. Detector `[]`.
- **P3** (aceitos, Apply) — Montar condensado vs vivo; Decidir sem filtros/modais/+detalhes; Promover outline vs fill `DESIGN.md`; mock 16/16 vs 5 linhas; `#PF-896-24` no chrome copiado; `oos_verdict` top-level vs nested; chip GO/NO-GO full-width (desktop block + wrap mobile ≤720px — Apply encolhe).
- **Disposition:** P3 no Apply; não reabrir grelha; Q1 não reaberta. Sem segundo rework (nenhum P0 novo).
- **Proto:** https://dev.criptofarol.com.br/prototypes/card-896-discovery-calmar-nogo/
- **Snapshots:** `.impeccable/critique/896-card-896-discovery-calmar-nogo.md` (autor) · `896-card-896-discovery-calmar-nogo-assessment-A.md` · `896-card-896-discovery-calmar-nogo-assessment-B.md`
- **Spawns:** 1 autor + Assessment A + Assessment B.

Design Agent verdict: PASS
