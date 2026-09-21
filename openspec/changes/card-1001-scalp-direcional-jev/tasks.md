# Tasks — card-1001-scalp-direcional-jev

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Persistência e chaves

- [x] 1.1 — Estado do interruptor **por utilizador**, default desligado, persiste após reinício do Farol. Ligar A não liga B.
- [x] 1.2 — Ordens deste scalp usam a chave Spot de Meu Perfil (a mesma do Operar). Sem chave Spot → não envia. Sem conta da casa. Sem terceira chave. Sem saque.
- [x] 1.3 — TypeSafe/Jev só no ambiente do servidor; nunca no painel, logs em claro, chat ou git. Sem chave Jev → live não envia (stand-in MAY).

## 2. Loop BTCUSDT

- [x] 2.1 — Um par: BTCUSDT à vista. Sempre limitadora post-only que não cruza (compra no melhor bid, venda no melhor ask). Rejeição por cruzar espera o próximo ciclo — nunca market/IOC.
- [x] 2.2 — T = min(US$ 100, USDT livre desse utilizador com folga para taxa); clip ≤ US$ 10. Não exige 100,00.
- [x] 2.3 — Jev um pedido de cada vez, alvo ~1 s (piso 400 ms). Resposta >800 ms → não envia nesse ciclo. Toque do livro muda → cancela já, sem esperar o Jev.
- [x] 2.4 — Hold é o normal. Só posta se lado definido, confiança ≥ 0,7, vantagem acima da taxa, livro não tóxico, teto cabe. Perto do teto, só o lado que reduz.
- [x] 2.5 — Inventário começa em zero. Piso = BTC livre na largada. Só vende BTC que este loop comprou. Inventário 0 + Jev vende → segura.
- [x] 2.6 — Kill −2% de T: cancela só ordens deste bot, pára envio, estado «parado por kill», não religa sozinho, não zera a carteira.

## 3. Convívio com Operar

- [x] 3.1 — Operar (MARKET após confirmação) permanece disponível com o scalp ligado ou desligado. Este card não redesenha o modal Operar.
- [x] 3.2 — USDT livre partilhado: T recalcula. Se Operar/ordem fora reduzir BTC livre abaixo do inventário do bot, clipa ao livre acima do piso; não conta o fill alheio no P&L deste scalp.

## 4. Painel no Monitor

- [x] 4.1 — Módulo Scalp BTCUSDT no `/monitor` entre o `page-sub` e os KPIs, alinhado ao proto `frontend/public/prototypes/card-1001-scalp-direcional-jev/index.html`. Não é rota nova. Não vive dentro do Operar.
- [x] 4.2 — Interruptor visível: desligado (default) / ligado / parado por kill. Sem chave Spot: switch disabled + Meu Perfil. Calibração visível. P&L (realizado + não realizado − taxas − custo Jev) com perda tão visível quanto ganho. Sem «estratégia lucrativa» / «formador de mercado».
- [x] 4.3 — Board intacta: `table.signals`, Status, Preço, Distância, Tags, Operar, Par / Estratégia. Ligar o scalp não substitui o Operar.

## 5. Copy 24/7

- [x] 5.1 — Landing v4 + `docs/landing-page.md`: deixa de afirmar «não é bot 24/7» / confirmação-sempre como absoluta; admite scalp opcional no Monitor (default off, nunca saque); Operar continua a confirmar. Alinhado a `landing.html` do proto.
- [x] 5.2 — `/help` fora do `OnboardingGuide`: deixa de dizer só «nao e bot»; admite Operar-com-confirmação e scalp opcional. `OnboardingGuide` intacto (Q7=B).
- [x] 5.3 — Meu Perfil: uma cláusula de que a mesma chave Spot também alimenta este scalp se o utilizador ligar.

## 6. Testes e evidência

- [x] 6.1 — Testes dos critérios observáveis do issue #1001 (switch off/on/kill, persistência, post-only, inventário zero, A liga e B não, sem chave Spot).
- [x] 6.2 — Playwright desktop+mobile do painel no `/monitor` (default desligado, ligar, desligar, parado por kill) contra o proto.
- [x] 6.3 — `openspec verify` desta change. TypeSafe ausente do painel e dos logs em claro.
