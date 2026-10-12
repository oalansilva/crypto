# #1071 — remediação de segredos históricos

Esta entrega prepara o procedimento, inventaria fontes disponíveis e retira o backup do versionamento. Resultado operacional permanece **incompleto**. Inventário, configuração diferente, ignore, visibilidade privada e scanner sem achados não comprovam revogação. A limpeza histórica global pertence a este card e deve ocorrer depois de invalidação completa, homologação e release solicitada.

## Responsabilidade e autorização

| Etapa | Responsável | Evidência/autorização necessária |
| --- | --- | --- |
| Coleta local/read-only e higiene do tip | Apply/operador | Design aprovado; apenas fontes autorizadas; bruto restrito |
| Visibilidade e credenciais Binance | Alan | Ação concreta de Alan e prova do provedor; Design não altera visibilidade |
| Comparação com configuração carregada | Operador | Acesso autorizado ao ambiente; recusa não será contornada |
| Invalidação, configuração e restart por ambiente | Operador autorizado/Alan | Operação concreta e janela definidas; sem autorização neste Apply |
| Freeze, proteções, publicação de refs enumeradas | Operador/Alan/donos | Invalidação completa, mapa final, homologação, release explícita e autorização irreversível concreta |
| QA, integração, Done e Pronto | Pai | Fluxo existente, checks/guards e provas de cada etapa; agente não move gates humanos |

Não há autorização nesta etapa para rotação DEV/PROD, acesso a configuração protegida antes recusado, mudança de visibilidade, rewrite real, mudança de proteções ou force-push. O operador deve confrontar o registro de pendências em [card-1071-evidence.md](card-1071-evidence.md) com os relatórios allowlisted antes de cada operação.

## Armazenamento e coleta

Operador mantém bruto fora de qualquer checkout, em diretório privado 0700, arquivos 0600 e backup pericial 0400. O armazenamento deve permanecer protegido, sem sincronização pública e acessível só à conta operadora. Responsável: operador da VM. Retenção: quarentena até Pronto e revisão explícita de Alan; nenhuma destruição automática. Cópias destinadas à recuperação/retenção longa devem ser cifradas com chave separada sob custódia do operador. Não executar `set -x`, imprimir env, cat/diff/show de conteúdo comprometido, subir bruto ao CI/Drive público ou enviar material a scanner remoto.

Ferramenta fixada: **Gitleaks 8.24.3**, configuração `scripts/secret-remediation/gitleaks.toml` (regras padrão dessa versão + nomes conhecidos/URL de banco). Instalador verifica checksum do release oficial, recusa arquitetura/plataforma desconhecida e nunca extrai paths arbitrários do tar. O checksum aqui é do software, nunca de segredo. Não usar baseline, supressões do repositório, configuração via env ou `gitleaks:allow` para esconder achados do incidente. A versão/configuração precisam ser novamente aprovadas caso mudem.

Exemplo de instalação em diretório novo e privado fora do Git:

```bash
python3 scripts/secret-remediation/install_scanner.py --restricted-root /CAMINHO/PRIVADO/tools-1071
```

Antes de coletar, executar a fixture que deve produzir achados. O CI roda **somente fixtures sintéticas e o ensaio**, nunca o inventário real:

```bash
CARD1071_GITLEAKS=/CAMINHO/PRIVADO/tools-1071/gitleaks python3 -m pytest -q -c /dev/null -p no:cacheprovider scripts/secret-remediation
```

Coleta read-only; cada rodada usa diretório novo. `--remote` somente enumera refs/API, sem fetch/escrita no Git compartilhado:

```bash
python3 scripts/secret-remediation/inventory.py \
  --repo /CAMINHO/WORKTREE/card-1071-segredos-historico \
  --restricted-root /CAMINHO/PRIVADO/inventory-RODADA \
  --scanner /CAMINHO/PRIVADO/tools-1071/gitleaks \
  --backup /CAMINHO/WORKTREE/card-1071-segredos-historico/.local_backups/backtest.db.bak.20260224T134424Z \
  --remote
```

