# monitor-multiclass Specification

## Purpose
TBD - created by archiving change card-1122-favoritos-alertas-acoes-etfs. Update Purpose after archive.
## Requirements
### Requirement: Monitor lista favoritos de ação e ETF
`GET /api/opportunities/` SHALL incluir os favoritos de ação e ETF do usuário (Binance Ações e fonte antiga), além da cripto. Cada linha MUST trazer:
- `asset_class` (`crypto`, `stock`, `etf`) e `currency`;
- `configuration` (fonte, sessão, ajuste, rótulo curto e longo);
- `market_state` (`market-session-awareness`);
- `notify_telegram` do favorito (alerta ligado).

A tela MUST mostrar essas linhas nas seções de hoje (Em posição, Saída / cobertura), com o filtro de estrelas e o de tempo gráfico valendo para todas as classes. O Monitor MUST NOT ler série de outro mercado para a ação ou o ETF.

#### Scenario: Monitor com cripto, ação e ETF
- **WHEN** Alan tem favoritos com estrela de BTC/USDT 1d, ETH/USDT 4h, NVDA 1d (Binance Ações), NVDA 1d (fonte antiga) e SPY 1d
- **THEN** o Monitor MUST mostrar as cinco linhas
- **AND** o filtro de tempo gráfico MUST oferecer 1d e 4h

### Requirement: Linha mostra classe, configuração e estado do mercado
A linha de ação e de ETF SHALL ser compacta, perto da altura da linha de cripto (decisão 5 de Alan, 26/10/2026). Abaixo da estratégia, ela MUST mostrar a identidade abreviada: classe, moeda e configuração ("Ação · USD · Binance · NY · split"; fonte antiga "Ação · USD · Stooq · antiga · diário"), com o rótulo longo no `title` e no detalhe. Dois favoritos do mesmo ativo e tempo MUST ser distinguíveis só por essa linha. O estado do mercado MUST ficar sob a pílula de Status, dentro da coluna, sem alargá-la, em quatro tons:
- **Pregão aberto:** "Aberto · fecha 17:00 (16:00 NY)", discreto, com ponto.
- **Mercado fechado:** "Fechado · abre hoje 10:30 (09:30 NY)", com o motivo quando é fim de semana ou feriado ("Fechado · feriado em NY · abre sex. 11:30 (09:30 NY)"), em cinza, com relógio.
- **Dados atrasados:** "Dados atrasados · falta seg. 26/10", em âmbar, com triângulo de aviso, e "Sinal em espera".
- **Dados insuficientes:** pílula "Sem leitura" e "Dados insuficientes · 40 de 200 candles", em cinza com borda tracejada, com ampulheta, e "Sem sinal".

No cartão do celular, o mesmo estado aparece com o texto completo ("Pregão aberto · fecha 17:00 (16:00 em NY)", "Mercado fechado · fim de semana · abre seg., 26 out., 10:30 (09:30 em NY)", "Dados atrasados · último candle sex., 23 out.; esperado seg., 26 out." e "Sinal em espera até o dado normalizar", "Sem sinal até completar o histórico"). Cada estado MUST ter ícone + texto, nunca só cor. A tag "Alerta" MUST NOT aparecer nas Tags nem na faixa de identidade do detalhe: o estado do alerta fica no controle da estratégia ("Controle de alerta por estratégia no Monitor"). Quando a linha está em espera por causa de outro tempo gráfico do mesmo ativo (`stale_timeframe`/`stale_detail`), o estado MUST dizer o tempo gráfico e os horários da série atrasada ("Dados atrasados no 15m · falta 14:30"; no cartão e no `title` da linha, "Dados atrasados no 15m · último 14:15; esperado 14:30"), e MUST NOT dizer que falta um candle do próprio tempo gráfico que já chegou. O indicador "Em carteira" MUST contar ativos distintos (dois favoritos de NVDA contam um ativo).

#### Scenario: Sábado no Monitor
- **WHEN** Alan abre o Monitor no sábado
- **THEN** NVDA e SPY MUST mostrar "Mercado fechado · abre seg., 26 out., 10:30 (09:30 em NY)"
- **AND** BTC/USDT MUST NOT mostrar estado de mercado

#### Scenario: NVDA atrasada
- **WHEN** NVDA da Binance Ações está `stale`
- **THEN** a linha MUST mostrar "Dados atrasados" com o candle que falta sob a pílula de Status, e "Sinal em espera"; o cartão, o último candle e o esperado
- **AND** a linha de NVDA da fonte antiga MUST mostrar o seu próprio estado

#### Scenario: Cripto atrasada
- **WHEN** BTC/USDT está `stale` pelo servidor
- **THEN** a linha e o cartão MUST mostrar "Dados atrasados" e "Sinal em espera"
- **AND** o "alerta" do cartão MUST trazer o último candle e o esperado no lugar de "Sem candle válido/atual para esta resolução."
- **AND** os dois textos MUST NOT aparecer juntos

