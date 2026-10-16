## ADDED Requirements

### Requirement: Calendário mensal e anual com limite no mês de destino

Combo e Descoberta MUST resolver `1m`, `3m`, `6m`, `1y` e `2y` subtraindo respectivamente 1, 3, 6, 12 e 24 meses da referência UTC original. MUST preservar o dia quando existir e usar o último dia do mês de destino quando não existir, sem transbordar. A data final MUST permanecer igual à referência.

#### Scenario: Dia existente e limites mensais
- **WHEN** as duas telas resolvem `1m` nas referências abaixo
- **THEN** ambas MUST produzir as datas iniciais correspondentes e manter a referência como final

| Referência | Inicial |
| --- | --- |
| 2026-05-15 | 2026-04-15 |
| 2026-03-31 | 2026-02-28 |
| 2026-05-31 | 2026-04-30 |
| 2024-03-31 | 2024-02-29 |

#### Scenario: Todas as opções e virada do ano sem encurtamento cumulativo
- **WHEN** as duas telas resolvem as referências abaixo para cada opção
- **THEN** ambas MUST produzir as datas iniciais da tabela e preservar a data final

| Referência | 1m | 3m | 6m | 1y | 2y |
| --- | --- | --- | --- | --- | --- |
| 2026-05-15 | 2026-04-15 | 2026-02-15 | 2025-11-15 | 2025-05-15 | 2024-05-15 |
| 2026-03-31 | 2026-02-28 | 2025-12-31 | 2025-09-30 | 2025-03-31 | 2024-03-31 |
| 2024-02-29 | 2024-01-29 | 2023-11-29 | 2023-08-29 | 2023-02-28 | 2022-02-28 |
| 2026-01-31 | 2025-12-31 | 2025-10-31 | 2025-07-31 | 2025-01-31 | 2024-01-31 |

### Requirement: Paridade entre apresentação e janela consumida

Com a mesma referência e opção, Combo e Descoberta MUST apresentar datas coerentes e enviar/consumir a mesma janela no backtest. Datas explícitas existentes MUST continuar prevalecendo na Descoberta; o fallback sem datas MUST seguir a mesma regra de calendário.

#### Scenario: Fim de mês nos fluxos das telas
- **WHEN** a referência UTC é 2026-03-31 e o operador escolhe `1m` no Combo ou na Descoberta
- **THEN** a data inicial apresentada onde já houver apresentação de datas e enviada no payload MUST ser 2026-02-28, com final 2026-03-31
- **AND** preflight/criação da Descoberta e envio do Combo MUST manter essa janela até o consumidor do backtest
- **AND** resolver `1m` no backend sem datas explícitas com a mesma referência MUST produzir a mesma janela

#### Scenario: Datas explícitas preservadas
- **WHEN** um snapshot contém `period_type=6m`, `start_date=2025-01-01` e `end_date=2025-12-31`
- **THEN** a Descoberta MUST continuar usando 2025-01-01 a 2025-12-31, sem recalcular pelo relógio atual

### Requirement: Preservação dos outros modos

A correção MUST preservar datas inicial/final de períodos por dias, personalizado e todo o histórico para as mesmas entradas, assim como lista de opções, labels e defaults existentes.

#### Scenario: Quinze dias
- **WHEN** `15d` é resolvido com referência 2026-08-15
- **THEN** a janela MUST continuar sendo 2026-07-31 a 2026-08-15 nas duas telas

#### Scenario: Personalizado
- **WHEN** o operador informa 2026-01-01 a 2026-06-01 no período personalizado
- **THEN** ambas as datas MUST ser preservadas exatamente; campos vazios e impedimentos existentes MUST manter o comportamento anterior

#### Scenario: Todo o histórico
- **WHEN** o operador seleciona `all`
- **THEN** a resolução MUST continuar retornando início/final nulos e o payload da Descoberta MUST continuar sem limites de data explícitos