Captura `git --log-opts="--all --full-history -m" --redact=100`, snapshot do conteúdo atualmente rastreado e mensagens de commits. Cada scan usa `--gitleaks-ignore-path` apontando para arquivo vazio 0600 e cwd restrito. Gitleaks 8.24.3 também carrega `source/.gitleaksignore` independentemente dessa flag: o scan Git usa diretório neutro 0700 com gitfile restrito referenciando o Git original, sem alterar refs/configuração; scans de diretório exigem snapshots neutros e recusam fonte com `.gitleaksignore`, marcando incompleto. Logs, JSON original, mapa de refs/SHAs, versões conhecidas e schema ficam restritos. Histórico disponível não equivale a clone completo do provedor. Snapshot usa nomes opacos e verifica symlinks em todos os componentes entre worktree e arquivo; arquivos faltantes/symlinks tornam a etapa incompleta e não são copiados. Shallow, falha de scanner, JSON inválido e código inesperado nunca produzem resultado limpo. Saída 0 significa execução da coleta; `overall=incomplete` e pendências continuam vinculantes. Saída 2 sinaliza falha de coleta/scanner/backup. `no_findings` vale somente para aquela fonte, nunca para o incidente.

Somente `evidence.json`, construído com vocabulário fechado, pode ser candidato à publicação. Não copiar JSON/log original: `--redact=100` sozinho é insuficiente. IDs sequenciais apontam para alertas originais apenas pelo mapa privado; nomes arbitrários de rules, caminhos, mensagens, fingerprints, hashes de segredo e linhas nunca são exportados. Arquivos de implementação/relatórios devem passar por comparação local em memória com todos os valores conhecidos antes de revisão. Esta comparação não consulta configuração DEV/PROD.

## Cobertura e classificação

Cobrir branches/tags locais/remotas, PRs abertos/fechados e `refs/pull/*`; comparar o mapa remoto com objetos realmente obtidos em clone dedicado. Classificar aliases/renames dos arquivos conhecidos e ocorrências em arquivos preservados, blobs binários, mensagens de commits/tags e configuração atual. Inventariar worktrees com commits, staged, unstaged, untracked, stashes/reflogs; conteúdo adicional exige coleta privada por dono. Enumerar releases/anexos, Actions artifacts/logs/caches e LFS; metadado coletado não prova payload examinado. Conteúdo remoto não local, logs/payloads, refs internas e caches não verificáveis têm pendência por fonte/responsável. Acesso negado registra bloqueio, sem contorno.

Cada alerta em `card-1071-inventory.json` tem classificação conservadora `possivel_segredo` e responsável operador. Até revisão controlada, continua pendente. O operador agrupa versões iguais por comparação em memória, associa serviço/ambiente e registra falso positivo/configuração pública com justificativa fixa e verificável. `VITE_API_URL` é candidato a configuração pública, não prova por nome. Nenhum possível segredo vira inofensivo por falta de prova.

O backup é copiado antes da remoção do índice e aberto por SQLite `mode=ro&immutable=1`, `query_only=ON`, `trusted_schema=OFF`, extensões desligadas. Nenhum SQL dos dados ou aplicação contida é executado. São examinadas todas as células de todas as colunas/tabelas normais, inclusive texto/JSON/BLOB. Tabelas virtuais são recusadas; objetos adicionais e falhas permanecem registrados. SQLite é perícia deste arquivo, nunca runtime/QA do produto. Categorias numéricas/null/vazio descrevem somente tipo; texto/JSON/binário e candidatos de credencial/dado pessoal exigem análise semântica, proprietário e tratamento. Regex não prova ausência de dados sensíveis. Remoção do índice não elimina a cópia restrita nem o histórico.

Depois de conferir preservação read-only e classificação, remover `.local_backups/` do índice preservando a cópia, adicionar ignore ancorado e validar em checkout descartável que `git add .` não adiciona probe inofensivo. Não restaurar esse backup no runtime, refazer #687 ou alterar o loader de configuração.

## Matriz de invalidação e continuidade

Cada ID de alerta é uma obrigação de triagem e invalidação até classificação conclusiva. Matriz abaixo aplica-se a **cada variante histórica relevante** identificada pelo mapa privado; aplicar a DEV e PROD separadamente. Estado inicial de todos os IDs: pendente; aplicabilidade a cada ambiente: indeterminada; nenhuma revogação comprovada neste Apply. O operador registra data, prova e resultado por ID/ambiente, sem valores ou retorno de conta.

