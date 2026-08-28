# bootstrap-env-append-only Specification

## Purpose
TBD - created by archiving change card-752-bootstrap-env-append-only. Update Purpose after archive.
## Requirements
### Requirement: CLI fail-closed com --file obrigatório e patch via --from-file/stdin

O script `ops/bootstrap_env.py` SHALL exigir `--file` (sem default) apontando para o dotenv destino concreto; SHALL aceitar patch via `--from-file <path>` e/ou stdin (`KEY=VALUE`), sem flag `--set`; SHALL aplicar `--from-file` primeiro e stdin por cima (stdin ganha quando a mesma chave aparece nas duas fontes no patch). Destino ausente ou invocação sem `--file` SHALL sair com exit ≠0 e não criar ficheiro nesse path. Patch sem nenhuma chave `KEY=VALUE` (ficheiro vazio, só comentários/linhas vazias, ou stdin TTY/pipe vazio) SHALL sair com exit ≠0 sem escrita e sem backup.

#### Scenario: Destino inexistente ou sem --file
- **WHEN** operador invoca o script sem `--file` ou com `--file` apontando para path inexistente/não-regular
- **THEN** o processo SHALL sair com exit ≠0
- **AND** nenhum ficheiro SHALL ser criado nesse path

#### Scenario: Patch vazio em ambas as fontes
- **WHEN** `--from-file` aponta para ficheiro vazio ou só com comentários/linhas vazias e stdin não traz nenhuma `KEY=VALUE` (TTY ou pipe vazio)
- **THEN** o script SHALL sair com exit ≠0
- **AND** o destino SHALL permanecer inalterado e sem backup novo

#### Scenario: --from-file e stdin juntos com mesma chave
- **WHEN** `--from-file` contém `FOO=a` e stdin contém `FOO=b` (fora do piso) e destino saudável
- **THEN** o destino SHALL ficar com `FOO=b`
- **AND** demais chaves do destino SHALL permanecer

#### Scenario: Sem --set na argv
- **WHEN** CLI é inspeccionada
- **THEN** não SHALL existir flag `--set` que aceite `KEY=VALUE` via argv

### Requirement: Merge por chave append-only com piso DATABASE_URL+JWT_SECRET imutável

O resultado SHALL ser `destino ∪ patch`; nenhuma chave do destino SHALL desaparecer. O piso `DATABASE_URL` + `JWT_SECRET` SHALL ser presente e não-vazio (após strip) no destino antes e no resultado; chaves comentadas não contam. Se o patch trouxer piso com valor diferente do destino (comparação após strip) SHALL sair com exit ≠0 sem backup e sem `mv`. Omitir piso no patch ou repetir mesmo valor SHALL ser válido. Demais chaves do patch SHALL fazer update-or-insert. Destino sem piso (ausente, vazio ou só whitespace) ou resultado sem piso SHALL recusar com exit ≠0 e destino não substituído.

#### Scenario: Segunda corrida idêntica sem mutação
- **WHEN** destino existente com piso e outras chaves (ex.: `WORKFLOW_DATABASE_URL`) recebe duas corridas com mesmo patch de 4 chaves Telegram
- **THEN** na primeira, outras chaves SHALL continuar no destino
- **AND** na segunda corrida o exit SHALL ser 0 sem backup novo e sem `mv`

#### Scenario: Destino sem DATABASE_URL
- **WHEN** destino não tem `DATABASE_URL` (wiped, tmp só com Telegram, ou valor vazio/whitespace)
- **THEN** o script SHALL sair com exit ≠0
- **AND** o destino SHALL não ser substituído e o conteúdo anterior SHALL permanecer

#### Scenario: Destino sem JWT_SECRET
- **WHEN** destino não tem `JWT_SECRET` (ausente ou vazio/whitespace)
- **THEN** o mesmo fail-closed do cenário anterior SHALL ocorrer

#### Scenario: Patch sem piso preserva piso do destino
- **WHEN** patch não traz piso e destino é saudável
- **THEN** o piso SHALL permanecer vindo do destino no resultado

#### Scenario: Patch traz piso com valor diferente
- **WHEN** patch traz `JWT_SECRET` ou `DATABASE_URL` com valor diferente do destino
- **THEN** o script SHALL sair com exit ≠0, destino inalterado e sem bak novo

### Requirement: Preservar comentários, linhas vazias, ordem e sufixo; chaves novas no fim