#### Scenario: 1d em espera por causa do 15m
- **WHEN** a linha de NVDA 1d está em espera porque o 15m de NVDA está atrasado, e o candle 1d de ontem chegou
- **THEN** a linha MUST mostrar "Dados atrasados no 15m" com o horário que falta do 15m ("Dados atrasados no 15m · falta 14:30") e "Sinal em espera"
- **AND** o cartão MUST mostrar o último e o esperado do 15m
- **AND** MUST NOT mostrar "falta" do candle 1d de ontem

#### Scenario: Ticker com série curta
- **WHEN** um favorito de QQQ 1d tem 40 candles fechados e a estratégia precisa de 200
- **THEN** a linha MUST ficar em "Saída / cobertura" com a pílula "Sem leitura" e "Dados insuficientes · 40 de 200 candles"
- **AND** nenhum sinal, alerta ou aviso de atraso MUST sair dela

#### Scenario: Linha compacta
- **WHEN** o Monitor mostra NVDA 1d com pregão aberto a 1440 px
- **THEN** a linha MUST ter altura próxima da linha de BTC/USDT (no protótipo, 178 px contra 158 px)

### Requirement: Carteira é só informação da tela
Para ação e ETF, a tag "Carteira" e o controle do cartão SHALL usar a marcação manual de hoje (`MonitorPreference`); a cripto MUST manter a carteira derivada da Binance de hoje. A carteira MUST NOT mudar o alerta (`favorite-telegram-alerts`): a frase "Ação/ETF na carteira recebe entrada e saída no Telegram." MUST sair, e o detalhe MUST trazer, junto do controle de alerta, "Entrada e saída saem com ou sem o ativo na carteira. Desligado, nada sai no Telegram para esta estratégia." O cartão do celular MUST NOT repetir essa frase; ela aparece uma vez por página na ajuda "Como usar o Monitor" ("Controle de alerta por estratégia no Monitor"). O Monitor do admin MUST continuar abrindo com o filtro "Em portfólio", como hoje (quem não é admin, "Todos"), e MUST NOT mostrar aviso, contador ou link sobre estratégias fora da carteira com alerta ligado (decisão d2-3 de Alan, 27/10/2026): o admin troca para "Todos" quando precisar.

#### Scenario: Marcar NVDA na carteira
- **WHEN** Alan marca NVDA na carteira no cartão
- **THEN** a tag MUST virar "● Carteira" e a preferência MUST ser gravada para NVDA
- **AND** os alertas de NVDA MUST continuar os mesmos

#### Scenario: Admin abre o Monitor
- **WHEN** Alan abre o Monitor
- **THEN** o filtro MUST estar em "Em portfólio", com só as estratégias na carteira
- **AND** nenhum aviso de estratégias fora da carteira com alerta ligado MUST aparecer

#### Scenario: Admin troca para Todos
- **WHEN** Alan, com o Monitor em "Em portfólio", escolhe "Todos"
- **THEN** NVDA, fora da carteira, MUST aparecer com o controle de alerta

### Requirement: Gráfico e trades pela série do favorito
"Abrir Gráfico" e "Ver Trades" de ação e ETF da Binance SHALL ler a série do favorito no tempo gráfico dele pelo histórico da Binance Ações (`/api/market/history`), sem forçar 1d. Na fonte antiga, os dois botões MUST ficar visíveis e indisponíveis (`aria-disabled`, `title` e `aria-label` com "(indisponível)") na linha, no cartão e no detalhe, e o motivo MUST aparecer em texto visível abaixo deles: "Fonte antiga: gráfico e trades depois da migração para a Binance.". O detalhe de um favorito MUST mostrar o estado e os valores dele mesmo (na fonte antiga em saída: "Saída confirmada" e "Risco residual").

#### Scenario: NVDA da fonte antiga no celular
- **WHEN** Alan toca em "Ver Trades" no cartão de NVDA da fonte antiga
- **THEN** nada abre, e o cartão mostra o motivo em texto

#### Scenario: NVDA 1h
- **WHEN** Alan abre o gráfico de um favorito NVDA 1h
- **THEN** o gráfico MUST mostrar candles de 1h do pregão regular

