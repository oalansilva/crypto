## ADDED Requirements

### Requirement: Monitor lista favoritos de ação e ETF
`GET /api/opportunities/` SHALL incluir os favoritos de ação e ETF do usuário (Binance Ações e fonte antiga), além da cripto. Cada linha MUST trazer:
- `asset_class` (`crypto`, `stock`, `etf`) e `currency`;
- `configuration` (fonte, sessão, ajuste, rótulo curto e longo);
- `market_state` (`market-session-awareness`);
- `notify_telegram` do favorito.

A tela MUST mostrar essas linhas nas seções de hoje (Em posição, Saída / cobertura), com o filtro de estrelas e o de tempo gráfico valendo para todas as classes. O Monitor MUST NOT ler série de outro mercado para a ação ou o ETF.

#### Scenario: Monitor com cripto, ação e ETF
- **WHEN** Alan tem favoritos com estrela de BTC/USDT 1d, ETH/USDT 4h, NVDA 1d (Binance Ações), NVDA 1d (fonte antiga) e SPY 1d
- **THEN** o Monitor MUST mostrar as cinco linhas
- **AND** o filtro de tempo gráfico MUST oferecer 1d e 4h

### Requirement: Linha mostra classe, configuração, estado do mercado e "Alerta"
A linha de ação e de ETF SHALL ser compacta, perto da altura da linha de cripto (decisão 5 de Alan, 26/10/2026). Abaixo da estratégia, ela MUST mostrar a identidade abreviada: classe, moeda e configuração ("Ação · USD · Binance · NY · split"; fonte antiga "Ação · USD · Stooq · antiga · diário"), com o rótulo longo no `title` e no detalhe. Dois favoritos do mesmo ativo e tempo MUST ser distinguíveis só por essa linha. O estado do mercado MUST ficar sob a pílula de Status, dentro da coluna, sem alargá-la, em quatro tons:
- **Pregão aberto:** "Aberto · fecha 17:00 (16:00 NY)", discreto, com ponto.
- **Mercado fechado:** "Fechado · abre hoje 10:30 (09:30 NY)", com o motivo quando é fim de semana ou feriado ("Fechado · feriado em NY · abre sex. 11:30 (09:30 NY)"), em cinza, com relógio.
- **Dados atrasados:** "Dados atrasados · falta seg. 26/10", em âmbar, com triângulo de aviso, e "Sinal em espera".
- **Dados insuficientes:** pílula "Sem leitura" e "Dados insuficientes · 40 de 200 candles", em cinza com borda tracejada, com ampulheta, e "Sem sinal".

No cartão do celular, o mesmo estado aparece com o texto completo ("Pregão aberto · fecha 17:00 (16:00 em NY)", "Mercado fechado · fim de semana · abre seg., 26 out., 10:30 (09:30 em NY)", "Dados atrasados · último candle sex., 23 out.; esperado seg., 26 out." e "Sinal em espera até o dado normalizar", "Sem sinal até completar o histórico"). Cada estado MUST ter ícone + texto, nunca só cor. Nas tags, o favorito marcado "Alertar" MUST mostrar "Alerta", e o desmarcado, nada. O indicador "Em carteira" MUST contar ativos distintos (dois favoritos de NVDA contam um ativo).

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

#### Scenario: Ticker com série curta
- **WHEN** um favorito de QQQ 1d tem 40 candles fechados e a estratégia precisa de 200
- **THEN** a linha MUST ficar em "Saída / cobertura" com a pílula "Sem leitura" e "Dados insuficientes · 40 de 200 candles"
- **AND** nenhum sinal, alerta ou aviso de atraso MUST sair dela

#### Scenario: Linha compacta
- **WHEN** o Monitor mostra NVDA 1d com pregão aberto a 1440 px
- **THEN** a linha MUST ter altura próxima da linha de BTC/USDT (no protótipo, 178 px contra 158 px)

### Requirement: Carteira de ação e ETF
Para ação e ETF, a tag "Carteira" e o controle do cartão SHALL usar a marcação manual de hoje (`MonitorPreference`). O texto de ajuda do controle MUST dizer "Ação/ETF na carteira recebe entrada e saída no Telegram." A cripto MUST manter a carteira derivada da Binance de hoje.

#### Scenario: Marcar NVDA na carteira
- **WHEN** Alan marca NVDA na carteira no cartão
- **THEN** a tag MUST virar "● Carteira" e a preferência MUST ser gravada para NVDA

### Requirement: Gráfico e trades pela série do favorito
"Abrir Gráfico" e "Ver Trades" de ação e ETF da Binance SHALL ler a série do favorito no tempo gráfico dele pelo histórico da Binance Ações (`/api/market/history`), sem forçar 1d. Na fonte antiga, os dois botões MUST ficar visíveis e indisponíveis (`aria-disabled`, `title` e `aria-label` com "(indisponível)") na linha, no cartão e no detalhe, e o motivo MUST aparecer em texto visível abaixo deles: "Fonte antiga: gráfico e trades depois da migração para a Binance.". O detalhe de um favorito MUST mostrar o estado e os valores dele mesmo (na fonte antiga em saída: "Saída confirmada" e "Risco residual").

#### Scenario: NVDA da fonte antiga no celular
- **WHEN** Alan toca em "Ver Trades" no cartão de NVDA da fonte antiga
- **THEN** nada abre, e o cartão mostra o motivo em texto

#### Scenario: NVDA 1h
- **WHEN** Alan abre o gráfico de um favorito NVDA 1h
- **THEN** o gráfico MUST mostrar candles de 1h do pregão regular

### Requirement: Faixa da transição no Monitor
Quando o usuário tem alertas ligados e nenhum favorito próprio marcado "Alertar", o Monitor SHALL mostrar acima dos indicadores uma faixa `role=status`: "Os alertas do Telegram agora vêm dos seus favoritos marcados "Alertar". Você ainda não marcou nenhum." Ela MUST ter o link "Marcar em Favoritos" (alvo de 44 px) e MUST sumir quando houver um favorito marcado (decisão 1 de Alan). Só para quem recebia alerta do catálogo (`favorite-telegram-alerts`), a faixa MUST acrescentar "Até <data do deploy> você recebia os alertas do catálogo do Cripto Farol; agora cada pessoa escolhe os próprios."

#### Scenario: Usuário só do catálogo
- **WHEN** um usuário que recebia alertas do catálogo, com Telegram ligado e sem favorito marcado, abre o Monitor
- **THEN** a faixa MUST aparecer com a frase com data e o link para Favoritos

#### Scenario: Usuário que nunca recebeu
- **WHEN** um usuário com Telegram ligado, sem favorito marcado, que nunca recebeu alerta do catálogo, abre o Monitor
- **THEN** a faixa MUST aparecer sem a frase com data
