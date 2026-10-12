# #1071 — evidência sanitizada do Apply (2026-10-12 UTC)

Estado operacional: **incompleto**. Nenhuma revogação, contenção de visibilidade, comparação com configuração efetivamente carregada, operação PROD ou reescrita real comprovada nesta etapa. Este registro e a matriz acompanham #1071 até Pronto, inclusive após archive. Não encerrar pendências apenas porque a preparação/implementação está marcada no OpenSpec.

Contrato: [runbook](card-1071-runbook.md). Evidência de vocabulário fechado e matriz: [inventário](card-1071-inventory.json). Mapeamentos de valores/refs/SHAs, scanner JSON/stdout/stderr e schema estão em armazenamento restrito fora do Git (0700/0600); backup pericial preservado read-only (0400). Responsável por custódia/retensão: operador da VM; revisar retenção com Alan no fechamento, sem destruição automática.

## Cobertura obtida

| Fonte | Resultado | Limite |
| --- | --- | --- |
| Refs locais | 119 enumeradas; scanner `--all` | Checkout shallow: histórico anterior não comprovado |
| Árvore rastreada | 4.991 entradas enumeradas na rodada anterior à remoção do backup | Snapshot anterior não verificava symlinks ancestrais; cobertura incompleta até recoleta corrigida; untracked adicional exige revisão |
| Histórico disponível | 1.269 alertas observados na coleta anterior | IDs `history-000001` a `history-001269`: todos pendentes, operador; total pode omitir fingerprints ignorados, não comprova cobertura completa nem segredos distintos |
| Conteúdo rastreado | 218 alertas observados na coleta anterior | IDs `tracked_content-000001` a `tracked_content-000218`: todos pendentes, operador; fingerprints ignorados e symlinks ancestrais não excluídos; fixtures/falsos positivos a classificar |
| Mensagens de commits disponíveis | Scanner anterior terminou, zero alertas observados | Estado incompleto: suppressions herdadas não excluídas; ausência não comprovada; tags e metadados de paths/refs têm revisão pendente |
| Versões dos três arquivos conhecidos | Cinco nomes de configuração encontrados; quatro variantes candidatas de credencial identificadas localmente | Aliases/renames e fontes não obtidas continuam pendentes; nenhuma comparação DEV/PROD executada |
| Remoto | 743 refs anunciadas, 141 objetos ausentes do checkout | Conteúdo de refs/PRs faltantes exige clone completo dedicado, sem alterar Git dos worktrees |
| PRs/releases | 663 PRs e 9 releases enumerados via API read-only | Metadados não comprovam payloads, anexos/caches examinados |
| Actions | 5.982 artifacts, 2.613 runs e 7 caches enumerados | Conteúdo de arquivos/logs/cache não examinado; operador deve classificar/tratar |
| Worktrees/stash/reflogs | 41 worktrees, nenhum stash atual, 2.608 entradas de reflog e 29.926 objetos enumerados | Conteúdo local de outros worktrees e reflog-only não examinado; cada dono participa da recuperação |
| LFS | Coleta incompleta | Ferramenta/acesso indisponível nesta rodada; payloads não comprovados |
| Configuração DEV/PROD | Não comparada | Permanece indeterminada; leitura antes recusada não contornada |

Coleta original executada com código 0 (execução), `overall=incomplete`, todos os scanners terminaram. A correção pós-review qualifica os três scans como `incomplete`: o coletor anterior não excluía suppressions de fingerprints e verificava apenas o componente final do snapshot. Contagens e faixas originais foram preservadas como observações para não perder as pendências existentes; não constituem totais completos. Recoleta corrigida dessas fontes permanece pendente, responsável operador, sem repetir nesta correção o inventário remoto/backup inteiro. Gitleaks 8.24.3 ARM64 verificado pelo checksum oficial, configuração padrão da versão + regras conhecidas/URL, sem baseline. SHA de software serve só à verificação local do binário; nenhum valor, hash/fingerprint de segredo, linha, path dinâmico ou saída original foi publicado.

Cada ID das faixas acima recebeu explicitamente `possivel_segredo`, dono operador, aplicabilidade de ambiente indeterminada e invalidação DEV/PROD pendente. A matriz JSON contém oito linhas para as quatro variantes locais conhecidas × DEV/PROD (`VAR-*`), sem valores. O mapa privado associa essas linhas às versões originais. `VITE_API_URL` é configuração pública **a confirmar**. Nenhum alerta indeterminado pode ser ignorado para Pronto.

## Backup e prevenção de republicação

Cópia preservada fora do Git, leitura imutável/read-only, extensões desabilitadas e schema não confiável. Todas as células de 5 tabelas, 59 colunas e 80 linhas foram examinadas pelo classificador. Categorias agregadas: 187 numéricas, 140 null, 511 texto pendente e 160 JSON pendente. Sete objetos adicionais de schema foram enumerados. Esses resultados não encerram análise semântica, dados pessoais/estratégias/valores embutidos ou retenção; todas as colunas/tabelas têm pendência atribuída ao operador no JSON.

Arquivo removido do worktree e índice após preservação; ignore ancorado `/.local_backups/`. `git check-ignore` passou no worktree e em repositório descartável; `git add .` habitual no descartável não incluiu probe inofensivo. Índice entregue sem `.local_backups/`; cópia restrita permanece 0400. Nenhuma história real foi reescrita e o backup continua em versões anteriores/refs remotas até manutenção autorizada.

