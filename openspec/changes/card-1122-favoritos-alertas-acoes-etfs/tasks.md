## 1. Dados e identidade

- [x] 1.1 Migração Alembic: colunas `data_source`, `session` e `adjustment` em `favorite_strategies`, com backfill (par com `/` → `ccxt`/`24x7`/`none`; `parameters.data_source = binance_equity` → `binance_equity`/`regular_ny`/`split` ou `analysis_conventions`; ticker sem fonte → `stooq`/`eod`/`legacy`).
- [x] 1.2 Na mesma migração: default de `notify_telegram` falso e `UPDATE` para falso nos favoritos de quem não é admin (e-mails de `ADMIN_EMAILS` mantêm a marca). — **substituída pela 8.1 (default ligado e dados existentes).**
- [x] 1.3 Tabelas `monitor_favorite_alert_states` (FK com `ON DELETE CASCADE`, semeada de `monitor_observed_statuses` para os favoritos marcados) e `monitor_data_health`; `favorite_id` e `event_key` em `monitor_telegram_alerts`, com índice único parcial `(user_id, event_key)` para `sending`/`sent`/`dry_run`/`unknown`.
- [x] 1.4 `favorite_uniqueness.py`: `find_existing_favorite` e `lock_and_find_duplicate` comparam fonte, sessão e ajuste e os põem na chave do lock; helper único que deriva a configuração de `data_source` + `asset` + `conventions`, com rótulos curto e longo.
- [x] 1.5 `routes/favorites.py`:
  - sai `_refuse_equity_favorite`;
  - `POST` grava a configuração e devolve o 409 "Estratégia já existe nos favoritos com esta configuração";
  - `GET /exists` aceita `data_source`/`session`/`adjustment`;
  - `PATCH` aceita `notify_telegram` do dono, recusa com 403 o favorito do catálogo visível e responde 404 ao favorito que a pessoa não vê;
  - a lista usa a vitrine só para quem não tem favorito próprio de nenhuma classe;
  - a resposta traz `configuration`.
- [x] 1.6 Lote (`batch_backtest_service.py`) e Descoberta (`discovery_service.py`) gravam `tier = 3` em qualquer classe, `notify_telegram = false` e a configuração, e passam a configuração à checagem de duplicata. — **substituída pela 8.3 (lote e Descoberta sem estrela, alerta ligado).**

## 2. Calendário, candle fechado e estado do mercado

- [x] 2.1 `nyse_calendar.py`: `last_closed_start(timeframe, now)` (1d no fechamento do pregão, inclusive meio pregão; blocos de 15m/1h/4h ancorados às 09:30) e `market_status(now)` (`open`/`closed` com motivo, fechamento e próxima abertura); equivalente 24/7 para cripto.
- [x] 2.2 `opportunity_service.py`:
  - ação/ETF entram nas listas (sai `_is_equity_favorite` e o filtro por `/`);
  - a série de ação/ETF é cortada no último candle fechado e não descarta a última linha;
  - a janela de histórico de ação/ETF é contada em pregões;
  - `indicator_cache_key` inclui a fonte;
  - cada linha traz `asset_class`, `currency`, `configuration`, `market_state` e `notify_telegram`;
  - a vitrine vale só sem favorito próprio de nenhuma classe.
- [x] 2.3 Atraso real: a comparação com `last_closed_start(tf, now − tolerância)` por série e o episódio por ativo em `monitor_data_health` (abre, mantém, fecha) entram no cálculo usado pelo Monitor e pelo scan.

## 3. Alertas do Telegram

- [x] 3.1 `monitor_telegram_alerts.py`: — **substituída pela 8.2 (estrela + alerta ligado, sem filtro de estrelas do sistema).**
  - o scan percorre os usuários elegíveis, cada um com os próprios favoritos marcados (com o filtro de estrelas do sistema);
  - avalia a união uma vez;
  - decide a transição pelo estado por favorito (a primeira leitura é só base);
  - entrega só ao dono.
