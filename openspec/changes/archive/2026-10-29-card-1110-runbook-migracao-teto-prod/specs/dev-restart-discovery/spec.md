## MODIFIED Requirements

### Requirement: Descoberta religada uma vez com os limites do #1093
Depois da trava passar, o restart SHALL ligar a Descoberta exatamente uma vez, já com os units recém-instalados, e SHALL só sair com sucesso com os quatro serviços ativos. Os limites efetivos da Descoberta SHALL ser MemoryHigh=3 GiB, MemoryMax=4 GiB e MemorySwapMax=512 MiB (valores do #1110 sobre a contenção do #1093).

#### Scenario: Limites efetivos após o restart
- **WHEN** o restart termina com a Descoberta antes ativa
- **THEN** `systemctl show` da Descoberta informa 3221225472 / 4294967296 / 536870912 e a Descoberta tem um único start nesse restart