### Requirement: Controle de alerta por estratégia no Monitor
Toda linha de estratégia própria com pelo menos 1 estrela SHALL ter um controle de alerta do Telegram, ligado por padrão (decisão 1 de Alan, 27/10/2026):
- **linha, a partir de 1280 px:** primeiro botão da célula de ações, antes de "Abrir Gráfico", com `role="switch"`, `aria-checked`, sino (ligado) ou sino cortado com borda tracejada (desligado), o texto visível "Alerta" e o estado "ligado"/"desligado" ao lado; o nome acessível MUST conter "Alerta" e identificar o ativo, o tempo gráfico, a estratégia e, em ação/ETF, a configuração curta ("Alerta no Telegram · NVDA 1d · Médias Móveis: Tendência em Virada · Binance Ações"). A célula MUST quebrar em linha sem alargar a tabela nem criar rolagem horizontal;
- **linha, de 1024 a 1279 px:** o mesmo interruptor na célula Status, abaixo da pílula e do estado do mercado, porque nessa faixa a célula de ações fica fora da área visível; só um interruptor por linha MUST aparecer em cada largura;
- **cartão (390 px):** o mesmo interruptor na faixa de controle, com "Alerta: ligado"/"Alerta: desligado" e alvo de 44 px, sem a ajuda da carteira;
- **detalhe:** o mesmo interruptor na faixa de controle, com o estado atual da estratégia, e a ajuda da carteira ("Carteira é só informação da tela");
- **ajuda "Como usar o Monitor"**, uma vez por página e fora da vitrine: "Toda estratégia aqui manda alerta no Telegram, com ou sem o ativo na carteira; para parar de receber, desligue o "Alerta" da linha."

Clicar MUST gravar `notify_telegram` do favorito (`PATCH /api/favorites/{id}`), sem abrir nem fechar a linha; a linha, o cartão e o detalhe aberto da mesma estratégia MUST mostrar o mesmo estado. Em erro, o controle MUST voltar ao estado anterior e o status da página MUST dizer "Não foi possível mudar o alerta. Tente de novo.". Favorito sem estrela não aparece no Monitor, então não há estado de linha sem estrela; linha do catálogo MUST mostrar "Catálogo · sem alerta", sem controle.

#### Scenario: Desligar o alerta de ETH/USDT
- **WHEN** Alan ativa o controle "Alerta" ligado da linha de ETH/USDT 4h
- **THEN** o controle MUST ficar com `aria-checked="false"`, o sino cortado e "desligado"
- **AND** `notify_telegram=false` MUST ser gravado para esse favorito
- **AND** a linha MUST continuar fechada

#### Scenario: Detalhe aberto acompanha o controle
- **WHEN** Alan desliga o alerta de NVDA na linha e abre o detalhe de NVDA
- **THEN** o controle do detalhe MUST estar desligado
- **AND** religar no detalhe MUST religar o controle da linha

#### Scenario: Duas estratégias do mesmo ativo
- **WHEN** NVDA tem duas linhas (Binance Ações e fonte antiga)
- **THEN** cada uma MUST ter o próprio controle, com nomes acessíveis diferentes (a configuração distingue as duas)

#### Scenario: Celular
- **WHEN** Alan abre o Monitor a 390 px
- **THEN** cada cartão de estratégia própria com estrela MUST ter "Alerta: ligado" ou "Alerta: desligado" com alvo de pelo menos 44 px

#### Scenario: Linha do catálogo
- **WHEN** quem não tem estratégia própria com estrela vê a vitrine
- **THEN** as linhas MUST mostrar "Catálogo · sem alerta" e nenhum controle

### Requirement: Faixa da vitrine no Monitor
Quando o Monitor mostra o catálogo (vitrine) a quem não é admin e não tem favorito próprio com estrela, ele SHALL mostrar acima dos indicadores uma faixa `role=status`, com ícone de informação (não o sino): "Estas estratégias são o catálogo do Cripto Farol: só exibição, sem alerta no Telegram. Os alertas vêm das estratégias que você acompanha no Monitor. Dê pelo menos 1 estrela a uma estratégia sua em Favoritos (ou salve lá um resultado do Combo): ela entra aqui com o alerta ligado." Ela MUST ter o link "Ir para Favoritos" (alvo de 44 px). Só para quem recebia alerta do catálogo (`favorite-telegram-alerts`), a faixa MUST acrescentar "Até <data da troca> você recebia os alertas do catálogo; agora cada pessoa recebe os das próprias estratégias." O texto "Você ainda não marcou nenhum" MUST sair. Quem tem estratégia própria com estrela não vê a faixa, mesmo com todos os alertas desligados.

#### Scenario: Usuário só do catálogo
- **WHEN** um usuário que recebia alertas do catálogo, sem favorito próprio com estrela, abre o Monitor
- **THEN** a faixa MUST aparecer com a frase com data e o link para Favoritos

#### Scenario: Usuário que nunca recebeu
- **WHEN** um usuário sem favorito próprio com estrela, que nunca recebeu alerta do catálogo, abre o Monitor
- **THEN** a faixa MUST aparecer sem a frase com data

#### Scenario: Todos os alertas desligados
- **WHEN** um usuário com estratégias próprias com estrela desligou todos os alertas
- **THEN** a faixa MUST NOT aparecer

