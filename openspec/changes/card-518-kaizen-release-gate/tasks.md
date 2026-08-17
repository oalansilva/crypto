## 1. Release guard: data e documentação

- [x] 1.1 Implementar resolução única de `RELEASE_DATE` com default UTC, validação estrita de formato/data e uso compartilhado pelos checks de doc e kaizen
- [x] 1.2 Refatorar a validação de release docs para que `pre` bloqueie placeholders na doc canônica da data e exija `PROD_DEPLOY_EVIDENCE` quando essa doc existir
- [x] 1.3 Repetir no `post` a validação da doc canônica, preservando detecção de duplicatas divergentes da mesma data e sem deixar dívida histórica bloquear outra data no `pre`

## 2. Release guard: gates finais do post

- [x] 2.1 Adicionar check fail-closed de heading versionado de `/kaizen release` em `docs/kaizen-log.md` para a `RELEASE_DATE`; heading de triagem do mesmo dia não satisfaz
- [x] 2.2 Normalizar `RELEASE_BRANCHES` (trim/dedupe), exigir lista não vazia no `post` e rejeitar tokens vazios, refs inválidas e prefixos fora de `change-`/`card-`/`release-`
- [x] 2.3 Após o fetch/prune da execução, bloquear quando qualquer branch declarada ainda existir localmente ou em `origin`, e confirmar sucesso somente com ausência nos dois lados
- [x] 2.4 Tornar `main` local ausente/stale um blocker em `post`, mantendo o guard read-only e indicando sync explícito por fast-forward
- [x] 2.5 Atualizar mensagens do guard que ainda descrevem branch cleanup como posterior a `Pronto`; o novo `post` e a deleção ocorrem antes da promoção

## 3. Contrato operacional e evidência kaizen

- [x] 3.1 Atualizar `AGENTS.md` com a ordem canônica: merge da release → deploy PROD → `/kaizen release` → doc + kaizen-log em um único PR documental → sync de `main` local → delete branches → `post` → `Pronto`
- [x] 3.2 Atualizar `AGENTS.md` para exigir erro explícito no handoff quando Task/subagent retornar sessão ausente, `0 messages` ou `0 parts`, sem sucesso/fallback silencioso
- [x] 3.3 Registrar em `docs/kaizen-log.md` a mudança de processo do card #518 e a relação com F-3/F-6/F-7 da auditoria de 2026-08-14, sem reescrever entradas históricas

## 4. Testes focados com Git temporário e gh fake

- [x] 4.1 Criar teste shell hermético do `release-guard` com bare origin/repo temporário, data fixa por `RELEASE_DATE` e executável `gh` fake sem rede
- [x] 4.2 Cobrir `pre`: placeholder bloqueia com arquivo/linha; doc sem deploy evidence bloqueia; doc limpa com evidence passa; doc ausente no PR de código não exige deploy prematuro
- [x] 4.3 Cobrir kaizen no `post`: ausência bloqueia, heading de triagem da mesma data não vale e heading canônico de release vale
- [x] 4.4 Cobrir `RELEASE_BRANCHES`: unset/vazio/token inválido bloqueiam; branch somente local e somente remota bloqueiam; ausência local+remota passa após prune
- [x] 4.5 Cobrir `main` local stale como blocker e alinhada como sucesso; confirmar que o guard não altera refs automaticamente
- [x] 4.6 Confirmar pelo fake `gh` que `pre` mantém zero chamadas de snapshot Project/PR e que os limites remotos existentes de `post` não regridem
- [x] 4.7 Adicionar check focado do contrato documental de spawn vazio em `AGENTS.md` e registrar no handoff qualquer simulação/ocorrência com erro explícito

## 5. Validação e handoff

- [x] 5.1 Rodar `bash -n scripts/release-guard` e o teste shell focado até resultado terminal verde
- [x] 5.2 Validar a change OpenSpec e reconciliar proposal/design/specs/tasks sem executar suíte ampla, restart, deploy ou comandos de board
- [x] 5.3 Publicar novamente os artefatos OpenSpec no comentário existente do card e solicitar somente `Design -> Aprovação de Design`; aguardar Alan mover para `Pronto para Dev` antes de implementar
