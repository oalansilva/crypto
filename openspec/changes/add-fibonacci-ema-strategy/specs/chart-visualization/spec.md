# chart-visualization Specification Delta

## ADDED Requirements

### Requirement: Visualização de EMA 200
O gráfico de resultados SHALL exibir a linha EMA 200 quando a estratégia Fibonacci EMA é executada.
A EMA 200 MUST ser exibida em cor azul (#3b82f6).
A legenda MUST mostrar "EMA 200" com a cor correspondente.

#### Scenario: Visualizar EMA 200 no Gráfico Principal
- DADO que um backtest com Fibonacci EMA foi executado
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO uma linha azul representando EMA 200 é exibida no painel principal
- E a legenda mostra "EMA 200" em azul

### Requirement: Visualização de Níveis de Fibonacci
O gráfico de resultados SHALL exibir linhas horizontais para os níveis de Fibonacci 0.5 e 0.618.
O nível 0.5 MUST ser exibido em cor verde (#10b981).
O nível 0.618 MUST ser exibido em cor dourada (#f59e0b).
As legendas MUST mostrar "Fib 0.5" e "Fib 0.618" com as cores correspondentes.

#### Scenario: Visualizar Níveis de Fibonacci no Gráfico
- DADO que um backtest com Fibonacci EMA foi executado
- E swing high = 50000, swing low = 40000
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO uma linha horizontal verde é exibida em 45000 (Fib 0.5)
- E uma linha horizontal dourada é exibida em 46180 (Fib 0.618)
- E a legenda mostra "Fib 0.5 (45000)" em verde e "Fib 0.618 (46180)" em dourado

### Requirement: Visualização de Swing Points
O gráfico de resultados SHALL exibir marcadores para swing highs e swing lows.
Swing highs MUST ser marcados com triângulo vermelho apontando para baixo.
Swing lows MUST ser marcados com triângulo verde apontando para cima.
Os marcadores MUST aparecer no preço exato do swing.

#### Scenario: Visualizar Swing Points no Gráfico
- DADO que um backtest com Fibonacci EMA foi executado
- E swing high detectado em 50000
- E swing low detectado em 40000
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO um triângulo vermelho aparece em 50000
- E um triângulo verde aparece em 40000
- E tooltips mostram "Swing High: 50000" e "Swing Low: 40000"

### Requirement: Atualização Dinâmica de Fibonacci
Os níveis de Fibonacci MUST ser atualizados quando novos swing points são detectados.
Níveis antigos MUST ser removidos ou marcados como inativos.
Apenas os níveis do swing mais recente MUST ser exibidos ativamente.

#### Scenario: Atualizar Fibonacci com Novo Swing
- DADO que Fibonacci está calculado entre swing_high=50000 e swing_low=40000
- E um novo swing_high=55000 é detectado
- QUANDO o gráfico é atualizado
- ENTÃO os níveis antigos (baseados em 50000) são removidos
- E novos níveis são calculados e exibidos (baseados em 55000)

### Requirement: Sincronização de Indicadores com Parâmetros
Os indicadores visualizados MUST refletir os parâmetros configurados pelo usuário.
Se o usuário configurar ema_period=150, a legenda MUST mostrar "EMA 150".
Se o usuário configurar fib_level_1=0.382, a legenda MUST mostrar "Fib 0.382".

#### Scenario: Visualizar Indicadores com Parâmetros Customizados
- DADO que um backtest foi executado com ema_period=150, fib_level_1=0.382, fib_level_2=0.786
- QUANDO o usuário visualiza o gráfico
- ENTÃO a legenda mostra "EMA 150", "Fib 0.382", "Fib 0.786"
- E os indicadores calculados usam os valores corretos

### Requirement: Metadados de Indicadores para Visualização
O backend SHALL retornar metadados de indicadores na resposta do backtest.
Os metadados MUST incluir: name, color, data, panel, type.
O campo type MUST ser "line" para EMA, "horizontal" para Fibonacci, "marker" para swings.

#### Scenario: Resposta da API com Indicadores Fibonacci
- DADO que um backtest com Fibonacci EMA foi executado
- QUANDO o frontend solicita os resultados
- ENTÃO a resposta inclui array de indicadores
- E cada indicador contém name, color, data, panel, type
- E EMA 200 tem type="line", panel="main", color="#3b82f6"
- E Fib 0.5 tem type="horizontal", panel="main", color="#10b981", value=45000
- E Fib 0.618 tem type="horizontal", panel="main", color="#f59e0b", value=46180
- E Swing High tem type="marker", panel="main", color="#ef4444", shape="triangle-down"
- E Swing Low tem type="marker", panel="main", color="#10b981", shape="triangle-up"

### Requirement: Zona de Tolerância Visual
O gráfico SHALL exibir uma zona sombreada ao redor dos níveis de Fibonacci representando a tolerância.
A zona MUST ter transparência (alpha=0.2).
A cor da zona MUST corresponder à cor do nível Fibonacci.

#### Scenario: Visualizar Zona de Tolerância
- DADO que Fibonacci 0.5 = 45000 com tolerância = 0.005 (0.5%)
- QUANDO o usuário visualiza o gráfico
- ENTÃO uma zona verde sombreada é exibida entre 44775 e 45225
- E a zona tem transparência para não obstruir o gráfico
