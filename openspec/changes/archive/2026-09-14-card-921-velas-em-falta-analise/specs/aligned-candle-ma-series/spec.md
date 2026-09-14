## ADDED Requirements

### Requirement: Velas e médias partilham o último timestamp carregado
Nas superfícies `/combo/results` (análise aberta pelos Favoritos) e gráfico do Monitor, cada série de média (SMA/EMA ou equivalente) SHALL terminar no timestamp da última vela que a tela realmente carregou. O gráfico MUST NOT pintar linha de média à frente dessa vela (buraco à direita com linha solta).

#### Scenario: Médias teriam pontos depois da última vela na análise
- **WHEN** a análise em `/combo/results` tem pontos de média com timestamp depois da última vela carregada
- **THEN** o gráfico MUST NOT mostrar linha de média à frente dessa vela
- **AND** o último ponto de média visível coincide com a última vela carregada

#### Scenario: Médias teriam pontos depois da última vela no Monitor
- **WHEN** o gráfico do Monitor tem pontos de média com timestamp depois da última vela carregada
- **THEN** o gráfico MUST NOT mostrar linha de média à frente dessa vela
- **AND** o último ponto de média visível coincide com a última vela carregada

#### Scenario: Vale em outro ativo
- **WHEN** o operador abre a análise ou o gráfico do Monitor noutro par cripto que não BTC
- **THEN** a média também MUST NOT avançar à frente da última vela carregada

### Requirement: Análise usa a série de mercado em dia ao abrir
Ao abrir a análise, se a série de mercado daquele par/intervalo já está em dia, a última vela do gráfico SHALL coincidir com a última vela de mercado. O gráfico MUST NOT permanecer no snapshot antigo da análise.

#### Scenario: BTC 1d com mercado em dia
- **WHEN** a série de mercado BTC 1d já está em dia (medido: mercado em 12/09, snapshot do favorito em 15/08)
- **AND** o operador abre a análise pelos Favoritos
- **THEN** a última vela do gráfico coincide com a última vela de mercado
- **AND** o gráfico MUST NOT ficar parado em 15/08

### Requirement: Universo de pares de mercado fica em dia
Este card SHALL encher todos os pares de mercado cripto do produto, mesmo os que não estão agora no Monitor nem nos Favoritos, nos intervalos que a análise e o Monitor deixam abrir (Monitor: 15m, 1h, 4h e 1d; análise: o intervalo do favorito). Depois de encher, a série SHALL continuar até o presente.

#### Scenario: Par fora do ecrã também é enchido
- **WHEN** um par de mercado não está nos Favoritos nem visível no Monitor
- **THEN** a série desse par também fica em dia nos intervalos 15m, 1h, 4h e 1d
- **AND** o aceite MUST NOT restringir-se ao que está no ecrã

#### Scenario: Par 1d parado em maio
- **WHEN** um par 1d está parado em maio (ex.: DOGE)
- **AND** o preenchimento corre
- **THEN** a série de mercado chega ao presente
- **AND** o gráfico deixa de mostrar o buraco desses meses

#### Scenario: Intervalos 15m, 1h e 4h
- **WHEN** o operador abre 15m, 1h ou 4h no Monitor, ou o intervalo do favorito na análise
- **THEN** a média MUST NOT avançar à frente da última vela
- **AND** se esse intervalo estava parado, também é enchido

#### Scenario: Continuidade depois de encher
- **WHEN** dias ou semanas passam após o enchimento
- **THEN** essas séries continuam até o presente
- **AND** MUST NOT voltar a ficar meses atrás

### Requirement: 1:1 lista↔setas do 917 permanece
O aceite 1:1 lista↔setas da análise (`/combo/results`) SHALL continuar a passar. Este card MUST NOT reabrir nem substituir a origem das setas.

#### Scenario: Abrir análise depois deste card
- **WHEN** o operador abre a análise com velas e médias alinhadas
- **THEN** cada operação da lista continua a ter seta na vela certa
- **AND** o zoom inicial recente (~180 velas) permanece