- [x] 3.2 Evento com `event_key` (o limite do aviso de falha da carteira fica sem uso: 8.2):
  - reserva `sending` antes do envio e grava `sent`/`failed`;
  - `sending` antigo vira `unknown` sem reenvio;
  - `failed` volta na varredura seguinte enquanto o evento for o atual;
  - a janela `min_repeat_minutes` deixa de decidir duplicata;
  - alertas de sinal e avisos de atraso não passam pelo limite `monitor_telegram_rate_limit_count`/`…_window_minutes` (uma mensagem por alerta); o limite fica só no aviso de falha da carteira Binance.
- [x] 3.3 Matriz: — **substituída pela 8.2 (carteira fora da decisão e fim do aviso operacional).**
  - ação/ETF com a marca na carteira recebe entrada e saída, e sem a marca não recebe;
  - a cripto fica como hoje;
  - falha da carteira Binance pula só os favoritos de cripto do usuário, e o aviso operacional diz que ações e ETFs seguem.
- [x] 3.4 Mensagem de sinal com classe e moeda, configuração (rótulo longo), data do candle fechado, valores na moeda e "Este alerta não envia ordem: é só o sinal da estratégia."; `payload_json` com `favorite_id`, configuração e `candle_time`.
- [x] 3.5 Aviso "Dados atrasados": — **substituída pela 8.2 (aviso a quem tem o ativo no Monitor com alerta ligado).**
  - um por usuário, ativo e episódio, a quem tem favorito marcado do ativo na carteira, em ação, ETF e cripto;
  - sinais do ativo em espera enquanto o episódio dura;
  - recuperação sem mensagem;
  - mercado fechado nunca manda mensagem.
- [x] 3.6 Transição de quem recebia pelo catálogo (pelo menos um alerta do catálogo `sent` antes do deploy) e não tem favorito marcado: aviso único "Mudança nos alertas" no dia da troca, com os ativos que recebia, chave de evento `transition` (um por usuário); sem período de transição; nenhum aviso para quem nunca recebeu. A API do Monitor informa se a pessoa recebia pelo catálogo, para a faixa. — **substituída pela 8.4 (critério, texto e marca da transição).**
- [x] 3.7 `ops/run_monitor_telegram_alert_scan.py` e `POST /api/admin/monitor-telegram-alerts/run`: resumo com eventos por favorito, avisos de atraso, avisos de transição e `unknown` (sem `rate_limited` para sinal e atraso).
- [x] 3.8 `signal_monitor.py`: guarda que só consulta ativos terminados em `USDT`.

## 4. Atualização diária

- [x] 4.1 `favorite_backtest_refresh_service.py`:
  - frescor de ação/ETF pelo calendário, e sem candle fechado novo o ciclo pula a otimização e mantém `SUCCESS`;
  - `binance_equity` coleta por `prepare_equity_history(intrabar=True)`, com precisão diária marcada quando falta 15m;
  - série curta grava `INSUFFICIENT` com "N de M candles";
  - o fim do período "todo o histórico" de ação/ETF é o último pregão fechado.
- [x] 4.2 `favorite_operational_period._first_candle_iso` usa a fonte do favorito.

## 5. Frontend

- [x] 5.1 Monitor (`MonitorStatusTab.tsx`, `OpportunityCard.tsx`, `types.ts`, `signalResolution.ts`) — tag "Alerta", frase da carteira e faixa substituídas pela 8.6:
  - linhas e cartões de ação/ETF;
  - linha compacta: identidade abreviada abaixo da estratégia (rótulo longo no `title` e no detalhe) e estado do mercado sob a pílula de Status, com texto curto na tabela e completo no cartão;
  - quatro tons com ícone + texto: aberto, fechado, atrasado (com "Sinal em espera") e dado insuficiente (pílula "Sem leitura", "N de M candles");
  - cripto `stale` pelo servidor mostra "Dados atrasados" no lugar de "Sem candle válido/atual" (nunca os dois); `market_state` no lugar da regra "3 períodos" para ação/ETF;
  - tag "Alerta";
  - texto de ajuda da carteira de ação/ETF; "Em carteira" conta ativos distintos;
  - filtros e indicadores com todas as classes;
  - faixa da transição com a frase datada só para quem recebia pelo catálogo, tudo como em `index.html` do protótipo.
