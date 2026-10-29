# asset-history-coverage Specification

## Purpose
TBD - created by archiving change card-1118-historico-binance. Update Purpose after archive.
## Requirements
### Requirement: Seletor de ativos mostra a cobertura do histórico

Em cada linha do seletor de ativos (Descoberta, Combo e Otimização), o fato de histórico SHALL mostrar, para cripto, ação e ETF: "Histórico sob demanda" quando nada foi coletado; o início da cobertura, quantos timeframes há, as lacunas e a última atualização quando há histórico; "Coletando histórico" com o progresso enquanto a coleta roda; a falha com o motivo e o que já foi coletado ("já coletado: …") quando a coleta falhou; e "Parcial" quando a Binance não cobre o início pedido na última consulta. O texto "Histórico não coletado" MUST NOT aparecer.

Quando os timeframes começam em datas diferentes, o resumo SHALL dizer de qual timeframe é cada "desde" e MUST NOT usar um "desde" único que sugira o período mais longo para todos. A contagem de lacunas do resumo SHALL somar só lacunas de séries nativas; a lacuna que o 15m derivado herda do 5m MUST NOT ser contada de novo.

Até o #1119 aceitar ação e ETF nas análises, o estado sob demanda dessas classes SHALL explicar que a coleta começa quando as análises aceitarem a classe, sem botão nem outro gatilho na tela.

#### Scenario: Ação coberta com inícios diferentes

- **WHEN** NVDA tem 1d desde 11 nov. 2014 e 5m e 15m desde 19 mai. 2026, sem lacunas
- **THEN** a linha mostra "1d desde 11 nov. 2014 · 5m e 15m desde 19 mai. 2026 · sem lacunas · atualizado" com data e hora

#### Scenario: Cripto coberta com início comum

- **WHEN** BTC/USDT tem 1d, 4h, 1h e 15m desde 17 ago. 2017
- **THEN** a linha mostra "Histórico desde 17 ago. 2017 · 4 timeframes"

#### Scenario: Lacuna do 5m não conta duas vezes

- **WHEN** SPY tem uma lacuna no 5m e o bloco correspondente do 15m derivado fica incompleto
- **THEN** a linha mostra "1 lacuna"
- **AND** a tabela mostra a lacuna no 5m e, no 15m, a mesma falta como "herdada do 5m"

#### Scenario: Ação nunca pedida

- **WHEN** AAPL nunca foi pedido numa consulta
- **THEN** a linha mostra "Histórico sob demanda" e diz que a coleta começa quando as análises aceitarem ações

#### Scenario: Coleta falhou

- **WHEN** a coleta de QQQ parou por limite de requisições da Binance
- **THEN** a linha diz que a coleta falhou, o motivo e "já coletado:" com o timeframe e a data de início

### Requirement: Detalhe da cobertura por timeframe

Cada linha com histórico SHALL ter o botão "Cobertura" que abre, abaixo da linha, uma tabela por timeframe com período coberto, lacunas (com data, hora e fuso), última atualização (com o fuso no rótulo) e origem. Lacunas de ação e ETF SHALL estar no horário de Nova York, escrito na célula. O 15m de ação e ETF SHALL aparecer como "montado do 5m". A série de ação e ETF SHALL mostrar "pregão regular" e o ajuste. O botão SHALL ficar fora do `<label>` da linha, ter `aria-expanded`, funcionar por teclado (Enter e Space alternam; Esc fecha e devolve o foco ao botão) e MUST NOT marcar nem desmarcar o ativo.

#### Scenario: 15m derivado

- **WHEN** Alan abre a cobertura de NVDA
- **THEN** a linha de 15m diz "montado do 5m"

#### Scenario: Abrir não seleciona

- **WHEN** Alan aciona "Cobertura" de SPY com o teclado
- **THEN** a tabela abre e SPY continua fora da seleção

#### Scenario: Esc fecha

- **WHEN** a tabela de SPY está aberta e Alan aperta Esc com o foco no botão ou dentro da tabela
- **THEN** a tabela fecha, `aria-expanded` volta a `false` e o foco fica no botão "Cobertura"

#### Scenario: Fuso das lacunas

- **WHEN** Alan abre a cobertura de SPY
- **THEN** a lacuna do 5m aparece como "14 out. 2026, 10:05–10:40, horário de Nova York"
- **AND** a coluna de atualização diz o fuso local no rótulo

### Requirement: Decidir mostra até quando a amostra fica guardada

No Decidir da Descoberta, a linha de evidência SHALL dizer até quando a amostra da varredura fica guardada e que favoritos guardam a amostra do último refresh. Cada resultado SHALL mostrar o estado da própria amostra da varredura; resultado promovido a favorito SHALL dizer também que Favoritos guarda a amostra do último refresh. Depois do prazo, a linha de evidência e os resultados SHALL mostrar "não reproduzível exatamente", com o mesmo tamanho de texto nas duas.

#### Scenario: Amostra vencida

- **WHEN** a varredura terminou há mais de 30 dias
- **THEN** o Decidir mostra "não reproduzível exatamente" na evidência e nos resultados
- **AND** o resultado favoritado diz também "favorito: Favoritos guarda a amostra do último refresh"

