UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#1122](https://github.com/oalansilva/crypto/issues/1122), sexta história do épico [#1116](https://github.com/oalansilva/crypto/issues/1116). O briefing é o issue grelhado (fronteira vazia), com as 5 decisões de Alan de 26/10/2026 dentro de Entra; não houve reentrevista. A "Transição da cripto" ficou para o Design. Alan decidiu esse ponto e mais quatro no Design, em 26/10/2026 (seção "Decisões de Alan no Design", abaixo). O *como* abaixo foi conferido em `develop` @ f093e2cc, depois do #1117 ao #1121. Os OpenSpec deles (`card-1117-*`, `card-1118-historico-binance`, `card-1119-backtest-acoes-etfs`, `card-1120-lote-multiclasse`, `card-1121-descoberta-acoes-etfs`) são os contratos reutilizados. O calendário de NY (`market_history/nyse_calendar.py`), `prepare_equity_history` (`equity_backtest.py:241`) e as chaves `analysis_*` do favorito vêm deles.

Estado atual, conferido no código:

- **Origem do alerta = catálogo do admin.** `run_monitor_telegram_alert_scan` lê `get_catalog_opportunities(tier_filter, alerts_only=True)` (`monitor_telegram_alerts.py:572-575`), que são os favoritos dos e-mails admin com `notify_telegram = true` (`opportunity_service.py:881-906`). Cada transição vai a todo usuário elegível (`list_eligible_alert_users`, `user_telegram_service.py:77-86`) que tem o símbolo na carteira (`:602-652`). O parâmetro `user_id` do scan não limita nada (`routes/monitor_telegram_alerts.py:20-24`, "Deprecated").
- **Estado por par, não por favorito.** `MonitorObservedStatus` tem unique `(symbol, timeframe)` (`models.py:365-380`); `_collect_transitions` grava um estado por par (`monitor_telegram_alerts.py:450-475`). Dois favoritos no mesmo ativo e tempo se sobrescrevem.
- **Anti-repetição por janela.** `_has_duplicate_recent` (`:255-276`) compara usuário + símbolo + tempo + status nos últimos `min_repeat_minutes` (360 por padrão), sem identidade do evento.
- **Ação e ETF fora de propósito.** `_is_equity_favorite` (`opportunity_service.py:48-59`, "o Monitor segue só cripto até o #1122") tira os favoritos `binance_equity` de todas as listas, e `get_opportunities` e `get_catalog_opportunities` filtram por `/` (`:1023-1056`). No front, o Monitor mostra só `asset_type === 'crypto'` (`MonitorStatusTab.tsx:862` e `:880-884`). Favoritos desabilita estrelas, Telegram e Revalidar de ação/ETF (`FavoritesDashboard.tsx:503`, `:561-582`, `:1837-1846`; textos em `favoriteClass.ts:92-93`, `:217-224`). O resultado recusa favoritar (`routes/favorites.py:65-94`, `ComboResultsPage.tsx:451-472`). O lote e a Descoberta gravam ação/ETF com `tier = None` (`batch_backtest_service.py:738`, `discovery_service.py:2346`).
- **Matriz de posição.** `should_send_position_aware_alert` (`monitor_telegram_alerts.py:146-169`) só manda a entrada quando a pessoa não tem posição e só a saída quando tem. Para ação/ETF a posição é sempre falsa (`monitor_portfolio_status.py:91-97`), então a saída seria silenciada. Uma falha da carteira Binance pula o usuário inteiro (`monitor_telegram_alerts.py:615-626`).
- **Candle fechado e frescor por tempo corrido.** O scan e o Monitor descartam sempre a última linha como "em formação" (`df_closed = df_with_inds.iloc[:-1]`, `opportunity_service.py:1455`) e decidem o fechamento por `T + período ≤ agora` (`:286-333`). Para ação 1d às 08:05 BRT, a última linha já é o pregão fechado de ontem; descartá-la atrasa o sinal em um pregão. O Monitor marca "Sem candle válido/atual" quando o candle tem mais de 3 períodos (`signalResolution.ts:161-169`). Toda segunda de manhã, a ação 1d cairia nisso (sexta 04:00 UTC → segunda 11:00 UTC > 3 dias). A atualização diária mede idade por tempo corrido (`favorite_backtest_refresh_service.py:188-204`: 7 dias no 1d, `max(3h·n, 12h)` em horas). Ela só busca o 15m do intrabar para `ccxt` (`:457`). No período "todo o histórico", o fim vira a data de hoje (`:599-600`). O primeiro candle do período operacional usa a fonte inferida do símbolo (Stooq para ticker), não a do favorito (`favorite_operational_period.py:34-54`).
- **Identidade do favorito.** `lock_and_find_duplicate` e `find_existing_favorite` recebem `data_source` e `asset` desde o #1120, mas não os comparam (`favorite_uniqueness.py:16-115`). `GET /favorites/exists` não conhece fonte (`routes/favorites.py:698-740`). Sessão e ajuste não existem como campo.
- **"Alertar" só do admin.** `PATCH /favorites/{id}` recusa `notify_telegram` de quem não é admin (`routes/favorites.py:1198-1202`). A coluna "Telegram" só aparece para admin (`FavoritesDashboard.tsx:1700`, `:1774`) e some abaixo de 1540 px (`index.css:1991-1996`), então na tela de 1440 nem o admin a vê. O default da coluna é `True` (`models.py:161`): qualquer favorito novo, inclusive os centenas de um lote, nasce "marcado".
- **Vitrine do catálogo.** Quem não é admin e não tem favorito de cripto vê o catálogo do admin no Monitor (`opportunity_service.py:742-799`, `_has_monitor_candidate` em `:944-949`) e em Favoritos (`routes/favorites.py:800-866`). Quem tem só NVDA cai na vitrine e não vê o próprio favorito.
- **Cadência.** O scan roda uma vez por dia, às 11:05 UTC (08:05 BRT), pelos timers `criptofarol-{dev,prod}-telegram-alert-scan.timer` e `ops/run_monitor_telegram_alert_scan.py`.
- **`signal_monitor`** (`services/signal_monitor.py:38-117`) fecha os sinais BUY do feed de sinais (`binance_service`, pares USDT) consultando o ticker da Binance Spot a cada 60 s. Ele não lê favoritos, então ação/ETF nunca entra nele.
- **Gráfico do Monitor.** O Monitor força 1d para ação (`MonitorStatusTab.tsx:643-648`) e lê `/api/market/candles`, que recusa ticker (`api.py:467-477`, spec `crypto-only-mvp`).