- [x] 5.2 Gráfico e trades do Monitor para ação/ETF Binance pela série do favorito (`/api/market/history`, no tempo do favorito); na fonte antiga, os dois botões indisponíveis (`aria-disabled`, `title`, `aria-label`) na linha, no cartão e no detalhe, com o motivo em texto visível; o detalhe mostra o estado e os valores do próprio favorito; ação/ETF sem "Operar".
- [x] 5.3 Favoritos (`FavoritesDashboard.tsx`, `favoriteClass.ts`): — **substituída pela 8.7 (Favoritos sem "Alertar").**
  - "Alertar" para todo dono: coluna a partir de 1280 px; de 1024 a 1279 px, o controle na célula Ações; no celular, "Alertar: on/off" com alvo de 44 px; `aria-label` em todas as linhas desde a carga;
  - "Fora da carteira: sem alerta" em ação/ETF com "Alertar" ligado e o ativo fora da carteira;
  - estrelas, "Alertar" e Revalidar de ação/ETF ligados;
  - status com o último pregão e "Aguardando dados";
  - rótulos de configuração (fonte antiga);
  - resumo por estrelas com todas as classes;
  - vitrine sem controle e com a faixa;
  - saem `PENDING_EQUITY_TEXT`, `OFF_EQUITY_TITLE` e `tierNoteText`, como em `favorites.html`.
- [x] 5.4 Resultado (`ComboResultsPage.tsx`, `SaveFavoriteModal.tsx`, `equityExecution.ts`): "Salvar nos Favoritos" de ação/ETF com a identidade, a nota de "Alertar" e da carteira, a duplicata e o sucesso com "Ver em Favoritos" (44 px, recebe o foco); o modal vira diálogo que prende o foco, fecha com Esc em qualquer foco e devolve o foco ao gatilho; sai `FAVORITE_REFUSED_REASON`, como em `results.html`. — **nota do modal substituída pela 8.8.**
- [x] 5.5 Combo (`assetSelection.ts`): texto de 1 ação de `configure.html`. Descoberta (`discoveryMulticlass.ts`, `DiscoveryPage.tsx`): título, destino Tier 3 (com a nota de "Alertar" e da carteira) e confirmação de `discovery.html` para ação/ETF. Perfil (`TelegramAlertsForm.tsx`): frase de `profile.html`. — **textos da Descoberta e do Perfil substituídos pela 8.8.**

## 6. Testes e verificação

- [x] 6.1 Testes de backend, um por cenário:
  - só A recebe;
  - NVDA Binance e Stooq separados;
  - duas estratégias juntas;
  - scan repetido, `sending`→`unknown` e volta legítima;
  - entrada e saída de NVDA na carteira, NVDA fora da carteira e cripto como hoje;
  - sete favoritos mudando na mesma varredura geram sete mensagens, sem `rate_limited`; o aviso de falha da carteira continua limitado;
  - atraso, persistência e recuperação, em NVDA e em BTC/USDT;
  - transição: aviso único só para quem recebia pelo catálogo;
  - sábado, feriado de 26/11/2026 e meio pregão de 27/11/2026;
  - falha da carteira com NVDA seguindo;
  - primeira leitura sem alerta;
  - lote sem "Alertar";
  - 409 da mesma configuração e coexistência de fontes;
  - refresh de domingo, `INSUFFICIENT` e fim do período;
  - `signal_monitor` sem ticker;
  - nenhuma ordem criada.
- [x] 6.2 Teste da migração: backfill da configuração, marcas de quem não é admin zeradas, estado semeado do par.
- [x] 6.3 (cenários de "Alertar", carteira e faixa substituídos pela 8.11) E2E Playwright com a API simulada, a 1440 e a 390 px: `/monitor` (estados aberto, fechado, feriado, atraso de ação e de cripto, dado insuficiente, "Alerta", fonte antiga indisponível e faixa com e sem data), `/favorites` ("Alertar" do dono a 1440, 1280 e 1024 px e no celular, aviso fora da carteira, estrelas e status de ação/ETF, vitrine), `/combo/results` (salvar, foco preso, Esc e duplicata), `/combo/configure`, `/combo/discovery` (modal) e `/profile`.
- [x] 6.4 Comparar cada rota entregue com o HTML do protótipo e registrar no handoff os elementos seguidos e qualquer desvio justificado.
- [x] 6.5 Ensaio no DEV com dry-run do scan (`force_dry_run`): um usuário com NVDA e BTC/USDT marcados e um sem marca; conferir no resumo os eventos, o aviso de atraso e a ausência de mensagem de mercado fechado. — **substituída pela 8.13 (ensaio com a regra nova).** <!-- covenant-flow:after-qa -->

