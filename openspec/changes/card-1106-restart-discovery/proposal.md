## Why

Desde o #1093, o `./restart` do DEV aborta sempre que a Descoberta está ligada, que é o estado normal; toda integração no develop (T14) cai em `I8` no passo `restart` e o card fica preso em QA. A trava do #1093 está certa (não aplicar limites novos sobre uma árvore antiga em execução), mas ninguém para a Descoberta antes de instalar os limites.

O texto abaixo, de `## Problema` até `## Não entra`, é cópia integral do body do issue #1106 (lido por REST em 2026-10-16). O *como* está em `design.md`.

## Problema

Quem sofre é o operador do fluxo (Alan e os agentes): toda integração no develop trava em QA porque o restart do DEV recusa rodar com a Descoberta ligada, que é o estado normal.

Desde o #1093, `./restart` do DEV falha sempre que `criptofarol-dev-discovery-worker.service` está ativo, que é o estado normal.

`./restart` chama `install-discovery-workers-systemd.sh` em toda execução. O script (linha ~129) recusa rodar com o worker ativo:

```
Stop/drain DEV Discovery and verify empty cgroup before installing limits.
```

A trava existe para não aplicar o envelope de memória novo sobre uma árvore antiga em execução, o que poderia causar OOM imediato. Mas ninguém drena nem para o worker antes, então o restart aborta.

## Impacto

- Todo T14 (`process_event integrar_develop`) cai em `I8` no passo `restart`, e o card fica preso em QA.
- Ocorreu no T14 do #1086 em 2026-10-16. Só passou depois de parar o worker à mão (`systemctl stop`), conferir o cgroup vazio e repetir o T14.

## Reprodução

1. Confirmar `systemctl is-active criptofarol-dev-discovery-worker.service` = `active`.
2. Rodar `./restart` no DEV, direto ou via T14.
3. O restart aborta com a mensagem acima.

## Ideias para o grill (não decididas)

- (a) `./restart` drena e para só o worker de Discovery antes de instalar os units, confere o cgroup vazio e sobe de novo.
- (b) A trava só vale quando o envelope/units instalados realmente mudam. Se forem iguais, o restart segue.

## História

Como operador do fluxo de cards,
quero que o restart do DEV funcione com a Descoberta ligada sem eu precisar parar nada à mão,
para que a integração no develop não fique presa em QA e a proteção de memória do #1093 continue valendo.

## Entra

- Restart do DEV com a Descoberta ligada termina com sucesso, sem passo manual, e ao final backend, frontend, worker de runtime e Descoberta estão ativos.
- A integração no develop de um card conclui o passo de restart e o card sai de QA normalmente.
- A Descoberta volta ativa já com os limites de memória do #1093 (alto 5 GiB, máximo 6 GiB, swap 512 MiB).
- A proteção do #1093 continua: os limites novos nunca são aplicados por cima de uma Descoberta antiga ainda rodando. Se depois da parada ainda restar processo da Descoberta, o restart falha com mensagem clara e não força nada.
- Restart com a Descoberta já parada continua funcionando como hoje.
- Decidido no grill: todo restart do DEV para a Descoberta antes de aplicar os limites, confere que nada sobrou e liga de novo, mesmo quando a configuração dela não mudou.
- Decidido no grill: uma busca em andamento na hora do restart é interrompida, como já acontecia antes do #1093, e retoma sozinha depois, gastando uma das suas tentativas.

Critérios observáveis:

- Dado a Descoberta ativa, quando o restart do DEV roda (direto ou pela integração no develop), então ele sai com sucesso e os quatro serviços ficam ativos.
- Dado a Descoberta ativa, quando o restart termina, então os limites efetivos dela são 5 GiB / 6 GiB / 512 MiB.
- Dado que sobrou processo da Descoberta após a parada, quando o restart tenta instalar os limites, então ele para com mensagem que diz o que restou, sem aplicar os limites.
- Dado a Descoberta ativa com configuração igual à instalada, quando o restart roda, então a Descoberta é parada e ligada de novo do mesmo jeito.
- Dado uma busca da Descoberta em andamento, quando o restart roda, então ele não espera nem recusa: interrompe a busca, termina com sucesso, e a busca retoma depois com uma tentativa a menos.

## Não entra

- Mudar os limites de memória do #1093.
- PROD.

## What Changes

- O restart do DEV passa a parar a Descoberta (`criptofarol-dev-discovery-worker.service`) antes de instalar os units, sempre, mesmo com configuração igual (ideia (a) do issue, fechada no grill). A trava do #1093 no instalador continua com a mesma condição e é ela que confere que nada sobrou.
- Se sobrar processo da Descoberta depois da parada, o restart para com mensagem que lista o que restou (PID e comando) e diz que os limites não foram aplicados; não força nada.
- A Descoberta é ligada uma única vez por restart, já com os limites do #1093 (5 GiB / 6 GiB / 512 MiB), e o restart só termina com sucesso com os quatro serviços ativos.
- Busca em andamento é interrompida pela parada e retoma depois pela recuperação do #1093, gastando uma tentativa (decisão do grill). Nenhuma regra de tentativas, circuito ou limite muda.
- Testes automatizados sem systemd real cobrem a ordem parar → conferir → instalar → ligar e o caso de falha; a verificação no DEV fecha os critérios observáveis.

## Capabilities

### New Capabilities

- `dev-restart-discovery`: ciclo da Descoberta dentro do restart canônico do DEV — parar sempre, conferir que nada sobrou, instalar os limites, ligar uma vez e falhar de forma clara quando sobra processo.

### Modified Capabilities

Nenhuma. Os requisitos de limites, tentativas e circuito da Descoberta (change `card-1093-discovery-memory`, ainda não arquivada) não mudam; este card só acrescenta o contrato do restart.

## Impact

- `restart` (bloco `CANONICAL DEV RESTART`) e `install-discovery-workers-systemd.sh` (só a mensagem da trava e o que ela informa; a condição não muda).
- Testes: `backend/tests/unit/test_dev_restart_contract.py` e `scripts/test_install_discovery_workers.sh`.
- `docs/discovery-memory-operations.md`: nota curta sobre o ciclo da Descoberta no restart normal.
- Indireto: T14 (`scripts/process-fsm/t14.py`) volta a passar no passo `restart` sem mudança de código.
- Fora: unit `ops/systemd/criptofarol-dev-discovery-worker.service` (limites do #1093), PROD, backend da Descoberta (tentativas, circuito, recuperação).
