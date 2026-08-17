## Why

O fechamento da release de 2026-08-14 fragmentou a evidência documental em seis PRs, exigiu um PR adicional de alinhamento do DAG e ainda terminou com lacunas operacionais: a auditoria `/kaizen release` ocorreu depois dos cards já estarem em `Pronto`, um spawn vazio foi tratado silenciosamente, `RELEASE_BRANCHES` não foi informado e 17 branches permaneceram. O guard atual detecta placeholders somente em `post`, quando a documentação já entrou no fluxo, e trata `main` local desatualizado e a ausência de `RELEASE_BRANCHES` apenas como warnings.

## What Changes

- Definir uma data canônica de fechamento (`RELEASE_DATE`, com default para a data UTC corrente) e fazer o `pre` bloquear a entrada da doc canônica dessa data quando houver placeholder ou quando faltar a evidência final de deploy exigida para o PR documental.
- Tornar a entrada de `/kaizen release` em `docs/kaizen-log.md`, identificada pela data canônica, pré-condição estrita do `post` e, portanto, da promoção dos cards para `Pronto`.
- Tornar `RELEASE_BRANCHES` obrigatório e não vazio no `post`, normalizar/validar seus nomes e exigir que cada branch do pacote esteja ausente tanto localmente quanto em `origin` após `git fetch --prune`.
- Exigir que `main` local esteja sincronizada com `origin/main` no `post`; o guard verifica e bloqueia, mas não altera refs automaticamente.
- Documentar a ordem de fechamento `merge da release → deploy PROD → /kaizen release → doc e kaizen-log em um único PR documental → sync de main local → limpeza das branches → post → Pronto`.
- Tornar resultado vazio de Task/subagent (`0 messages` ou `0 parts`) uma falha explícita de delegação, obrigatoriamente registrada no handoff, sem sucesso silencioso.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `release-worktree-hygiene`: antecipar a validação da doc, exigir evidência kaizen, lista/remoção das branches do pacote e alinhamento da `main` local no fechamento.
- `kaizen-continuous-improvement`: tornar a auditoria da release um gate anterior a `Pronto` e tornar spawns vazios falhas observáveis no handoff.

## Impact

- Affected files: `scripts/release-guard`, teste shell hermético do guard, `AGENTS.md`, `docs/kaizen-log.md` e artefatos OpenSpec desta change.
- Affected workflow: fechamento de lote/release e handoffs que delegam trabalho via Task tool.
- No runtime API, database, migration, frontend, route, component, or visual behavior changes.
- `UI impact: none` — a change altera exclusivamente processo, documentação operacional e script CLI.