## 7. Residuais da revisão (pós-T18)

- [x] 7.1 P1 — timeout local não é atraso real (`opportunity_service.py`): série que só estourou o orçamento do pool fica sem leitura na passada (sem `check_series`, sem episódio, sem sinal nem DM "Dados atrasados"); falha de leitura da fonte segue como atraso. A varredura do Telegram tem orçamento próprio (`OPPORTUNITIES_ALERT_FETCH_TIMEOUT_SECONDS`, padrão 300 s) e aproveita as leituras que terminaram depois dele; o GET do Monitor segue com 8 s. Teste: três séries, um leitor e orçamento curto, duas passadas, nenhuma DM de atraso e nenhum episódio aberto.
- [x] 7.2 P2 — saúde do dado por tempo gráfico (`market_state.py`, `monitor_telegram_alerts.py`): o atraso do ativo numa passada é decidido só pelas séries lidas nela; o episódio guardado só fecha quando nenhum detalhe segue atrasado (sem reabrir nem repetir o aviso). O detalhe de outro tempo gráfico não vira último/esperado da linha (vai em `stale_timeframe`/`stale_detail`), e a DM usa os horários e o rótulo da série atrasada. Testes: 15m atrasado + 1d em dia na passada seguinte (1d fora de espera) e DM com "(15m)", nunca "(1d)".
- [x] 7.3 P2 — contrato 403/404 (`specs/monitor-telegram-favorite-toggle/spec.md`): 403 para favorito do catálogo visível ao usuário e 404 para favorito que ele não vê, sem mudar nada; teste renomeado para `test_owner_marks_alertar_others_get_404_hidden_and_403_on_visible_catalog`. A decisão 3 do `design.md` (403) fica como está.
- [x] 7.4 P3 — aviso "Mudança nos alertas" só na primeira varredura depois de `monitor_telegram_favorite_origin_at` (marca `monitor_telegram_transition_scan_at`, janela de 2 dias), para quem recebia pelo catálogo e não tinha favorito marcado nesse momento. Testes: marcar logo após a troca e desmarcar depois não gera aviso; primeira varredura semanas depois da troca não avisa.
- [x] 7.5 P3 — cartão de NVDA atrasada a 390 px (`OpportunityCard.tsx`) como no protótipo: campos de risco de ação/ETF com valor (sem "indisponível — dado não confiável"), sem repetir o estado na linha "alerta" e sem a configuração longa no cartão do celular; altura ~975 px contra ~960 px do protótipo. A cripto segue como hoje (teste próprio).
- [x] 7.6 P3 — comparação geométrica de Favoritos: no compare do #1120, texto, estilo e altura voltam à tolerância de 3 px (só a largura da mesa a 1440 aceita até 75 px, pela coluna "Alertar"); no E2E do #1122, `/favorites` contra `favorites.html` a 1440, 1280 e 1024 px (colunas e mesa ±4 px, linhas ±6 px, controle "Alertar" ±3 px).

## 8. Nova regra de alertas (pós-T18 de 27/10)

Decisões de Alan de 27/10/2026 (design.md, "Decisões de Alan para a nova regra", "Decisões de Alan no Design d2" e decisões 2, 3, 6, 8, 9, 10, 12, 16 e 18 a 21). Nenhuma tarefa edita `design.md`, specs, `.design-digest` ou o protótipo.

