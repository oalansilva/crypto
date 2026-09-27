## Context

Card **#1001**, Status=Design. Briefing = issue grelhado (Problema, História, Entra, Não entra). Sem reentrevista.

Hoje o Farol autenticado manda Spot só pelo **Operar** em `/monitor`: clique humano, MARKET, confirmação por ordem (`SpotMarketTradePanel`). Não há scalp direcional limitador. Jev não chega a valer como leitura que o Farol executa. Catálogo HEAD: `/monitor` (`table.signals` + «Operar»).

Impeccable (Operate): audience = utilizador autenticado com (ou sem) chave Spot em Meu Perfil; outcome = ligar/desligar o scalp na própria conta, ver calibração e P&L, parar (interruptor ou kill) sem derrubar o Monitor; direction = clone `/monitor` + módulo de scalp acima dos KPIs, sem redesign da board nem do Operar; `DESIGN.md` permanece autoridade visual.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. `COPIED:start`/`COPIED:end` nas regiões clonadas. Delta fora desses blocos: módulo Scalp BTCUSDT (interruptor por utilizador + painel calibração/P&L/estados). Extras com copy visível: `landing.html` (landing v4) e `ajuda.html` (`/help`). Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Feature de produção, mesmo recorte das outras. Interruptor por utilizador; default desligado; persiste após reinício.
- Ordens na Spot Binance **desse** utilizador (chave de Meu Perfil, a mesma do Operar). Sem saque. Sem conta da casa. Sem terceira chave.
- BTCUSDT à vista; Jev ~1 s; sempre limitadora post-only que não cruza; T = min(US$ 100, USDT livre); clip ≤ US$ 10; kill −2% de T.
- Inventário só do que este loop comprou. Sucesso = calibração. P&L visível, não meta.
- Painel no `/monitor`: ligado / desligado / parado por kill; calibração; P&L negativo tão visível quanto o positivo.
- Copy «não é bot 24/7» deixa de ser absoluta (ver decisão 2).
- Operar continua; ligar o scalp não o substitui.

**Non-Goals:**

- Redesign da board do Monitor nem do modal Operar.
- Futuros, alavancagem, segundo par, RSI/médias/Bollinger, «compra se o Monitor comprar».
- Formador de mercado (bid e ask ao mesmo tempo); relógio 300 ms.
- Chave TypeSafe no git/chat/painel; conta da casa; chave extra.
- Vender BTC que o bot não comprou neste run; clip > US$ 10; exigir US$ 100,00.
- Lab-only, só-dev, «só Alan opera»; lucro como critério; paper 24 h.

## Decisions

1. **Interruptor e painel no `/monitor`, acima dos KPIs — não superfície nova, não dentro do Operar.**
   O Operar já vive no workbench autenticado `/monitor`. O interruptor é copy visível; Prototype N/A seria recusado. O módulo fica **irmão** da board (faixa persistente no `page` do Monitor, entre o `page-sub` e os KPIs): BTCUSDT à vista, switch, T/clip, calibração, P&L, estado. Não é item de nav novo. Não abre um `/scalp`.
   Alternativa rejeitada — **superfície nova** (`surface: new`, rota fora do catálogo): esconde o default-desligado de quem já está no Monitor; o resto do Farol «continua com o scalp off» fica menos observável. Sem justificativa que bata o clone.
   Alternativa rejeitada — **dentro do modal Operar**: mistura confirmação-por-clique (MARKET) com loop sem confirmar cada ordem; o Entra pede não misturar e não redesenhar o Operar.

2. **A copy «não é bot 24/7» muda neste card.**
   Hoje landing/FAQ/Ajuda dizem que o Farol não é bot 24/7 e que o utilizador confirma cada ordem. Com o scalp ligado isso deixa de ser verdade. A frase nova: **não opera sozinho por omissão** (default desligado; Operar continua a confirmar cada clique); **se ligar o scalp BTCUSDT no Monitor**, esse loop envia limitadoras post-only sem confirmar cada ordem, até desligar ou o kill. Nunca saque. Não é formador de mercado nem estratégia lucrativa.
   Alternativa rejeitada — **não mudar a copy**: mentira de produto no dia em que alguém ligar o scalp.
   Alternativa rejeitada — **trocar por «é um bot 24/7»**: overclaim; o default é off; kill/interruptor param; o Entra proíbe vender 24/7 lucrativo.

