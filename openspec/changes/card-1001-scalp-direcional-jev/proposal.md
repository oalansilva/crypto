## Why

Quem usa o Farol em produção só consegue mandar ordem Spot com clique humano a mercado no Operar: não há um scalp direcional limitador (que não cruza) com teto de dólares, então o Jev não chega a valer como leitura que o Farol executa.

## Problema

Quem usa o Farol em produção só consegue mandar ordem Spot com clique humano a mercado no Operar: não há um scalp direcional limitador (que não cruza) com teto de dólares, então o Jev não chega a valer como leitura que o Farol executa.

## História

Como utilizador do Farol com chave Spot em Meu Perfil, quero ligar um scalp direcional **em produção, no mesmo recorte das outras features**, que leia o livro BTCUSDT à vista, pergunte ao Jev e poste (ou cancele/segure) uma ordem limitadora que não cruza **na minha conta Binance**, com teto no USDT livre (máx. US$ 100), para ver se o modelo acerta o lado nos ~2 s seguintes — e quero poder **desligar a qualquer momento**, sem misturar com o clique do Operar e sem vender isto como estratégia lucrativa.

## Entra

**Quem e onde**
- Feature de produto do Farol: entra na publicação de produção. Não é processo lab. Não fica só no ambiente de desenvolvimento. Não é «só Alan opera».
- Ordens deste scalp saem da conta Binance **de cada utilizador que ligar**, com a mesma chave Spot de Meu Perfil que o Operar já usa. Sem saque. Quem não ligar não manda ordem deste scalp.
- Sem chave Spot em Meu Perfil → não envia. Não usa conta da casa. Não pede um terceiro tipo de chave.
- Interruptor é **por utilizador**: ligar o meu não liga o dos outros.
- O resto do Farol (Monitor, Operar, candles) continua a funcionar com este scalp desligado; ligar o scalp não substitui o Operar.
- Onde o interruptor e o painel deste scalp aparecem no Farol (junto do Operar vs superfície nova): Design.
- Se o texto do Farol que hoje diz que não é bot 24/7 muda neste card: Design.
- Como este scalp e o Operar (clique a mercado) convivem na mesma conta Binance do utilizador: Design. Este card não redesenha o Operar.

**Interruptor (ligar / desligar)**
- No Farol publicado há um controlo explícito **por utilizador**: **ligado** ou **desligado**. Não é preciso mexer em código nem reiniciar o Farol para desligar.
- **Desligado (até o próprio utilizador ligar, e depois de desligar):** não envia ordem, não gasta TypeSafe, cancela as ordens **deste** bot que ainda estejam no livro. Inventário e P&L ficam visíveis (histórico). O Farol continua normal.
- **Ligado:** passa a live; o primeiro tick já pode enviar ordem (sem confirmar cada ordem como o Operar).
- O estado **persiste** se o Farol reiniciar: se estava desligado, continua desligado até o próprio utilizador ligar outra vez.
- Kill automático (−2% de T) deixa o módulo no mesmo estado que “desligado” (sem envio, ordens do bot canceladas). Religar depois do kill é de novo o interruptor desse utilizador (não religa sozinho).

**Mercado e chaves**
- Um par: BTCUSDT à vista. Livro e negócios reais da Binance.
- Sem saque. Ordens deste scalp usam a chave Spot de Meu Perfil do utilizador que ligou (a mesma do Operar). Sem conta da casa. Sem terceiro tipo de chave.
- Chave TypeSafe só no ambiente do servidor. Nunca no chat, no card, nem no git. Sem a chave do Jev no ambiente, o live não envia (pode correr o stand-in).
- Capital do teto = USDT livre na Spot **desse utilizador**. Não exige 100,00.

**Teto e kill**
- T = o menor entre US$ 100 e o USDT livre **desse utilizador** (com folga para taxa). Com 99,63, T ≈ 99; o bot não tenta gastar 100.
- Cada ordem ≤ US$ 10.
- Kill do dia deste loop: prejuízo ≤ −2% de T (≈ −US$ 2). Cancela só as ordens do bot, desliga o envio, painel “parado por kill”. Não religa sozinho. Não zera a carteira.