- [x] 8.1 Migração Alembic `20261027_0001` (depois de `20261026_0001`): `server_default` de `notify_telegram` → `true`; d2-1 (`tier → NULL` nos favoritos com nota "gerado em lote …" ou "descoberta via sweep …" que ainda estão com 1 estrela) e d2-2 (`notify_telegram = true` em todos); semente de `monitor_favorite_alert_states` para os favoritos com estrela e alerta ligado ainda sem estado, a partir de `monitor_observed_statuses`; o downgrade devolve só o `server_default` falso. `models.py`: default `True`.
- [x] 8.2 `monitor_telegram_alerts.py`:
  - a varredura avalia, por usuário elegível, os próprios favoritos com `tier` 1–3 e `notify_telegram = true`; ignora `monitor_telegram_tier_filter` (preferência e variável de ambiente) e registra `tier_filter_ignored` no resumo quando preenchido; linhas do catálogo nunca entram;
  - sem carteira: toda mudança `EXIT→HOLD`/`HOLD→EXIT` sai, nas três classes; não chama `fetch_user_wallet_holdings` nem `resolve_portfolio_status_for_user`; saem o aviso operacional da carteira, `binance_sync_failed_users` e os motivos `outside_portfolio_scope`/`suppressed_*` do resumo;
  - aviso "Dados atrasados" a quem tem favorito do ativo com estrela e alerta ligado, sem olhar a carteira;
  - a mensagem de sinal e o aviso de atraso ganham a linha de como parar de receber (decisão 10).
- [x] 8.3 Dados e rotas:
  - `opportunity_service.get_alert_favorites`: só `tier IN (1,2,3)` e `notify_telegram`, sem `tier_filter`;
  - `routes/favorites.py` `PATCH`: `tier` de nulo para 1–3 no favorito próprio grava `notify_telegram = true` na mesma transação; trocar entre 1–3 não mexe; `notify_telegram` segue só do dono (403 no catálogo visível, 404 no invisível);
  - `batch_backtest_service.py` e `discovery_service.py`: `tier = None` e `notify_telegram = True` em qualquer classe; a promoção da Descoberta recusa pedido com tier (422 "promoção sem estrela") e cria o favorito sem estrela;
  - `POST /favorites`: alerta ligado ao nascer (sem estrela, como hoje).
- [x] 8.4 Transição e faixa:
  - aviso "Mudança nos alertas" com o texto novo, a quem recebia pelo catálogo e não tem estratégia própria com estrela e alerta ligado;
  - a marca `monitor_telegram_transition_scan_at` só é gravada sem dry-run e sem nenhuma entrega de transição `failed`; em dry-run nem a reserva da chave `transition` é gravada (residual P2 da w3);
  - `alert_origin_for_user` / `GET /api/opportunities/alert-origin`: `has_monitored_strategy`, `alerts_on`, `received_catalog_alerts`, `catalog_until` e `show_banner` = vitrine (quem não é admin, sem favorito próprio com estrela); sai `has_marked_favorite`.
- [x] 8.5 Monitor lê `stale_detail` (residual P2 da w3; `marketState.ts`, `MarketStateBadge.tsx`, `OpportunityCard.tsx`): linha retida por outro tempo gráfico mostra "Dados atrasados no 15m · falta 14:30" e o cartão (e o `title` da linha) "Dados atrasados no 15m · último 14:15; esperado 14:30", nunca "falta" do candle do próprio tempo que já chegou.
- [x] 8.6 Monitor (`MonitorStatusTab.tsx`, `OpportunityCard.tsx`, `types.ts`), como em `index.html` do protótipo:
  - interruptor "Alerta" (`role=switch`, `aria-checked`, nome com ativo, tempo, estratégia e, em ação/ETF, a configuração; sino ou sino cortado + "ligado"/"desligado") como primeiro botão da célula de ações da linha (1280 px ou mais) e na célula Status de 1024 a 1279 px, no cartão (390, "Alerta: ligado/desligado", 44 px) e no detalhe (com o estado atual; linha e detalhe sincronizados); grava por `PATCH /favorites/{id}` com atualização otimista, volta em erro e anuncia no status; não abre a linha;
  - "Catálogo · sem alerta" (12 px) no lugar do interruptor na vitrine;
  - sai a tag "Alerta" das Tags e da faixa de identidade do detalhe; sai "Ação/ETF na carteira recebe entrada e saída no Telegram."; entra a ajuda "Entrada e saída saem com ou sem o ativo na carteira. Desligado, nada sai no Telegram para esta estratégia." só no detalhe (o cartão do celular não a repete);
  - ajuda "Como usar o Monitor" com "Toda estratégia aqui manda alerta no Telegram, com ou sem o ativo na carteira; para parar de receber, desligue o "Alerta" da linha." (fora da vitrine);
  - faixa da vitrine nova (texto da decisão 16, ícone de informação no lugar do sino), com a frase datada só para quem recebia pelo catálogo e "Ir para Favoritos" (44 px);
  - Monitor do admin continua abrindo em "Em portfólio", sem aviso de estratégias fora da carteira (d2-3).
