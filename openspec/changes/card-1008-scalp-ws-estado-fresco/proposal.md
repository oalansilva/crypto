## Why

O loop do scalp monta o `state` por REST (saldos + livro) em série; quando a decisão chega, o livro que o Jev viu tem 700–900 ms — quase metade do horizonte actual do #1001 (~2 s). Sem um stream sempre aberto, qualquer feature de fluxo via REST rebenta o orçamento; o Farol já tem `binance_realtime_connector`, mas o scalp não o usa.

Relacionado a #1001 (Done). Pré-requisito de #1006. #1007 (calibração / registo de ciclos) está Cancelado e não será implementado neste momento. Não mexe em interruptor, T, clip, kill, GTX.

## Problema

O loop do scalp monta o `state` por REST, em série: 2 chamadas assinadas de saldo, 1 chamada de livro, depois o Jev (~600 ms), depois a ordem. Quando a decisão chega, o livro que o Jev viu tem 700–900 ms. No horizonte actual do #1001 (~2 s) isso é quase metade da janela. Qualquer feature de fluxo via REST (negócios recentes por ciclo) acrescenta mais um hop e estoura o orçamento. O Farol já tem um conector WebSocket Binance (`binance_realtime_connector`), mas o scalp não o usa. Os «2 s» são esse horizonte do #1001, não o tamanho fixo da memória deste card.

## História

Como operador com o scalp ligado, quero que o livro (melhor bid/ask com quantidades) e os negócios recentes de BTCUSDT que alimentam o Jev venham de um stream sempre aberto, para o pedido sair com dados frescos no horizonte actual do #1001 (~2 s), sem pedir livro/trades extra à Binance por ciclo. Os 2 s são esse horizonte, não o tamanho da memória deste card.

## Entra

- Um stream por processo (não por utilizador) de `bookTicker` e `aggTrade` de BTCUSDT, partilhado por todos os utilizadores com o scalp ligado.
- O loop lê o toque (bid, ask, bid_qty, ask_qty) e uma janela deslizante curta de negócios da memória, não por REST. Rascunho: últimos ~5 s. Não fixa 2 s. Não guarda 1–5 min neste card.
- Saldos continuam por REST assinado (por utilizador), mas fora do caminho crítico do ciclo (cache curta, refresh a cada N s ou após fill).
- Se o stream cair: o ciclo não envia ordem (segura), cancela resting deste bot se o toque tiver mudado, tenta religar; painel mostra «livro indisponível». Sem fallback silencioso para REST velho.
- Idade do toque (`age_ms`) entra no ciclo; se > 500 ms, o ciclo não envia.
- Critérios: com o scalp ligado, nenhuma chamada REST a `/api/v3/ticker/bookTicker` por ciclo; ordem só sai com `age_ms` ≤ 500; queda do WS não deixa ordem no livro fora do toque; dois utilizadores ligados usam um único stream.

## Não entra

- Enriquecer o `state` do Jev com as features e agregados de 1–5 min (é #1006).
- Tamanho exacto da memória se a janela curta não chegar aos agregados do #1006: Design deste card e do #1006 (facto já no #1006).
- Calibração / registo de ciclos (#1007, Cancelado; não será implementado neste momento).
- Livro L2+ (`depth`); só toque + trades.
- Mudar o relógio do Jev (~1 s), post-only, T, clip, kill.
- Trocar o conector WS existente do resto do Farol.

## What Changes

- Um stream por processo (não por utilizador) de `bookTicker` + `aggTrade` BTCUSDT, partilhado por todos os utilizadores com o scalp ligado. Reutiliza `binance_realtime_connector`; não substitui o conector `@ticker` do resto do Farol.
- O ciclo lê toque (bid, ask, bid_qty, ask_qty) e janela deslizante curta (~5 s rascunho) da memória, não REST. Saldos REST ficam fora do caminho crítico.
- `age_ms` do toque entra no ciclo; se > 500 ms, não envia. Queda do WS: não envia, cancela resting deste bot se o toque mudou, tenta religar; **sem** fallback silencioso para REST velho.
- Painel do scalp no `/monitor` mostra «livro indisponível» quando o stream está caído ou o toque está velho. Interruptor, T, clip, kill, GTX, relógio ~1 s e post-only não mudam.
- Critérios observáveis: scalp ligado → nenhuma REST `/api/v3/ticker/bookTicker` por ciclo; ordem só com `age_ms` ≤ 500; queda WS não deixa ordem no livro fora do toque; dois utilizadores ligados = um único stream.

## Capabilities

### New Capabilities

- `scalp-ws-fresh-state`: stream partilhado `bookTicker` + `aggTrade` BTCUSDT, memória de toque + janela curta, `age_ms`, fail-closed sem REST velho, um stream por processo.

### Modified Capabilities

- `monitor`: o módulo Scalp BTCUSDT já no workbench `/monitor` passa a mostrar «livro indisponível» quando o stream cai ou o toque está velho; board, Operar, interruptor, T/clip/kill não são redesenhados.

## Impact

- Backend: loop do scalp deixa de chamar REST `/api/v3/ticker/bookTicker` no caminho crítico; lê memória do stream partilhado; saldos REST com cache curta; painel `/api/scalp/status` expõe disponibilidade do livro (copy «livro indisponível»).
- Frontend: `ScalpModule` no `/monitor` — delta de estado/copy; não redesenha board, Operar, interruptor, T/clip/kill.
- Conector: reutilizar `binance_realtime_connector` (nova subscrição BTCUSDT `bookTicker`+`aggTrade` no mesmo processo); o `@ticker` top-pares do resto do Farol permanece.
- Protótipo: clone `/monitor` canónico + delta «livro indisponível». Sem extra `/favorites` / landing. Sem painel ANTES/DEPOIS no index.
- Sem features 1–5 min (#1006), sem `depth`, sem #1007, sem trocar o conector do resto do Farol.