**O que o bot é (analista)**
- Scalp direcional com entrada maker: um lado por vez. Não é formador de mercado (bid e ask ao mesmo tempo).
- Relógio: pedido ao Jev a cada **~1 s** (piso 400 ms, tarde >800 ms). 300 ms era a Monad e é mais rápido que o Jev lento; 1 s alinha com o horizonte de ~2 s. Cancelar ordem desactualizada é imediato (livro), não espera 1 s. Isto não muda taxa vs spread.
- **Sempre ordem limitadora que não cruza** (post-only). Nunca a mercado, nunca “se não preencher manda market”. Na conta normal da Binance à vista a **comissão maker e taker é a mesma** (~0,10%; ~0,075% com BNB): o limit **não** corta esses 10 bp. O que poupa é o **spread** (~0,1–1 bp) e não virar taker por engano. P&L esperado continua pequeno negativo. Clip US$ 10.
- **BNB na Spot:** o desconto da Binance de até 25% nas taxas à vista **continua activo** (FAQ oficial: até nova ordem). Exige BNB na carteira Spot **e** o interruptor “usar BNB para taxas” ligado na Binance — o bot não liga isso. Com desconto: ~0,075% (7,5 bp) em vez de 0,10%. Ainda é muito maior que o spread. O loop **não vende BNB**; BNB não entra no inventário. Sem BNB ou interruptor off → volta a 0,10%.
- Sucesso = calibração (quando diz compra com confiança alta, o mid de ~2 s sobe com que frequência?). P&L é número no painel, não meta. Perda tão visível quanto ganho. O painel não diz “estratégia lucrativa” nem “formador de mercado”.
- Subida do BTC não é ganho. Só lucra na subida se já tiver fill de compra e o preço subir mais que a taxa até vender. Ordem no livro sem fill + preço dispara = perdeu a subida. Se estiver a vender/reduzir, a subida prejudica.

**Como decide comprar ou vender**
1. **Só se o módulo estiver ligado.** Dois relógios:
   - **Jev (direção):** um pedido de cada vez, alvo **~1 s** entre pedidos (piso 400 ms). Horizonte da pergunta ~2 s → cerca de duas olhadelas por janela. Se a resposta passar de **800 ms**, esse ciclo é tarde e **não** envia ordem. Nunca dois pedidos em paralelo.
   - **Livro (proteção):** se o melhor bid/ask andar e a nossa ordem ficar fora do toque, **cancela já**, sem esperar o Jev.
2. O Jev (ou stand-in, para comparar) no mesmo pedido: vantagem acima da taxa nos ~2 s? lado comprar / vender / nenhum? livro tóxico? reduzir agora?
3. O código decide. Hold é o normal. Só posta se lado definido, confiança do lado ≥ 0,7, vantagem acima da taxa, livro não tóxico, e o teto ainda cabe.
4. **Sempre** limitadora no toque: compra no melhor bid; venda no melhor ask; nunca cruza. Se a Binance rejeitar por cruzar, **espera o próximo ciclo** — não manda a mercado. Sem ordem a mercado neste card.
5. Perto do teto, só o lado que reduz. Reduzir manda vender mesmo se o lado ainda for compra. Só vende BTC que este loop comprou.
6. Inventário começa em zero. Piso = BTC livre na largada (poeira). Pedido de venda com inventário zero → segura. Nunca vende o BTC que já estava na conta.

**Registo**
- Cada tick, intenção, ordem e fill fica registado e visível para quem tem este scalp.
- P&L = realizado + não realizado − taxas − custo Jev, só do inventário do bot.

### Critérios observáveis

- Farol a arrancar com o interruptor desligado → nenhuma ordem deste scalp; Monitor e o resto iguais.
- Alguém desliga com o módulo a correr → deixa de enviar, cancela as ordens deste bot no livro, deixa de chamar o Jev; o Farol não cai.
- Reinício do Farol com o interruptor desligado → continua desligado; não volta a enviar sozinho.
- Interruptor ligado → o primeiro ciclo (livro + Jev, quando a resposta chegar a tempo) pode enviar post-only, se as regras e o teto deixarem.
- Jev ainda a responder → não abre segundo pedido. Sem resposta em 800 ms → não envia nesse ciclo. Toque do livro muda com ordem nossa fora → cancela já, sem esperar o Jev.
- Live ligado, Jev compra, confiança ≥ 0,7, vantagem acima da taxa, teto cabe → pode enviar post-only de compra ≤ US$ 10 no melhor bid.
- Jev “nenhum”, vantagem fraca ou confiança < 0,7 → sem ordem nova; cancela resting.
- Inventário do bot = 0 e Jev pede vender → não vende; BTC do piso intacto.
- Exposição do bot = T → recusa compra; nunca pede mais USDT do que o livre.
- Toda ordem deste loop é limitadora post-only. Fill, se houver, é maker. Rejeição por cruzar não vira a mercado nem IOC.
- Prejuízo do dia ≤ −2% de T → mesmo efeito que desligar (sem envio, ordens do bot canceladas); não religa sozinho.
- Sem saque. Chave TypeSafe não aparece no painel nem nos logs em claro.
- Sem posição, só ordem no livro, preço sobe sem fill → não conta como ganho.
- Painel: interruptor visível (ligado/desligado); calibração visível; P&L negativo tão visível quanto o positivo; sem copy de formador de mercado lucrativo.
- Publicação de produção inclui esta feature no mesmo recorte das outras (não fica de fora do lote).
- Sem chave Spot em Meu Perfil, ou interruptor desligado → nenhuma ordem deste scalp na conta desse utilizador.
- Utilizador A liga e B não liga → só A pode ter ordem deste scalp; B não manda.
- Ordem deste scalp sai da chave Spot de Meu Perfil (a mesma do Operar), nunca de uma conta da casa.

