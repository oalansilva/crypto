## Context

Card **#1008**, Status=Design. Briefing = issue grelhado (Problema, História, Entra, Não entra). Sem reentrevista. Relacionado a #1001 (Done). Pré-requisito de #1006. #1007 Cancelado.

Hoje o loop do scalp monta `state` por REST: 2 saldos assinados + 1 `GET /api/v3/ticker/bookTicker`, depois o Jev (~600 ms), depois a ordem. O livro que o Jev viu chega com 700–900 ms — quase metade do horizonte do #1001 (~2 s). «2 s» é esse horizonte, não o tamanho da memória deste card. O Farol já tem `binance_realtime_connector` (`@ticker` top-pares, com fallback REST no disconnect); o scalp não o usa. `LiveExchange.book()` chama REST. `Book` só tem bid/ask, sem qty nem `age_ms`. Queda de livro hoje dá `skip_reason=no_book` sem cancelar resting e sem copy no painel.

Módulo vigente: `frontend/src/components/monitor/ScalpModule.tsx` (estados `off|on|kill|nokey`). Catálogo HEAD: `/monitor` (`table.signals` + Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia). Copy visível no Entra («livro indisponível» no painel do scalp) ⇒ **com-tela**.

Impeccable (Operate): audience = operador autenticado com o scalp ligado no Monitor; outcome = ver que o livro não está fresco e que o loop não envia; direction = clone `/monitor` + delta de copy/estado no módulo existente, sem redesign da board, Operar, interruptor, T/clip/kill; `DESIGN.md` permanece autoridade visual.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rúbrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. `COPIED:start`/`COPIED:end` nas regiões clonadas. Delta fora desses blocos: estado/copy «livro indisponível» no módulo Scalp BTCUSDT (interruptor, T, clip, kill, board e Operar intactos). Sem extra `/favorites` / landing (copy visível só nesta superfície). Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Um stream por processo (não por utilizador) de `bookTicker` + `aggTrade` BTCUSDT, partilhado por todos os utilizadores com o scalp ligado.
- O ciclo lê toque (bid, ask, bid_qty, ask_qty) e janela deslizante curta (~5 s rascunho) da memória, não REST.
- Saldos REST assinados fora do caminho crítico (cache curta).
- `age_ms` > 500 ms bloqueia envio. Queda do WS: não envia; cancela resting deste bot (não deixa ordem fora do toque); tenta religar; painel mostra «livro indisponível»; sem fallback silencioso para REST velho.
- Critérios: scalp ligado → nenhuma REST `/api/v3/ticker/bookTicker` por ciclo; ordem só com `age_ms` ≤ 500; dois utilizadores ligados = um único stream.
- Copy visível no painel do `/monitor`; estados `off|on|kill|nokey` permanecem.

**Non-Goals:**