**Audience:** Alan e as pessoas do beta fechado, que acompanham estratégias no Monitor e recebem o Telegram para decidir quando agir.
**Outcome:** cada pessoa recebe alerta só dos favoritos que ela marcou, um por favorito, no candle fechado certo de cada mercado. A ação na carteira recebe entrada e saída, há um aviso único quando o dado atrasa de verdade, e mercado fechado aparece só na tela.
**Direction:** clone+delta Operate de `/monitor` (página primária) e das telas com copy visível: `/favorites`, `/combo/results`, `/combo/configure`, `/combo/discovery` (modal de promoção) e `/profile`. Usa os tokens do produto, sem mundo visual novo, e o tema `monitor-theme` vivo (`--wait`, `--hold`, tags).
**Scope:** origem por usuário, estado/evento por favorito, matriz de ação/ETF, atraso e mercado fechado, identidade de configuração, ação/ETF no Monitor e na atualização, "Alertar" do dono e favoritar ação/ETF. Fora: novos canais, robô, compra/venda e proteção (histórias de operação), migração da fonte antiga (#1126), posição real de ação/ETF (#1124).

Regiões clonadas da página viva, só estas. A captura veio de `https://dev.criptofarol.com.br` (bundle `index-DUWqPrYj.js` / `index-WJwiIv3A.css`), com a API simulada, a 1440 e a 390 px, e as regiões estão marcadas com `COPIED:start`/`COPIED:end`:

- `index.html` (canônico, `/monitor`):
  - fundo vivo e AppNav desktop (barra lateral e topo, 1440 px) e móvel (topo, 390 px);
  - ajuda "Como usar o Monitor" e aviso educacional;
  - topo do Monitor (busca, "Telegram: on", Tema, Atualizar), cabeçalho e indicadores;
  - filtros (Em portfólio/Todos, Timeframe, Estrelas, Estratégia);
  - seções "Em posição" e "Saída / cobertura", com as linhas e os cartões de BTC/USDT, SOL/USDT e ETH/USDT;
  - detalhe aberto de BTC/USDT, de uma segunda captura com a linha aberta, guardado num `<template>`.
- `favorites.html` (`/favorites`): AppNav, ajuda, cabeçalho "Estratégias favoritas", resumo e filtro por estrelas, filtros, a tabela e os cartões de BTC/USDT e ETH/USDT, e o rodapé da lista.
- `results.html` (`/combo/results`, resultado de NVDA 1d): página inteira, menos o bloco da recusa.
- `configure.html` (`/combo/configure` com NVDA): página inteira, menos o texto de 1 ação.
- `discovery.html` (`/combo/discovery`, Decidir com o modal de promoção de NVDA): página inteira, menos o título, o destino e o botão do modal.
- `profile.html` (`/profile`): página inteira, menos a frase do cartão "Alertas Telegram".
- `live.css`: o CSS vivo inteiro (`index-WJwiIv3A.css`), sem poda.

O toast transitório "Atualizado · N estratégias analisadas" ficou fora das capturas. O estado de formulário que o React põe por propriedade foi refletido em atributo.

O delta fica só nos blocos `DELTA:start`/`DELTA:end`:
- **Monitor:**
  - linhas e cartões de NVDA (Binance Ações), SPY (ETF) e NVDA (fonte antiga), com a identidade abreviada, o estado do mercado sob a pílula de Status, "Alerta", carteira e o texto de ajuda;
  - QQQ (ETF com série curta), escondido fora do cenário "dado insuficiente";
  - detalhe de NVDA (fonte antiga) gerado do cartão dela, com os botões indisponíveis e o motivo em texto;
  - tag "Alerta" em BTC e SOL; estado "Dados atrasados" de BTC/USDT (linha, cartão e motivo do alerta), escondido fora do cenário;
  - indicadores e contagens ("Em carteira" conta ativos distintos);
  - faixa da transição (frase com data só para quem recebia pelo catálogo);
  - painel Demonstração com os cenários e as mensagens do Telegram.
- **Favoritos:**
  - coluna "Alertar" para o dono, a partir de 1280 px; entre 1024 e 1279 px, o mesmo controle na célula Ações;
  - o controle "Alertar" de BTC/USDT e ETH/USDT, trocado para ter `aria-label` desde a carga e, no celular, o rótulo "Alertar: on/off" com alvo de 44 px;
  - aviso "Fora da carteira: sem alerta" (cenário "SPY fora da carteira");
  - linhas e cartões de NVDA, SPY e NVDA (fonte antiga), com estrelas, "Alertar" e Revalidar ligados, status de atualização com o último pregão e a configuração da fonte antiga;
  - resumo por estrelas contando todas as classes, sem a nota "ainda não";
  - faixa e vista da vitrine do catálogo;
  - Demonstração.
- **Resultado:** "Salvar nos Favoritos" liberado, modal com a identidade, a nota de "Alertar" e da carteira, a duplicata, o sucesso com "Ver em Favoritos" (44 px) e o foco preso no modal; Demonstração.
- **Combo:** o texto de 1 ação.
- **Descoberta:** "Promover a favorito tier 3", destino "Tier 3 · observação" com a configuração e a nota de "Alertar" e da carteira.
- **Perfil:** a frase da origem dos alertas.
- **Cola do clone:** invólucros `.cf-desk`/`.cf-mob` do AppNav e `<template>` do detalhe de BTC.

## Decisões de Alan no Design (26/10/2026)

Registradas no issue e incorporadas nas decisões, nos specs e nas tasks abaixo. Não há pergunta aberta.

1. **Transição da cripto.** Quem hoje recebe alerta de cripto só pelo catálogo, sem favorito próprio marcado, recebe um aviso único no Telegram no dia da troca e vê uma faixa no Monitor até marcar um favorito. Não há período de transição. A frase com data ("Até 26/10 você recebia…") aparece só para quem recebia alerta do catálogo (decisão 16).
2. **Favorito novo nunca nasce marcado para alertar**, inclusive no lote e na Descoberta. Marcar "Alertar" é sempre ato do dono (decisão 3).
3. **Varredura de ação e ETF:** só a passada das 08:05 BRT (decisão 15).
4. **Sem limite na varredura.** Alertas de sinal e avisos de atraso da varredura não são cortados pelo limite de mensagens por hora; a identidade do evento já impede repetição. Cada alerta continua sendo uma mensagem própria. O limite configurável fica só no aviso de falha da carteira Binance (decisão 5).
5. **Linha de ação/ETF no Monitor compacta:** o estado do mercado fica sob a pílula de Status e a linha de identidade é abreviada, perto da altura da linha de cripto (decisão 13, com as medidas).

## Goals / Non-Goals

**Goals:**

- Alertas a partir dos favoritos de cada usuário marcados "Alertar", em cripto, ação e ETF; o catálogo deixa de ser origem.
- Um estado e um alerta por favorito; mesmo ativo com configurações distintas não colide.
- Evento idempotente: reinício, reprocessamento e varredura repetida não duplicam.
- Ação/ETF na carteira recebe entrada e saída; nenhuma depende da Binance; falha da carteira pausa só a cripto.
- Candle fechado, mercado fechado, feriado e atraso pelo calendário da classe, sem falso atraso.
- Um aviso de atraso real por ativo e episódio; mercado fechado só na tela.
- Fonte, sessão e ajuste na identidade e na chave de duplicata.
- Ação/ETF no Monitor, na atualização diária e favoritável por todo caminho que já favorita cripto.
- Alerta ≠ ordem, escrito na mensagem.

**Non-Goals:**

- Novos canais de notificação ou robô de negociação (Não entra).
- Compra/venda manual e proteção nativa de ação/ETF (histórias de operação); Operar continua só cripto.
- Migrar os favoritos de fonte antiga para a Binance (#1126).
- Posição real de ação/ETF (#1124); até lá a carteira de ação/ETF é a marcação manual.
- Mensagem no Telegram para mercado fechado, abertura ou feriado (Não entra).
- Mudar a cadência do scan diário (decisão 3 de Alan: só a passada das 08:05).
- Escolher sessão (pré/pós-pregão) ou ajuste na tela: hoje há um valor só (regular de NY, split).

## Decisions

1. **Página primária = `/monitor`; extras com copy visível.** O Monitor é onde se acompanha e onde aparecem atraso e mercado fechado; é a rota canônica do gate ("table.signals" e os textos do catálogo estão em COPIED). Cinco outras rotas mudam texto ou controle visível e têm clone extra na mesma pasta:
   - `/favorites`: "Alertar", estrelas e Revalidar de ação/ETF, status e configuração;
   - `/combo/results`: "Salvar nos Favoritos" de ação/ETF;
   - `/combo/configure`: o texto de 1 ação;
   - `/combo/discovery`: destino do modal;
   - `/profile`: a frase da origem dos alertas.

   Alternativa rejeitada: Favoritos como primária. O "Alertar" mora lá, mas os estados do mercado, que são o centro do card, só existem no Monitor.

2. **Origem = favoritos marcados de cada usuário.** `run_monitor_telegram_alert_scan` passa a:
   - (a) listar os usuários elegíveis;
   - (b) para cada um, ler os próprios favoritos com `notify_telegram = true`, de qualquer classe, respeitando `monitor_telegram_tier_filter` sobre o nível do favorito;
   - (c) avaliar as oportunidades da união desses favoritos uma vez só (o cache `fonte:símbolo_tempo` de `_calculate_opportunities` já deduplica a coleta);
   - (d) decidir a transição por favorito e entregar ao dono.

   `get_catalog_opportunities(alerts_only=True)` deixa de ser chamado pelo scan. A vitrine do catálogo continua só para exibição (`monitor-curated-fallback`) e passa a valer só para quem não tem favorito próprio de nenhuma classe. Assim, quem tem só NVDA vê o NVDA dele. O `user_id` do `POST /api/admin/monitor-telegram-alerts/run` continua sem efeito (o scan é de todos). Alternativa rejeitada: marca por usuário sobre as linhas do catálogo (`MonitorStrategyPreference.notify_telegram`). Ela manteria o catálogo como origem, contra a decisão de Alan.

3. **"Alertar" é do dono e nasce desligado.** `PATCH /favorites/{id}` aceita `notify_telegram` do dono, admin ou não, e recusa com 403 quem não é dono (inclusive na vitrine). Em Favoritos, a coluna vira "Alertar" para todo dono:
   - **a partir de 1280 px**, coluna própria (o vivo a esconde abaixo de 1540 px). Medido no protótipo: a Estratégia fica com 252 px a 1280 e 271 px a 1440;
   - **de 1024 a 1279 px**, a coluna some e o mesmo controle (sino, com `aria-pressed`) vai para a célula Ações, que quebra em 2×2. A Estratégia fica com 241 px a 1180 e 90 px a 1024, o mesmo que o vivo já tem sem a coluna (antes do rework, a coluna a deixava com 4 px a 1024);
   - **no celular**, o botão diz "Alertar: on" ou "Alertar: off" (não "TG") e tem alvo de 44 px.

   O controle mantém o visual vivo (sino + On/Off) e ganha `aria-label` "Alertar no Telegram: ligado/desligado" em todas as linhas, inclusive as de cripto, desde a carga. Quando "Alertar" está ligado num favorito de ação ou ETF cujo ativo não está na carteira, a linha mostra "Fora da carteira: sem alerta. Marque o ativo como "No portfólio" no Monitor" (decisão 6: fora da carteira, ação/ETF não alerta). Todo favorito novo nasce com `notify_telegram = false`, inclusive os do lote e da Descoberta, e o default da coluna vira falso (decisão 2 de Alan). Isso evita que um lote de 300 ações comece a mandar alerta. A migração mantém as marcas que o admin já tinha nos próprios favoritos (hoje o catálogo), e Alan continua recebendo o que marcou. As marcas de quem não é admin vão para falso: o default `True` nunca foi escolha dessas pessoas.

4. **Estado por favorito.** Nova tabela `monitor_favorite_alert_states` (`favorite_id` PK com FK `ON DELETE CASCADE`, `status`, `candle_time`, `observed_at`, `payload_json`). A primeira leitura grava a base, sem alerta (hoje, sem estado anterior, a matriz já suprime). A migração semeia o estado de cada favorito marcado a partir de `monitor_observed_statuses` pelo par `(symbol, timeframe)`. Assim, a primeira varredura depois do deploy não perde nem repete a transição em curso. `monitor_observed_statuses` fica só para leitura até o archive (P3 decide removê-la). Alternativa rejeitada: chave composta (símbolo, tempo, estratégia, fonte…). Ela é frágil, porque parâmetros mudam no refresh; o favorito já é a identidade.

5. **Evento com identidade e reserva.** `monitor_telegram_alerts` ganha `favorite_id` e `event_key`. A chave do sinal é `sha256(user|favorite|nova leitura|início do candle fechado)`; a do aviso de atraso, `sha256(user|delay|fonte|símbolo|episódio)`. Um índice único parcial `(user_id, event_key) WHERE result_status IN ('sending','sent','dry_run','unknown')` garante que nenhuma segunda reserva passe. O fluxo:
   - reserva `sending`, com commit;
   - chama o Telegram;
   - grava `sent` ou `failed`.

   No começo de cada varredura, `sending` com mais de 10 min vira `unknown` e nunca é reenviado: no máximo uma vez, porque duplicar é pior que perder, e o `unknown` fica visível no resumo e no log. `failed` (antes de o Telegram aceitar) não reserva, então a varredura seguinte tenta de novo enquanto o evento for o atual. A janela `min_repeat_minutes` deixa de decidir duplicata. Alternativa rejeitada: só a janela de tempo, que duplica depois de 6 h e engole a volta legítima à mesma leitura.

   **Sem limite na varredura (decisão 4 de Alan).** Alertas de sinal e avisos de atraso da varredura não passam pelo limite de mensagens por usuário e janela (`monitor_telegram_rate_limit_count`/`…_window_minutes`): cada um sai como mensagem própria, e a chave do evento é o que impede repetição. O limite configurável continua valendo só para o aviso operacional de falha da carteira Binance (um por usuário e janela). Comportamento observável: se sete favoritos marcados de uma pessoa mudam no mesmo candle, saem sete mensagens na mesma varredura, e o resumo do scan não tem `rate_limited` para sinal nem para atraso.

6. **Matriz com ação/ETF na carteira.** `should_send_position_aware_alert` recebe a classe:
   - **ação/ETF:** `in_portfolio` é a marca manual (`MonitorPreference`). Com a marca, `EXIT→HOLD` = "buy" e `HOLD→EXIT` = "sell"; sem a marca, `outside_portfolio_scope`.
   - **cripto:** a matriz de hoje, sem mudança.

   Quando o #1124 trouxer posição real de ação/ETF, a regra de ação/ETF passa a usar a posição (ponto de extensão: `SymbolPortfolioStatus.derived_active` por classe). Falha da carteira Binance: o usuário vai para `binance_sync_failed_users`. Pulam só os favoritos de cripto daquele usuário; ação/ETF segue. O aviso operacional passa a dizer "Os alertas de cripto ficam pausados até a sincronização voltar; ações e ETFs seguem."

7. **Candle fechado pelo calendário.** Novo helper em `nyse_calendar.py`: `last_closed_start(timeframe, now)`, que devolve o início do último candle cujo fechamento (fim do bloco de 15m/1h/4h ancorado às 09:30, ou o fechamento do pregão, inclusive meio pregão, no 1d) é ≤ agora. Para cripto, o equivalente 24/7 (`floor(now, tf) - tf`). `_calculate_opportunities`, para ação/ETF:
   - corta a série nos candles fechados (`index ≤ last_closed_start`);
   - usa a série inteira como `df_closed`, sem o `iloc[:-1]` que assume candle em formação;
   - usa o último candle fechado como `df_for_distance`.

   A cripto mantém o caminho de hoje. Com isso, às 08:05 BRT de terça, NVDA 1d lê segunda. A leitura de ação/ETF vem de `BinanceEquityMarketDataProvider`, que completa só o trecho que falta (`market_data_providers.py:637-680`). O favorito de fonte antiga lê Stooq como hoje. A janela de histórico do Monitor de ação/ETF passa a ser contada em pregões (`expected_candles`), não em dias corridos: 75 dias corridos de 4h dão ~100 velas, pouco para médias longas (P3 o tamanho).

8. **Estado do mercado e atraso real.** `_calculate_opportunities` devolve `market_state` por linha: `{state: open|closed|stale, reason: session|weekend|holiday|after_hours, closes_at, next_open, last_candle, expected_candle, stale_since}`. A regra:
   - **`closed`:** ação/ETF fora de `session_window(hoje)`.
   - **`stale`:** o último candle recebido é menor que `last_closed_start(tf, now − tolerância)`. A tolerância é por tempo (P3; ex.: 15m→10 min, 1h→15 min, 4h→30 min, 1d→90 min), para a publicação da Binance. Falha de leitura sem nenhum candle também conta.
   - **`open`:** o resto.

   **Atraso real** é faltar o candle de um pregão (ou bloco) que o calendário diz que já fechou. Ele é detectado na varredura seguinte, mesmo com o mercado fechado agora. É assim que se lê "atraso real durante o pregão" do issue: a varredura diária roda às 08:05 BRT, fora do pregão de NY, e acha na terça a falta do candle de segunda.

   A cripto só pode ser `open` ou `stale`. Nova tabela `monitor_data_health` (`data_source`, `symbol`) guarda o episódio: estado, `stale_since`, `episode_id`, detalhe por tempo e `updated_at`. O ativo fica `stale` se qualquer série monitorada dele está; o episódio fecha quando todas normalizam. No front, `resolveOpportunitySignal` deixa de usar a regra "3 períodos" para ação/ETF. Ela usa `market_state` (sem atraso → sem "Sem candle válido"), e a cripto continua com a regra de hoje mais o `stale` do servidor. **Precedência na cripto:** quando o servidor diz `stale`, a linha e o cartão mostram só "Dados atrasados · último candle …; esperado …" (com "Sinal em espera"), e o "alerta" do cartão traz esse texto no lugar de "Sem candle válido/atual para esta resolução.". Os dois nunca aparecem juntos. A regra "3 períodos" só vale quando a resposta não traz `market_state`.

   **Dado insuficiente no Monitor** (quarto tom). O favorito com menos candles fechados do que a análise precisa entra na seção "Saída / cobertura" com a pílula "Sem leitura" e, abaixo dela, o ícone de ampulheta + "Dados insuficientes · 40 de 200 candles", em cinza com borda tracejada, e "Sem sinal até completar o histórico". Ele não gera alerta nem aviso de atraso; quando a série completa, a primeira leitura é só base. Os horários na tela ficam em BRT, com NY entre parênteses para ação/ETF.

9. **Aviso único e mercado fechado só na tela.** O scan manda o aviso "Dados atrasados" uma vez por usuário, ativo e episódio. Ele vai a quem receberia alerta daquele ativo: favorito marcado e o ativo na carteira. O aviso traz o ativo, a fonte, o último candle, o esperado e "sinais em espera". Enquanto o ativo está `stale`, os favoritos dele não geram alerta de sinal: a leitura de dado incompleto não decide. A recuperação fecha o episódio sem mensagem, e a leitura normal decide o sinal, com a data do candle que o produziu. `closed` nunca gera mensagem. Isso vale para cripto também (24/7): um atraso real da Binance Spot também deixa o sinal inválido.

10. **Mensagem e alerta ≠ ordem.** `build_monitor_alert_candidate` recebe o favorito. A mensagem ganha:
    - "Ativo: NVDA (Ação · USD)";
    - "Configuração: <rótulo longo>";
    - "Candle: <data do pregão> (pregão fechou às 17:00 BRT)";
    - valores na moeda do ativo;
    - a linha "Este alerta não envia ordem: é só o sinal da estratégia." (a redação antiga, "Ordem: nenhuma enviada", podia ser lida como "não há ordem sua" por quem operou pelo Operar).

    O `payload_json` guarda `favorite_id`, configuração e `candle_time`. Nenhum caminho do scan cria `MonitorSpotOrderRequest`. O `signal_monitor` ganha uma guarda explícita: só consulta ativos que terminam em `USDT` e nunca recebe ação/ETF. O teste cobre isso, sem calendário (não há sinal de ação lá).

11. **Identidade de configuração.** `favorite_strategies` ganha `data_source`, `session` e `adjustment` (string, com backfill pela regra do spec `favorite-configuration-identity`). Colunas, não `parameters`: o mapeamento de parâmetros do Monitor casa chave com alias de indicador (`opportunity_service.py:1313-1365`), e "session" ou "adjustment" em `parameters` poderiam virar `length` de um indicador. Os pontos que passam a usar a configuração:
    - `find_existing_favorite` e `lock_and_find_duplicate` comparam os três campos e os põem na chave do lock;
    - `GET /favorites/exists` aceita `data_source`/`session`/`adjustment`, com default pela classe do catálogo;
    - create, lote, Descoberta e refresh gravam a configuração vinda do resultado (`analysis_asset`/`analysis_conventions`).

    Rótulos: cripto "Binance Spot · 24/7"; Binance Ações "Binance Ações · NY · split" (longo "… pregão regular de NY · ajustado por split"); fonte antiga "Stooq · fonte antiga · diário". `conventionsShort` (`favoriteClass.ts:146-150`), que hoje põe "Binance Ações" em qualquer ticker, passa a usar a configuração. O 409 vira "Estratégia já existe nos favoritos com esta configuração".

12. **Ação e ETF favoritáveis e com 1 estrela.** Saem:
    - `_refuse_equity_favorite` e `asset_class_not_favoritable`;
    - a recusa em `ComboResultsPage`;
    - `FAVORITE_REFUSED_REASON`;
    - o texto de 1 ação do Combo (`assetSelection.ts:1113`);
    - `EQUITY_DESTINATION`/`EQUITY_DESTINATION_NOTE`/`promotionTitle` por classe;
    - `PENDING_EQUITY_TEXT`, `OFF_EQUITY_TITLE` e `tierNoteText`.

    O resultado de ação/ETF abre o mesmo `SaveFavoriteModal`, com a linha de identidade, a nota "Depois de salvar, marque "Alertar" em Favoritos…" e a duplicata como texto no modal (`role=alert`). O Combo com 1 ação continua abrindo o resultado ("…para acompanhar, salve nos Favoritos por lá."). O lote e a Descoberta gravam `tier = 3` em qualquer classe; os favoritos de ação/ETF já gravados ficam como estão (o dono marca as estrelas). Estrelas, "Alertar" e Revalidar de ação/ETF funcionam como na cripto. O Revalidar já passa `data_source` (`walk_forward_revalidation.py:79`).

13. **Monitor com ação/ETF.** `_is_equity_favorite` sai das listas, e `get_opportunities` deixa de filtrar por `/`. A resposta ganha `asset_class`, `currency`, `configuration`, `market_state` e `notify_telegram`. Na tela:
    - os filtros de classe da lista e do tempo passam a aceitar todas as classes;
    - **linha compacta (decisão 5 de Alan):** abaixo da estratégia, a identidade abreviada "Ação · USD · Binance · NY · split" (fonte antiga: "Ação · USD · Stooq · antiga · diário"), com o rótulo longo no `title` e no detalhe ("configuração …"). O estado do mercado fica **sob a pílula de Status**, com ícone + texto curto, quebrando dentro da coluna sem alargá-la: aberto "Aberto · fecha 17:00 (16:00 NY)"; fechado "Fechado · fim de semana · abre seg. 10:30 (09:30 NY)", "Fechado · feriado em NY · abre sex. 11:30 (09:30 NY)" ou "Fechado · abre hoje 10:30 (09:30 NY)", em cinza com relógio; atrasado "Dados atrasados · falta seg. 26/10" em âmbar com triângulo e "Sinal em espera"; insuficiente "Dados insuficientes · 40 de 200 candles" com ampulheta e "Sem sinal". O texto completo (último e esperado, data e motivo) fica no `title` e no cartão;
    - **medidas (protótipo):** a 1440, a linha de NVDA tem 178 px aberta e 190 px atrasada, contra 158 px da linha de BTC (+13% e +20%; antes eram 230 e 305 px). A 390, o cartão de NVDA tem 913 px aberto e 960 px atrasado, contra 813 px do cartão de BTC (+12% e +18%; antes 935 e 982 px). A 1280 e a 1024 a linha fica em 178/190 px (BTC 142 px);
    - nas tags, "Alerta" no favorito marcado (a coluna Tags viva some abaixo de 1440 px; incumbente);
    - no cartão do celular, a identidade abreviada e "Alerta" numa linha, e o estado do mercado completo abaixo, entre a faixa de controle e o detalhe;
    - o indicador "Em carteira" conta ativos distintos (as duas NVDA contam uma vez);
    - a carteira de ação/ETF usa o "No portfólio/Fora do portfólio" vivo e ganha "Ação/ETF na carteira recebe entrada e saída no Telegram.";
    - Operar continua só cripto USDT.

    "Abrir Gráfico"/"Ver Trades" de ação/ETF Binance leem `/api/market/history?asset_id=…&timeframe=<tf do favorito>`. Na fonte antiga, os dois ficam visíveis e indisponíveis (`aria-disabled`, `title` e `aria-label` "… (indisponível)") na linha, no cartão e no detalhe, e o motivo aparece em texto abaixo deles: "Fonte antiga: gráfico e trades depois da migração para a Binance." (no toque não há tooltip). O detalhe da fonte antiga é o do próprio favorito ("Saída confirmada", "Risco residual"), não o de outra linha. Ação/ETF não tem "Operar" na linha, no cartão nem no detalhe. `indicator_cache_key` (`opportunity_service.py:1268`) passa a incluir a fonte, para NVDA Binance e NVDA Stooq não dividirem indicadores.

14. **Atualização diária com calendário.** Em `favorite_backtest_refresh_service.py`:
    - `_ensure_fresh_frame`/`_ensure_fresh_candles` de ação/ETF comparam o último candle com `last_closed_start` (decisão 7) e não com `_max_candle_age`;
    - sem candle fechado novo desde a última atualização, o ciclo pula a otimização e mantém `SUCCESS`;
    - `_prepare_market_data` de `binance_equity` usa `prepare_equity_history(intrabar=True)`, e a falta de 15m vira precisão diária marcada (como no lote), não falha;
    - série curta grava `INSUFFICIENT` com "N de M candles" (Favoritos mostra "Aguardando dados: N de M candles", em cinza);
    - no período "todo o histórico", o fim de ação/ETF é a data do último pregão fechado;
    - `favorite_operational_period._first_candle_iso` recebe a fonte do favorito.

    O status de sucesso de ação/ETF em Favoritos passa a "Backtest atualizado: 24/10, 08:12 · último pregão 23/10".

15. **Cadência sem mudança.** O scan continua uma vez por dia, às 08:05 BRT (timers sem mudança). O sinal de ação/ETF 1d do pregão sai na manhã seguinte, antes da abertura de NY. O de sexta sai no sábado e o de véspera de feriado no dia do feriado; o calendário garante que nada disso vire atraso. Favorito intradiário (15m/1h/4h) de qualquer classe segue a cadência diária de hoje. Alan decidiu manter só a passada das 08:05 (decisão 3); não há passada depois do fechamento de NY.

16. **Transição da cripto (decisão 1 de Alan).** Quem hoje recebe pelo catálogo e não tem favorito próprio marcado deixa de receber no deploy, como o issue diz, sem período de transição. "Quem recebia pelo catálogo" é quem tem pelo menos um alerta do catálogo enviado (`sent`) em `monitor_telegram_alerts` antes do deploy. Para essas pessoas:
    - um aviso único no Telegram no dia da troca ("Mudança nos alertas"), com os ativos que a pessoa recebia e como voltar a receber, com chave de evento própria (`transition`, uma por usuário);
    - a faixa `role=status` no Monitor, "Os alertas do Telegram agora vêm dos seus favoritos marcados "Alertar". Você ainda não marcou nenhum. Até <data do deploy> você recebia os alertas do catálogo do Cripto Farol; agora cada pessoa escolhe os próprios.", com o link "Marcar em Favoritos" (44 px), até a pessoa marcar um favorito.

    Quem tem o Telegram ligado, nenhum favorito marcado e nunca recebeu alerta do catálogo vê a mesma faixa sem a frase com data e não recebe o aviso. Em Favoritos, a vitrine ganha a faixa "Estas estratégias são o catálogo do Cripto Farol e não mandam alerta…", e as linhas do catálogo ficam sem o controle.

17. **Regressão.** Os testes de contrato cobrem:
    - só A recebe NVDA e BTC/USDT marcados;
    - NVDA Binance e NVDA Stooq, com estados e alertas separados;
    - duas estratégias de BTC/USDT 1d mudando juntas;
    - scan repetido, queda com `sending` e volta legítima;
    - NVDA na carteira com entrada e saída, NVDA fora da carteira, e cripto com a matriz de hoje;
    - atraso na terça, persistência na quarta e recuperação sem mensagem;
    - sábado, feriado (26/11/2026) e meio pregão (27/11/2026);
    - falha da carteira com NVDA seguindo;
    - favorito novo com a primeira leitura sem alerta;
    - lote de ações nascendo sem "Alertar";
    - 409 da mesma configuração e coexistência de fontes;
    - refresh de domingo sem falha, `INSUFFICIENT` e fim do período no último pregão;
    - `signal_monitor` sem ticker.

    O E2E Playwright de `/monitor`, `/favorites`, `/combo/results`, `/combo/configure`, `/combo/discovery` e `/profile`, com a API simulada, segue o protótipo.

## Risks / Trade-offs

- [Quem recebia pelo catálogo para de receber no deploy] → é a decisão do issue. Alan decidiu o aviso único e a faixa, sem período (decisão 16).
- [Scan por usuário custa mais] → a coleta é deduplicada por `fonte:símbolo_tempo` na mesma varredura. O beta tem poucos usuários; o número de favoritos marcados é o limite, e um lote não marca nada.
- [Varredura sem limite pode mandar muitas mensagens num dia de virada] → decisão 4 de Alan: cada alerta é uma mensagem, e o volume é limitado pelo que a pessoa marcou (lote e Descoberta nascem sem "Alertar"). A chave do evento impede repetição; o limite configurável fica só no aviso de falha da carteira.
- [No máximo uma vez perde mensagem em queda no meio do envio] → o `unknown` fica no resumo e no log. Duplicar alerta é o defeito que o issue pede para evitar.
- [Tolerância do atraso mal calibrada gera aviso falso] → o aviso é um só por episódio, e a tolerância é por tempo gráfico (P3 com dado real do DEV).
- [Aviso de atraso também na cripto é comportamento novo] → um por ativo e episódio, só para quem tem o ativo marcado e na carteira; o sinal com dado incompleto é pior.
- [Favoritos de fonte antiga (Stooq) podem atrasar mais] → o aviso diz a fonte; a migração é do #1126.
- [Mudança do default `notify_telegram` altera o hábito do admin] → os favoritos novos de Alan deixam de entrar sozinhos no Telegram (decisão 2 de Alan).
- [Servidor de protótipos lê os worktrees só ao iniciar] → o pai reiniciou `criptofarol-dev-prototypes.service`; a URL pública responde 200 e serve o disco (conferido no rework r1).

### P3 aceitos (detalhe de Apply)

- Nomes de tabela, colunas e campos: `monitor_favorite_alert_states`, `monitor_data_health`, `event_key`, `market_state` e as subchaves, `configuration`, `INSUFFICIENT`; forma do resumo do scan.
- Tolerâncias do atraso por tempo gráfico; o limite de 10 min para `sending` virar `unknown`; o tamanho da janela de histórico em pregões.
- Remover `monitor_observed_statuses` e `monitor_telegram_min_repeat_minutes` depois do archive.
- Nome do feriado na tela ("feriado em Nova York" sempre; o nome quando `exchange_calendars` der).
- Texto exato da mensagem do Telegram, do aviso de atraso e da transição (as do protótipo são a base).
- `classify_asset_type` (`asset_classification.py:18`) não distingue ETF: a classe vem de `analysis_asset`/catálogo.
- O índice único parcial precisa de PostgreSQL. Nos testes com SQLite, a guarda é a consulta antes da reserva.
- Incumbentes fora do card, todos em COPIED:
  - reset `*` vivo que zera padding (cartões do modal de Salvar e da Descoberta sem respiro, pílulas e filtros apertados);
  - coluna "Par / Estratégia" estreita, que quebra o nome da estratégia em monoespaçado;
  - "Confirmar gestão" cortado no cartão a 390;
  - valores em "$" no Monitor;
  - "Operar indisponível · Validando disponibilidade…" com a API simulada;
  - logo do AppNav por caminho absoluto, que só carrega no domínio DEV;
  - cores, tamanhos e raios literais do vivo (#b7bdc6, #929aa5, #474d57; 9, 10, 11 e 15 px; raios de 5 e 10 px) usados no delta para casar com o tema `monitor-theme`, fora da rampa do `DESIGN.md` (achados do hook do detector, classificados como intencionais);
  - `gray-on-color` em `favorites.html` (linha 14): o detector casa por linha, e a linha 14 é o corpo inteiro. Nela há uma estrela desligada (`text-zinc-400`) e uma ligada (`bg-amber-400`) em elementos diferentes. Nenhum elemento tem as duas classes, e a captura viva de `/favorites` dá o mesmo achado. Herdado, não mexido;
  - coluna Tags do Monitor some abaixo de 1440 px (a tag "Alerta" só aparece a 1440 e no cartão); Estratégia de Favoritos com 90 px a 1024 sem a coluna "Alertar" (igual ao vivo);
  - `.btn` do `monitor-theme` sem anel de foco, tags de 10 px, rótulos `#707a8a` (4,0:1) e o reset que zera padding;
  - `SaveFavoriteModal` vivo sem semântica de diálogo (o Apply leva a do protótipo).
- Achados P3 da dupla (A e B), aceitos como detalhe de Apply:
  - contar `unknown` no resumo do admin com o favorito e o candle;
  - aviso de atraso por (fonte, ativo): NVDA em duas fontes pode gerar dois avisos, e o texto diz a fonte;
  - leitura que muda e volta enquanto o ativo está atrasado não gera alerta na recuperação (a leitura normal decide);
  - migração que zera "Alertar" de quem não é admin (a marca nunca teve efeito para essas pessoas);
  - lote e Descoberta com 1 estrela põem ação/ETF no Monitor como a cripto; observar o volume com lote grande;
  - horário do fechamento na mensagem ("17:00 BRT" no verão de NY, 18:00 BRT no inverno): o Apply calcula pelo calendário;
  - vitrine com apelido e nota do admin: a redação é do servidor (`monitor-curated-fallback`);
  - vocabulário "Tier 3" na Descoberta × "1 estrela"/"Acompanhar" em Favoritos (incumbente);
  - "Pregão aberto" na fonte antiga (Stooq, só diário) não promete dado intradiário; o Apply pode trocar por "Pregão aberto · fonte diária";
  - o aviso de atraso pode dizer quantos favoritos do ativo ficaram em espera;
  - ícone do par de ação/ETF com 9 px ("NVDA"); o Apply pode usar o logo;
  - `discovery.html` dá `classify=BLOCKED` contra o catálogo (`/combo/discovery` pede "Rascunho de varredura", que não existe no Decidir com o modal); o gate só lê o canônico;
  - `parse_live_route` leva `surface: existing` como justificativa (já apontado no #1120 e no #1121);
  - dois favoritos marcados do mesmo ativo mudando juntos não têm cenário na Demonstração; o spec e o E2E cobrem.
- Protótipo:
  - linhas copiadas (SOL, ETH) e as de Favoritos não abrem o detalhe; só BTC e as de ação/ETF abrem;
  - os números de preço, risco e métricas são amostra; a data da faixa ("Até 26/10") é a do deploy;
  - QQQ com 40 pregões na Binance Ações é amostra do estado de dado insuficiente.

## Migration Plan

1. Alembic:
   - colunas `data_source`, `session` e `adjustment` em `favorite_strategies`, com backfill;
   - default de `notify_telegram` falso, com `UPDATE` para falso nos favoritos de quem não é admin;
   - tabelas `monitor_favorite_alert_states` (semeada de `monitor_observed_statuses` para favoritos marcados) e `monitor_data_health`;
   - `favorite_id` e `event_key` em `monitor_telegram_alerts`, com índice único parcial.
2. Deploy do servidor e do front juntos. O primeiro scan depois do deploy usa a base semeada. O aviso de transição sai uma vez, só para quem recebia alerta do catálogo (decisão 16).
3. Rollback: voltar o código devolve o scan pelo catálogo, que ainda tem `monitor_observed_statuses`. As colunas novas ficam sem uso. As marcas zeradas de quem não é admin não voltam: elas nunca tiveram efeito.

## Open Questions

Nenhuma. As cinco perguntas do Design foram respondidas por Alan em 26/10/2026 (seção "Decisões de Alan no Design").

## Apply contract

O Apply lê este `design.md` e os HTML de `frontend/public/prototypes/card-1122-favoritos-alertas-acoes-etfs/` como spec de layout.

**Contrato visível (não P3):**

- **Monitor:**
  - linhas e cartões de ação/ETF nas seções vivas;
  - linha compacta: identidade abreviada abaixo da estratégia e estado do mercado sob a pílula de Status, perto da altura da linha de cripto (decisão 13);
  - estado do mercado com ícone + texto em quatro tons: aberto, fechado (motivo e próxima abertura em BRT e NY, feriado), atrasado (último e esperado + "Sinal em espera") e dado insuficiente ("Sem leitura", "N de M candles", "Sem sinal");
  - cripto atrasada com "Dados atrasados" no lugar de "Sem candle válido/atual", nunca os dois;
  - tag "Alerta";
  - carteira de ação/ETF com o texto de ajuda; "Em carteira" conta ativos distintos;
  - gráfico de ação/ETF pela série do favorito; na fonte antiga, os dois botões indisponíveis na linha, no cartão e no detalhe, com o motivo em texto, e o detalhe do próprio favorito;
  - indicadores e filtros com todas as classes;
  - faixa da transição com a frase datada só para quem recebia pelo catálogo.
- **Favoritos:**
  - "Alertar" do dono: coluna a partir de 1280 px, célula Ações de 1024 a 1279 px, "Alertar: on/off" com 44 px no celular, `aria-label` em todas as linhas desde a carga;
  - "Fora da carteira: sem alerta" quando "Alertar" está ligado num ativo de ação/ETF fora da carteira;
  - estrelas, "Alertar" e Revalidar de ação/ETF ligados;
  - status "Backtest atualizado: … · último pregão …" e "Aguardando dados: N de M candles";
  - configuração da fonte antiga;
  - resumo por estrelas com todas as classes, sem a nota "ainda não";
  - vitrine sem "Alertar" e com a faixa.
- **Resultado:** "Salvar nos Favoritos" de ação/ETF, modal com identidade, nota de "Alertar" e da carteira, duplicata e sucesso com "Ver em Favoritos" (44 px, recebe o foco); o modal prende o foco, Esc fecha sempre e o foco volta ao gatilho.
- **Combo:** texto de 1 ação.
- **Descoberta:** "Promover a favorito tier 3" e destino Tier 3 para ação/ETF, com a nota de "Alertar" e da carteira.
- **Perfil:** frase da origem dos alertas.
- **Telegram:** mensagem de sinal com configuração, candle e "Este alerta não envia ordem: é só o sinal da estratégia."; aviso único de atraso (ação, ETF e cripto); nada para mercado fechado; uma mensagem por alerta, sem limite por hora na varredura; aviso de transição só para quem recebia pelo catálogo.
- **Comportamentos dos specs:**
  - origem por usuário e estado/evento por favorito;
  - matriz de ação/ETF e falha da carteira só para cripto;
  - candle fechado pelo calendário;
  - atraso real sem falso positivo;
  - identidade e duplicata;
  - atualização pelo calendário;
  - favorito novo sem "Alertar".

**P3 aceito (Apply):** os itens da subseção "P3 aceitos" em Risks / Trade-offs.

## Prototype

- **Canônico:** `frontend/public/prototypes/card-1122-favoritos-alertas-acoes-etfs/index.html`, clone de `/monitor`. URL: https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/
  - BTC/USDT, SOL/USDT e ETH/USDT vêm da captura viva.
  - NVDA (Binance Ações), SPY (ETF) e NVDA (fonte antiga) entram nas seções vivas, na linha compacta: identidade abreviada abaixo da estratégia, estado do mercado sob a pílula de Status e "Alerta" quando marcado. O NVDA da fonte antiga tem 1 estrela (igual a Favoritos), fica sem "Alerta", na Saída, com "Abrir Gráfico" e "Ver Trades" indisponíveis e o motivo em texto na linha, no cartão e no detalhe.
  - O chevron abre o detalhe de NVDA, SPY, NVDA (fonte antiga, gerado do cartão dela: "Saída confirmada", "Risco residual") e BTC, com "No portfólio/Fora do portfólio". Na ação/ETF, o detalhe mostra a configuração longa e "Ação/ETF na carteira recebe entrada e saída no Telegram.". Desmarcar a carteira com "Em portfólio" esconde as linhas de NVDA; "Todos" as traz de volta. "Em carteira" mostra 5 ativos (as duas NVDA contam uma vez).
  - O filtro Timeframe funciona.
- **Demonstração** (fim da página, no fluxo), com o momento da leitura e as mensagens do Telegram daquela varredura (uma mensagem por alerta):
  - Seg. 15:00, pregão aberto (padrão): "Aberto · fecha 17:00 (16:00 NY)" na linha; nenhuma mensagem.
  - Sáb.: "Fechado · fim de semana · abre seg. 10:30 (09:30 NY)". Sai o alerta de entrada de NVDA (Binance Ações), do pregão de sexta, com "Este alerta não envia ordem: é só o sinal da estratégia.". NVDA da fonte antiga não muda e não alerta. A nota diz que a varredura não tem limite por hora.
  - Dom. 08:05, atraso real de BTC/USDT: a linha e o cartão de BTC mostram "Dados atrasados" e "Sinal em espera", e o "alerta" do cartão traz o último e o esperado no lugar de "Sem candle válido/atual". Sai um aviso "Dados atrasados" de BTC/USDT.
  - Feriado (26/11): "Fechado · feriado em NY · abre sex. 11:30 (09:30 NY)"; nenhuma mensagem.
  - Atraso real de NVDA (ter. 08:05): "Dados atrasados · falta seg. 26/10" em âmbar e "Sinal em espera"; o cartão traz o último e o esperado. SPY e a fonte antiga ficam fechados fora do pregão. Sai um aviso único.
  - Dado normalizado (qua. 08:05): NVDA vai para "Saída / cobertura", e sai o alerta de saída com "Este alerta não envia ordem: é só o sinal da estratégia.". Recuperação sem mensagem.
  - QQQ com histórico curto: a linha de QQQ aparece em "Saída / cobertura" com "Sem leitura", "Dados insuficientes · 40 de 200 candles" e "Sem sinal"; nenhuma mensagem.
  - Quem recebia pelo catálogo: faixa com a frase "Até 26/10 você recebia…" e "Marcar em Favoritos" (44 px), sem "Alerta" nas linhas, e a mensagem "Mudança nos alertas".
  - Telegram ligado, nunca recebeu: a mesma faixa sem a frase com data e nenhuma mensagem.
- **Extra `favorites.html`** (clone de `/favorites`):
  - "Alertar": coluna a partir de 1280 px; de 1024 a 1279 px, sino na célula Ações; no celular, "Alertar: on/off" com 44 px. Todos os controles, inclusive de BTC/USDT e ETH/USDT, têm `aria-label` desde a carga e anunciam a troca;
  - NVDA (Binance, 2 estrelas, Alertar ligado), NVDA (fonte antiga, 1 estrela, "Stooq · fonte antiga · diário", desligado) e SPY (1 estrela, ligado) com estrelas, Alertar e Revalidar funcionando;
  - status "Backtest atualizado: 24/10, 08:12 · último pregão 23/10";
  - resumo "Acompanhar 2 · Interesse alto 2 · Top picks 1", sem a nota "ainda não".
  - Demonstração: "SPY fora da carteira" mostra "Fora da carteira: sem alerta. Marque o ativo como "No portfólio" no Monitor" sob o status de SPY (some ao desligar "Alertar"); a vitrine mostra a faixa do catálogo e "Catálogo · não alerta" no lugar do controle; a lista mostra os três status (atualizado, "Aguardando dados: 40 de 200 candles", falha por atraso real).
- **Extra `results.html`** (clone de `/combo/results` com NVDA 1d): "Salvar nos Favoritos" ligado. O modal mostra:
  - "NVDA · Ação · USD" e "Binance Ações · pregão regular de NY · ajustado por split · 1d · Long";
  - a nota "O favorito nasce sem alerta. Para receber os sinais no Telegram, marque "Alertar" em Favoritos e marque o ativo como "No portfólio" no Monitor." (até 75ch);
  - o sucesso com "Ver em Favoritos" (44 px, recebe o foco), ou a duplicata "Já está nos favoritos com esta configuração…" (Demonstração).

  O modal prende o foco (Tab e Shift+Tab), Esc fecha com o foco em qualquer lugar e o foco volta a "Salvar nos Favoritos".
- **Extra `configure.html`** (clone de `/combo/configure` com NVDA): "1 ação (NVDA): otimiza e abre o resultado; para acompanhar, salve nos Favoritos por lá."
- **Extra `discovery.html`** (clone de `/combo/discovery`, Decidir com o modal de NVDA): "Promover a favorito tier 3" e "Tier 3 · observação", com a configuração e a nota "Para receber no Telegram, marque "Alertar" lá e marque o ativo como "No portfólio" no Monitor.".
- **Extra `profile.html`** (clone de `/profile`): frase nova do cartão "Alertas Telegram".
- **Apoio:** `live.css` (CSS vivo inteiro), `delta.css`, `delta.js`. Nenhuma página é painel ANTES/DEPOIS nem "N estados"; cada Demonstração fica no fim, no fluxo.

## Prototype Validation

Evidência do rework r1 (26/10/2026), depois da onda dupla. Qualquer mudança posterior nos arquivos abaixo a invalida.

- **Captura viva:** a mesma do autor (a1): Playwright Python, Chromium headless shell 1243, `pt-BR`, tema escuro, fuso `America/Sao_Paulo`, API simulada, a 1440 e a 390 px, de `https://dev.criptofarol.com.br` (bundle `index-DUWqPrYj.js` / `index-WJwiIv3A.css`). Páginas: `/monitor` (fechado e com a linha de BTC aberta), `/favorites`, `/profile`, `/combo/results` (NVDA e o modal de BTC), `/combo/configure` com NVDA e `/combo/discovery` com o modal de NVDA. Toda região COPIED das seis páginas é substring literal de uma captura (0 fora), e nenhum marcador cai dentro de tag. `live.css` = `index-WJwiIv3A.css` inteiro (sha `8f4edf0aca9a…`).
- **Gate do clone** (`scripts/process-fsm/design_clone_gate.py`, catálogo do HEAD):
  - `design_token_gap` = None, com tokens em L1–L3;
  - `evaluate_clone_gate` = True e `clone_gate_ok` = True;
  - `classify(index.html, /monitor)` = PASS;
  - `copied_utf8_sum` 59.700 B. Os 8 textos e `table.signals` do catálogo estão em COPIED.
- **Bytes por página** (copiado × delta, sem os marcadores):

  | Arquivo | Bytes | sha256 | COPIED | DELTA |
  |---|---|---|---|---|
  | `index.html` (canônico) | 145.709 | `d0d7aa5a80af…` | 26 pares, 59.518 B | 26 pares, 82.421 B |
  | `favorites.html` | 112.651 | `09880e120ada…` | 21 pares, 52.624 B | 24 pares, 56.548 B |
  | `results.html` | 46.546 | `95909352c0c3…` | 6 pares, 38.956 B | 6 pares, 6.375 B |
  | `configure.html` | 33.736 | `d94216041b57…` | 5 pares, 32.530 B | 5 pares, 143 B |
  | `discovery.html` | 47.508 | `f3720c4db2d7…` | 7 pares, 45.478 B | 7 pares, 774 B |
  | `profile.html` | 30.564 | `9824fe0bc64d…` | 5 pares, 29.295 B | 5 pares, 239 B |
  | `live.css` | 248.557 | `8f4edf0aca9a…` | clone inteiro | — |
  | `delta.css` | 10.868 | `9e34bd03b55b…` | — | delta |
  | `delta.js` | 24.866 | `37794adfaaa2…` | — | delta |

  O delta do `index.html` é grande porque as linhas, os cartões e os detalhes de ação/ETF (inclusive QQQ e o detalhe próprio da fonte antiga) são gerados a partir da marcação viva de BTC/ETH. Em `favorites.html`, os controles "Alertar" de BTC/USDT e ETH/USDT viraram DELTA (aria-label e rótulo do celular), por isso o COPIED caiu de 55.441 para 52.624 B.
- **URL pública:** os 9 arquivos respondem 200 em `https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/`, idênticos ao disco (sha256), e a pasta `/` serve o `index.html`.
- **`openspec validate card-1122-favoritos-alertas-acoes-etfs --strict`:** válido.
- **Browser gate na URL pública:** Playwright Python, contexto novo por largura: 1440×900, 1280×800 e 1024×768 (desktop) e 390×844 (`isMobile`, toque), fuso São Paulo. Resultado: **223/223 asserts PASS**, 0 `pageerror`, 0 `console.error`, 0 resposta ≥ 400, sem rolagem horizontal em nenhum cenário medido. Cobre:
  - **Monitor:** 3 linhas ou cartões de ação/ETF visíveis e QQQ escondido; identidade abreviada; estado sob a pílula de Status; "Em carteira" 5; estrela única da fonte antiga; os dois botões da fonte antiga indisponíveis com o motivo visível (linha a 1440/1280/1024, cartão a 390, detalhe); detalhe da fonte antiga com "Saída confirmada" e "Risco residual", sem preço de BTC; detalhe de NVDA sem "Operar"; fim de semana, cripto atrasada (sem "Sem candle válido" junto), atraso de NVDA, recuperação, dado insuficiente (quarto tom com ícone próprio, "Sem leitura", "Em carteira" 6), transição com e sem a frase datada; "Este alerta não envia ordem" e nenhum "Ordem: nenhuma enviada"; nota de "sem limite por hora"; parágrafos da Demonstração com `max-width`.
  - **Medidas da linha (decisão 5):** a 1440, BTC 158 px, NVDA 178 px aberta e 190 px atrasada (antes 230/305); a 1280 e a 1024, BTC 142 px, NVDA 178/190 px; a 390, cartão de BTC 813 px, de NVDA 913 px aberto e 960 px atrasado (antes 935/982).
  - **Favoritos:** coluna "Alertar" a 1440 e 1280; a 1024 (e 1180) a coluna some e o sino da célula Ações liga/desliga em sincronia com a coluna; Estratégia com 271 px (1440), 252 px (1280), 241 px (1180) e 90 px (1024, igual ao vivo); `aria-label` em todos os controles visíveis desde a carga, inclusive cripto; no celular "Alertar: on" com 44 px; fonte antiga com 1 estrela; "Fora da carteira: sem alerta" aparece com "SPY fora da carteira" e some ao desligar; vitrine com faixa e sem controle.
  - **Resultado:** nota com "No portfólio" e `max-width`; 12 Tabs e 3 Shift+Tab sem sair do modal; depois de salvar, o foco vai para "Ver em Favoritos" (≥ 44 px); Esc com o foco fora do modal fecha e devolve o foco ao Salvar; duplicata; Esc depois da duplicata.
  - **Combo, Descoberta e Perfil:** os textos novos ("No portfólio" na Descoberta) e nenhum texto antigo.
- **Detector Impeccable CLI** (`node .agents/skills/impeccable/scripts/detect.mjs --json`):
  - 0 achados em `delta.css`, `delta.js` e `discovery.html`;
  - nos HTML, só achados do incumbente: `flat-type-hierarchy` (Monitor, Favoritos, Combo, Perfil), `gray-on-color` (Favoritos, linha 14, falso positivo herdado da captura viva, ver P3; Combo, em COPIED), `ai-color-palette` (Resultado, Combo);
  - o hook de design marca no `delta.css` as cores, os tamanhos e os raios literais do `monitor-theme` (P3 aceito).
- **Scripts:** autor em `c1122/` (captura, `clone.py`, `check.py`, `run_gate.py`); rework em `c1122r1/` (`build_monitor.py`, `build_favorites.py`, `build_extras.py`, `build.sh`, `gate_r1.py`, `measure.py`, `shots.py`, `numbers.sh`), no scratchpad da sessão.

## Design Critique

Com-tela. Teto 1+1+1: autor, dupla A/B e 1 rework. O rework (r1) aplicou as decisões de Alan no Design, o P1 e os P2 de produto e mecânicos da dupla. Não houve segundo rework.

- Autor: `design-autor 1122 d1` (isolado). Rework: `design-autor 1122 r1` (isolado).
- Assessment A: `assessment-a 1122 d1b` (isolado; produto, UX, acessibilidade, fidelidade). Assessment B: `assessment-b 1122 d1` (isolado; detector + navegador). O primeiro nascimento do A (`assessment-a 1122 d1`) foi negado pelo hook antes de nascer (faltava `model_selection_wave_capture`) e não rodou.
- Verdict: **PASS** (A: PASS com rework; B: PASS com rework; os dois aplicados no r1). Tokens: `UI impact: affected` / `live_route: /monitor` / `surface: existing`.
- Proto canônico: https://dev.criptofarol.com.br/prototypes/card-1122-favoritos-alertas-acoes-etfs/ (clone de `/monitor`). Páginas extras com texto visível alterado: `favorites.html`, `results.html`, `configure.html`, `discovery.html`, `profile.html`.
- Snapshots: `.impeccable/critique/1122-card-1122-favoritos-alertas-acoes-etfs-A.md` e `…-B.md`. O Gist OpenSpec não é a crítica.

- **P0**: nenhum.
- **P1, corrigido no r1**: a 1024 px a coluna "Alertar" apagava a Estratégia em Favoritos (4 px). Agora a coluna aparece a partir de 1280 px e, entre 1024 e 1279, o controle vai para a célula Ações (Estratégia com 90 px a 1024, como o vivo).
- **Juízo, decidido por Alan no Design** (comentários [1–3](https://github.com/oalansilva/crypto/issues/1122#issuecomment-6423794112), [4 revista](https://github.com/oalansilva/crypto/issues/1122#issuecomment-6424255998), [5](https://github.com/oalansilva/crypto/issues/1122#issuecomment-6424140420)), aplicado no r1:
  - transição da cripto: aviso único no Telegram no dia da troca e faixa no Monitor até marcar um favorito, sem período de transição; a frase com data só para quem recebia alerta do catálogo;
  - favorito novo nunca nasce marcado para alertar;
  - varredura de ação/ETF só às 08:05;
  - sem limite na varredura: sinal e aviso de atraso não são cortados, cada alerta é uma mensagem; o limite fica só no aviso de falha da carteira Binance;
  - linha de ação/ETF compacta no Monitor (190 px no pior caso a 1440, antes 305 px).
- **P2 de produto, corrigidos no r1**: cenário de cripto atrasada e precedência "Dados atrasados" sobre "Sem candle válido"; estado de dado insuficiente no Monitor ("40 de 200 candles"); aviso "Fora da carteira: sem alerta" e notas citando "No portfólio"; texto "Este alerta não envia ordem: é só o sinal da estratégia."; definição de atraso real (falta o candle de um pregão que já fechou).
- **P2 mecânicos, corrigidos no r1**: detalhe da NVDA de fonte antiga sem preços de BTC e com "Abrir Gráfico"/"Ver Trades" indisponíveis; estrelas e contagem "Em carteira" coerentes; motivo da indisponibilidade em texto visível; botão "Alertar" com 44 px e `aria-label` em todas as linhas; modal de Salvar com foco preso, Esc e retorno do foco; `75ch` nas notas.
- **P3 aceitos, para o Apply**: os itens da subseção de P3 aceitos em Risks / Trade-offs, mais os achados do detector nos HTML em regiões COPIED do incumbente (`flat-type-hierarchy`, `gray-on-color` em Favoritos linha 14, `ai-color-palette`) e as cores, tamanhos e raios literais do tema do Monitor no `delta.css`.
- **Disposition:** o delta visível fica no Monitor (`/monitor`): ação e ETF como favoritos acompanhados, estado do mercado (aberto, fechado, atrasado, dados insuficientes), alerta por favorito com estratégia e configuração, e a faixa da transição; Favoritos ganha "Alertar" por favorito e configurações distintas do mesmo ativo; Resultado, Combo, Descoberta e Perfil só trocam os textos "ainda não". Migração dos favoritos de fontes antigas fica para o #1126; compra/venda e posição real, para o #1124.

### Proxies

- `design.md` words: 8343 (antes desta seção)
- HTML generated vs copied (`index.html`): 82421 vs 59518
- Spawns: 4 (design-autor d1, assessment-a d1b, assessment-b d1, design-autor r1); mais 1 nascimento negado pelo hook (`assessment-a 1122 d1`)