Ao acrescentar/atualizar, o script SHALL preservar comentários (`#...`), linhas vazias e ordem do destino; chaves já presentes SHALL mudar só o valor na mesma linha, preservando sufixo de comentário na mesma linha (`#`/`;`); chaves novas SHALL ir para o fim na ordem efetiva do patch (ordem do `OrderedDict` após merge file→stdin).

#### Scenario: Comentários e ordem preservados
- **WHEN** destino com comentários e linhas vazias recebe patch que acrescenta chave nova e atualiza existente (fora do piso)
- **THEN** comentários/vazias/ordem das linhas antigas SHALL permanecer
- **AND** a chave existente SHALL mudar só o valor na sua linha com sufixo preservado
- **AND** a chave nova SHALL ir para o fim

### Requirement: Backup timestamped e replace atómico com chmod 600

Antes de qualquer escrita, o script SHALL criar backup timestamped do destino no mesmo diretório com padrão `.env.bak-YYYYMMDD-HHMMSS` (com hora/segundos para não colidir no mesmo dia; se colidir, sufixo `.<n>` incremental) e `chmod 600` no bak. A escrita SHALL ser via ficheiro temporário no mesmo filesystem (`mkstemp` no diretório do destino), `fsync`, `chmod 600` no temporário e `os.replace` atómico para o destino. O script SHALL recusar se o destino antes ou o resultado não tiverem piso. Após escrita SHALL fazer `chmod 600` no destino; no no-op idempotente não SHALL alterar perms nem criar bak. EACCES no destino (não-owner) SHALL sair com exit ≠0 sem criar/truncar.

#### Scenario: Escrita bem-sucedida cria bak e modo 600
- **WHEN** escrita bem-sucedida ocorre
- **THEN** o modo do destino SHALL ser `600`
- **AND** SHALL existir um bak timestamped no mesmo diretório com modo `600`

#### Scenario: Merge idêntico não cria bak nem mv
- **WHEN** merge é idêntico ao destino (segunda corrida já aplicada)
- **THEN** exit SHALL ser 0 sem backup novo, sem `mv`, sem mutação e sem `chmod`

#### Scenario: EACCES sem truncar
- **WHEN** destino não é gravável pelo utilizador (ex.: `root:root 600` e operador sem permissão)
- **THEN** exit SHALL ser ≠0 sem criar/truncar destino nem bak

### Requirement: Testes em tmp e saída sem valores

A suíte automatizada do card SHALL usar apenas fixtures em `tmp_path`/tmp e SHALL NUNCA abrir para escrita os dotenv reais de DEV/PROD. A saída do script (stdout/stderr) SHALL conter só nomes de chaves / contagens / paths e SHALL NUNCA conter valores de secrets.

#### Scenario: Testes só em tmp
- **WHEN** a suíte de testes do card corre
- **THEN** nenhum teste SHALL abrir para escrita `backend/.env`, `.env`, `/srv/apps/dev/...` ou `/srv/apps/prod/...` reais
- **AND** todos os cenários SHALL usar diretórios temporários

#### Scenario: Saída não vaza valores
- **WHEN** script corre com patch contendo valores
- **THEN** stdout/stderr SHALL conter nomes de chaves, contagens ou paths
- **AND** SHALL NOT conter os `VALUE` do patch ou do destino

### Requirement: Doc DEV vs PROD e home backend para Telegram

Após o card, `docs/monitor-telegram-alerts.md` SHALL conter secção curta que documenta DEV vs PROD, que um bot Telegram = um webhook (`setWebhook` para PROD invalida o DEV; PROD e DEV não partilham webhook ao mesmo tempo) e que as vars Telegram (`MONITOR_TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `MONITOR_TELEGRAM_BOT_USERNAME`, `MONITOR_TELEGRAM_ALERTS_ENABLED`) vão para o dotenv do backend (`<checkout>/backend/.env`, o que o unit faz `source`), não para o dotenv da raiz (home `BINANCE_*`).

#### Scenario: Operador liga webhook
- **WHEN** operador lê `docs/monitor-telegram-alerts.md` para ligar o webhook
- **THEN** SHALL estar escrito que um bot = um `setWebhook` e que PROD e DEV não partilham webhook
- **AND** SHALL estar escrito quais vars vão para o dotenv do backend e que o unit faz `source` desse ficheiro

