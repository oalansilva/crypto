# #1071 — handoff Done técnico DEV

Data: 2026-10-12 UTC. Estado recebido do pai: T14 `integrar_develop` PASS, `Status=Done`; [PR #1092](https://github.com/oalansilva/crypto/pull/1092) integrado por squash em `develop`, commit `99a3070cd9d117539fe6de734361f07d5e1c4611`. O pai efetuou sync, `./restart` no DEV canônico e health público pelo `process_event`. A verificação QA abaixo observou esse commit no checkout canônico limpo `/srv/apps/dev/criptofarol/source`. Os únicos arquivos escritos nesta continuação são `tasks.md` e este handoff no worktree `/srv/apps/dev/criptofarol/crypto-worktrees/card-1071-segredos-historico`.

Done técnico não comprova incidente contido, invalidação de segredos, saneamento histórico ou Pronto. A tarefa 4.2 foi fechada com os checks comprovados e dispensa explícita de Alan, em 2026-10-13, exclusivamente do teste de login QA (“ignore isso”); esse teste não foi executado nem é apresentado como aprovado. A tarefa 4.3 registra os resultados e todas as obrigações abertas. A continuação de 2026-10-13 diagnosticou o estado Telegram inicial como isolamento esperado, conforme seção abaixo. Nenhuma operação PROD, rotação, rewrite real ou operação financeira foi executada por este QA.

## CI e evidência visual

SHA revisado e verificado no CI: `598833ea2ca4bc702a9dc29da1bb1137bdb67744`. [Run 38261521373](https://github.com/oalansilva/crypto/actions/runs/38261521373), attempt 1. Watcher nativo único com timeout de 35 minutos terminou com exit 0; todos os checks QA iniciados chegaram a PASS: `qa-gate`, `backend-coverage-gate`, `backend-unit-tests`, `backend-tests`, `backend-format`, `frontend-build`, `frontend-lint`, `frontend-tests`, `openspec-validate`, `process-fsm`, `qa-policy`, `new-route-playwright-coverage` e `changes`.

- Remediação: 26 testes passaram sem skips; Gitleaks 8.24.3 com checksum verificado. Ensaio somente sintético com recuperação cifrada, preservação de trabalho/refs, clone independente e integridade Git PASS; `real_refs_modified=false`.
- Harness geral `process-fsm`: 680 passed, 9 skipped, 4 warnings. O resultado não é apresentado como zero skips global.
- Playwright: 263 testes funcionais e 34 visuais desktop/mobile passaram. A API do job confirmou `Run functional Playwright tests`, `Run visual Playwright tests` e upload SUCCESS; a etapa que registraria dispensa foi SKIPPED. Nenhuma dispensa visual foi usada.
- [Artifact visual 11753122057](https://github.com/oalansilva/crypto/actions/runs/38261521373/artifacts/11753122057): `playwright-artifacts-38261521373-1`, 283.692 bytes, não expirado na consulta.
- `deploy-staging` foi SKIPPED pela condição versionada de execução somente em push de `develop` com staging habilitado. Não substitui o restart/smoke DEV realizado após integração.

## Smoke DEV sanitizado

Observações públicas às 15:01:34 UTC e PostgreSQL às 15:01:54 UTC, posteriores ao restart do pai. Só foram emitidos status HTTP, booleanos, estados de serviços e resultados de conexão; nenhuma URL com credencial, valor de configuração, token, conteúdo de banco ou erro bruto.

| Verificação | Resultado | Limite |
| --- | --- | --- |
| Checkout canônico DEV | `develop`, commit de integração acima, limpo | Nenhuma edição no source pelo QA |
| Backup no Git/ignore | `git ls-files .local_backups` sem entradas; `git check-ignore .local_backups/card-1071-harmless-probe` positivo | Probe foi apenas path consultado, sem criação; histórico continua pendente |
| `https://dev.criptofarol.com.br/api/health` | HTTP 200, `status=ok`, serviço esperado | Saúde básica não valida login ou revogação |
| `https://dev.criptofarol.com.br/login` | HTTP 200, HTML com assets do bundle | Página servida; login autenticado não executado |
| `/api/auth/me` sem autenticação | HTTP 401 esperado | Rejeição de acesso anônimo, sem prova de token antigo rejeitado ou login válido |
| Banco da aplicação | PostgreSQL, `SELECT 1` PASS, nome esperado `crypto_app_dev` confirmado por booleano | Sem comparação de credenciais históricas/vigentes |
| Banco workflow | PostgreSQL, `SELECT 1` PASS | Sem leitura de linhas ou confirmação de rotação |
| Backend/frontend | `active/running`, `Result=success` | Arranques observados 14:27:57 / 14:26:27 UTC |
| Runtime/discovery workers | `active/running`, `Result=success` | Arranques observados 14:28:03 / 14:27:57 UTC; nenhum job financeiro disparado |
| Candle writer | serviço `inactive/dead`, `Result=success`; timer `active/waiting` | Última execução 14:27:39 UTC; não reiniciado por este QA |
| Telegram alert scan | serviço `failed`, `Result=exit-code`, status 1; timer `active/waiting` | Arranque 11:05:04 UTC, anterior à integração/restart; funcionamento não comprovado; sem leitura de logs brutos ou nova execução |
| Login válido de conta controlada | não executado; dispensado por Alan em 2026-10-13 para o smoke QA de 4.2 | Canal protegido não disponibilizado; não criada nem substituída conta; autenticação válida não comprovada |

## Continuação QA — 2026-10-13 UTC

O pedido de conclusão retomou somente verificações DEV e artefatos de processo. O checkout canônico continua limpo em `99a3070cd9d117539fe6de734361f07d5e1c4611`; backup permanece não rastreado e probe de ignore positivo. Às 01:16:07 UTC, health público e página login responderam HTTP 200 e `/api/auth/me` sem autenticação retornou HTTP 401 esperado. Às 01:16:48 UTC, PostgreSQL aplicação/workflow passaram novamente em `SELECT 1`, com alvo `crypto_app_dev` confirmado em memória. Backend, frontend e workers runtime/discovery permanecem `active/running`, `Result=success`.

### Telegram: isolamento esperado comprovado

O scanner é um oneshot diário às 11:05 UTC, não um daemon. O `failed/exit 1` observado em 2026-10-12 11:05:04 UTC é o resultado do último disparo; timer `active/waiting`, próximo disparo 2026-10-13 11:05 UTC. O unit efetivo tem `CRYPTO_TELEGRAM_ALERT_SCAN_BLOCK_PROD_BOT=1`. O [contrato Telegram](../../../docs/monitor-telegram-alerts.md) descreve expressamente que esse guard em DEV retorna `CONFIG_INCOMPLETE` sem chamar o bot PROD.

Journal consultado read-only, capturado em diretório local restrito 0700 com arquivos 0600, fora do Git. Resumo por allowlist: seis registros, dois eventos `DEV_ISOLATION`, um `CONFIG_INCOMPLETE`, zero `SENT`, `FAILED` ou traceback. Nenhuma mensagem bruta, token, usuário, destino ou conteúdo de alerta foi exportado.

Smoke seguro: execução direta do wrapper versionado `ops/run_monitor_telegram_alert_scan.py`, com o mesmo flag de isolamento explicitamente ativo, confirmou exit 1 e a resposta fixa esperada `CONFIG_INCOMPLETE: DEV_ISOLATION blocked PROD bot token_configured=False eligible_users=0`, stderr vazio. Esse ramo termina antes de importar banco/scanner ou alcançar Bot API; nenhum envio ou alteração de configuração ocorreu. Não foi iniciado o service/timer, instalado bot ou executado scan de entrega.

Conclusão: barreira DEV funcional e estado antigo intencional, anterior a #1071; não é falha de implementação deste card nem impedimento adicional de 4.2. A entrega real de Telegram em DEV continua não testada e não é inferida a partir do smoke de isolamento.

### Login: histórico da busca, procedimento e dispensa localizada

Busca realizada em docs, scripts, testes, artifacts OpenSpec e configuração canônica, sem exibir valores de credenciais ou identidades. `docs/beta-e2e-validation-2026-05-13.md` registra um usuário QA local histórico; não fornece senha/canal protegido vigente. O banco DEV contém uma identidade sintética com prefixo de teste e domínio reservado `example.com`, ativa/não banida, mas ela não corresponde a nenhum procedimento ou registro nos docs/scripts/archive consultados. Ela não foi utilizada nem alterada. Dotenv raiz/backend e ambiente do processo não têm chaves provisionadas QA/E2E/SMOKE/TEST_USER/TEST_EMAIL/TEST_PASSWORD; nenhum arquivo de credencial QA reconhecido foi encontrado nos locais padrão consultados.

A fixture `auth_db_session` em `backend/tests/unit/test_database_and_auth.py` usa banco de testes isolado e verificação/senha mockadas; os guards de `backend/tests/conftest.py` e `backend/tests/unit/conftest.py` impedem transplantar sua limpeza/reset para o banco runtime DEV. O contrato atual exige convite para registro público e impede remoção física de usuários. Portanto, os testes não fornecem um provisionador runtime temporário reversível autorizado; nenhuma conta foi criada por bypass, senha redefinida, convite emitido ou usuário real usado.

Dado mínimo solicitado pelo pai a Alan antes da dispensa: **caminho de arquivo protegido ou procedimento vigente que forneça identidade QA reconhecida e sua credencial de login DEV**. Não enviar senha/token no chat, Git ou CI. O arquivo deve ter custódia reconhecida e acesso restrito; identidade de teste deve ser explicitamente identificada, sem credencial pessoal.

Procedimento preparado para eventual validação futura: conferir identidade, permissões do canal e alvo DEV; carregar credencial somente em memória; chamar `/api/auth/login`; manter tokens somente em memória; comprovar HTTP 200 e identidade correspondente em `/api/auth/me`; verificar renovação em `/api/auth/refresh` e sessão renovada; emitir apenas booleanos/status/resultados, sem corpo de resposta, identidade, senha ou token; descartar os valores em memória ao fim. Falha deve ser registrada por etapa/status, sem erro bruto. Esse procedimento não foi executado e não exige redefinir senha, ler variantes históricas ou disparar ações financeiras/mensagens.

**Dispensa explícita:** em 2026-10-13, Alan respondeu **“ignore isso”** à pendência exclusiva do teste de login QA. O pai registrou esse contexto na continuação deste filho. A dispensa localizada permite marcar 4.2 concluída com os demais checks já comprovados, preservando a ausência de prova de login/sessão válida. Não é dispensa de QA visual (que passou), de testes de segurança/invalidação de JWT, Binance ou banco, de continuidade PROD, de gates humanos ou de release. Nenhuma dessas obrigações foi encerrada por essa resposta.

## Residual já no card

Preservado integralmente do [comentário 6126046157](https://github.com/oalansilva/crypto/issues/1071#issuecomment-6126046157), sem nova classificação ou ciclo:

P2 — mecanico — scripts/secret-remediation/rehearsal.py:13: ambiente Git herdado pode atingir worktree real. subprocess.run herda GIT_WORK_TREE; definir essa variável para checkout real permite que comandos git add, checkout e stash operem nessa árvore apesar do cwd sintético. Correção indicada pelo reviewer: remover variáveis que redirecionam Git de todos os subprocessos e testar com árvore externa sentinela. Residual preservado sem reclassificação após o teto 1+1; não houve terceiro ciclo. O ensaio deve ser executado com ambiente Git neutro enquanto esta limitação persistir.

O ensaio CI já verde não foi repetido nesta continuação. Review final e fechamento contra `origin/develop` reutilizaram o mesmo SHA-256 exato do patch revisado; nenhuma mudança de produto foi adicionada pelo QA.

## Registro operacional até Pronto

O [runbook](../../../docs/security/card-1071-runbook.md), o [inventário](../../../docs/security/card-1071-inventory.json) e a [evidência qualificada](../../../docs/security/card-1071-evidence.md) continuam válidos. Inventário e coleta anterior permanecem incompletos; contagens são observações anteriores, sem nova recoleta ou declaração de cobertura completa. Bruto e cópia pericial restritos permanecem fora do Git, sob custódia do operador, sem destruição automática.

| Obrigação | Estado | Responsável | Condição para comprovar |
| --- | --- | --- | --- |
| Contenção de visibilidade | pendente | Alan | Visibilidade privada verificada no provedor; não comprova revogação |
| Cobertura e classificação de cada alerta | pendente | Operador/donos | Clone completo, recoleta corrigida e fontes revisadas; zero indeterminado e falsos positivos/publicidade justificados |
| Binance histórica DEV/PROD | pendente | Alan/operador | Cada par invalidado por prova autoritativa ou teste conclusivo; par válido funcional |
| JWT histórico DEV/PROD | pendente | Operador | Access/refresh antigos não expirados rejeitados, equivalentes novos e login aceitos; todos consumidores recarregados |
| Banco histórico DEV/PROD | pendente | Operador | Endpoint/roles mapeados, senha antiga invalidada, nova conexão válida e sessões tratadas; `SELECT 1` atual sozinho não encerra |
| Outros segredos/variantes não obtidas | pendente | Operador/dono | Matriz expandida e prova completa de invalidação por variante |
| Backup/dados sensíveis | pendente | Operador/proprietário | Classificação semântica completa, retenção/tratamento e remoção histórica autorizada |
| QA/continuidade DEV de 4.2 | comprovado com dispensa localizada | Pai/QA/operador | CI/visual, integração/restart, saúde, bancos, workers e isolamento Telegram comprovados; teste de login QA não executado, dispensado por Alan em 2026-10-13; obrigações de segurança/PROD permanecem nas demais linhas |
| Homologação e release | pendente | Alan/pai | Gates humanos e pedido explícito no fluxo existente |
| Freeze/preservação do trabalho real | pendente | Operador/donos | Janela e mapa privado completos; cópia cifrada/restaurada conferida por cada dono |
| Rewrite/publicação global | pendente | Operador/Alan | Invalidação completa anterior, homologação/release, autorização concreta de refs/proteções/leases e validação pré-push |
| PR refs/caches/anexos/LFS | pendente | Operador/provedor | Resolução comprovada; falta de acesso ou recusa continua bloqueio visível |
| Recuperação/proteções/não recontaminação | pendente | Operador/donos | Clone independente limpo, trabalho saneado reaplicado, proteções/automações restauradas |
| PROD/fecho/Pronto | pendente | Operador/pai | Deploy/hooks e testes conclusivos PROD; todas obrigações comprovadas; guards PASS/T16 |

Próximo passo humano: Alan homologar em `develop` pelo fluxo existente. O operador conclui as pendências de continuidade e as obrigações antes de Pronto. Falha de credencial nova recupera com outra inédita ou componente pausado; nunca restaurar segredo, backup investigado ou ref contaminada. Cópias externas de terceiros ficam fora da garantia de eliminação.