## Verificações da implementação

- Fixtures sintéticas cobrem exportação por allowlist, nomes/caminhos/mensagens/erro hostis, exit status inconsistente, falha operacional, JSON inválido, armazenamento inseguro/symlink/Git e inspeção de texto/JSON/BLOB de backup. Integração usa a versão real fixada e deve encontrar candidatos sintéticos.
- Ensaio `git-filter-repo 2.47.0` exclusivamente sintético: bundle e cópia cifrada restaurável; staged/unstaged/untracked/stash preservados; branches/tags e commits pendentes preservados; paths, blobs e mensagens removidos; `git fsck --full`; clone limpo independente e trabalho pendente reaplicado sobre base limpa. Nenhuma ref real modificada.
- Comparação privada em memória contra as quatro variantes locais conhecidas: zero ocorrências nos artefatos de implementação verificados. Isso não compara nem valida configuração carregada dos ambientes.
- CI `process-fsm` inclui somente testes e ensaio sintéticos desta ferramenta; não coleta Git real nem bruto no CI público. QA padrão/visual e restart/smoke DEV seguem after-qa.

Validação do Apply original: **21 testes passaram**, incluindo integração com scanner real fixado; ensaio sintético completo PASS; OpenSpec estrito PASS; Black (quatro arquivos Python), compilação Python, YAML/contrato de CI sintético, `git diff --check` e ignore/probe PASS. Dez artefatos comparados em memória com quatro variantes locais conhecidas: zero ocorrências. Permissões do bruto conferidas: diretórios 0700, arquivos 0600, backup 0400.

Correção única pós-review dos dois P2 mecânicos: arquivo vazio 0600 explícito por scan; cwd restrito; fonte Git neutra com gitfile para impedir carga incondicional do ignore na fonte; fonte de diretório com ignore recusada. Essa carga adicional da versão fixada está no [código oficial do Gitleaks 8.24.3](https://github.com/gitleaks/gitleaks/blob/v8.24.3/cmd/root.go#L226-L246). Snapshot recusa symlink no componente final ou em qualquer ancestral até o worktree e marca `tracked_content=incomplete`. Fixtures reais reproduzem supressão padrão de fingerprints em worktree Git e cwd de diretório e confirmam detecção pelo coletor corrigido; fixture adicional comprova recusa de ignore na fonte, e fixtures sintéticas comprovam que links finais/ancestrais externos não são copiados. Checks após correção: **26 testes passaram**, sem skips; Black, compilação Python, OpenSpec estrito pela instalação local e `git diff --check` PASS; comparação privada de 14 artefatos entregues contra as quatro variantes conhecidas: zero ocorrências. Nenhuma coleta real nova, revogação ou cobertura completa foi declarada. Antes de revisão/commit, pai materializa diff sem payload binário do backup removido.

## Pendências operacionais impeditivas de Pronto

| Obrigação | Estado | Responsável | Condição de fechamento |
| --- | --- | --- | --- |
| Visibilidade privada | pendente | Alan | Estado verificado no provedor; não comprova revogação |
| Cobertura e classificação de cada alerta | pendente | Operador/donos | Clone completo, fontes acima revisadas, zero indeterminado e falsos positivos/publicidade justificados |
| Binance histórica, DEV/PROD | pendente | Alan/operador | Cada par invalidado por prova autoritativa ou teste conclusivo e par válido funcional |
| JWT histórico, DEV/PROD | pendente | Operador | Access/refresh antigos ainda válidos rejeitados; novos e login aceitos; todos consumidores recarregados |
| Banco histórico, DEV/PROD | pendente | Operador | Endpoint/roles mapeados, senha antiga invalidada, nova conexão válida e sessões tratadas |
| Outros segredos e variantes não obtidas | pendente | Operador/dono | Matriz expandida por variante e prova completa de invalidação |
| Conteúdo do backup/dados sensíveis | pendente | Operador/proprietário | Classificação semântica completa, retenção/tratamento e remoção histórica autorizada |
| QA/continuidade DEV | pendente | Pai/QA/operador | CI/visual padrão, integração, restart DEV e smoke sanitizado de login/banco/serviço necessário |
| Homologação e release | pendente | Alan/pai | Gates humanos e pedido explícito no fluxo existente |
| Freeze/preservação do trabalho real | pendente | Operador/donos | Janela e mapa privado completos, cópia cifrada/restaurada conferida por cada dono |
| Rewrite/publicação global | pendente | Operador/Alan | Invalidação completa anterior; homologação/release; autorização concreta de refs/proteções/leases; validação pré-push |
| PR refs/caches/anexos/LFS | pendente | Operador/provedor | Resolução comprovada; falta de acesso ou recusa continua bloqueio visível |
| Recuperação/proteções/não recontaminação | pendente | Operador/donos | Clone independente limpo, trabalho saneado reaplicado, proteções/automações restauradas |
| PROD/fecho | pendente | Operador/pai | Deploy/hooks e testes conclusivos PROD; todas as obrigações comprovadas; guards PASS/T16 |

Falha da credencial nova recupera com outra inédita ou componente pausado. Falha parcial da publicação mantém freeze, restaura proteções e corrige para frente pela história limpa. Nunca restaurar segredo, backup investigado ou ref contaminada. Cópias externas de terceiros ficam fora de qualquer garantia de eliminação.