## Não entra

- Monitor (cards, estados, Operar a mercado com clique). Este card não redesenha o Operar.
- Futuros, alavancagem, segundo par, RSI/médias/Bollinger, “compra se o Monitor comprar”.
- Bid e ask ao mesmo tempo; “um tick para dentro”.
- Relógio fixo a cada 300 ms. Pedir ao Jev mais depressa que ~1 s (estados repetidos, ciclos tarde).
- Chave TypeSafe no chat, no card ou no git.
- Tratar o BTC antigo como posição do bot; vender o que o bot não comprou neste run.
- Clip > US$ 10; exigir exactamente US$ 100,00.
- Módulo que não dá para desligar sem mexer no servidor; desligar o Farol inteiro para parar o scalper.
- Saque; lucro como critério de sucesso; paper obrigatório 24 h.
- Processo lab, só ambiente de desenvolvimento, ou «só Alan opera».
- Conta Binance da casa ou chave global do Farol para enviar este scalp.
- Pedir uma chave Binance extra além da Spot de Meu Perfil.

## What Changes

- Feature de produção no mesmo recorte das outras: interruptor **por utilizador** no Farol publicado; default **desligado**; persiste após reinício.
- Loop BTCUSDT à vista: lê o livro, pergunta ao Jev (~1 s), posta ou cancela/segura **limitadora post-only que não cruza** na conta Binance do utilizador que ligou (chave Spot de Meu Perfil, a mesma do Operar). Sem saque. Sem conta da casa. Sem terceira chave.
- T = min(US$ 100, USDT livre desse utilizador, com folga para taxa); clip ≤ US$ 10; kill −2% de T (painel «parado por kill», não religa sozinho).
- Inventário só do que este loop comprou. Piso = BTC livre na largada. P&L = realizado + não realizado − taxas − custo Jev, só desse inventário. Sucesso = calibração; P&L visível, não meta.
- Painel no workbench `/monitor` (não superfície nova; não dentro do modal Operar): interruptor ligado/desligado/parado por kill, calibração, P&L (perda tão visível quanto ganho). Sem copy «estratégia lucrativa» nem «formador de mercado».
- Copy que hoje diz «não é bot 24/7» / «confirma cada ordem» deixa de ser absoluta: o default continua a não operar sozinho; o Operar continua a confirmar; o scalp, se ligado, envia sem confirmar cada ordem.
- Operar (MARKET após confirmação) continua intacto na mesma conta; o scalp não o substitui nem o tranca.

## Capabilities

### New Capabilities

- `scalp-direcional-jev`: loop por utilizador (interruptor persistente, Jev ~1 s, livro, post-only que não cruza, T/clip/kill, inventário só deste run, chaves Spot de Meu Perfil, TypeSafe só no servidor, convívio com o Operar na mesma conta).
- `scalp-monitor-panel`: interruptor e painel visíveis no `/monitor` autenticado (estados desligado / ligado / parado por kill; calibração; P&L; bloqueio sem chave Spot).

### Modified Capabilities

- `monitor`: o workbench `/monitor` passa a mostrar o módulo de scalp BTCUSDT sem redesenhar a board (Status, Preço, Distância, Tags, Operar, Par / Estratégia) nem o clique a mercado.
- `landing-conversion-copy`: a copy pública deixa de afirmar «não é bot 24/7» / «sempre confirma cada ordem» como verdade absoluta; admite o scalp opcional no Monitor, default desligado, nunca saque.
- `user-onboarding`: `/help` (fora do `OnboardingGuide`) deixa de dizer só «nao e bot»; admite o mesmo recorte (Operar confirma; scalp opcional no Monitor).

## Impact

- Frontend: painel e interruptor em `/monitor` (`MonitorStatusTab` / shell autenticado); copy em landing v4, `docs/landing-page.md`, `/help` e chrome de Meu Perfil (mesma chave Spot também alimenta o scalp se ligar). Operar (`SpotMarketTradePanel`) não é redesenhado.
- Backend: loop por utilizador (estado persistido, livro BTCUSDT, Jev/stand-in, post-only, cancelamento, inventário, P&L, kill); usa a chave Spot já ligada em Meu Perfil. TypeSafe só no ambiente do servidor.
- Binance: Spot à vista BTCUSDT do próprio utilizador; sem saque; sem conta da casa.
- Protótipo: clone `/monitor` canónico + extras de copy (`landing.html`, `ajuda.html`). Sem painel ANTES/DEPOIS no index.
- Sem futuros, segundo par, formador de mercado, paper 24 h, lab-only, ou chave extra.
