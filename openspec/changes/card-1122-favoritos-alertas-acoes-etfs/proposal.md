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

## What Changes

- **Origem dos alertas = favoritos de cada usuário.** O Telegram passa a avaliar os favoritos que cada usuário com alertas ligados marcou "Alertar", em cripto, ação e ETF. O catálogo curado do admin deixa de ser a origem. O Monitor continua mostrando o catálogo como vitrine para quem não tem favorito próprio. **BREAKING** para quem hoje recebe alerta de cripto só pelo catálogo (transição pela decisão 1 de Alan em `design.md`: aviso único no Telegram e faixa no Monitor, sem período de transição).
- **"Alertar" é de cada dono.** Todo usuário marca e desmarca "Alertar" nos próprios favoritos, em Favoritos; a marca deixa de ser exclusiva do admin. Favorito novo nasce sem a marca (decisão de Alan). A migração mantém só as marcas que o admin já tinha nos próprios favoritos.
- **Um estado e um alerta por favorito.** O estado observado passa a ser por favorito, e não mais por ativo e tempo gráfico. Dois favoritos no mesmo ativo e tempo (outra estratégia ou outra configuração) mudam e alertam separados. A mensagem identifica a estratégia e a configuração (fonte, sessão, ajuste) e diz que nenhuma ordem foi enviada.
- **Evento com identidade.** Cada alerta tem a chave favorito + leitura nova + candle fechado. Reinício, reprocessamento ou nova varredura com o mesmo dado não reenviam. A janela de repetição por tempo sai.
- **Entrada e saída para ação/ETF na carteira.** Ação ou ETF marcado na carteira recebe a entrada e a saída. Nenhuma das duas depende de posição na Binance. Quando a posição real existir (#1124), o alerta segue a posição, como na cripto. Falha da carteira Binance pausa só os alertas de cripto.
- **Calendário e candle fechado.** Ação e ETF são avaliados no último candle fechado pelo calendário de Nova York (#1118). Fim de semana, feriado e horário fora do pregão não geram atraso falso.
- **Atraso real e mercado fechado.** Quando falta um candle que o calendário diz que já fechou, o Telegram recebe um único aviso por ativo, que não se repete até o dado normalizar. Mercado fechado, feriado e abertura aparecem só na tela do Monitor.
- **Identidade do favorito.** Fonte, sessão e ajuste entram na identidade e na chave de duplicata. NVDA na Binance e NVDA na fonte antiga coexistem, e a mesma configuração repetida é recusada como duplicata.
- **Ação e ETF no Monitor e na atualização diária.** O Monitor lista os favoritos de ação e ETF com classe, moeda, configuração e estado do mercado. A atualização diária usa o calendário e o intradiário da Binance Ações. Quando faltam candles, o favorito fica em "Aguardando dados". Estrelas, "Alertar" e "Revalidar" de ação e ETF passam a funcionar em Favoritos.
- **Favoritar ação e ETF por todo caminho que já favorita cripto.** Sai a recusa do #1119 na página do resultado. O lote e a Descoberta gravam ação e ETF com 1 estrela, como a cripto. Saem os textos "ainda não para ações e ETFs" e "ainda não podem ser favoritados".
- **Alerta ≠ ordem.** Favoritar ou receber alerta nunca envia ordem. O `signal_monitor` continua só no feed de sinais cripto e nunca recebe ação/ETF.

## Capabilities

### New Capabilities

- `favorite-telegram-alerts`:
  - origem por usuário e por favorito marcado, com estado e evento por favorito;
  - entrada e saída de ação/ETF na carteira;
  - mensagem com a configuração e sem ordem;
  - aviso único de atraso, e mercado fechado só na tela;
  - falha da carteira pausando só a cripto;
  - transição da cripto.
- `market-session-awareness`: candle fechado e estado do mercado pelo calendário da classe (aberto, fechado, feriado, atraso real), sem atraso falso. O Monitor, o Telegram e a atualização diária usam a mesma regra.
- `favorite-configuration-identity`:
  - fonte, sessão e ajuste na identidade e na unicidade do favorito, com os rótulos de configuração;
  - fonte antiga coexistindo com a Binance;
  - favoritar ação e ETF pelo resultado;
  - lote e Descoberta gravando com 1 estrela, e "Alertar" desligado ao nascer.
- `monitor-multiclass`: Monitor com os favoritos de ação e ETF, a linha de classe e configuração, o estado do mercado, a carteira manual com entrada e saída e o gráfico pela série do favorito.

### Modified Capabilities

- `crypto-only-mvp`: o Monitor passa a incluir ação e ETF (sobre o texto do #1121).
- `monitor-telegram-general-alerts`: saem os requisitos do catálogo curado como origem.
- `monitor-telegram-favorite-toggle`: a marca passa a ser do dono do favorito, não só do admin.
- `monitor-telegram-alerts`: anti-repetição por evento; matriz por favorito, com ação/ETF na carteira; escopo pelos favoritos do usuário; falha da carteira só para cripto.
- `monitor-curated-fallback`: favorito próprio de qualquer classe tira o usuário da vitrine do catálogo.
- `favorite-backtest-refresh`: frescor pelo calendário, intradiário da Binance Ações, "Aguardando dados" e período operacional que termina no último pregão.
- `favorites`: sai a recusa de favoritar ação/ETF do #1119.
- `discovery-promotion`: ação e ETF passam a ser promovidos com 1 estrela, como a cripto.
- `multiclass-batch`: o lote passa a gravar ação e ETF com 1 estrela, como a cripto.
- `favorites-class-comparison`: estrelas, "Alertar" e "Revalidar" de ação/ETF passam a funcionar.

## Impact

- Backend:
  - `services/monitor_telegram_alerts.py`:
    - origem por usuário, com estado e evento por favorito;
    - matriz com ação/ETF;
    - aviso de atraso e mensagem nova;
    - falha da carteira só para cripto.
  - `services/opportunity_service.py`:
    - ação/ETF no Monitor e no scan;
    - candle fechado e estado do mercado pelo calendário;
    - configuração e estado na oportunidade;
    - vitrine só para quem não tem favorito próprio.
  - `services/monitor_portfolio_status.py`: carteira manual de ação/ETF com entrada e saída.
  - `services/favorite_uniqueness.py`, `routes/favorites.py`:
    - chave com fonte, sessão e ajuste, e `exists` com a configuração;
    - "Alertar" do dono e fim da recusa de ação/ETF;
    - lista sem vitrine para quem tem favorito próprio de qualquer classe.
  - `services/favorite_backtest_refresh_service.py`, `services/favorite_operational_period.py`:
    - frescor e fim do período pelo calendário;
    - intradiário da Binance Ações e "Aguardando dados";
    - fonte do favorito na busca do primeiro candle.
  - `services/market_history/nyse_calendar.py`: helpers de último candle fechado, próxima abertura e estado do mercado.
  - `services/batch_backtest_service.py`, `services/discovery_service.py`: 1 estrela para ação/ETF e "Alertar" desligado.
  - `services/signal_monitor.py`: guarda explícita para nunca consultar ação/ETF.
  - `ops/run_monitor_telegram_alert_scan.py`: resumo com eventos e avisos de atraso.
- Frontend:
  - `components/monitor/MonitorStatusTab.tsx`, `OpportunityCard.tsx`, `types.ts`, `ChartModal.tsx`, `chartData.ts`: ação e ETF, configuração, estado do mercado, "Alerta", carteira, gráfico pela série do favorito e faixa da transição.
  - `pages/FavoritesDashboard.tsx`, `lib/favoriteClass.ts`: coluna "Alertar" para todo dono, estrelas e Revalidar de ação/ETF, status de atualização pelo calendário, configuração da fonte antiga e faixa da transição.
  - `pages/ComboResultsPage.tsx`, `components/SaveFavoriteModal.tsx`, `lib/equityExecution.ts`: "Salvar nos Favoritos" de ação/ETF, com a configuração e a duplicata.
  - `lib/assetSelection.ts` (Combo), `lib/discoveryMulticlass.ts`, `pages/DiscoveryPage.tsx`: saem os textos de recusa, e o destino passa a ser 1 estrela.
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
  - o default de `notify_telegram` passa a ser falso, e as marcas de quem não é admin são zeradas.
- Operação: o timer diário (08:05 BRT) continua o mesmo. Alan decidiu manter só a passada das 08:05. Alertas de sinal e avisos de atraso da varredura não passam pelo limite de mensagens por hora; o limite fica só no aviso de falha da carteira Binance.
- Dependências: #1117 a #1121 em `develop`. O #1124 (posição real de ação/ETF) e o #1126 (migração da fonte antiga) dependem deste card.