3. **Convívio com o Operar: mesma chave, caminhos independentes, sem mutex.**
   Mesma chave Spot de Meu Perfil. Operar = MARKET após confirmação, qualquer par USDT elegível. Scalp = só BTCUSDT, post-only, só inventário deste loop. T recalcula com o USDT **livre** (se o Operar gastar USDT, T encolhe). O scalp nunca tranca o Operar. Kill cancela só ordens **deste** bot. Se o Operar (ou ordem fora do loop) reduzir o BTC livre abaixo do inventário do bot, o painel mostra aviso e o loop clipa o inventário ao BTC livre acima do piso — não vende o piso, não assume o fill do Operar como P&L deste scalp.
   Alternativa rejeitada — **mutex** (desligar Operar enquanto o scalp está on, ou o contrário): o Entra diz que ligar o scalp não substitui o Operar e que o resto do Farol continua.
   Alternativa rejeitada — **posição partilhada na Binance**: misturaria fills do Operar no inventário/P&L do bot (Não entra: só o que este loop comprou).

4. **Chave TypeSafe / Jev.** Só no ambiente do servidor. Sem chave Jev: live não envia; stand-in pode correr. O painel diz «Jev indisponível — sem envio live», nunca mostra o segredo.

5. **Estados visíveis do módulo.** `desligado` (default) · `ligado` · `parado por kill`. Religar após kill = o mesmo interruptor desse utilizador. Sem chave Spot: switch disabled + «Configure a chave Spot em Meu Perfil».

## Risks / Trade-offs

- [Risco] Copy landing/Ajuda fica «não é bot 24/7» absoluta → o live mente. Mitigação: decisão 2; extras `landing.html` / `ajuda.html`; tasks de copy.
- [Risco] Apply mete o switch no modal Operar ou numa rota nova. Mitigação: decisão 1; proto no index `/monitor`.
- [Risco] Mutex Operar↔scalp. Mitigação: decisão 3; spec de convívio; Operar intacto.
- [Risco] Inventário Binance vs inventário do bot quando o Operar vende BTC. Mitigação: clip + aviso; P3 o formato exacto do aviso.
- [Risco] TypeSafe vaza para o painel/logs. Mitigação: critério observável; review.
- [Risco] Landmark `7d` some no clone. Mitigação: `data-landmark="7d"` no COPIED do thead (incumbente HEAD).
- [Risco] Painel vender «estratégia lucrativa». Mitigação: copy ban no spec e no proto.

## Migration Plan

Sem migração de schema de favoritos/sinais. Estado do interruptor = persistência **por utilizador**, default desligado. Rollback = esconder o módulo, cancelar ordens deste bot, interruptor off. Chaves Spot de Meu Perfil não se apagam. Landing/Ajuda revertem a copy se o card não publicar.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-1001-scalp-direcional-jev/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/monitor` (`index.html`): módulo Scalp BTCUSDT acima dos KPIs; interruptor por utilizador; estados desligado (default) / ligado / parado por kill; calibração visível; P&L negativo tão visível quanto o positivo; sem «estratégia lucrativa» / «formador de mercado»; landmarks `table.signals` + Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia; coluna Operar e modal Operar intactos.
- Sem chave Spot: não liga; copy aponta Meu Perfil.
- Landing e `/help`: copy deixa de afirmar bot-24/7 / confirmação-sempre como absoluta (decisão 2).
- Meu Perfil: uma cláusula de que a mesma chave Spot também alimenta este scalp se o utilizador ligar.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Tabela vs JSON do estado persistido (interruptor, inventário, P&L do dia).
- Worker/loop vs request no processo do Farol.
- Cliente HTTP do Jev / stand-in; timeout 800 ms.
- Flag Binance post-only (`GTX` / `timeInForce`) exacta.
- Formato numérico da calibração (n acertos / n sinais).
- Overlay vs faixa do módulo no proto (vivo = faixa no `page`, não modal).
- Aviso de inventário clipado após Operar: wording exacto.
- Detector `side-tab` nos cards mobile — incumbente do clone.
- Clip Operar/Ver Trades a 1280 — incumbente da board.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-1001-scalp-direcional-jev/` → `frontend/public/prototypes/card-1001-scalp-direcional-jev/index.html`. Clone da página viva `/monitor` + delta do módulo scalp. Landmarks: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia.
- Extras: `landing.html` (FAQ/benefício carteira), `ajuda.html` (grelha Carteira). Sem painel ANTES/DEPOIS no index.
- `cp`/clone = copied; delta do scalp + copy 24/7 = generated.