| Serviço/chave | DEV | PROD | Responsável | Prova exigida e condição de fechamento |
| --- | --- | --- | --- | --- |
| Binance — todos os pares históricos | pendente | pendente | Alan/operador | Revogação autoritativa de cada par ou rejeição antiga conclusiva, par vigente funcional |
| JWT_SECRET — todas as variantes | pendente | pendente | Operador | Access e refresh antigos não expirados rejeitados; equivalentes novos e login aceitos; todos os validadores recarregados |
| DATABASE_URL/WORKFLOW_DATABASE_URL | pendente | pendente | Operador | Separar URL pública/senha; rejeição antiga contra endpoint/role correto, nova conexão válida e sessões antigas tratadas |
| Outros IDs de possível segredo | pendente | pendente | Operador/dono do serviço | Classificação e prova autoritativa ou teste conclusivo; mapear todas as versões/consumidores |
| Backup e dados pessoais/sensíveis | pendente | pendente | Operador/proprietário dos dados | Análise semântica de todos os alertas, retenção/tratamento e remoção histórica autorizada |

Comparação em memória de valores histórico × configuração **efetivamente carregada** produz apenas igual/diferente/ausente/indeterminado. Configuração protegida não lida continua indeterminada; arquivo novo com valor diferente não comprova invalidação. Confirmar origem real da configuração e consumidores sem imprimir systemd env, `/proc/*/environ` ou dados de banco. DEV usa `crypto_app_dev`; PROD usa `crypto_app`; fonte e serviços vêm de `.covenant-flow/overlay.yaml` e da skill de ambientes.

**Binance:** Alan revoga pares expostos e cria outro quando necessário com permissões mínimas. Operador instala pelo canal protegido; usa somente consulta autenticada não financeira e conta controlada. Não executar ordens, saques ou jobs financeiros. Distinguir erro de credencial revogada de rede/IP/permissões; quando teste antigo não for viável, exigir comprovação autoritativa. Emitir apenas resultado; sem retorno de conta no log.

**JWT:** preservar o fail-closed de #684. Conta de teste controlada e claims equivalentes; criar em memória token access e refresh com prazo ainda válido usando cada variante antiga. Testar `/api/auth/me` e `/api/auth/refresh`: antigo rejeitado por validação/assinatura, token novo aceito. Testar `/api/auth/login` e refresh novo. Token antigo apenas expirado rejeitado não conta. Reiniciar todos os signatários/validadores e trabalhadores consumidores definidos no overlay, sem fallback para chave antiga. Usuários fazem login novamente.

**PostgreSQL:** mapear roles e todos os consumidores de ambas as URLs, inclusive workers/migrações/workflow. Conectar antiga e nova somente ao endpoint previsto, com timeout curto e `SELECT 1`; nenhuma linha de produto retornada. Invalidar role/senha antiga quando ainda válida, atualizar consumidores protegidos, tratar conexões antigas pertinentes e testar nova aceitação + antiga rejeição de autenticação. Falha de rede não é rejeição conclusiva. Nenhuma migração destrutiva.

Falha da nova credencial: corrigir canal/permissão, emitir outra inédita válida ou pausar componente; jamais restaurar valor comprometido. Após integração/QA, pai/operador executa `./restart` no DEV canônico e smoke em `https://dev.criptofarol.com.br` (health, login, banco e serviço necessário sem operação financeira). CI/visual/restart/smoke continuam tarefas after-qa. PROD somente na janela autorizada; respeitar serviços e oneshots do overlay.

## Freeze e recuperação antes de rewrite real

1. Completar classificação e invalidação de **todos** os segredos; ausência de prova bloqueia rewrite. Confirmar visibilidade privada por Alan sem assumir contenção de clones existentes.
2. Depois de Done + homologação e release explícita, publicar pacote funcional homologado/deploy PROD pelo fluxo normal e guards. Freeze definitivo captura refs finais após isso; não introduzir funcionalidade não homologada em `main` por manutenção histórica.
3. Operador/donos combinam janela e suspendem pushes, merges, deploys e jobs que alterem refs. Registrar em armazenamento protegido cada `ref → SHA antigo → SHA novo → ação → dono`, tags/assinaturas, automações, PRs/releases e snapshot das proteções/rulesets. Ref desconhecida impede publicação. Branch em andamento tem preservação explícita, mesmo fora do pacote.
4. Inventariar trabalho commitado, staged, unstaged, untracked e stash em **cada** worktree. Fazer bundle de refs e arquivos/patches privados separados, cifrar fora do Git com chave em custódia separada, restaurar em diretório isolado e conferir bytes/resultados com o dono. Bundle sozinho não guarda trabalho não commitado. Quarentena contaminada não é patch saneado e nunca será publicada como `backup/*`. Não apagar worktrees nem cópias sem autorização própria.
5. Criar clone completo novo dedicado, fora dos sources DEV/PROD e do Git compartilhado dos worktrees. Obter/comparar todas as refs autorizadas. Stashes ficam na recuperação privada, não importados como `refs/stash` no clone de rewrite; gate de fresh-clone deve passar. Falha é parada: não usar `--force`.

