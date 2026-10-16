## Context

#1071 em Design. `proposal.md` preserva o briefing do issue. Repositório público; `.env.binance`, `backend/.env` e `frontend/.env` conhecidos no histórico; backup `.local_backups/backtest.db.bak.20260224T134424Z` no tip. Comparação histórico × configuração DEV/PROD não realizada; não há comprovação de rotação. Schema do backup não classifica suas linhas. Este Design não lê segredos nem executa contenção, rotação, rewrite ou release.

UI impact: none
live_route: N/A — remediação de segredos e higiene Git, sem superfície de produto.
surface: none

Prototype: N/A — operação Git/configuração, sem tela.
Impeccable: N/A — nenhuma interface criada ou alterada.
HTML generated: N/A
HTML copied: N/A

## Goals / Non-Goals

**Goals:** comprovar invalidação de cada segredo exposto; configuração válida distinta dos valores históricos; retirar backup e material sensível do tip e da história publicada controlada; preservar trabalho pendente e demonstrar continuidade DEV/PROD.

**Non-Goals:** refazer #684/#687, cifrar credenciais em repouso (#692), reabrir visibilidade pública ou garantir eliminação de cópias externas. Os limites históricos de #687 valem para aquela entrega; esta capacidade adiciona a remediação aceita por Alan.

## Decisions

### 1. Separar implementação DEV da operação global

O Apply entrega remoção do backup do índice, ignore `.local_backups/`, procedimento operacional versionado e verificações seguras reproduzíveis. Não introduz novo loader de segredos. Agente implementa e prepara evidências; Alan controla Binance/visibilidade, T7 e homologação; operador autorizado aplica configuração, revogação e manutenção Git; pai conduz eventos, revisão, integração e release.

Done técnico exige integração/QA/restart DEV e resultado do inventário autorizado, com pendências identificadas por ambiente, responsável e condição de fechamento. Não significa incidente contido. Rotação PROD ou rewrite ainda não autorizados permanecem pendentes no registro operacional; não simular sua execução marcando uma tarefa de preparação. Homologação por Alan antecede pedido explícito de release. Limpeza global incluindo `main` ocorre nessa janela posterior e integra os critérios de Pronto deste mesmo card. T16 permanece condicionado aos guards e à validação PROD; não se cria aresta de emergência nem se desliga `qa-gate`.

Alternativa de reescrever apenas a branch do card deixa a exposição noutras refs; reescrever `main` no Apply anteciparia operação de produção. Ambas rejeitadas.

### 2. Inventário privado, evidência mínima

Antes da operação, operador estabelece diretório restrito fora do Git (permissões 0700/0600, armazenamento protegido, sem sincronização pública), retenção e responsável. Sem shell tracing, argumentos com segredos, dumps no terminal, logs de respostas, CI público ou envio a scanners remotos. Material bruto fica local e restrito; evidência publicável usa apenas ID opaco sequencial, nome da chave/serviço, presença, ambiente, data, classificação, resultado e justificativa. Sem valor, trecho, hash de segredo, fingerprint ou URL com credencial. Mapa técnico de refs/SHAs de commits permanece separado e restrito quando apontar diretamente para conteúdo exposto.

Inventariar branches/tags remotas com `git ls-remote --heads --tags`, refs locais e worktrees, PRs abertos/fechados acessíveis e `refs/pull/*` disponíveis; comparar lista remota com refs efetivamente obtidas num clone completo. Enumerar também stash/reflogs locais controlados, releases/anexos, Actions artifacts/logs/caches e LFS quando existirem. Cada fonte recebe cobertura, responsável e limitação; falta de acesso nunca significa zero achados. Refs não anunciadas ou retenção interna do provedor exigem acompanhamento separado.