## Prototype Validation

- **Comando (autor):** Playwright Chromium headless (source `frontend/node_modules/playwright`) contra `http://127.0.0.1:8877/prototypes/card-1001-scalp-direcional-jev/` (static `frontend/public`; o Caddy 5176 ainda não lista este worktree). Desktop 1280×800 e mobile 390×844. Default desligado → ligar → simular kill → religar → desligar. 130 asserts, 0 page errors. `curl`/HTTP 200 não substitui.
- **URL canónica:** `frontend/public/prototypes/card-1001-scalp-direcional-jev/index.html` (HTTP DEV após o pai publicar: `https://dev.criptofarol.com.br/prototypes/card-1001-scalp-direcional-jev/`). Extras: `landing.html`, `ajuda.html`.
- **Digest (UTF-8 sha256, gate deste autor):**
  - `index.html` `f05701794415896410db11db13a900334dd91d45061d875fae3720fb0e353cc8` · 44239 B = 21077 copied + 23162 generated. Pares `COPIED:start`/`COPIED:end`: 10/10; soma UTF-8 copiada 21077 (> 0). T5 mede só este index.html. `design_clone_gate.classify` = PASS; landmarks `/monitor` ok.
- **browser_gate:** PASS · viewports 1280×800 e 390×844 · screenshots em `.impeccable/critique/1001-autor-*-off|on|kill.png`.
- **Detector Impeccable:** `detect.mjs --json` → `[]` (exit 0).

## Open Questions

Nenhuma. Fronteira veio grelhada. Os três *como* estacionados no Entra fecham nas decisões 1–3.

## Impeccable

Mode Operate. Snapshot longo em `.impeccable/critique/`. `DESIGN.md` não sobrescrito.

- audience: operador autenticado no Monitor, com ou sem Spot
- outcome: ligar/desligar o scalp na própria conta e ler calibração/P&L/kill
- direction: clone `/monitor` + faixa persistente; tokens incumbentes
- scope: interruptor + painel + copy 24/7; board e Operar intactos

Design Agent verdict: PASS

## Design Critique

Method: dual-agent (A: Assessment A 1001 · B: Assessment B 1001). Sem rework: dupla sem P0/P1 de produto.

**P0:** nenhum  
**P1:** nenhum

**P2 (não bloqueia T5; Design não reabre):**
- Landing ainda tem «quem decide é sempre você» / «não para decidir por você» enquanto o FAQ já admite o loop. Disposition: n/a (A).
- Ajuda: intro carteira sem distinguir Spot/scalp; grelha não diz que, ligado, envia sem confirmar cada ordem. Disposition: n/a (A).
- Kill/status sem `aria-live`. Disposition: n/a (A).
- Sem extra Meu Perfil nesta onda. Disposition: n/a (A).

**P3 detalhe de Apply (aceito, não reabrir como P0/P1):**
- Persistência, worker/Jev/`GTX`, formato da calibração, overlay vs faixa, wording do inventário clipado, clip Operar 1280, `side-tab`.
- Fixtures proto («Simular kill» / «Ver sem chave Spot»).
- Detector `overused-font` Inter nos extras (incumbente landing/Ajuda).
- 404 `posthog-config.js` na landing DEV.
- Estado «Jev indisponível» não mockado no proto.

**Tokens do autor:** ok — `UI impact: affected` · `live_route: /monitor` · `surface: existing`. Clone `/monitor` + faixa; não ANTES/DEPOIS. Landmarks e `copied` 21077 PASS (B). Browser 210 asserts, 0 FAIL (B). Detector canónico `[]` (B).

Snapshot: `.impeccable/critique/` (A: `1001-card-1001-scalp-direcional-jev-assessment-A.md`; B: `1001-card-1001-scalp-direcional-jev-assessment-B.md`). Gist OpenSpec **não** é a crítica.

proxy modelo: design-autor → Grok 4.6 (grok-4.6)  
proxy modelo: Assessment A → Grok 4.6 (grok-4.6)  
proxy modelo: Assessment B → Grok 4.6 (grok-4.6)
