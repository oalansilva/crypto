## Why

Sexta história do épico #1116. O catálogo (#1117), o histórico Binance (#1118), o backtest (#1119), o lote (#1120) e a Descoberta (#1121) já estão em `develop`. Ação e ETF já viram favorito, mas ficam fora do Monitor, do Telegram e da atualização com calendário. O alerta ainda sai do catálogo curado do admin. O estado observado é um só por ativo e tempo gráfico, e a proteção contra repetição é por janela de tempo. Por isso hoje nenhuma ação ou ETF recebe alerta. Pela regra atual, a saída de uma ação marcada na carteira também seria silenciada.

## Problema

Alan pode perder sinais, receber alertas repetidos ou ver falsos erros de atraso em dias sem pregão.

## História

Como usuário, quero favoritar e acompanhar estratégias de ações/ETFs, recebendo alertas confiáveis para decidir quando agir.

## Entra

- [ ] Favoritos conservam fonte, sessão, ajuste e identidade de execução; configurações de dados distintas não colidem como duplicatas.
- [ ] Atualização e período operacional respeitam calendário, sessões, candle fechado e dados insuficientes; fim de semana/feriado não produz falso stale.
- [ ] Canais de alerta existentes atendem ações/ETFs e distinguem sinal, dados atrasados e mercado fechado; restart/reprocessamento não duplica evento.
- [ ] Quem recebe: em cripto, ações e ETFs, cada usuário recebe alertas dos próprios favoritos marcados para alertar; o catálogo curado do admin deixa de ser a origem dos alertas, inclusive na cripto (muda quem recebe os alertas de cripto hoje). Dado que o usuário A marcou para alertar um favorito de NVDA ou de BTC/USDT e o usuário B não tem esse favorito, quando o sinal muda só A recebe.
- [ ] Transição da cripto (ponto não fechado no refinamento): quem hoje recebe alertas de cripto só pelo catálogo curado, sem favorito próprio marcado, deixa de recebê-los com a mudança. Se haverá aviso ou período de transição para esses usuários é decidido no Design com Alan.
- [ ] Entrada e saída: para ação/ETF marcada na carteira, o alerta sai tanto na entrada quanto na saída; nenhuma das duas é silenciada por falta de posição na Binance. Quando a posição real de ação/ETF existir (#1124), o alerta passa a seguir essa posição, como na cripto.
- [ ] Um alerta por favorito: dois favoritos no mesmo ativo e tempo gráfico (estratégias ou configurações diferentes) têm estados separados; cada mudança gera o próprio alerta, que identifica a estratégia e a configuração (fonte, sessão, ajuste).
- [ ] Atraso e mercado fechado: o Telegram recebe o sinal e, quando há atraso real de dados durante o pregão, um único aviso por ativo, sem repetir até o dado normalizar. Mercado fechado (fora do pregão, fim de semana, feriado) aparece só na tela, sem mensagem no Telegram.
- [ ] Favoritar/receber alerta não envia ordem; quando informações operacionais existirem, distinguir sinal de ordem enviada e execução confirmada.
- [ ] Validar ação, ETF e cripto, incluindo configurações distintas do mesmo ativo, atraso real, mercado fechado e recuperação.

## Não entra

- Novos canais de notificação ou robô de negociação automática.
- Compra/venda manual e proteção nativa, tratadas nas histórias de operação.
- Migrar para a Binance os favoritos de ações/ETFs gravados com fontes antigas; isso é do #1126, que depende deste card.
- Mensagem no Telegram para mercado fechado, abertura ou feriado; esses estados ficam só na tela.

> Seções acima copiadas do body do issue [#1122](https://github.com/oalansilva/crypto/issues/1122) (grelhado, fronteira vazia; 5 decisões de Alan de 26/10/2026 dentro de Entra). Não houve reentrevista. A "Transição da cripto" ficou para o Design; Alan a decidiu em 26/10/2026, com outras quatro decisões, registradas em `design.md`.

> **Regra nova de alertas (27/10/2026).** Depois do "Não homologar", Alan mudou quem recebe: alerta = o que a pessoa acompanha no Monitor (estratégia própria com estrela, ligado por padrão e desligado no Monitor); a carteira não decide; o catálogo não alerta; lote e Descoberta salvam sem estrela. O bullet "Entrada e saída" de Entra, acima, fica mais amplo: entrada e saída saem com ou sem o ativo na carteira, em todas as classes. Detalhe em `design.md`.

## What Changes

- **Origem dos alertas = o que cada pessoa acompanha no Monitor.** O Telegram passa a avaliar, para cada usuário com alertas ligados, as estratégias próprias com pelo menos 1 estrela (as que aparecem no Monitor) e com o alerta ligado, em cripto, ação e ETF. O catálogo curado do admin deixa de ser a origem e não alerta ninguém. **BREAKING** para quem hoje recebe alerta de cripto só pelo catálogo (aviso único no Telegram e faixa na vitrine do Monitor, sem período de transição).
- **Alerta ligado por padrão, desligado no Monitor (regra de 27/10/2026).** O alerta de cada estratégia nasce ligado e o dono o desliga no próprio Monitor, por estratégia (linha, cartão e detalhe). O "Alertar" sai de Favoritos. Dar a estrela põe a estratégia no Monitor com o alerta ligado; tirar todas as estrelas tira do Monitor e para o alerta. A migração trata os dados que já existem como Alan decidiu: tira a estrela automática de lote e Descoberta e liga o alerta de tudo o que fica no Monitor (decisões d2-1 e d2-2 do design). O Monitor do admin continua abrindo em "Em portfólio", sem aviso de estratégias fora da carteira (d2-3).
- **Um estado e um alerta por favorito.** O estado observado passa a ser por favorito, e não mais por ativo e tempo gráfico. Dois favoritos no mesmo ativo e tempo (outra estratégia ou outra configuração) mudam e alertam separados. A mensagem identifica a estratégia e a configuração (fonte, sessão, ajuste) e diz que nenhuma ordem foi enviada.
- **Evento com identidade.** Cada alerta tem a chave favorito + leitura nova + candle fechado. Reinício, reprocessamento ou nova varredura com o mesmo dado não reenviam. A janela de repetição por tempo sai.
- **A carteira não decide quem recebe.** Entrada e saída saem com ou sem o ativo na carteira, em cripto, ação e ETF; a cripto perde a supressão da reentrada com saldo e a da saída sem saldo. A varredura não lê mais a carteira Binance, e o aviso de falha dela sai. O Monitor continua mostrando a carteira como informação.
- **Calendário e candle fechado.** Ação e ETF são avaliados no último candle fechado pelo calendário de Nova York (#1118). Fim de semana, feriado e horário fora do pregão não geram atraso falso.
- **Atraso real e mercado fechado.** Quando falta um candle que o calendário diz que já fechou, o Telegram recebe um único aviso por ativo, que não se repete até o dado normalizar. Mercado fechado, feriado e abertura aparecem só na tela do Monitor.
- **Identidade do favorito.** Fonte, sessão e ajuste entram na identidade e na chave de duplicata. NVDA na Binance e NVDA na fonte antiga coexistem, e a mesma configuração repetida é recusada como duplicata.
- **Ação e ETF no Monitor e na atualização diária.** O Monitor lista os favoritos de ação e ETF com classe, moeda, configuração e estado do mercado. A atualização diária usa o calendário e o intradiário da Binance Ações. Quando faltam candles, o favorito fica em "Aguardando dados". Estrelas e "Revalidar" de ação e ETF passam a funcionar em Favoritos.
- **Favoritar ação e ETF por todo caminho que já favorita cripto.** Sai a recusa do #1119 na página do resultado. O lote e a Descoberta gravam o favorito sem estrela, em qualquer classe: ele fica em Favoritos, fora do Monitor e sem alerta, até a pessoa dar a estrela. Saem os textos "ainda não para ações e ETFs" e "ainda não podem ser favoritados".
- **Alerta ≠ ordem.** Favoritar ou receber alerta nunca envia ordem. O `signal_monitor` continua só no feed de sinais cripto e nunca recebe ação/ETF.

## Capabilities

### New Capabilities

- `favorite-telegram-alerts`:
  - origem por usuário e por estratégia com estrela e alerta ligado, com estado e evento por favorito;
  - entrada e saída com ou sem o ativo na carteira, nas três classes;
  - mensagem com a configuração e sem ordem;
  - aviso único de atraso, e mercado fechado só na tela;
  - carteira Binance fora da varredura;
  - transição da cripto.
- `market-session-awareness`: candle fechado e estado do mercado pelo calendário da classe (aberto, fechado, feriado, atraso real), sem atraso falso. O Monitor, o Telegram e a atualização diária usam a mesma regra.
- `favorite-configuration-identity`:
  - fonte, sessão e ajuste na identidade e na unicidade do favorito, com os rótulos de configuração;
  - fonte antiga coexistindo com a Binance;
  - favoritar ação e ETF pelo resultado;
  - lote e Descoberta gravando sem estrela, e o alerta ligado ao nascer.
- `monitor-multiclass`: Monitor com os favoritos de ação e ETF, a linha de classe e configuração, o estado do mercado, o controle de alerta por estratégia, a carteira só como informação, a faixa da vitrine e o gráfico pela série do favorito.

### Modified Capabilities

- `crypto-only-mvp`: o Monitor passa a incluir ação e ETF (sobre o texto do #1121).
- `monitor-telegram-general-alerts`: saem os requisitos do catálogo curado como origem.
- `monitor-telegram-favorite-toggle`: o alerta é do dono, ligado por padrão e desligado no Monitor; só estratégia com estrela alerta.
- `monitor-telegram-alerts`: anti-repetição por evento; saem a matriz da carteira, o escopo "Em portfólio" e o aviso de falha da carteira.
- `monitor-curated-fallback`: favorito próprio com estrela, de qualquer classe, tira o usuário da vitrine do Monitor; a vitrine não alerta.
- `favorite-backtest-refresh`: frescor pelo calendário, intradiário da Binance Ações, "Aguardando dados" e período operacional que termina no último pregão.
- `favorites`: sai a recusa de favoritar ação/ETF do #1119.
- `discovery-promotion`: a promoção cria o favorito sem estrela, em qualquer classe.
- `multiclass-batch`: o lote grava o favorito sem estrela, em qualquer classe.
- `favorites-class-comparison`: estrelas e "Revalidar" de ação/ETF passam a funcionar; a estrela é a porta do Monitor; Favoritos sem controle de alerta.

## Impact

- Backend:
  - `services/monitor_telegram_alerts.py`:
    - origem por usuário, com estado e evento por favorito;
    - entrada e saída sem a matriz da carteira, nas três classes, e sem ler a carteira Binance;
    - aviso de atraso e mensagem nova, com a linha de como parar de receber;
    - sem o aviso operacional de falha da carteira Binance.
  - `services/opportunity_service.py`:
    - ação/ETF no Monitor e no scan;
    - candle fechado e estado do mercado pelo calendário;
    - configuração e estado na oportunidade;
    - vitrine só para quem não tem favorito próprio.
  - `services/monitor_portfolio_status.py`: carteira manual de ação/ETF só para a tela (sai da decisão de alerta).
  - `services/favorite_uniqueness.py`, `routes/favorites.py`:
    - chave com fonte, sessão e ajuste, e `exists` com a configuração;
    - alerta do dono (dar a estrela liga) e fim da recusa de ação/ETF;
    - lista sem vitrine para quem tem favorito próprio de qualquer classe.
  - `services/favorite_backtest_refresh_service.py`, `services/favorite_operational_period.py`:
    - frescor e fim do período pelo calendário;
    - intradiário da Binance Ações e "Aguardando dados";
    - fonte do favorito na busca do primeiro candle.
  - `services/market_history/nyse_calendar.py`: helpers de último candle fechado, próxima abertura e estado do mercado.
  - `services/batch_backtest_service.py`, `services/discovery_service.py`: favorito sem estrela e com o alerta ligado; a Descoberta recusa pedido com tier.
  - `services/signal_monitor.py`: guarda explícita para nunca consultar ação/ETF.
  - `ops/run_monitor_telegram_alert_scan.py`: resumo com eventos e avisos de atraso.
- Frontend:
  - `components/monitor/MonitorStatusTab.tsx`, `OpportunityCard.tsx`, `types.ts`, `ChartModal.tsx`, `chartData.ts`: ação e ETF, configuração, estado do mercado, controle de alerta por estratégia, carteira, gráfico pela série do favorito e faixa da transição.
  - `pages/FavoritesDashboard.tsx`, `lib/favoriteClass.ts`: estrelas e Revalidar de ação/ETF, legenda "No Monitor"/"Fora do Monitor", status de atualização pelo calendário, configuração da fonte antiga e faixa da vitrine; sem controle de alerta.
  - `pages/ComboResultsPage.tsx`, `components/SaveFavoriteModal.tsx`, `lib/equityExecution.ts`: "Salvar nos Favoritos" de ação/ETF, com a configuração e a duplicata.
  - `lib/assetSelection.ts` (Combo), `lib/discoveryMulticlass.ts`, `pages/DiscoveryPage.tsx`: saem os textos de recusa, e o destino passa a ser Favoritos sem estrela.
  - `components/telegram/TelegramAlertsForm.tsx`: texto do Perfil sobre a origem dos alertas.
- APIs:
  - `GET /api/opportunities/` inclui ação e ETF e ganha `asset_class`, `currency`, `configuration`, `market_state` e `notify_telegram` por linha.
  - `PATCH /api/favorites/{id}` aceita `notify_telegram` do dono.
  - `GET /api/favorites/exists` aceita `data_source`, `session` e `adjustment`.
  - `POST /api/favorites/` aceita ação e ETF.
  - `POST /api/admin/monitor-telegram-alerts/run` devolve eventos por favorito e avisos de atraso.
- Dados (Alembic):
  - `favorite_strategies` ganha `data_source`, `session` e `adjustment`, com backfill;
  - tabela nova de estado por favorito, semeada do estado por par;
  - tabela nova de saúde do dado por ativo;
  - `monitor_telegram_alerts` ganha `favorite_id` e `event_key`, com índice único parcial;
  - `20261027_0001`: o default de `notify_telegram` volta a ser verdadeiro (alerta ligado por padrão); a estrela automática de lote e Descoberta que ainda está em 1 sai (d2-1); o alerta de todos os favoritos fica ligado (d2-2); semente do estado dos favoritos que passam a alertar. (A migração anterior, `20261026_0001`, já aplicada no DEV, deixou o default falso e zerou as marcas de quem não é admin.)
- Operação: o timer diário (08:05 BRT) continua o mesmo. Alan decidiu manter só a passada das 08:05. Alertas de sinal e avisos de atraso da varredura não passam pelo limite de mensagens por hora; com o fim do aviso de falha da carteira Binance, o limite fica sem uso na varredura (remoção depois do archive).
- Dependências: #1117 a #1121 em `develop`. O #1124 (posição real de ação/ETF) e o #1126 (migração da fonte antiga) dependem deste card.