Usar Gitleaks local, versão fixada no Apply, com `git --log-opts="--all" --redact=100` e relatório JSON restrito; scanner usa patches Git e oferece `dir` para conteúdo de diretório ([Gitleaks oficial](https://github.com/gitleaks/gitleaks)). Validar previamente a saída com fixture sintética que falhe: redaction sozinha não autoriza publicar JSON. Capturar stdout/stderr localmente; exportador de allowlist descarta `Secret`, `Match`, linhas, fingerprints, mensagens e caminhos não saneados. Diferenciar zero achados, achados e falha operacional; execução incompleta bloqueia inventário. Registrar versão, configuração e contagem de refs, sem bypass por baseline que oculte o incidente.

Complementar scanner com inventário de versões dos arquivos conhecidos, busca controlada por nomes de chaves, aliases/renames e análise de metadados/mensagens; regras genéricas podem não detectar senhas de URL ou material binário. Para cada valor identificado, comparar localmente em memória com configuração efetivamente carregada em DEV/PROD e variantes históricas, emitindo somente igual/diferente/ausente/indeterminado. Scanner limpo não prova revogação nem ausência universal.

Backup: abrir cópia restrita read-only, sem executar SQL vindo dos dados, extensões ou aplicações contidas nele. Inspecionar todas as tabelas/colunas e campos texto/JSON com classificador controlado; registrar categorias e contagens sem linhas. SQLite serve somente à perícia desse arquivo, nunca runtime/QA. Segredo recebe o mesmo processo de invalidação; dados pessoais/sensíveis recebem tratamento, proprietário e pendência. Resultado ambíguo permanece pendente.

### 3. Provar invalidação antes de limpar história

Alan confirma visibilidade privada e registra resultado; não presumir que já mudou. Para cada segredo, operador associa todas as versões históricas ao serviço/ambiente e prova revogação, expiração verificável ou impossibilidade de uso. “Valor atual diferente” ou falha de rede/IP/permissão não bastam.

Binance: Alan gera par novo quando necessário, com permissões mínimas e sem ampliar escopo, instala por canal protegido e revoga todos os pares expostos. Evidência combina estado de revogação no provedor com requisição autenticada não financeira controlada usando credencial antiga, quando viável; rejeição precisa ser distinguida de falha de transporte. Não realizar ordens, saques nem publicar retorno de conta. Sem teste antigo viável, exigir prova autoritativa da revogação; sem ambas, pendência bloqueia limpeza histórica.

JWT: trocar segredo comprometido, recarregar todos os processos validadores/signatários e confirmar ausência de aceitação do antigo. Testar token access e refresh não expirados de conta controlada assinados com cada segredo histórico relevante: rejeição por assinatura/validação, comparada com token de mesmas claims assinado pelo segredo vigente aceito. Validar login novo e renovação; somente token expirado rejeitado não prova rotação. Não manter fallback para segredo antigo; sessões antigas precisam novo login. #684 é reaproveitado, sem alterar seu contrato.

Banco: distinguir URL pública de senha embutida; verificar roles/consumidores reais de `DATABASE_URL` e `WORKFLOW_DATABASE_URL`. Se histórico ainda permite autenticação, trocar senha ou desabilitar role exposta, atualizar todos os consumidores, encerrar conexões/sessões antigas pertinentes e validar conexão nova restrita e rejeição da credencial antiga contra o endpoint correto. Não executar migração destrutiva nem retornar linhas. Credencial já comprovadamente inválida dispensa rotação redundante. Outros segredos seguem a mesma regra.

Nunca restaurar configuração comprometida para recuperar disponibilidade. Se nova credencial falhar, corrigir permissões/canais ou emitir outra inédita, mantendo componente afetado pausado até teste passar.

### 4. Congelamento, preservação e rewrite dedicado

Só após comprovação de invalidação completa: operador e responsáveis combinam janela, impedem pushes/merges/deploys concorrentes e capturam mapa `ref → SHA antigo → SHA novo → ação → dono`. Guardar também proteções/rulesets vigentes, PRs e releases afetados. Cada branch em curso recebe ação explícita de preservação; nenhuma desaparece por não pertencer ao pacote da release.

Antes de congelar, inventariar alterações commitadas, staged, unstaged, untracked e stashes em cada worktree. Guardar cópia de recuperação restrita e cifrada fora do repo, testar restauração isolada e conferir com o responsável. Separar patches de trabalho saneados de cópia contaminada em quarentena; nenhuma ref `backup/*` publicada. Destruição de cópias locais exige autorização própria; definir retenção/revisão, sem promessa de apagamento físico.

Executar git-filter-repo >=2.47 em clone completo novo dedicado, nunca no `source` DEV/PROD nem no Git compartilhado dos worktrees. Validar origem, lista de refs e condição de clone limpo; falha do fresh-clone check é parada, não convite a `--force`. Remover os caminhos conhecidos e seus aliases com `--sensitive-data-removal --invert-paths --path ...`; remover blobs binários sensíveis integralmente. Ocorrências embutidas em arquivos preservados usam `--replace-text`; mensagens de commits/tags usam `--replace-message`, com expressões guardadas apenas no diretório protegido. Mapa de commits e refs é produto da operação, não segredo a publicar ([manual oficial](https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt)).

Pré-publicação: comparar inventário de refs, árvore de cada tip (diferenças apenas nas remoções/substituições previstas), scanner sobre todas as refs reescritas, busca exata local de valores/blobs conhecidos e ausência de todos os caminhos sensíveis. Conferir trabalhos preservados, testes relevantes e integridade Git. Inspecionar assinaturas/tags afetadas e atualizar referências de automações; registrar perdas de identidade histórica. Novo achado volta à classificação/invalidação. Divergência inesperada ou ref desconhecida cancela publicação.

### 5. Publicação controlada e recuperação

Apresentar a Alan o mapa final, evidências, refs afetadas, janela e mudanças temporárias mínimas de proteção. A aprovação de Design não autoriza force-push/proteções; autorização operacional concreta continua necessária antes dessa etapa irreversível. Não executar `push --mirror` indiscriminado. Publicar somente refs enumeradas, com expectativas explícitas dos SHAs antigos e tentativa atômica quando suportada; conferir novamente o remoto imediatamente antes. Divergência de SHA aborta, preserva trabalho e exige novo cálculo/validação. Restaurar proteções e verificar seu estado mesmo em falha parcial; não manter bypass de CI.

GitHub trata refs de PR como somente leitura; rewrite pode deixar caches acessíveis e comprometer diffs/assinaturas. Inventariar refs residuais, abrir solicitação de suporte por canal autorizado com metadados mínimos e registrar resposta; suporte pode recusar limpeza mitigável por rotação. Não prometer expurgo de terceiros ([GitHub: remoção de dados sensíveis](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)). Cache/ref sensível ainda acessível sob controle do projeto ou sem resolução permanece pendência impeditiva de Pronto; recusa do provedor é bloqueio visível, não sucesso.

Validar com novo clone independente do remoto, repetir varredura/ausência/cobertura de refs e conferir exclusões de anexos/caches controláveis. Operador recria clones locais controlados ou migra worktrees por rebase dos commits exclusivamente pendentes sobre os SHAs limpos, usando o mapa de bases; revisar cada patch, rescanner e testar antes de push. Nunca merge/pull da história antiga. Worktree suja não recebe reset destrutivo; dono confirma recuperação antes da liberação. Reabrir/atualizar PRs e CI sobre novos SHAs. Revalidar proteções, branches preservadas e automações antes de encerrar congelamento.

## Risks / Trade-offs

- [Detecção incompleta] → combinar scanner, análise de conteúdo e registro de cobertura; sem comprovação, pendência.
- [Indisponibilidade na rotação] → janela, smoke por consumidor, pausa localizada e credencial inédita de recuperação.
- [Perda de trabalho ou recontaminação] → mapa de refs, cópia restrita testada, congelamento e restauração revisada.
- [Rewrite parcial publicado] → manter congelamento; reconciliar refs contra mapa validado e completar apenas história limpa. Nunca voltar refs ao histórico contaminado.
- [Cópias externas] → revogação é defesa principal; evidência limita a afirmação às fontes verificadas.

## Migration Plan

1. **Apply/DEV:** materializar procedimento e verificador sanitizado; inventário autorizado; remover backup do índice preservando cópia restrita e ignorá-lo; validar probe inofensivo com `git check-ignore` e inclusão habitual em checkout descartável. Testes do verificador usam apenas fixtures sintéticas. Rodar revisão, CI/QA visual padrão e integração normal. Após integrar, `./restart` em `environments.dev.source` e smoke em `https://dev.criptofarol.com.br`, login, PostgreSQL e acesso não financeiro ao serviço necessário. Registrar pendências operacionais, inclusive ausência de autorização, sem declarar remediação total.
2. **Operações autorizadas:** concluir revogação/rotação por ambiente antes do rewrite. DEV e PROD seguem paths/services do overlay, sem misturar bancos `crypto_app_dev`/`crypto_app`. Atualizar configuração protegida efetivamente carregada; reiniciar apenas consumidores afetados; confirmar workers e não executar jobs financeiros para smoke.
3. **Após Done + homologação + release explícita:** preparar pacote normal homologado com guards; usar `release-*` quando necessário. Concluir publicação normal do pacote e deploy PROD pelos hooks do overlay, então congelar refs finais e executar manutenção histórica global autorizada. Não incluir mudanças funcionais não homologadas em `main`; rewrite só saneia história. Revalidar os SHAs publicados e a equivalência funcional após sua mudança; atualizar referências das evidências anteriores pelo mapa.
4. **PROD e fecho:** atualizar checkout canônico PROD à história limpa preservando configuração, `alembic upgrade head`, build e serviços definidos no overlay; não reiniciar oneshots por simetria. Confirmar `https://criptofarol.com.br/api/health`, autenticação antiga rejeitada/nova aceita e conectividade necessária. Sync normal `main → develop` usa exclusivamente história limpa. Kaizen, archive/sync e higiene do pacote seguem o runbook; `PRESERVED_BRANCHES` continuam preservadas e recuperadas. `release-guard post` PASS + evidência completa habilitam o pai a T16; pendência de segredo, backup sensível, ref/cache ou PROD impede Pronto.

Rollback antes da publicação descarta a tentativa dedicada e mantém cópias de trabalho preservadas; depois da publicação é correção para frente a partir de história limpa. Rollback de aplicação pode usar conteúdo funcional anterior saneado com configuração nova, jamais refs/segredos comprometidos. Não restaurar backup investigado no runtime.

## Open Questions

Nenhuma decisão de escopo pendente. No Apply/operador: quantidade de credenciais e refs afetadas, classificação das linhas do backup, dependências efetivas de configuração, cobertura do provedor e janela de manutenção. São resultados a obter, não fatos já demonstrados. Acesso recusado permanece bloqueio visível e não será contornado.

## Design Critique

- P0–P3: zero achados na crítica independente de 2026-10-12.
- disposition: aceitar para submissão à Aprovação de Design; rework desnecessário.
- verdict: PASS de Design; não substitui aprovação humana nem comprova remediação executada.
