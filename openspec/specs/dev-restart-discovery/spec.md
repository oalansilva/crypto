# dev-restart-discovery Specification

## Purpose
TBD - created by archiving change card-1106-restart-discovery. Update Purpose after archive.
## Requirements
### Requirement: Restart do DEV para a Descoberta antes de instalar os limites
O restart canônico do DEV SHALL parar `criptofarol-dev-discovery-worker.service` antes de instalar os units da Descoberta, em todo restart, inclusive quando a configuração instalada é igual ao template e quando há busca em andamento. O restart MUST NOT esperar a busca terminar além do tempo de parada do próprio serviço. Se a parada falhar, o restart SHALL sair com código diferente de zero sem instalar os units.

#### Scenario: Descoberta ativa
- **WHEN** a Descoberta está ativa e o restart do DEV roda, direto ou pela integração no develop
- **THEN** a Descoberta é parada antes da instalação dos units, o restart sai com sucesso e backend, frontend, worker de runtime e Descoberta ficam ativos

#### Scenario: Configuração igual à instalada
- **WHEN** a Descoberta está ativa com units iguais ao template e o restart roda
- **THEN** a Descoberta é parada e ligada de novo do mesmo jeito

#### Scenario: Descoberta já parada
- **WHEN** a Descoberta está parada e o restart roda
- **THEN** o restart funciona como hoje e termina com os quatro serviços ativos

#### Scenario: Parada falha
- **WHEN** a parada da Descoberta retorna erro
- **THEN** o restart sai com código diferente de zero, diz que a Descoberta não parou e não instala os units

### Requirement: Limites nunca sobre processo remanescente
A trava do instalador SHALL continuar recusando a instalação com a Descoberta ativa ou com processo no seu cgroup. Ao recusar por processo remanescente, a mensagem SHALL citar o cgroup, cada PID com seu comando e que os limites não foram aplicados. O restart MUST NOT matar nem forçar processos remanescentes.

#### Scenario: Sobrou processo após a parada
- **WHEN** depois da parada ainda há processo no cgroup da Descoberta e o restart tenta instalar os limites
- **THEN** o restart para com código diferente de zero, a mensagem diz o que restou, e nenhum unit é gravado, recarregado ou ligado

### Requirement: Descoberta religada uma vez com os limites do #1093
Depois da trava passar, o restart SHALL ligar a Descoberta exatamente uma vez, já com os units recém-instalados, e SHALL só sair com sucesso com os quatro serviços ativos. Os limites efetivos da Descoberta SHALL ser MemoryHigh=3 GiB, MemoryMax=4 GiB e MemorySwapMax=512 MiB (valores do #1110 sobre a contenção do #1093).

#### Scenario: Limites efetivos após o restart
- **WHEN** o restart termina com a Descoberta antes ativa
- **THEN** `systemctl show` da Descoberta informa 3221225472 / 4294967296 / 536870912 e a Descoberta tem um único start nesse restart

### Requirement: Busca interrompida retoma pela recuperação existente
Uma busca em andamento na hora do restart SHALL ser interrompida pela parada e SHALL retomar depois pela recuperação do #1093, gastando uma tentativa. Este contrato MUST NOT alterar tentativas, backoff, circuito ou limites.

#### Scenario: Busca em andamento
- **WHEN** uma busca da Descoberta está em andamento e o restart roda
- **THEN** o restart não espera nem recusa e termina com sucesso, e a busca retoma depois com uma tentativa a menos