- [x] 8.7 Favoritos (`FavoritesDashboard.tsx`, `favoriteClass.ts`), como em `favorites.html`: saem a coluna "Alertar", o sino da célula Ações, o "Alertar: on/off" do celular, o aviso "Fora da carteira" e a leitura da carteira para ele; entram a ajuda das estrelas, a legenda "No Monitor"/"Fora do Monitor" na célula das estrelas (linha e cartão) e "No Monitor · alerta ligado" depois da primeira estrela, o resumo "Acompanhar · No Monitor, com alerta ligado", estrelas de 44 px no cartão do celular (e `aria-label` "1 estrela"…), o status ao dar a primeira e tirar a última estrela e a faixa da vitrine nova (só Combo).
- [x] 8.8 Textos: nota do `SaveFavoriteModal`; Descoberta (`discoveryMulticlass.ts`, `DiscoveryPage.tsx`): título "Promover a favorito", destino "Favoritos · sem estrela", nota, "Em Favoritos" na linha e no aviso de sucesso, pedido sem `tier`; Perfil (`TelegramAlertsForm.tsx`): frase nova. Como em `results.html`, `discovery.html` e `profile.html`.
- [x] 8.9 Testes de backend, um por cenário: só o dono com estrela e alerta ligado recebe; sem estrela não alerta; alerta desligado não alerta; catálogo (inclusive com a estrela da preferência) não alerta; entrada de NVDA fora da carteira; saída de SPY; BTC com saldo recebe a reentrada; SOL sem saldo recebe a saída; a varredura não chama a carteira e a falha da Binance não muda nada nem manda aviso; atraso a quem tem o ativo no Monitor com alerta ligado e não a quem desligou; `tier_filter` ignorado; dar a estrela liga, trocar 1→2 não mexe, tirar as estrelas para, tirar e dar de novo religa um alerta desligado; mensagem de sinal e aviso de atraso com a linha de como parar; lote e Descoberta sem estrela; Descoberta recusa tier; transição com o critério novo e sem marca em dry-run nem com `failed`; PATCH 403/404. Ajustar ou remover os testes da matriz e do aviso operacional que deixam de valer.
- [x] 8.10 Teste da migração `20261027_0001`: default, d2-1, d2-2 e semente de estado; downgrade.
- [x] 8.11 E2E Playwright (`card-1122-favoritos-alertas-acoes-etfs.spec.ts`) com a API simulada, a 1440, 1280, 1024 e 390 px: interruptor da linha, do cartão e do detalhe (estado, `aria-checked`, nome, 44 px, sem abrir a linha, detalhe sincronizado, erro); vitrine com "Catálogo · sem alerta" e faixa nova com e sem data; sem a tag "Alerta"; ajuda da carteira no detalhe e não no cartão; frase da ajuda do Monitor; "Dados atrasados" e `stale_detail` na linha e no cartão; admin em "Em portfólio" sem aviso, e "Todos" com as estratégias fora da carteira; Favoritos sem "Alertar" em nenhuma largura, legenda, resumo "Acompanhar", estrelas de 44 px no celular e status das estrelas, vitrine; textos do Resultado, da Descoberta e do Perfil.
- [x] 8.12 Comparar cada rota entregue com o HTML do protótipo e registrar no handoff os elementos seguidos e os desvios justificados; a comparação geométrica de `/favorites` contra `favorites.html` (1440, 1280, 1024) passa a medir a tabela sem a coluna "Alertar", e o compare do #1120 volta à tolerância de 3 px também na largura da mesa.
- [x] 8.13 Ensaio no DEV com dry-run do scan (`force_dry_run`), depois da migração: um usuário com NVDA (fora da carteira) e BTC/USDT com estrela e alerta ligado, ETH/USDT desligado e QQQ sem estrela; conferir no resumo os eventos só dos ligados com estrela, nenhuma chamada à carteira, o aviso de atraso e nenhuma mensagem de mercado fechado; conferir que a marca da transição não foi gravada. <!-- covenant-flow:after-qa -->