`git-filter-repo` mínimo **2.47**, ensaio fixado em **2.47.0**. Remover paths conhecidos e aliases por `--sensitive-data-removal --invert-paths --path ...`, incluindo backup binário integral; conteúdo preservado usa `--replace-text`, mensagens de commits/tags usam `--replace-message`. Expressões/valores ficam somente em arquivo restrito, nunca args literais, repositório ou transcript. Confirmar cobertura de binários, mensagens e tags; procurar valores/blobs conhecidos localmente em memória. Guardar mapas resultantes restritos; SHAs que apontam material exposto não são evidência pública.

Ensaio que cria exclusivamente repositórios sintéticos e nunca aceita caminho de repositório real:

```bash
python3 scripts/secret-remediation/rehearsal.py \
  --filter-repo /CAMINHO/PRIVADO/tools/bin/git-filter-repo \
  --restricted-root /CAMINHO/PRIVADO/rehearsal-RODADA
```

Antes da publicação, comparar árvores de cada tip ao esperado (apenas remoções/substituições aprovadas), refs antigas/novas, branches preservadas e mapas de base limpa. Rodar scanner em todas as refs reescritas, busca exata privada de valores/blobs conhecidos, ausência de paths sensíveis, `git fsck --full` e testes pertinentes. Tratar assinaturas inválidas/tags e referências de automações. Novo achado retorna à classificação/invalidação. Diff inesperado, recuperação não testada, fonte incompleta ou ref sem dono cancela a publicação.

## Publicação e validação independente

Alan recebe mapa final privado, provas, refs afetadas, janela e alterações temporárias mínimas de proteção; precisa autorizar concretamente publicação irreversível/proteções. Design aprovado não basta. Reconsultar remoto imediatamente antes; SHA diferente do antigo esperado aborta. Publicar somente refs enumeradas com expectativas explícitas dos SHAs antigos (leases) e tentativa atômica se suportada; nunca `push --mirror` indiscriminado. Manter congelamento e restaurar/verificar proteções mesmo em falha parcial; reconciliar a partir do mapa validado e avançar apenas com história limpa. Nunca voltar refs à história contaminada nem desligar CI.

Clonar o remoto novamente, de modo independente, conferir cobertura refs/tags/PRs, repetir scanner/busca exata privada e comparar árvores/SHAs. Inventariar PR refs read-only, caches, anexos/releases, LFS e artifacts/logs; remover apenas elementos controláveis autorizados. Suporte do provedor usa canal autorizado e metadados mínimos; não enviar bruto pelo card. Cache/ref ainda acessível ou recusa sem resolução permanece bloqueio de Pronto. Não prometer apagar clones/forks de terceiros.

Recriar clones controlados ou reaplicar **somente trabalho pendente saneado** sobre bases limpas mapeadas, após conferir recuperação com o dono. Nunca `merge`/`pull` da história antiga. Não resetar worktree suja. Revisar/rescannar patches; testar antes de push, atualizar/reabrir PRs e CI, confirmar proteções/automações e ausência de recontaminação antes de liberar freeze. Aplicação pode voltar a conteúdo funcional anterior saneado com credencial nova; não restaurar backup investigado no runtime.

PROD: checkout canônico, migração/build/restart dos hooks do overlay, sem restart de oneshots por simetria. Verificar health público, autenticação antiga rejeitada/nova aceita, banco e consumidores. Revalidar provas após SHAs mudarem. Sync normal `main → develop` usa só história limpa; archive, Kaizen, branches preservadas e `release-guard pre/post` seguem runbook existente. Pronto exige todas as obrigações comprovadas e pai no T16; merge isolado não é prova.

Referências primárias: [Gitleaks 8.24.3](https://github.com/gitleaks/gitleaks/tree/v8.24.3), [git-filter-repo 2.47.0](https://github.com/newren/git-filter-repo/blob/v2.47.0/Documentation/git-filter-repo.txt), [GitHub: dados sensíveis e caches/PR refs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
