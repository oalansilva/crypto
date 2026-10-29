UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1122](https://github.com/oalansilva/crypto/issues/1122), sexta história do épico [#1116](https://github.com/oalansilva/crypto/issues/1116).

**Esta é a segunda rodada de Design (d2).** A primeira (26/10/2026) foi aprovada, implementada e integrada em `develop` (PR #1142, `d72e8c77`; residuais no PR #1143, `9b83d25e`) e está no DEV. Em 27/10/2026 Alan não homologou e mudou a regra de quem recebe alerta no Telegram (comentários "Não homologar" e "Decisões de Alan para a nova regra de alertas"). Este documento descreve a regra nova como **delta sobre o que já está implementado**. O resto do card (calendário, candle fechado, estado do mercado, atraso real, identidade de configuração, ação e ETF no Monitor e na atualização, evento com identidade) fica como está, com os ajustes de texto dos residuais da revisão.

O *como* abaixo foi conferido em `develop` @ 9b83d25e. Os OpenSpec do #1117 ao #1121 seguem como contratos reutilizados.

### O que está implementado hoje (regra anterior, no DEV)

- **Origem = favorito marcado "Alertar".** `run_monitor_telegram_alert_scan` (`monitor_telegram_alerts.py:1054`) lê `get_alert_opportunities` (`opportunity_service.py:1278`): favoritos de qualquer dono com `notify_telegram = true`, filtrados por `monitor_telegram_tier_filter` (`:1268-1276`). O favorito sem estrela, se marcado, também alerta ("Unstarred marked favorite remains eligible by default").
- **"Alertar" mora em Favoritos e nasce desligado.** Coluna a partir de 1280 px, sino na célula Ações de 1024 a 1279 px, "Alertar: on/off" no celular (`FavoritesDashboard.tsx:559-620`). O aviso "Fora da carteira: sem alerta…" aparece em ação/ETF fora da carteira (`:622`). O default da coluna é falso (`models.py:163`, migração `20261026_0001`), e as marcas de quem não é admin foram zeradas.
- **Matriz da carteira.** `should_send_position_aware_alert` (`monitor_telegram_alerts.py:296-334`): ação/ETF só alerta com a marca "No portfólio", e então manda entrada e saída; a cripto segue a matriz da posição na Binance (com saldo, a reentrada é suprimida; sem saldo, a saída é suprimida). A varredura busca a carteira Binance de quem tem cripto (`:1165-1192`), e uma falha pausa a cripto da pessoa e manda o aviso operacional "Sua carteira Binance está indisponível…" (`:773-840`), o único com limite por janela.
- **Atraso.** O aviso "Dados atrasados" vai a quem tem favorito marcado do ativo **e** o ativo na carteira (`:1262-1275`).
- **Lote e Descoberta gravam 1 estrela** (`batch_backtest_service.py:743`, `discovery_service.py:2347`), com `notify_telegram = false`. A Descoberta recusa qualquer tier diferente de 3 (`discovery_service.py:2195-2200`). O salvar pelo resultado não grava estrela (`routes/favorites.py`, sem `tier` no create).
- **Monitor.** Lista os favoritos próprios com estrela (filtro padrão "Com estrela" = `1,2,3`, `MonitorStatusTab.tsx:221`, `:531`); quem não é admin e não tem favorito próprio com estrela vê a vitrine do catálogo (`opportunity_service.py:822-870`). A tag "Alerta" mostra a marca (`MonitorStatusTab.tsx:1570`). O detalhe de ação/ETF diz "Ação/ETF na carteira recebe entrada e saída no Telegram." (`OpportunityCard.tsx:375`). A faixa diz "Os alertas do Telegram agora vêm dos seus favoritos marcados "Alertar". Você ainda não marcou nenhum." (`:1223-1236`), alimentada por `GET /api/opportunities/alert-origin` (`alert_origin_for_user`, `monitor_telegram_alerts.py:955`). O Monitor do admin abre em "Em portfólio" (`:222`); quem não é admin vê "Todos" (`:933`).
- **Transição.** O aviso "Mudança nos alertas" sai na primeira varredura depois de `monitor_telegram_favorite_origin_at`, a quem recebia pelo catálogo e não tem favorito marcado. A marca `monitor_telegram_transition_scan_at` é gravada também em dry-run e quando a entrega falha (`:1354`, residual P2 da w3).
- **Atraso por tempo gráfico no Monitor.** O servidor já manda `stale_timeframe`/`stale_detail` (`market_state.py:209-220`), mas o Monitor não lê esses campos (`marketState.ts:177-185`, residual P2 da w3).

### Banco DEV (contagem somente leitura, 27/10/2026)

Revisão `20261026_0001`; `monitor_telegram_favorite_origin_at` = 26/10 20:58; `monitor_telegram_transition_scan_at` ausente (nenhuma varredura depois da troca); `monitor_telegram_tier_filter` ausente nas preferências do sistema; `monitor_telegram_alerts` vazia.

| Origem | Classe | Total | 1 estrela | 2–3 estrelas | Sem estrela | "Alertar" ligado |
|---|---|---|---|---|---|---|
| Lote | Ação/ETF | 7 | 3 | 4 | 0 | 7 |
| Lote | Cripto | 6 | 2 | 4 | 0 | 6 |
| Descoberta | Cripto | 6 | 6 | 0 | 0 | 6 |

Os 19 favoritos são do admin (único usuário com favorito e com Telegram ligado). Os outros 6 usuários não têm Telegram vinculado. Uma preferência de carteira, fora da carteira. O PROD não foi consultado (ele ainda não tem a migração `20261026_0001`); o Apply conta antes do `alembic upgrade` (Migration Plan).

**Audience:** Alan e as pessoas do beta fechado, que acompanham estratégias no Monitor e recebem o Telegram para decidir quando agir.
**Outcome:** cada pessoa recebe no Telegram a entrada e a saída de toda estratégia própria que acompanha no Monitor, em cripto, ação e ETF, com ou sem o ativo na carteira, até desligar aquela estratégia no próprio Monitor. O catálogo não alerta, e lote e Descoberta não enchem o Telegram.
**Direction:** clone+delta Operate de `/monitor` (página primária, recapturada do DEV com a implementação anterior do #1122) e das telas com texto visível que muda: `/favorites`, `/combo/results` (modal de Salvar), `/combo/discovery` (modal de promoção) e `/profile`. Tokens do produto, sem mundo visual novo.
**Scope:** quem recebe (estrela + alerta ligado, sem carteira), onde se liga e desliga (Monitor), o que sai de Favoritos, lote e Descoberta sem estrela, catálogo sem alerta, transição e faixa revistas, dados existentes, residuais da revisão (`stale_detail` no Monitor, marca da transição, specs de atraso, 403/404). Fora: tudo o que o Design anterior já deixava fora (novos canais, robô, compra/venda, migração da fonte antiga #1126, posição real #1124).

### Regiões clonadas (só estas)

Captura de `https://dev.criptofarol.com.br` em 27/10/2026, bundle vivo `index-C9_PkDmo.js` / `index-DOHmvARO.css` (já com a implementação anterior do #1122), API simulada, relógio fixo na seg., 26/10/2026, 15:00 BRT, a 1440 e a 390 px. O rework r2 recapturou o mesmo bundle a 1440 px com o Monitor como abre ("Em portfólio") e com os estados dos cenários (SPY em saída; NVDA atrasada, fechada e aberta); o trecho fora da lista é idêntico byte a byte nas capturas. Regiões marcadas com `COPIED:start`/`COPIED:end`:

- `index.html` (canônico, `/monitor`, visão do admin como abre, em "Em portfólio"):
  - fundo vivo e AppNav desktop e móvel; ajuda "Como usar o Monitor" e aviso educacional;
  - topo (busca, "Telegram: on", Tema, Atualizar), cabeçalho e indicadores; filtros;
  - lista inicial em "Em portfólio" (BTC/USDT, SPY e SOL/USDT em "Em posição"; "Saída / cobertura" vazia), com a contagem viva;
  - listas trocadas pelo filtro e pelos cenários (`<template>`, cada uma uma captura inteira de indicadores, filtros e seções): "Todos" (BTC/USDT, SOL/USDT, NVDA da Binance Ações, SPY, ETH/USDT e NVDA da fonte antiga, já com a identidade abreviada, o estado do mercado e a fonte antiga indisponível do Design anterior); "Em portfólio" e "Todos" com SPY em "Saída / cobertura"; "Todos" com NVDA em "Dados atrasados";
  - detalhes abertos de BTC/USDT e de NVDA, e de NVDA atrasada (`<template>`);
  - a vitrine do catálogo de uma pessoa sem estratégia própria com estrela, com a faixa viva (`<template>`, captura com outro usuário).
- `favorites.html` (`/favorites`): página inteira do admin com BTC/USDT, ETH/USDT, NVDA (Binance), NVDA (fonte antiga), SPY, QQQ (lote, sem estrela) e AAPL (Descoberta, sem estrela), e a vitrine de outro usuário (`<template>`).
- `results.html` (`/combo/results`, resultado de NVDA 1d com o modal "Salvar nos Favoritos" aberto).
- `discovery.html` (`/combo/discovery`, Decidir com o modal de promoção de NVDA).
- `profile.html` (`/profile`).
- `live.css`: `index-DOHmvARO.css` inteiro, sem poda.

O toast transitório "Atualizado · N estratégias analisadas" fica fora. O estado de formulário que o React põe por propriedade foi refletido em atributo. `configure.html` sai da pasta: o texto do Combo com 1 ação já está vivo e esta rodada não muda o Combo.

O delta fica só nos blocos `DELTA:start`/`DELTA:end`:

- **Monitor:** o controle "Alerta" por estratégia na célula de ações da linha (1280 px ou mais), na célula Status de 1024 a 1279 px, no cartão (390) e no detalhe; o texto fixo "Catálogo · sem alerta"; a tag "Alerta" sai das Tags e da faixa de identidade do detalhe; a frase da carteira sai do cartão e fica só no detalhe; a frase nova na ajuda "Como usar o Monitor"; o estado "Dados atrasados no 15m" lido do `stale_detail` (texto e `title` da linha e do cartão); a faixa da vitrine (texto e ícone de informação no lugar do sino); o painel Demonstração com os cenários e as mensagens do Telegram; os invólucros das listas trocáveis.
- **Favoritos:** sai a coluna "Alertar", o sino da célula Ações, o "Alertar: on/off" do celular e o aviso "Fora da carteira"; entram a linha de ajuda das estrelas, a legenda "No Monitor"/"Fora do Monitor" na célula das estrelas, o texto do resumo "Acompanhar" e a faixa da vitrine revista; no CSS, as estrelas do cartão do celular com 44 px; Demonstração.
- **Resultado:** a nota do modal.
- **Descoberta:** título, destino e nota do modal.
- **Perfil:** a frase do cartão "Alertas Telegram".
- **Cola do clone:** invólucros `.cf-desk`/`.cf-mob` do AppNav e os `<template>`.

## Decisões de Alan para a nova regra (27/10/2026)

Registradas no issue depois do "Não homologar" e incorporadas nas decisões, nos specs e nas tasks abaixo.

1. **Alerta = o que a pessoa monitora.** Estratégia própria listada no Monitor (favorito com pelo menos 1 estrela) manda alerta no Telegram, ligado por padrão. A pessoa desliga no próprio Monitor, por estratégia. O "Alertar" sai de Favoritos (decisões 3 e 18).
2. **A carteira não decide quem recebe.** Entrada e saída saem com ou sem o ativo na carteira, e a cripto perde a exceção da posição na Binance. A regra é a mesma para ação, ETF e cripto (decisão 6).
3. **O catálogo não alerta.** A vitrine de quem não tem estratégia própria é só exibição (decisões 2 e 16).
4. **Lote e Descoberta salvam sem estrela.** O favorito fica em Favoritos, fora do Monitor e sem alerta, até a pessoa dar a estrela (decisão 12).

## Decisões de Alan no Design d2 (27/10/2026)

Respostas às perguntas Q1, Q2 e Q3 da rodada d2 (comentário "Decisões de Alan no Design d2") e à pergunta da dupla sobre o aviso de estratégias fora da carteira (comentário "Design d2: dupla A/B e decisão de Alan"). As três saíram de Open Questions.

1. **d2-1 (Q1). A migração tira a estrela automática.** Os favoritos de lote e Descoberta que hoje estão no Monitor com a estrela automática (1 estrela) perdem essa estrela: saem do Monitor e só voltam quando Alan der a estrela, que liga o alerta (decisão 20).
2. **d2-2 (Q2). Tudo o que fica no Monitor sai da migração com alerta ligado.** As marcas "Alertar" de hoje não contam: a migração liga o alerta de todos os favoritos; Alan desliga no Monitor o que não quiser (decisão 20).
3. **d2-3 (Q3). O Monitor continua abrindo em "Em portfólio", sem aviso.** Substitui a recomendação anterior do autor ("abrir em Todos"). O Monitor do admin abre em "Em portfólio", como hoje, e **não mostra aviso** das estratégias fora da carteira com alerta ligado (o "+N fora da carteira com alerta ligado · Ver todos" proposto pela dupla foi recusado). Alan troca para "Todos" quando precisar (decisão 21).

## Decisões de Alan no Design anterior (26/10/2026)

1. **Transição da cripto** (aviso único no dia da troca e faixa no Monitor, sem período de transição): **mantida**, com o critério e o texto da regra nova (decisão 16).
2. **Favorito novo nunca nasce marcado para alertar:** **substituída** pela regra nova 1 e 4. O favorito novo nasce com o alerta ligado, mas só alerta quando ganha estrela; lote e Descoberta nascem sem estrela.
3. **Varredura de ação e ETF só às 08:05 BRT:** mantida (decisão 15).
4. **Sem limite na varredura:** mantida para sinal e atraso. O aviso de falha da carteira Binance, que era o único com limite, deixa de existir (decisão 6).
5. **Linha de ação/ETF compacta no Monitor:** mantida (implementada).

## Goals / Non-Goals

**Goals:**

- Alertas das estratégias próprias que a pessoa acompanha no Monitor (com estrela), em cripto, ação e ETF, ligados por padrão e desligáveis no Monitor, por estratégia.
- Entrada e saída sempre, com ou sem o ativo na carteira, nas três classes.
- Catálogo, lote e Descoberta não alertam sozinhos.
- Um estado e um alerta por favorito; evento idempotente (sem mudança).
- Candle fechado, mercado fechado, feriado e atraso pelo calendário da classe, sem falso atraso; um aviso de atraso por ativo e episódio; mercado fechado só na tela (sem mudança).
- Identidade de configuração; ação e ETF no Monitor e na atualização (sem mudança).
- Alerta ≠ ordem (sem mudança).

**Non-Goals:**

- Os do Design anterior: novos canais, robô, compra/venda e proteção de ação/ETF, migração da fonte antiga (#1126), posição real de ação/ETF (#1124), mensagem de mercado fechado, cadência nova, escolha de sessão ou ajuste.
- Ligar ou desligar o alerta em Favoritos ou no Perfil (o Perfil continua com o interruptor geral do Telegram).
- Alerta por classe, por ativo ou por tempo gráfico: o controle é por estratégia (favorito).

## Decisions

1. **Página primária = `/monitor`; extras com texto visível.** O controle de alerta mora no Monitor, que é a rota canônica do gate. Quatro rotas mudam texto ou controle visível e têm clone extra na mesma pasta:
   - `/favorites`: sai "Alertar", entram a ajuda das estrelas e a legenda "No Monitor"/"Fora do Monitor";
   - `/combo/results`: nota do modal de Salvar;
   - `/combo/discovery`: título, destino e nota do modal de promoção;
   - `/profile`: a frase da origem dos alertas.

   O `/combo/configure` não muda nesta rodada.

2. **Quem recebe = dono de estratégia com estrela e alerta ligado.** Delta sobre `run_monitor_telegram_alert_scan` e `get_alert_favorites`:
   - (a) lista os usuários elegíveis (Telegram vinculado e ligado no Perfil), como hoje;
   - (b) para cada um, lê os **próprios** favoritos com `tier ∈ {1, 2, 3}` **e** `notify_telegram = true`, de qualquer classe. O favorito sem estrela nunca alerta, mesmo com a marca ligada (sai o cenário "Unstarred marked favorite remains eligible by default");
   - (c) avalia a união uma vez (sem mudança);
   - (d) decide a transição por favorito e entrega ao dono, **sem consultar a carteira** (decisão 6).

   **`monitor_telegram_tier_filter` deixa de valer para o alerta.** O conjunto de estrelas que alerta é fixo e é o mesmo que o Monitor mostra por padrão ("Com estrela"). Um filtro de sistema poderia cortar em silêncio o que a pessoa acompanha, contra a decisão 1. A varredura ignora a preferência e a variável de ambiente; o resumo do scan registra `tier_filter_ignored` quando alguma delas está preenchida; a remoção da chave fica para depois do archive (P3). No DEV a preferência não existe.

   A vitrine do catálogo continua só para exibição e nunca alerta (decisão 3 de Alan): as linhas com `is_curated_fallback` nunca entram na varredura, e a estrela que quem não é admin dá numa linha do catálogo (`MonitorStrategyPreference`) também não alerta.

3. **Semântica do campo: `notify_telegram` = "alerta ligado", opt-out.** O campo continua o mesmo (`favorite_strategies.notify_telegram`, mesmo nome na API) e passa a querer dizer "o alerta desta estratégia está ligado no Monitor":
   - default `true` (coluna e `server_default`), em todo caminho de criação: resultado, lote, Descoberta;
   - o favorito só alerta com estrela; sem estrela, o valor fica guardado e não tem efeito;
   - **dar a estrela liga o alerta:** um `PATCH` do dono que leva `tier` de nulo para 1, 2 ou 3 grava `notify_telegram = true` na mesma transação ("entra no Monitor com alerta ligado", decisão 4 de Alan). Trocar entre 1, 2 e 3 estrelas não mexe no alerta. Tirar todas as estrelas não mexe no valor, mas o favorito sai do Monitor e para de alertar; quando volta a ganhar estrela, volta ligado;
   - `PATCH /favorites/{id}` com `notify_telegram` é só do dono, admin ou não. Quem não é dono recebe **403 quando o favorito é do catálogo e está visível para ele (vitrine), e 404 quando ele não vê o favorito** (sem revelar que existe). Nada é gravado nos dois casos. É o comportamento já implementado; a redação anterior ("403 em qualquer caso") estava errada;
   - o `PATCH` de `notify_telegram` num favorito sem estrela é aceito e gravado (o Monitor não oferece o controle nessa linha; a API não precisa recusar).

   Alternativa rejeitada: coluna nova (`alert_muted`). O campo atual já carrega o sentido, a API e o front já o leem, e a migração inverte o default sem trocar nome. O nome da coluna é P3.

4. **Estado por favorito** (sem mudança). Delta: o favorito que passa a alertar pela regra nova (estrela + ligado) e ainda não tem estado ganha a base na primeira leitura, sem alerta. A migração da rodada d2 semeia o estado desses favoritos a partir de `monitor_observed_statuses` pelo par `(symbol, timeframe)`, como a migração anterior fez com os marcados, para a primeira varredura não perder nem repetir uma transição em curso.

5. **Evento com identidade e reserva** (sem mudança): chave do sinal `sha256(user|favorite|nova leitura|início do candle fechado)`, reserva `sending` → `sent`/`failed`, `sending` antigo → `unknown`, `failed` volta enquanto o evento for o atual. **Sem limite na varredura:** sinal e atraso não passam pelo limite por usuário e janela. Com o fim do aviso de falha da carteira (decisão 6), o limite configurável (`monitor_telegram_rate_limit_count`/`…_window_minutes`) fica sem uso na varredura; a remoção fica para depois do archive (P3).

6. **A carteira não decide (decisão 2 de Alan).** Sai a matriz da carteira da varredura:
   - toda mudança de leitura de um favorito que alerta sai: `EXIT→HOLD` = entrada (Compra), `HOLD→EXIT` = saída (Venda, com `Motivo=Stop` quando é stop), nas três classes, com ou sem o ativo na carteira e com ou sem saldo na Binance. A cripto com saldo passa a receber a reentrada, e a cripto sem saldo passa a receber a saída;
   - `should_send_position_aware_alert` sai do caminho do scan (vira só o sentido da mudança); `outside_portfolio_scope`, `suppressed_reentry`, `suppressed_flat_exit` e `suppressed_by_position_matrix` somem do resumo;
   - **a varredura não lê mais a carteira Binance.** `fetch_user_wallet_holdings` e `resolve_portfolio_status_for_user` deixam de ser chamados pelo scan. Uma falha da Binance não pausa nada, e **o aviso operacional "Sua carteira Binance está indisponível…" deixa de sair** (não há o que pausar). O contador `binance_sync_failed_users` sai do resumo;
   - o Monitor continua mostrando a carteira (tag "Carteira", filtro "Em portfólio", "No portfólio/Fora do portfólio", indicador "Em carteira") como informação e organização da tela. Ela não muda o alerta, e o texto de ajuda diz isso (decisão 18);
   - quando o #1124 trouxer posição real de ação/ETF, ela entra na tela, não na decisão de quem recebe.

   Alternativa rejeitada: manter a carteira só para a cripto. Alan pediu a mesma regra nas três classes e quer a compra justamente quando ainda não tem o ativo.

7. **Candle fechado pelo calendário** (sem mudança): `last_closed_start(timeframe, now)` em `nyse_calendar.py`; ação/ETF corta a série nos candles fechados e não descarta a última linha; cripto mantém o caminho de hoje.

8. **Estado do mercado e atraso real** (implementado; redação corrigida pelos residuais P1 e P2). `market_state` por linha: `open`, `closed` (só ação/ETF, com motivo e próxima abertura) e `stale`. A regra de atraso:
   - **atraso real** é faltar o candle de um pregão ou bloco que o calendário diz que já fechou, passada a tolerância do tempo gráfico; é detectado na varredura seguinte, mesmo com o mercado fechado;
   - **decisão por passada:** o ativo está atrasado numa passada só pelas séries **lidas nessa passada**. O detalhe guardado de outro tempo gráfico não decide a passada atual: o episódio só fecha quando nenhum detalhe segue atrasado, sem reabrir nem repetir o aviso;
   - **tempo esgotado da coleta local não é atraso:** série que não terminou dentro do orçamento da passada (inclusive a que terminou e não foi entregue antes de o orçamento estourar) fica sem leitura nessa passada: sem sinal, sem episódio e sem aviso. Falha de leitura **da fonte** (a fonte respondeu sem candle ou com erro) conta como atraso, com o motivo. A varredura do Telegram tem orçamento próprio (300 s); o GET do Monitor segue com 8 s;
   - **detalhe por tempo gráfico:** quando a linha de um tempo gráfico está em espera por causa de outro (ex.: 1d retido por um 15m atrasado), o servidor manda `stale_timeframe` e `stale_detail` (último, esperado e tempo gráfico da série atrasada). A DM usa esses horários e o rótulo da série atrasada. **Delta desta rodada:** o Monitor também lê `stale_detail`: a linha mostra "Dados atrasados no 15m · falta 14:30" e o cartão, o `title` da linha e o detalhe "Dados atrasados no 15m · último 14:15; esperado 14:30", em vez de "falta" de um candle do próprio 1d que já chegou (protótipo: cenário "Atraso no 15m", NVDA 1d na seg. às 15:00). O tom, o ícone e o "Sinal em espera" são os do atraso de hoje.

   **Dado insuficiente** e a precedência "Dados atrasados" sobre "Sem candle válido" na cripto: sem mudança.

9. **Aviso único de atraso e mercado fechado só na tela.** O aviso "Dados atrasados" sai uma vez por usuário, ativo e episódio, **a quem tem o ativo no Monitor com alerta ligado**: dono de pelo menos um favorito do ativo com estrela e `notify_telegram = true`. A carteira não entra. Quem desligou todas as estratégias do ativo não recebe o aviso. O resto fica: sinais do ativo em espera enquanto o episódio dura, recuperação sem mensagem, `closed` nunca manda mensagem, vale para cripto (24/7).

10. **Mensagem e alerta ≠ ordem:** "Ativo: NVDA (Ação · USD)", "Configuração: …", "Candle: …", valores na moeda, "Este alerta não envia ordem: é só o sinal da estratégia.". A mensagem não fala de carteira. **Delta r2 (como parar):** como tudo o que tem estrela passa a alertar, a mensagem de sinal ganha, depois da linha da ordem, "Para não receber mais desta estratégia: desligue o "Alerta" dela no Monitor ou tire a estrela em Favoritos."; o aviso "Dados atrasados" ganha "Para não receber avisos de NVDA: desligue o "Alerta" das estratégias de NVDA no Monitor.". O aviso de transição já diz como voltar a receber.

11. **Identidade de configuração** (sem mudança).

12. **Ação e ETF favoritáveis; lote e Descoberta sem estrela (decisão 4 de Alan).**
    - O lote grava o favorito com `tier = NULL` (sem estrela) em qualquer classe, cripto inclusive, com a nota "gerado em lote (<id8>)" e `notify_telegram = true`.
    - A Descoberta promove a favorito **sem estrela** em qualquer classe. O contrato muda: o pedido não leva tier; um pedido com qualquer tier é recusado (422, "promoção sem estrela"), e nada muda. No modal, o título vira "Promover a favorito", o destino "Favoritos · sem estrela" e a nota "Onde ver depois: Favoritos, sem estrela e fora do Monitor, com a configuração Binance Ações. Para acompanhar no Monitor e receber no Telegram, dê pelo menos 1 estrela lá. Reversível: retire o favorito; o histórico da varredura fica." (cripto sem a configuração). A linha promovida mostra "Em Favoritos" no lugar de "Favorito tier 3", no Decidir e nas parciais do Acompanhar; o aviso de sucesso diz "entrou em Favoritos sem estrela".
    - O resultado individual ("Salvar nos Favoritos") continua sem estrela, como hoje. A nota do modal vira: "O favorito entra sem estrela, só em Favoritos. Dê pelo menos 1 estrela lá para acompanhar no Monitor e receber os sinais no Telegram; o alerta já vem ligado e você desliga no Monitor."
    - O resto da decisão anterior (fim da recusa de ação/ETF, modal com identidade, duplicata, foco) fica.

13. **Monitor com ação/ETF** (implementado). Delta desta rodada: a tag "Alerta" sai da coluna Tags e da faixa de identidade do detalhe; no lugar entra o controle da decisão 18. A frase "Ação/ETF na carteira recebe entrada e saída no Telegram." sai.

14. **Atualização diária com calendário** (sem mudança).

15. **Cadência sem mudança:** só a passada das 08:05 BRT.

16. **Transição e faixa da vitrine (regra nova).** Quem recebia pelo catálogo continua perdendo esses alertas, sem período de transição (o catálogo não alerta).
    - **Aviso único "Mudança nos alertas"** na primeira varredura depois da troca (`monitor_telegram_favorite_origin_at`, janela de 2 dias), a quem tem pelo menos um alerta do catálogo `sent` antes da troca **e não tem estratégia própria com estrela e alerta ligado** nesse momento. Texto: "Os alertas do Telegram agora vêm das estratégias que você acompanha no Monitor, e não mais do catálogo do Cripto Farol. Você recebia: BTC/USDT e ETH/USDT. Para voltar a receber, salve a estratégia nos Favoritos e dê pelo menos 1 estrela: o alerta já vem ligado e você desliga no Monitor. Esta mensagem não se repete." Chave `transition`, uma por usuário.
    - **Residual P2 da w3:** a marca `monitor_telegram_transition_scan_at` só é gravada numa varredura **sem dry-run** em que **nenhuma** entrega de transição terminou `failed`. Com `failed`, a varredura seguinte, ainda dentro da janela, tenta de novo quem falhou; a chave do evento impede repetir quem já recebeu. Em dry-run nada é gravado (nem a marca nem a reserva da chave `transition`), para o ensaio não fechar a janela de verdade.
    - **Faixa no Monitor (vitrine):** aparece quando o Monitor mostra o catálogo, isto é, para quem não é admin e não tem favorito próprio com estrela, com ou sem Telegram ligado. `role=status`, acima dos indicadores, com o ícone de informação (lucide `Info`) no lugar do sino, porque a faixa diz que ali não há alerta:
      - forte: "Estas estratégias são o catálogo do Cripto Farol: só exibição, sem alerta no Telegram.";
      - texto: "Os alertas vêm das estratégias que você acompanha no Monitor. Dê pelo menos 1 estrela a uma estratégia sua em Favoritos (ou salve lá um resultado do Combo): ela entra aqui com o alerta ligado." (vale para quem não tem favorito e para quem só tem favoritos sem estrela, que também vê a vitrine);
      - só para quem recebia pelo catálogo: "Até 26/10 você recebia os alertas do catálogo; agora cada pessoa recebe os das próprias estratégias." (data da troca);
      - link "Ir para Favoritos" (alvo de 44 px).

      O texto antigo ("Você ainda não marcou nenhum") sai: não há mais o que marcar. Quem tem estratégia própria com estrela e desligou todos os alertas não vê faixa: o próprio controle mostra o estado.
    - `GET /api/opportunities/alert-origin` passa a devolver `has_monitored_strategy` (favorito próprio com estrela), `alerts_on` (quantos deles com alerta ligado), `received_catalog_alerts`, `catalog_until` e `show_banner` (vitrine). `has_marked_favorite` sai.
    - **Favoritos (vitrine):** a faixa vira "Estas estratégias são o catálogo do Cripto Farol e não mandam alerta. Os alertas do Telegram vêm das estratégias que você acompanha no Monitor: salve um resultado do Combo nos Favoritos e dê pelo menos 1 estrela aqui." A vitrine de Favoritos só aparece para quem não é admin e não tem nenhum favorito, e Descoberta e lote são só do admin; por isso a faixa fala só do Combo.

17. **Regressão.** Os testes de contrato passam a cobrir, além dos do Design anterior que seguem válidos:
    - só o dono recebe, com estrela e alerta ligado; sem estrela não alerta mesmo ligado; alerta desligado não alerta; catálogo não alerta (nem com a estrela da preferência de quem não é admin);
    - entrada sem o ativo na carteira (NVDA, BTC/USDT sem saldo); saída sem carteira (SPY); cripto com saldo recebendo a reentrada; cripto sem saldo recebendo a saída;
    - a varredura não chama a carteira Binance, e uma falha dela não muda nada nem manda aviso operacional;
    - atraso a quem tem o ativo no Monitor com alerta ligado, sem carteira; quem desligou todas as estratégias do ativo não recebe;
    - dar a estrela liga o alerta; trocar de 1 para 2 estrelas não mexe; tirar as estrelas para de alertar;
    - lote e Descoberta gravam sem estrela; a Descoberta recusa pedido com tier;
    - `tier_filter` ignorado;
    - transição: aviso só para quem recebia pelo catálogo e não tem estratégia com estrela e alerta ligado; a marca não é gravada em dry-run nem com entrega `failed`;
    - PATCH: 403 no catálogo visível, 404 no favorito invisível de outro;
    - migração d2 (dados existentes e default).

    O E2E Playwright de `/monitor`, `/favorites`, `/combo/results`, `/combo/discovery` e `/profile`, com a API simulada, segue o protótipo novo.

18. **Controle de alerta no Monitor (decisão 1 de Alan).** Em toda linha de estratégia própria com estrela:
    - **linha da tabela, a partir de 1280 px:** primeiro botão da célula de ações, antes de "Abrir Gráfico": `role="switch"`, `aria-checked`, sino (ligado) ou sino cortado (desligado), texto visível "Alerta" e o estado ao lado ("ligado"/"desligado", `aria-hidden`, porque o `aria-checked` já anuncia). Nome acessível "Alerta no Telegram · NVDA 1d · Médias Móveis: Tendência em Virada · Binance Ações" (contém o texto visível "Alerta"; o ativo, o tempo gráfico, a estratégia e, em ação/ETF, a configuração curta distinguem duas linhas do mesmo ativo: a NVDA da fonte antiga é "… · Stooq fonte antiga"; a cripto não leva configuração). Ligado usa a cor de sinal positivo do tema; desligado, o cinza do texto secundário com borda tracejada, nunca só cor. A célula de ações quebra em linha como hoje, sem alargar a tabela;
    - **linha da tabela, de 1024 a 1279 px:** o mesmo interruptor vai para a célula Status, abaixo da pílula e do estado do mercado. Medido no DEV vivo: nessa faixa a tabela passa da área do Monitor e a célula de ações fica cortada (a 1024 px a linha vai até 1211 px e o Monitor termina em 1006 px; incumbente, registrado nos P3). Só um dos dois interruptores da linha aparece em cada largura;
    - **cartão (390 px):** o mesmo interruptor na faixa de controle do cartão, ao lado de "No portfólio"/"Preço", com o texto "Alerta: ligado"/"Alerta: desligado" e alvo de 44 px. O cartão **não** repete a ajuda da carteira (r2: ela somava +60 a +80 px por cartão para a mesma frase), e a frase antiga da carteira de ação/ETF também sai dele;
    - **detalhe (linha aberta, mesa):** o mesmo interruptor na faixa de controle, com o estado atual da estratégia (o mesmo da linha; mudar um muda o outro), e abaixo dele a ajuda "Entrada e saída saem com ou sem o ativo na carteira. Desligado, nada sai no Telegram para esta estratégia." (no lugar da frase da carteira de ação/ETF);
    - **ajuda do Monitor, uma vez por página:** a ajuda "Como usar o Monitor" ganha, depois do texto de hoje, "Toda estratégia aqui manda alerta no Telegram, com ou sem o ativo na carteira; para parar de receber, desligue o "Alerta" da linha." É o lugar da regra da carteira no celular, e diz como parar. Não aparece na vitrine;
    - clicar grava pelo `PATCH /favorites/{id}` (`notify_telegram`) com atualização otimista; em erro, volta ao estado anterior e mostra "Não foi possível mudar o alerta. Tente de novo." no status da página (`role=status`). O clique não abre nem fecha a linha;
    - **favorito sem estrela não aparece no Monitor** (o filtro "Estrelas" do Monitor tem só "Todas", 3, 2 e 1, e a lista corta em `isRatedOpportunity`): não há estado de linha sem estrela; o "Fora do Monitor" vive em Favoritos (decisão 19);
    - **linha do catálogo (vitrine):** "Catálogo · sem alerta" (12 px, borda tracejada), sem controle;
    - o Telegram desligado no Perfil desliga tudo, como hoje ("Telegram: off" no topo); o interruptor por estratégia continua mostrando e gravando a escolha da estratégia;
    - Favoritos não tem mais controle de alerta (decisão 19).

19. **Favoritos sem "Alertar"; estrela é a porta do Monitor.** Saem de `/favorites`:
    - a coluna "Alertar" (1280 px ou mais), o sino da célula Ações (1024 a 1279 px), o "Alertar: on/off" do cartão no celular e o aviso "Fora da carteira: sem alerta…";
    - o `aria-label` "Alertar no Telegram: ligado/desligado".

    Entram:
    - abaixo do subtítulo "Catálogo operacional para escolher quais setups entram no Monitor por estrelas.", a ajuda "Com pelo menos 1 estrela, a estratégia entra no Monitor e manda alerta no Telegram, ligado por padrão (desligue no Monitor). Sem estrela, fica só aqui; lote e Descoberta salvam sem estrela.";
    - na célula das estrelas (linha e cartão), a legenda curta "No Monitor" (com estrela) ou "Fora do Monitor" (sem estrela), em texto secundário;
    - ao dar a primeira estrela, o status da página diz "QQQ 1d entrou no Monitor com o alerta ligado." e a legenda ao lado da estrela vira "No Monitor · alerta ligado" (no celular o status do topo fica fora da tela; a legenda é o retorno perto do dedo); ao tirar a última, "QQQ 1d saiu do Monitor e não manda mais alerta.";
    - no resumo por estrelas, o texto de "Acompanhar" (1 estrela) troca "Monitorar quando fizer sentido" por "No Monitor, com alerta ligado" (1 estrela já põe no Monitor com alerta); "Interesse alto" e "Top picks" ficam;
    - no cartão do celular, as estrelas passam de 28 para 44 px (agora decidem Monitor e alerta); na mesa ficam 24 px (≥ 24 px, WCAG 2.5.8).

    Com a coluna fora, a tabela volta à largura do vivo de antes do #1122 (sem a coluna, a Estratégia recupera a largura medida no protótipo).

20. **Dados que já existem (migração `20261027_0001`), como Alan decidiu (d2-1 e d2-2):**
    - **Estrela automática de lote e Descoberta sai (d2-1).** Hoje esses favoritos têm 1 estrela (`tier = 3`) e estão no Monitor; com "ligado por padrão" passariam a alertar. A migração tira a estrela automática (`tier → NULL`) só dos favoritos com nota "gerado em lote …" ou "descoberta via sweep …" que ainda estão com 1 estrela; os que a pessoa subiu para 2 ou 3 estrelas ficam (foi escolha). Eles saem do Monitor e voltam quando Alan der a estrela, que liga o alerta (decisão 3). No DEV: 11 saem do Monitor (5 do lote e 6 da Descoberta) e 8 ficam.
    - **Tudo o que fica no Monitor sai com alerta ligado (d2-2).** A migração liga o alerta de todos os favoritos (`notify_telegram = true`), que é o padrão novo; a pessoa desliga no Monitor. No DEV não muda nada (os 19 estão ligados). No PROD, a migração anterior zera as marcas de quem não é admin; sem este passo, ninguém além do admin receberia. Este passo também tira o risco anotado no QA (marcas do Alan zeradas quando `ADMIN_EMAILS` falta em PROD).

    A migração também: muda o `server_default` de `notify_telegram` para `true`; semeia o estado dos favoritos que passam a alertar (decisão 4); não mexe em `monitor_telegram_favorite_origin_at` nem na marca da transição. Downgrade: devolve o `server_default` falso; os dados mudados não voltam (registrado no Migration Plan).

21. **Monitor do admin continua abrindo em "Em portfólio", sem aviso (d2-3).** Com a regra nova, estratégia fora da carteira também alerta, e "Em portfólio" ao abrir deixa fora da vista as estratégias que mandam a compra de um ativo que Alan ainda não tem, e o interruptor delas. Alan decidiu manter o padrão de hoje ("Em portfólio" para o admin, "Todos" para quem não é admin) e **não mostrar aviso** de estratégias fora da carteira com alerta ligado: nada de contador "+N fora…" nem link "Ver todos" na barra de filtros. Ele troca para "Todos" quando precisar. A ajuda do Monitor e a mensagem do Telegram dizem como desligar (decisões 10 e 18). O protótipo abre em "Em portfólio" (BTC/USDT, SPY, SOL/USDT); o filtro troca de lista, e os cenários da Demonstração com linha fora da carteira trocam para "Todos".

## Risks / Trade-offs

- [Mais mensagens: cripto com saldo passa a receber a reentrada, cripto sem saldo a saída, e ação/ETF fora da carteira passa a alertar] → é a decisão de Alan. O volume é limitado pelo que a pessoa acompanha com estrela; lote e Descoberta nascem sem estrela; cada estratégia se desliga no Monitor.
- [Dados existentes com a estrela automática passariam a alertar] → a migração tira a estrela automática que ainda está em 1 (d2-1).
- [Estratégia fora da carteira com alerta ligado fica fora da vista ao abrir o Monitor em "Em portfólio"] → decisão de Alan (d2-3): sem aviso; ele troca para "Todos". A mensagem do Telegram e a ajuda do Monitor dizem como desligar.
- [A Descoberta muda de contrato (tier 3 → sem estrela)] → o front e o servidor mudam juntos; um cliente antigo que mande `tier: 3` recebe 422 e nada muda.
- [Falha da Binance deixa de avisar] → o aviso só existia para explicar a pausa; sem pausa, não há o que avisar. O Monitor continua mostrando o estado da carteira.
- [Quem recebia pelo catálogo continua perdendo os alertas] → aviso único e faixa na vitrine, com o caminho de volta (salvar e dar estrela).
- [Varredura sem limite] → sem mudança: a chave do evento impede repetição.
- [Servidor de protótipos lê o disco] → a URL pública serve os arquivos novos (conferido na validação abaixo).

### P3 aceitos (detalhe de Apply)

- Nome da coluna `notify_telegram` (mantido) e dos campos novos de `alert-origin` (`has_monitored_strategy`, `alerts_on`); forma do resumo do scan (`tier_filter_ignored`).
- Remoção, depois do archive, de `monitor_telegram_tier_filter`, `monitor_telegram_rate_limit_count`/`…_window_minutes`, `monitor_telegram_min_repeat_minutes` e `monitor_observed_statuses`; `should_send_position_aware_alert` pode virar um helper de sentido ou sair.
- Texto exato das mensagens do Telegram (as do protótipo são a base).
- Ícone do sino cortado (lucide `BellOff`) e a cor exata dos estados do interruptor dentro do tema `monitor-theme`.
- Mensagem de erro do interruptor e o tempo do status.
- Os P3 do Design anterior que seguem valendo: nomes de tabela e campos, tolerâncias do atraso, limite de 10 min do `sending`, janela em pregões, nome do feriado, `classify_asset_type` sem ETF, índice parcial só em PostgreSQL, aviso de atraso por (fonte, ativo), horário do fechamento calculado pelo calendário, "Pregão aberto" na fonte antiga, ícone de 9 px do par de ação/ETF.
- Incumbentes fora do card, em COPIED: tabela do Monitor mais larga que a área visível de 1024 a 1279 px, com a célula de ações (Abrir Gráfico, Ver Trades) cortada (por isso o interruptor vai para a célula Status nessa faixa); reset `*` vivo que zera padding; coluna "Par / Estratégia" estreita; "Confirmar gestão" cortado no cartão a 390; valores em "$"; "Operar indisponível" com a API simulada; logo do AppNav por caminho absoluto; `.btn` do `monitor-theme` sem anel de foco; tags de 10 px; rótulos `#707a8a`; coluna Tags some abaixo de 1440 px; `SaveFavoriteModal` e modal da Descoberta com o padding zerado pelo reset; achados do detector em regiões COPIED.
- Protótipo: os números de preço, risco e métricas são amostra; só BTC/USDT e NVDA abrem detalhe (os dois capturados abertos); o interruptor não grava nada; na vitrine, o AppNav continua o do admin (o conteúdo é o da outra pessoa).
- Detalhes de Apply aceitos da dupla d2 (A e B), resolvidos no Apply e não reabertos como P0/P1:
  - erro do interruptor e Telegram desligado no Perfil sem tela (os textos estão nas decisões 18 e no Perfil);
  - mercado fechado sem cenário na d2 (sem delta; vivo no DEV e no protótipo d1 no git);
  - anel de foco a 390 px no verde `#0ecb81` do vivo sobre o interruptor verde: usar o azul do desktop ou `outline-offset`;
  - tirar todas as estrelas e dar de novo religa o alerta que a pessoa tinha desligado (coerente com "estrela liga", decisão 3); registrar no teste 8.9;
  - `aria-label` "1 estrela"/"2 estrelas"/"3 estrelas" nas estrelas de Favoritos, além do `title` vivo;
  - amostra: SOL/USDT está no Monitor e não em `favorites.html`; a mensagem de entrada cita o candle de segunda com o relógio da página na segunda às 15:00 (a Demonstração simula a varredura de terça, 08:05);
  - "Em Favoritos" da linha promovida e do aviso de sucesso da Descoberta sem desenho (texto exato na decisão 12);
  - cor do "ligado" com `--hold` (verde de sinal; DESIGN.md regra 7 reserva verde/vermelho para preço): confirmar a cor no Apply, mantendo ícone e texto;
  - a vitrine depende do filtro de estrelas (`_has_monitor_candidate` com o `tier_filter` da tela): decidir no Apply se a condição ignora o filtro, para valer "favorito próprio com estrela";
  - herdados em COPIED: `.btn` do `monitor-theme` sem anel, estrelas de 24 px na mesa, tabela maior que a área de 1024 a 1279 px, rótulos `#707a8a`, reset que zera padding;
  - processo: a URL pública serve a d1 até o checkout DEV ter os arquivos novos (o pai resolve antes da Aprovação de Design); `discovery.html` dá BLOCKED no `classify` (informativo); `parse_live_route` captura `surface: existing` como justificativa (já visto no #1120 e #1121).

## Migration Plan

1. Alembic `20261027_0001` (depois de `20261026_0001`):
   - `server_default` de `notify_telegram` → `true`;
   - d2-1: `UPDATE favorite_strategies SET tier = NULL WHERE tier = 3 AND (notes LIKE 'gerado em lote%' OR notes LIKE 'descoberta via sweep%')`;
   - d2-2: `UPDATE favorite_strategies SET notify_telegram = true`;
   - semente de `monitor_favorite_alert_states` para os favoritos com estrela e alerta ligado ainda sem estado, a partir de `monitor_observed_statuses`.
2. Antes do `alembic upgrade` em PROD (release): contar, só leitura, os favoritos de lote/Descoberta com 1 estrela e as marcas por usuário, e registrar na nota da release. Com d2-2, a conferência de `ADMIN_EMAILS` deixa de ser necessária para as marcas.
3. Deploy do servidor e do front juntos. A primeira varredura depois do deploy usa a base semeada; a transição segue a decisão 16.
4. Rollback: voltar o código devolve o scan da rodada anterior (com carteira). As estrelas tiradas (d2-1) e as marcas ligadas (d2-2) não voltam pelo downgrade; o downgrade só devolve o `server_default` falso.

## Open Questions

Nenhuma. Q1, Q2 e Q3 da rodada d2 foram respondidas por Alan em 27/10/2026 e viraram as decisões d2-1, d2-2 e d2-3 ("Decisões de Alan no Design d2"); a pergunta da dupla sobre o aviso "+N fora da carteira" foi respondida junto com d2-3 (sem aviso).

## Apply contract

O Apply lê este `design.md` e os HTML de `frontend/public/prototypes/card-1122-favoritos-alertas-acoes-etfs/` como spec de layout. O que já está implementado e não muda fica como está.

**Contrato visível (não P3):**

- **Monitor:**
  - interruptor "Alerta" por estratégia própria com estrela na célula de ações da linha (1280 px ou mais), na célula Status de 1024 a 1279 px, no cartão (390, alvo de 44 px) e no detalhe, `role=switch`, `aria-checked`, nome acessível com ativo, tempo gráfico, estratégia e (ação/ETF) configuração, estado com ícone + texto; o detalhe abre com o estado atual e acompanha a linha nos dois sentidos;
  - "Catálogo · sem alerta" (12 px) no lugar do interruptor na vitrine; nenhum estado de linha sem estrela (ela não aparece no Monitor);
  - sem a tag "Alerta" nas Tags e na faixa de identidade do detalhe;
  - ajuda "Entrada e saída saem com ou sem o ativo na carteira…" só no detalhe, no lugar da frase da carteira; o cartão do celular não a repete;
  - frase da ajuda "Como usar o Monitor": "Toda estratégia aqui manda alerta no Telegram, com ou sem o ativo na carteira; para parar de receber, desligue o "Alerta" da linha." (fora da vitrine);
  - faixa da vitrine nova (texto da decisão 16 e ícone de informação), com a frase datada só para quem recebia pelo catálogo, e "Ir para Favoritos" (44 px);
  - "Dados atrasados" com "Sinal em espera" na linha e no cartão, e a linha retida por outro tempo gráfico com o horário e o rótulo da série atrasada (`stale_detail`: "Dados atrasados no 15m · falta 14:30"; cartão "… · último 14:15; esperado 14:30");
  - admin abre em "Em portfólio", como hoje, sem aviso de estratégias fora da carteira (d2-3);
  - célula de ações da linha com o interruptor (ajuste de Alan na Aprovação de Design, 28/10/2026): botões alinhados e da mesma largura por coluna, rótulo em uma linha; coluna única abaixo de 1600 px e grade 2 × 2 a partir de 1600 px, sem alargar a tabela em relação a hoje.
- **Favoritos:** sem "Alertar" em nenhuma largura e sem "Fora da carteira"; ajuda das estrelas; legenda "No Monitor"/"Fora do Monitor", e "No Monitor · alerta ligado" logo depois da primeira estrela; resumo "Acompanhar · No Monitor, com alerta ligado"; estrelas do cartão do celular com 44 px; status ao dar a primeira e tirar a última estrela; faixa da vitrine nova (só Combo).
- **Resultado:** nota nova do modal.
- **Descoberta:** "Promover a favorito", destino "Favoritos · sem estrela", nota nova, "Em Favoritos" na linha promovida e no aviso de sucesso.
- **Perfil:** "Receba DMs individuais quando mudar a leitura de uma estratégia sua que está no Monitor (cripto, ação ou ETF), com ou sem o ativo na carteira. Desligue por estratégia no Monitor. Mercado fechado e feriado aparecem só no Monitor."
- **Telegram:** entrada e saída sem carteira nas três classes; nada do catálogo, de favorito sem estrela ou de alerta desligado; aviso de atraso a quem tem o ativo no Monitor com alerta ligado; sem aviso operacional da carteira; aviso de transição novo; a mensagem de sinal e o aviso de atraso dizem como parar de receber (decisão 10).
- **Comportamentos dos specs:** quem recebe; opt-out por estratégia; estrela liga; lote e Descoberta sem estrela; `tier_filter` ignorado; carteira fora da decisão; transição sem marca em dry-run nem com `failed`; 403/404 do PATCH; atraso por passada e timeout local.

**P3 aceito (Apply):** os itens da subseção "P3 aceitos" em Risks / Trade-offs.

## Prototype

- **Canônico:** `frontend/public/prototypes/card-1122-favoritos-alertas-acoes-etfs/index.html`, clone de `/monitor` (visão do admin como abre, em "Em portfólio"). URL: https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/
  - Abre em "Em portfólio" com BTC/USDT (1 estrela, carteira), SPY (ETF, carteira) e SOL/USDT, sem aviso das estratégias fora da carteira (d2-3). "Todos" (o botão vivo do filtro) mostra também NVDA (Binance Ações, 2 estrelas, **fora da carteira**), ETH/USDT (alerta **desligado**) e NVDA (fonte antiga); "Em portfólio" volta. Cada lista é uma captura viva.
  - Interruptor "Alerta" em todas, ligado por padrão e desligado em ETH/USDT; clicar alterna e anuncia no status da página; a escolha vale em todas as listas e nos detalhes. Detalhes de BTC/USDT e NVDA com o interruptor (no estado atual) e a ajuda da carteira; a ajuda "Como usar o Monitor" diz como parar de receber.
- **Demonstração** (fim da página, no fluxo). Nenhum cenário vem escolhido ao abrir. Cada cenário troca a linha destacada (linha e cartão) para o estado depois da varredura e mostra as mensagens do Telegram; os que destacam linha fora da carteira trocam o filtro para "Todos":
  - Entrada sem carteira: NVDA (fora da carteira) vai de Venda para Compra e fica em "Em posição"; sai o alerta de entrada; troca para "Todos".
  - Saída: SPY vai de Compra para Venda e passa a "Saída / cobertura" (captura viva com SPY em saída, nos dois filtros); sai o alerta de saída; o filtro fica como está.
  - Cripto com saldo: BTC/USDT, com saldo na Binance, volta de Venda para Compra e fica em "Em posição"; sai a reentrada (antes era suprimida).
  - Alerta desligado: ETH/USDT vai de Compra para Venda e fica em "Saída / cobertura", com o interruptor desligado; nada sai; troca para "Todos".
  - Dados atrasados: a linha e o cartão de NVDA passam a "Dados atrasados · falta seg. 26/10" / "… · último candle sex., 23 out.; esperado seg., 26 out." com "Sinal em espera", em âmbar (captura viva); o aviso sai para quem tem NVDA no Monitor com alerta ligado, sem olhar a carteira; troca para "Todos".
  - Atraso no 15m: NVDA 1d em espera por causa do 15m: "Dados atrasados no 15m · falta 14:30" na linha e "… · último 14:15; esperado 14:30" no cartão e no detalhe (delta `stale_detail` sobre a captura do atraso); aviso com "(15m)"; troca para "Todos".
  - Catálogo sem alerta: a página troca para a vitrine de outra pessoa, com a faixa nova e "Catálogo · sem alerta" nas linhas; nada sai. Mostra também a mensagem única "Mudança nos alertas" de quem recebia pelo catálogo.
- **Extra `favorites.html`** (clone de `/favorites`): sem "Alertar"; ajuda das estrelas; resumo "Acompanhar · No Monitor, com alerta ligado"; "No Monitor"/"Fora do Monitor"; QQQ (lote) e AAPL (Descoberta) sem estrela; dar a primeira estrela em QQQ diz "QQQ 1d entrou no Monitor com o alerta ligado." e a legenda ao lado vira "No Monitor · alerta ligado"; tirar diz que saiu; estrelas de 44 px no cartão do celular. Demonstração: "Vitrine do catálogo" troca para a vitrine com a faixa nova (só Combo).
- **Extra `results.html`** (clone de `/combo/results` com o modal de NVDA aberto): nota nova.
- **Extra `discovery.html`** (clone de `/combo/discovery`, Decidir com o modal de NVDA): "Promover a favorito", "Favoritos · sem estrela" e a nota nova.
- **Extra `profile.html`** (clone de `/profile`): frase nova.
- **Apoio:** `live.css` (CSS vivo inteiro), `delta.css`, `delta.js`. Nenhuma página é painel ANTES/DEPOIS nem "N estados"; cada Demonstração fica no fim, no fluxo.

## Prototype Validation

Evidência do rework r2 da rodada d2 (27/10/2026), que substitui a da d2. Qualquer mudança posterior nos arquivos abaixo a invalida.

- **Captura viva:** Playwright Python, Chromium headless shell 1243, `pt-BR`, tema escuro, fuso `America/Sao_Paulo`, relógio fixo na seg., 26/10/2026, 15:00 BRT, API simulada, de `https://dev.criptofarol.com.br` (bundle `index-C9_PkDmo.js` / `index-DOHmvARO.css`, já com o #1122 anterior; conferido de novo no r2).
  - d2, a 1440 e a 390 px: `/monitor` do admin depois de "Todos" (fechado e com BTC/USDT e NVDA abertos), `/monitor` de outra pessoa (vitrine), `/favorites` do admin e de outra pessoa (vitrine), `/profile`, `/combo/results` e `/combo/discovery` com o modal de NVDA.
  - r2, a 1440 px: `/monitor` do admin como abre ("Em portfólio", sem clicar), e os estados dos cenários: SPY em saída em "Em portfólio" e em "Todos"; NVDA (Binance Ações) com `market_state = stale` (último 23/10, esperado 26/10) em "Todos", fechada e com o detalhe aberto. O trecho fora da lista (AppNav, ajuda, topo, toast) é idêntico byte a byte entre as capturas r2 e a d2.
  - Toda região COPIED das cinco páginas é substring literal de uma captura (0 fora) e nenhum marcador cai dentro de tag. `live.css` = `index-DOHmvARO.css` inteiro (sha `353ac045db2d…`).
- **Gate do clone** (`scripts/process-fsm/design_clone_gate.py`, catálogo do HEAD): `design_token_gap` = None (tokens em L1–L3); `classify(index.html, /monitor)` = PASS (landmarks na lista inicial "Em portfólio"); `evaluate_clone_gate` = True; `clone_gate_ok` = True; `copied_utf8_sum` 400.572 B. Favoritos e Resultado PASS; Descoberta BLOCKED (informativo, P3); Perfil sem entrada no catálogo.
- **Bytes por página** (copiado × delta, sem os marcadores):

  | Arquivo | Bytes | sha256 | COPIED | DELTA |
  |---|---|---|---|---|
  | `index.html` (canônico) | 557.519 | `2f6f95c304d8…` | 195 pares, 399.207 B | 219 pares, 120.562 B |
  | `favorites.html` | 162.945 | `25de498b7b29…` | 51 pares, 152.497 B | 59 pares, 2.884 B |
  | `results.html` | 45.463 | `5159b303aa6c…` | 5 pares, 44.216 B | 5 pares, 241 B |
  | `discovery.html` | 47.563 | `0bb4e4e150e8…` | 8 pares, 45.887 B | 8 pares, 355 B |
  | `profile.html` | 30.593 | `2781744bf5fb…` | 5 pares, 29.295 B | 5 pares, 287 B |
  | `live.css` | 254.138 | `353ac045db2d…` | clone inteiro | — |
  | `delta.css` | 6.721 | `01cc9fe95874…` | — | delta |
  | `delta.js` | 10.935 | `11cd4eec1dc8…` | — | delta |

  O `index.html` cresceu porque carrega seis listas vivas (Em portfólio, Todos, SPY em saída nos dois filtros, NVDA atrasada e NVDA em espera pelo 15m) e quatro detalhes; o delta de cada lista são os interruptores (linha, célula Status e cartão), as remoções da tag "Alerta" e da frase da carteira do cartão, e, na lista do 15m, o texto e o `title` do `stale_detail`. Fora das listas: a frase da ajuda do Monitor, a faixa da vitrine (texto e ícone) e o painel Demonstração.
- **Medidas (protótipo × vivo):** linha da tabela a 1440, 1280 e 1024 px: BTC/USDT 142 px (vivo 158 a 1440: a tag "Alerta" que sai alongava as Tags), NVDA 178, SPY 178, ETH/USDT 138 (iguais ao vivo). Cartão a 390 px: BTC/USDT 867 px (vivo 845; d2 929), NVDA 912 (vivo 913; d2 974), ETH/USDT 773 (vivo 721): sem a ajuda da carteira, o cartão só soma o interruptor. Favoritos, largura da Estratégia: 342 px a 1440 (vivo 271), 296 a 1280 (vivo 252), 90 a 1024 (igual). Parágrafos da Demonstração: até 82 caracteres por linha na mesa (d2: 91 a 96).
- **URL pública:** **ainda serve a d1.** `https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/` lê primeiro o checkout DEV (`/srv/apps/dev/criptofarol/source/frontend/public`, com o protótipo da `develop`). O browser gate rodou num servidor estático local da pasta `frontend/public` deste worktree (`python3 -m http.server 8793`, mesmo caminho `/prototypes/…`). A URL pública mostra o r2 quando o checkout DEV tiver estes arquivos (P3 de processo, do pai antes da Aprovação de Design).
- **`openspec validate card-1122-favoritos-alertas-acoes-etfs --strict`:** válido.
- **Browser gate** (servidor local; Playwright Python, contexto novo por largura: 1440×900, 1280×800, 1024×768 e 390×844 com toque, tema escuro): **459/459 asserts PASS**, 0 `pageerror`, 0 `console.error`, 0 resposta ≥ 400, sem rolagem horizontal em nenhuma página, filtro nem cenário. Cobre:
  - **Monitor, abertura (d2-3):** filtro em "Em portfólio", só BTC/USDT, SPY e SOL/USDT, contagem viva "(3)", nenhum aviso "+N fora da carteira"/"Ver todos"; ajuda "Como usar o Monitor" com a frase da carteira e de como parar; nenhum "Sem estrela · sem alerta"; cartões sem a ajuda da carteira; nenhuma tag "Alerta" nem frase antiga da carteira.
  - **Monitor, "Todos":** as 6 estratégias; 6 interruptores (célula de ações a 1440/1280, célula Status a 1024), dentro da área visível, nomes distintos com "Alerta", e o de NVDA com "· Binance Ações"; ETH desligado com texto; clicar desliga, sincroniza o cartão, anuncia e não abre a linha; **detalhe aberto mostra o estado atual (desligado), religar no detalhe religa a linha e desligar na linha desliga o detalhe aberto** (B P2-1); ajuda da carteira nos detalhes de BTC/USDT e NVDA; a escolha sobrevive à troca "Todos" ↔ "Em portfólio"; a 390, 6 cartões "Alerta: ligado/desligado" com 44 px.
  - **Demonstração** (cada cenário com a mensagem, a linha e o cartão destacados e visíveis): entrada troca para "Todos" e NVDA "Em posição"; saída mantém "Em portfólio" e SPY sai de "Em posição" para "Saída / cobertura" (também em "Todos"); reentrada com BTC "Em posição"; alerta desligado troca para "Todos", ETH em "Saída / cobertura" (Compra → Venda) e desligado; dados atrasados troca para "Todos", linha de NVDA "Dados atrasados · falta seg. 26/10" + "Sinal em espera" em tom de atraso, cartão "… · último candle sex., 23 out.; esperado seg., 26 out.", detalhe idem, e só NVDA atrasada; atraso no 15m com "Dados atrasados no 15m · falta 14:30" na linha, "… · último 14:15; esperado 14:30" no cartão e no detalhe, sem "falta seg. 26/10", e o aviso com "(15m)"; mensagens de sinal e de atraso com a linha de como parar.
  - **Vitrine:** vista própria escondida, status limpo, sem a frase "Toda estratégia aqui…"; faixa nova ("Dê pelo menos 1 estrela a uma estratégia sua em Favoritos…", sem "Salve uma") com ícone de informação e sem sino; com e sem a frase datada; "Ir para Favoritos" com 44 px; "Catálogo · sem alerta" com 12 px e nenhum interruptor.
  - **Favoritos:** nenhum "Alertar" nem "Fora da carteira"; resumo "No Monitor, com alerta ligado" no lugar de "Monitorar quando fizer sentido"; ajuda das estrelas; 5 "No Monitor" e 2 "Fora do Monitor"; primeira estrela em QQQ dá o status e a legenda "No Monitor · alerta ligado" ao lado da estrela (a 390, a menos de 80 px dela); tirar dá "QQQ 1d saiu do Monitor e não manda mais alerta."; estrelas do cartão a 390 com 44×44 px; vitrine com "salve um resultado do Combo nos Favoritos…", sem Descoberta nem lote, e status limpo.
  - **Resultado, Descoberta e Perfil:** textos novos presentes e nenhum texto antigo.
- **Detector Impeccable CLI** (`node .agents/skills/impeccable/scripts/detect.mjs --json`): **0 achados em `delta.css` e `delta.js`**; nos HTML só os achados do incumbente em COPIED, iguais aos da d2: `flat-type-hierarchy` (Monitor, Favoritos) e `gray-on-color` (Favoritos, estrela desligada/ligada da captura viva). O `delta.css` usa só tokens vivos (`--hold`, `--hold-soft`, `--hold-line`, `--t-2`, `--t-3`, `--line`, `--space-*`, `--text-*`, `--radius-*`, `--bg-*`, `--accent-*`, `--fav-muted-strong`), sem cor nem raio literal; os únicos px literais são os alvos de 44 px e os ícones de 14 px.
- **Scripts:** d2 em `c1122d2/` e r2 em `c1122r2/` no scratchpad da sessão (`capture_r2.py`, `build_r2.py`, `check_r2.py`, `gate.py`, `gate_r2.py`, `asserts.json`, `shots/`).

## Design Critique

Rodada d2 (depois do "Não homologar" de 27/10/2026). Com-tela. Teto 1+1+1: autor, dupla A/B e 1 rework. O rework (r2) aplicou as decisões de Alan, os P1 e os P2 da dupla. Não houve segundo rework.

- Autor: `design-autor 1122 d2` (isolado). Rework: `design-autor 1122 r2` (isolado).
- Assessment A: `assessment-a 1122 d2` (isolado; produto, UX, acessibilidade e fidelidade). Assessment B: `assessment-b 1122 d2` (isolado; detector, gate e navegador).
- Verdict: **PASS**. A e B deram PASS com rework, e os dois reworks foram aplicados no r2. Tokens: `UI impact: affected` / `live_route: /monitor` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/ (clone de `/monitor`). Páginas extras com texto visível alterado: `favorites.html`, `results.html`, `discovery.html` e `profile.html`. `configure.html` saiu, porque o Combo não muda nesta rodada.
- Snapshots: `.impeccable/critique/1122-card-1122-favoritos-alertas-acoes-etfs-A.md` e `…-B.md`, ambos na versão d2. O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1, corrigidos no r2**:
  - Estratégia fora da carteira escondida ao abrir o Monitor em "Em portfólio". Alan decidiu manter o filtro e não mostrar aviso; os cenários da Demonstração trocam para "Todos" quando destacam uma linha fora da carteira.
  - "Dados atrasados" não aparecia na linha no cenário de atraso. Agora NVDA aparece atrasada na linha, no cartão e no detalhe, e também há a variante do 15m.
- **Juízo, decidido por Alan** ([regra nova](https://github.com/oalansilva/crypto/issues/1122#issuecomment-6449522238), [d2](https://github.com/oalansilva/crypto/issues/1122#issuecomment-6450618990), [filtro](https://github.com/oalansilva/crypto/issues/1122#issuecomment-6451876500)):
  - alerta = estratégia própria no Monitor, ligado por padrão e desligável no Monitor;
  - a carteira não decide quem recebe, com a mesma regra para ação, ETF e cripto;
  - o catálogo não alerta;
  - lote e Descoberta salvam sem estrela;
  - a migração tira a estrela automática dos favoritos de lote/Descoberta e liga o alerta de tudo o que fica no Monitor;
  - o Monitor abre em "Em portfólio", sem aviso de fora da carteira.
- **P2, corrigidos no r2**:
  - o detalhe reflete o estado do interruptor da linha;
  - os cenários de saída e alerta desligado mudam a linha;
  - as faixas da vitrine e do Monitor não mandam quem não é admin para o lote ou a Descoberta;
  - o estado "Sem estrela · sem alerta" foi retirado;
  - o resumo de 1 estrela foi revisto;
  - "como parar de receber" aparece no Telegram e na ajuda;
  - a ajuda da carteira fica só no detalhe;
  - a legenda fica perto da estrela;
  - as estrelas do celular têm 44 px.
- **P3 aceitos, para o Apply**: os itens da subseção de P3 aceitos em Risks / Trade-offs. Também entram os achados do detector nos HTML em regiões COPIED do incumbente (`flat-type-hierarchy`, `gray-on-color`) e o que já vem da página viva: botões sem anel de foco e tabela mais larga que a área a 1024 px.
- **Disposition:** o delta visível fica no Monitor (`/monitor`):
  - interruptor "Alerta" por estratégia (`role=switch`), ligado por padrão, na linha, no cartão e no detalhe;
  - Demonstração com entrada sem carteira, saída, reentrada com saldo, catálogo sem alerta, alerta desligado e atrasos.

  Favoritos perde "Alertar", e as estrelas passam a ser a porta de entrada do Monitor. Resultado, Descoberta e Perfil trocam textos. A migração de fontes antigas fica para o #1126, e a posição real de ação/ETF, para o #1124.
- **Ajuste de Alan na Aprovação de Design (28/10/2026, T6):** os quatro botões da célula de ações (Alerta, Abrir Gráfico, Ver Trades e Operar) quebravam de linha encostados à direita, com larguras diferentes. Agora ficam numa coluna de mesma largura e, a partir de 1600 px, numa grade 2 × 2. Só mudou o `delta.css`. A tabela fica com a mesma largura que tinha antes do ajuste em 1024, 1280, 1366, 1440, 1600 e 1920 px. É um ajuste mecânico pedido por Alan, sem nova dupla nem rework.

### Proxies

- `design.md` words: 9384 (antes desta seção)
- HTML generated vs copied (`index.html`): 158312 vs 399207
- Spawns: 4 (design-autor d2, assessment-a d2, assessment-b d2, design-autor r2)
