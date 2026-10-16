## ADDED Requirements

### Requirement: Toda migração em PROD segue o runbook versionado
Antes de trocar o source PROD, depois de `git fetch origin`, o operador SHALL decidir se há migração comparando `alembic current` do banco PROD com `alembic heads` de `origin/main`, obtido num checkout descartável fora do source PROD, e SHALL registrar essa comparação. Revisão do banco diferente do head de `origin/main` SHALL seguir `docs/prod-migration-runbook.md`, sem avaliar compatibilidade caso a caso. Publicação sem revisão nova MUST seguir a linha de deploy PROD atual do overlay.

#### Scenario: Pacote com migração
- **WHEN** o operador prepara o deploy PROD e há ao menos uma revisão Alembic a aplicar
- **THEN** o deploy segue o runbook do início ao fim, qualquer que seja a revisão

#### Scenario: Pacote sem migração
- **WHEN**, depois do `git fetch` e antes de publicar, `alembic current` do banco PROD já é igual ao head de `origin/main`
- **THEN** o deploy segue a linha atual do overlay e o runbook não é exigido

#### Scenario: Decisão antes de publicar
- **WHEN** o operador aplica o gatilho
- **THEN** o source PROD ainda está no SHA anterior e nenhum worker foi parado

### Requirement: Ordem fixa com backup verificado e workers afetados parados
O runbook SHALL executar, nesta ordem: registro do estado inicial (SHA, revisão do banco, head de `origin/main`, units, saída da sonda da Descoberta como registro); parada dos workers afetados; backup `pg_dump` em formato custom com verificação de leitura por `pg_restore --list`; publicação do código; `alembic upgrade head`; build; restart da janela do publish e religamento dos timers; verificação. O runbook MUST NOT esperar busca ativa da Descoberta: a combinação interrompida SHALL ser reagendada pela recuperação do #1093, com uma tentativa a menos. Os workers afetados SHALL ser a lista fixa `criptofarol-prod-candle-writer.timer`, `criptofarol-prod-telegram-alert-scan.timer` (com seus oneshots concluídos), `criptofarol-prod-runtime-worker.service` e `criptofarol-prod-discovery-worker.service`. O runbook SHALL dizer, em linguagem de operador, o que para para os clientes enquanto eles estão parados: velas de PROD sem atualização, buscas novas da Descoberta pendentes e a em curso parada, backtests dos favoritos sem atualização e alerta diário do Telegram atrasado se cair na janela. Backend, frontend e leads MUST continuar servindo até a janela do publish. O backup SHALL ficar fora de qualquer checkout Git, com diretório 0700 e arquivo 0600.

#### Scenario: Workers parados antes do backup
- **WHEN** o operador chega ao passo de backup
- **THEN** os dois timers e os dois workers estão inativos, com `MainPID=0` e cgroup vazio

#### Scenario: Busca da Descoberta em curso
- **WHEN** a sonda registra busca ativa em PROD no passo inicial
- **THEN** o runbook não espera, para a Descoberta com os demais workers e a combinação interrompida volta à fila pela recuperação do #1093 com uma tentativa a menos

#### Scenario: Backup ilegível
- **WHEN** `pg_restore --list` falha, lista zero entradas ou não lista `alembic_version`
- **THEN** nada é publicado nem migrado, os dois serviços e os dois timers são religados e verificados, e o runbook encerra sem migrar

#### Scenario: Migração falha sem aplicar nada
- **WHEN** `alembic upgrade head` sai com erro e `alembic current` ainda é a revisão registrada no passo inicial
- **THEN** o source volta ao SHA registrado, os dois serviços e os dois timers são religados com o código anterior e verificados, e a correção fica com Alan

#### Scenario: Migração falha em revisão intermediária
- **WHEN** `alembic upgrade head` sai com erro e `alembic current` não é a revisão inicial nem o head, ou não responde
- **THEN** o source volta ao SHA registrado, os workers afetados continuam parados, nenhum downgrade automático é executado e a decisão entre restaurar o backup e corrigir para frente fica com Alan

### Requirement: Verificação pós-migração e evidência
Depois de subir, o runbook SHALL verificar `alembic current` igual ao head registrado no passo inicial, as units da janela ativas com arranque dentro da janela, os timers ativos, `https://criptofarol.com.br/api/health` com HTTP 200 e o estado da Descoberta PROD por `systemctl show`. A nota `docs/release-<data>.md` SHALL registrar o horário de cada passo, o backup (tamanho, número de entradas, SHA-256), as revisões aplicadas e os workers parados.

#### Scenario: Migração concluída
- **WHEN** o runbook termina sem erro
- **THEN** a nota da release mostra backup verificado, ordem dos passos com horários e os workers parados durante a migração

### Requirement: Runbook referenciado pelo overlay e pela documentação da Descoberta
`docs/crypto-overlay.md` SHALL citar `docs/prod-migration-runbook.md` na regra de deploy PROD como caminho obrigatório para pacote com migração. `docs/discovery-memory-operations.md` SHALL ter uma seção PROD que aponta para o runbook e descreve o teto da Descoberta PROD.

#### Scenario: Operador lê o overlay
- **WHEN** o operador consulta a linha de deploy PROD do overlay
- **THEN** encontra a regra "com migração, seguir `docs/prod-migration-runbook.md`"

#### Scenario: Operador lê a operação da Descoberta
- **WHEN** o operador abre `docs/discovery-memory-operations.md`
- **THEN** há uma seção PROD com os limites, a política de reinício, a espera por busca ativa para aplicar o teto e o link para o runbook

### Requirement: Evidência da migração da release 2026-10-16
`docs/release-2026-10-16.md` SHALL registrar a ordem dos passos da migração `20261013_0001`, reconstruída de fontes verificáveis (journal das units, backup, saída do Alembic). Um passo sem fonte MUST aparecer como "sem registro", nunca inventado.

#### Scenario: Nota da release atualizada
- **WHEN** o Apply atualiza a nota da release 2026-10-16
- **THEN** a nota mostra backup, ordem dos passos e workers parados, com a fonte de cada horário
