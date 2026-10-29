## ADDED Requirements

### Requirement: Teto da Descoberta de PROD aplicado só sem busca ativa
A aplicação dos limites na unit `criptofarol-prod-discovery-worker.service` SHALL usar o instalador a partir de `/srv/apps/prod/criptofarol/source` restrito à unit da Descoberta. Antes de parar qualquer coisa, o instalador SHALL consultar o ledger do #1093 e considerar busca ativa quando houver sweep `running` ou `cancelling`, lease com validade futura pelo relógio do PostgreSQL ou tentativa `running` sem fim; erro de consulta SHALL contar como ativa. Sweeps `pending` (na fila, sem execução) e `paused` SHALL ser listados e MUST NOT bloquear. Com busca ativa, o instalador SHALL reconsultar a cada 60 segundos até o prazo de espera (padrão 30 minutos, ajustável) e, esgotado, adiar: sair com código diferente de zero, informar "adiado: busca ativa" com os sweeps encontrados e não parar, gravar nem reiniciar nada; o operador repete depois. Sem busca ativa, SHALL parar só a Descoberta PROD, recusar se a unit seguir ativa ou o cgroup tiver processo, gravar só essa unit, recarregar e ligá-la uma vez. Runtime-worker, backend, frontend e leads de PROD MUST NOT ser reescritos nem reiniciados por esse passo.

#### Scenario: Busca de cliente em andamento
- **WHEN** há busca ativa em PROD e o operador aplica o teto
- **THEN** o instalador espera; se o prazo acabar, informa "adiado: busca ativa" e a Descoberta PROD segue rodando com a unit anterior até o operador repetir

#### Scenario: Busca só na fila
- **WHEN** há sweep `pending` em PROD, sem lease válida nem tentativa em execução, e o operador aplica o teto
- **THEN** o sweep aparece na listagem, não bloqueia a aplicação e é consumido quando a Descoberta PROD volta

#### Scenario: Sem busca ativa
- **WHEN** não há busca ativa em PROD e o operador aplica o teto
- **THEN** só a Descoberta PROD é parada, regravada e ligada uma vez, e as demais units PROD mantêm o mesmo arranque

#### Scenario: Sobra de processo após a parada
- **WHEN** depois da parada ainda há processo no cgroup da Descoberta PROD
- **THEN** o instalador recusa sem matar nada, lista os PIDs e informa que os limites não foram aplicados

### Requirement: Limites efetivos da Descoberta de PROD verificáveis
Depois da aplicação, `systemctl show criptofarol-prod-discovery-worker.service` SHALL informar MemoryHigh=4294967296, MemoryMax=5368709120, MemorySwapMax=536870912, OOMPolicy=kill, KillMode=control-group, Restart=on-failure, RestartUSec=1min, StartLimitBurst=3, StartLimitIntervalUSec=15min, TimeoutStopUSec=30s e ActiveState=active, e uma sonda de admissão com o perfil `prod` contra o cgroup da unit SHALL passar. O card que aplica o teto MUST NOT ir a Pronto sem essa verificação registrada.

#### Scenario: Verificação após aplicar
- **WHEN** o instalador termina a aplicação do teto em PROD
- **THEN** o `systemctl show` mostra os valores acima e a sonda de admissão do perfil `prod` passa

#### Scenario: Restart da janela do publish com o teto aplicado
- **WHEN** um deploy normal de PROD reinicia a janela do publish depois do teto aplicado
- **THEN** a Descoberta PROD gasta uma das três partidas permitidas em 15 minutos e volta com os mesmos limites
