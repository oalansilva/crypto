# Tasks — card-1008-scalp-ws-estado-fresco

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Stream partilhado BTCUSDT

- [x] 1.1 — Um stream por processo `bookTicker` + `aggTrade` BTCUSDT, partilhado por todos os utilizadores com o scalp ligado. Dois utilizadores ligados = um único stream.
- [x] 1.2 — Reutilizar `binance_realtime_connector` (reconnect/backoff). Não substituir o `@ticker` top-pares do resto do Farol. Não abrir WS por utilizador.

## 2. Memória no ciclo

- [x] 2.1 — O ciclo lê toque (bid, ask, bid_qty, ask_qty) e janela deslizante ~5 s de `aggTrade` da memória. Com o scalp ligado, nenhuma REST `/api/v3/ticker/bookTicker` por ciclo.
- [x] 2.2 — `age_ms` = relógio desde o último `bookTicker` em memória. `age_ms` > 500 ⇒ não envia. Sem fallback silencioso para REST velho.
- [x] 2.3 — Queda do WS: não envia; cancela resting deste bot (`cfscalp_`); tenta religar. Não deixa ordem deste bot no livro fora do toque. Não cancela Operar.
- [x] 2.4 — Saldos REST assinados (USDT/BTC) fora do caminho crítico: cache curta, refresh a cada N s ou após fill.

## 3. Painel no Monitor

- [x] 3.1 — `ScalpModule` no `/monitor`: quando ligado e o livro não está fresco, a linha de estado mostra exactamente «livro indisponível»; o interruptor permanece Ligado. Alinhado ao proto `frontend/public/prototypes/card-1008-scalp-ws-estado-fresco/index.html`.
- [x] 3.2 — Estados `off` / `kill` / `nokey` e controlos T, clip, kill, board e Operar intactos. Sem rota nova. Sem extra `/favorites` / landing.

## 4. Testes e evidência

- [x] 4.1 — Testes dos critérios: nenhuma REST bookTicker por ciclo com scalp ligado; ordem só com `age_ms` ≤ 500; queda WS cancela resting deste bot; dois utilizadores = um stream; painel «livro indisponível».
- [x] 4.2 — Playwright desktop+mobile do proto (ligado+livro fresco; stream caído / livro indisponível; off/kill/nokey como no clone).
- [x] 4.3 — `openspec verify` desta change.

## 5. Fonte única de frescura (pós-T18)

- [x] 5.1 — Fonte única de frescura: o livro que `/api/scalp/status` expõe (`book_available`, `age_ms`, copy «livro indisponível») MUST ser a mesma memória/frescura que o ciclo usa para enviar/bloquear. Snapshot partilhado escrito pelo processo que consome o WS; API lê snapshot quando não tem stream local.
- [x] 5.2 — Testes unitários do split-brain: status não fica `book_available=false` só porque o loop lock vive noutro processo se o livro do ciclo está fresco; painel fail-closed quando stream do ciclo caído/`age_ms`>500.