- Features/agregados 1–5 min (#1006).
- Tamanho exacto da memória se ~5 s não chegar ao #1006 (Design deste card e do #1006).
- Calibração / registo de ciclos (#1007, Cancelado).
- Livro L2+ (`depth`).
- Mudar relógio do Jev (~1 s), post-only, T, clip, kill, GTX, interruptor.
- Trocar o conector WS do resto do Farol (`@ticker` top-pares).
- Superfície nova, extra `/favorites` / landing, painel ANTES/DEPOIS.

## Decisions

1. **Stream dedicado BTCUSDT no mesmo processo do conector existente — não por utilizador, não substitui o `@ticker`.**
   Um combined stream `btcusdt@bookTicker` + `btcusdt@aggTrade`, um por processo, memória partilhada. Reutiliza o stack de `binance_realtime_connector` (reconnect, backoff, heartbeat). O stream `@ticker` top-pares que alimenta o resto do Farol **não muda** (incluindo o fallback REST dele, que é do Monitor, não do scalp).
   Alternativa rejeitada — **um WS por utilizador**: o Entra manda um stream por processo; dois utilizadores ligados = um único stream.
   Alternativa rejeitada — **piggyback no `@ticker`**: não traz `bidQty`/`askQty` nem `aggTrade`; no disconnect o conector vigente faz REST — exactamente o fallback silencioso que este card proíbe no caminho do scalp.
   Alternativa rejeitada — **trocar o conector do resto do Farol**: Não entra.

2. **Fail-closed no caminho do scalp: memória ou não envia; nunca REST `/api/v3/ticker/bookTicker` por ciclo.**
   Toque e janela vêm só da memória. `age_ms` = relógio de parede desde o último evento `bookTicker` em memória. `age_ms` > 500 ou stream caído ⇒ não envia. Sem fallback silencioso para REST velho (nem para «confirmar» o toque).
   Alternativa rejeitada — **REST só quando o WS cai**: é o fallback silencioso; o critério «nenhuma REST bookTicker por ciclo com o scalp ligado» cai.
   Alternativa rejeitada — **tratar «2 s» como tamanho da memória**: os 2 s são o horizonte do #1001; a janela deste card é ~5 s rascunho.

3. **Queda do WS cancela resting deste bot — não deixa ordem no livro fora do toque.**
   Sem livro fresco não há como provar que a resting ainda está no toque, e REST bookTicker está proibido. O critério «queda do WS não deixa ordem no livro fora do toque» manda cancelar as resting **deste** bot (prefixo `cfscalp_`) enquanto o livro está indisponível, e religar o stream. Operar / ordens que não são deste bot ficam.
   Alternativa rejeitada — **esperar o reconnect para comparar o toque**: durante a queda a resting pode ficar fora; viola o critério.
   Alternativa rejeitada — **REST bookTicker para ver se o toque mudou**: fallback silencioso.

4. **Painel: copy «livro indisponível» na linha de estado existente; `data-state` continua `on`; interruptor fica Ligado.**
   Não é quinto estado do switch. `off` / `kill` / `nokey` permanecem como no clone #1001. Quando o scalp está ligado e o livro não está fresco (stream caído **ou** `age_ms` > 500), `status_text` é exactamente «livro indisponível». Quando o livro volta a fresco, volta a copy «Ligado — …». Sem banner novo estilo kill (redesenho). `aria-live="polite"` na linha de estado para o operador ouvir a queda sem mudar o foco.
   Alternativa rejeitada — **`data-state=nobook` que desliga o switch visualmente**: mistura «o utilizador desligou» com «o livro caiu»; o Entra não mexe no interruptor.
   Alternativa rejeitada — **superfície nova / extra `/favorites`**: copy visível só no painel do scalp em `/monitor`.

5. **Saldos REST fora do caminho crítico; janela de trades ~5 s; #1006 não entra.**
   USDT/BTC livres continuam assinados por utilizador, com cache curta (refresh a cada N s ou após fill). A janela `aggTrade` é deslizante ~5 s (rascunho); não guarda 1–5 min. Features/agregados do Jev = #1006. Se ~5 s não chegar ao #1006, o tamanho exacto fecha no Design daquele card.
   Alternativa rejeitada — **user-data WS para saldos**: fora do Entra.
   Alternativa rejeitada — **buffer 1–5 min neste card**: Não entra.

## Risks / Trade-offs

- [Risco] Apply chama REST bookTicker «só no gap» → fallback silencioso. Mitigação: spec + critério observável; tasks 2.x.
- [Risco] Apply piggyback `@ticker` e herda REST no disconnect do conector. Mitigação: decisão 1; stream dedicado; o fallback REST do `@ticker` **não** alimenta o scalp.
- [Risco] Queda WS deixa resting no livro. Mitigação: decisão 3; cancelar `cfscalp_*` enquanto livro indisponível.
- [Risco] Painel inventa quinto estado ou redesenha kill/T/clip. Mitigação: decisão 4; proto `data-book` separado de `data-state`.
- [Risco] Clone perde landmark `7d`. Mitigação: `COPIED` + `design_clone_gate.classify` no index canónico.
- [Risco] Copy «livro indisponível» noutro sítio (toast, Operar, Favoritos). Mitigação: só a linha de estado do módulo scalp.

## Migration Plan

Sem migração de schema de favoritos/sinais. Memória do stream é processo-local (não Postgres). Rollback = voltar o ciclo a REST bookTicker (#1001) e esconder a copy; interruptor/T/clip/kill inalterados. O conector `@ticker` do resto do Farol não entra no rollback deste card.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-1008-scalp-ws-estado-fresco/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/monitor` (`index.html`): módulo Scalp BTCUSDT intacto (interruptor, T, clip, inventário, calibração, P&L, kill, nokey); quando ligado e o livro não está fresco, a linha de estado mostra exactamente «livro indisponível»; interruptor permanece Ligado; board e Operar intactos; landmarks `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia.
- Loop: um stream por processo `bookTicker`+`aggTrade` BTCUSDT; ciclo lê memória; `age_ms` > 500 ou stream caído ⇒ não envia; cancela resting deste bot; sem REST `/api/v3/ticker/bookTicker` por ciclo com o scalp ligado; dois utilizadores = um stream.
- Sem redesenho de interruptor, T, clip, kill, GTX, relógio ~1 s, post-only, board, Operar.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Nome interno do cache (`age_ms`, `book_available`, deque de `aggTrade`).
- N exacto da cache de saldos (segundos vs após fill).
- Como o helper de memória vive junto de `binance_realtime_connector` (módulo irmão vs método novo) — desde que não substitua o `@ticker`.
- Formato JSON extra em `/api/scalp/status` (campos além de `status_text`).
- Wording da copy «Ligado — …» quando o livro está fresco (incumbente #1001).
- Fixtures do proto («Simular livro indisponível»).
- Detector `side-tab` nos cards mobile — incumbente do clone.
- Clip Operar/Ver Trades a 1280 — incumbente da board.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-1008-scalp-ws-estado-fresco/` → `frontend/public/prototypes/card-1008-scalp-ws-estado-fresco/index.html`. Clone da página viva `/monitor` + delta «livro indisponível». Landmarks: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia.
- Extras: nenhum (copy visível só no painel do scalp em `/monitor`). Sem painel ANTES/DEPOIS no index.
- `cp`/clone = copied; delta livro indisponível = generated.

## Prototype Validation

- **Comando (autor):** Playwright Chromium headless contra `http://127.0.0.1:8878/prototypes/card-1008-scalp-ws-estado-fresco/` (static `frontend/public`; Caddy DEV ainda 404 este worktree). Desktop 1280×800 e mobile 390×844. Fluxo: default desligado → ligado+livro fresco → stream caído / «livro indisponível» (interruptor Ligado) → livro fresco → kill → nokey. 208 asserts, 0 page errors. `curl`/HTTP 200 não substitui. Script: `.impeccable/critique/1008-autor-gate.py`.
- **URL canónica:** `frontend/public/prototypes/card-1008-scalp-ws-estado-fresco/index.html` (HTTP DEV após o pai publicar: `https://dev.criptofarol.com.br/prototypes/card-1008-scalp-ws-estado-fresco/`). Sem extras.
- **Digest (UTF-8 sha256, gate deste autor):**
  - `index.html` `294b038c8d24b23c725523b9721b909406d0e54afbce47c98e1c5b3046aff607` · 46162 B = 21077 copied + 25085 generated. Pares `COPIED:start`/`COPIED:end`: 10/10; soma UTF-8 copiada 21077 (> 0). T5 mede só este index.html. `design_clone_gate.classify` = PASS; landmarks `/monitor` ok.
- **browser_gate:** PASS · viewports 1280×800 e 390×844 · screenshots em `.impeccable/critique/1008-autor-*-off|on-fresh|on-unavailable|kill|nokey.png`.
- **Detector Impeccable:** `detect.mjs --json` → `[]` (exit 0).

## Open Questions

Nenhuma. Fronteira veio grelhada. Os *como* do Entra fecham nas decisões 1–5.

## Impeccable

Mode Operate. Snapshot longo em `.impeccable/critique/`. `DESIGN.md` não sobrescrito.

- audience: operador autenticado no Monitor com o scalp ligado
- outcome: ver «livro indisponível» e que o loop não envia enquanto o stream não está fresco
- direction: clone `/monitor` + copy na linha de estado; tokens incumbentes
- scope: WS/memória + copy; board, Operar, interruptor, T/clip/kill intactos

Design Agent verdict: PASS

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla + 1 rework. Sem P0 novo de produto ⇒ sem segundo rework; P3 aceitos aqui, resolvidos no Apply.

Relatórios: `.impeccable/critique/1008-card-1008-scalp-ws-estado-fresco.md` (autor) · `1008-card-1008-scalp-ws-estado-fresco-assessment-A.md` · `1008-card-1008-scalp-ws-estado-fresco-assessment-B.md`. Snapshot T7 = Assessment A. Verdict A/B: **PASS**.

**P0:** nenhum  
**P1:** nenhum  
**P2:** nenhum (kill sem live region própria = incumbente #1001; linha de estado já tem `aria-live="polite"`)

**P3 (aceitos, detalhe de Apply — não reabrir como P0/P1):**
- Fixtures proto («Simular livro indisponível» / «Livro fresco» / kill / nokey).
- Clip Operar/Ver Trades a 1280/1440; busca truncada a 390; thead «Gráfico» + `data-landmark="7d"`; mobilebar BTCUSDT 4h — incumbente do clone.
- `DELTA:start=0`; cancel resting sempre enquanto o livro está indisponível vs Entra «se o toque tiver mudado» (fail-closed, não é tela).
- Nome interno do cache, N da cache de saldos, helper vs método no conector, campos JSON extra de `/api/scalp/status`.

**Disposition:** P3 → Apply. Não reabrir Qs grelhadas, interruptor/T/clip/kill, #1006/#1007, extra `/favorites` / landing.

**Tokens (rubrica D4):** `UI impact: affected` · `live_route: /monitor` · `surface: existing`. Clone `/monitor` + copy exacta «livro indisponível» com interruptor Ligado. Proto HTTPS 200, digest disco == URL. Landmarks e `copied` 21077 PASS. Detector `[]`.

Spawns: 3
proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)
proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)
