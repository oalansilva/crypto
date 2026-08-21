# Design: card-617-release-archive-via-release-branch

Este arquivo é o **refinamento do card #617**. O issue veio primeiro; o Dev implementa **a partir daqui** (Gist). OpenSpec SHALL ser superset do issue.

## UI impact

`none` — runbook de release/closeout e comportamento de `scripts/release-guard pre` em `release-*`. Sem superfície visual do produto. **Não** autoriza pular colunas de Design. Código/docs de apply só após `Pronto para Dev`.

## Prototype

**N/A** — sem superfície visual do produto; mudança operacional/documental.

## Impeccable

**N/A** — `UI impact: none`; pipeline Impeccable (context/shape/prototype/critique/audit/polish/browser) não se aplica.

## Origem

- Issue: [#617](https://github.com/oalansilva/crypto/issues/617)
- Tipo: change · Frente: Operação · Prioridade: P1 · label `kaizen`
- Change: `card-617-release-archive-via-release-branch`
- Incidente: kaizen release 2026-08-19 F-1; recidivas F-3 em 2026-08-20/21
- Evidência: `remote: error: GH006: Protected branch update failed for refs/heads/develop. Required status check "qa-gate" is expected.`

## Card primeiro, OpenSpec mais completo

Issue = intenção. Gist = contrato do Dev.

## Context

Hoje o overlay documenta dois caminhos de publicação:

1. PR `develop → main` quando `develop` só tem conteúdo Homologado.
2. Branch `release-*` quando `develop` tem conteúdo **não** homologado.

O incidente mostrou um terceiro caso real: `develop` só Homologado, mas o **push do archive** (paths `openspec/changes/archive/**`, etc.) para `refs/heads/develop` é recusado pela proteção que exige `qa-gate`. O archive não pode entrar em `origin/develop` antes do PR; o lote congela em `release-*` = `origin/develop` + archive e abre PR para `main`. Depois do merge, `origin/main` tem o archive e `origin/develop` ainda não — o `post` exige árvores idênticas, logo o sync `main → develop` é obrigatório no closeout.

Estado atual do guard (leitura, não apply):

- `unpublished_is_code_pr` já diffa `origin/main...HEAD` quando a branch corrente é `release-*`.
- Seção Local branches no `pre` já dá `continue` na branch corrente `release-*`.
- Drift local `develop` ≠ `origin/develop` só é blocker se `current_branch == develop`; em `release-*` vira warn.
- Não há check explícito “archive must be on origin/develop” — o risco é regressão documental (operador tenta forçar push em `develop`) e lacuna de runbook (sync `main → develop` implícito demais).

`AGENTS.md` é stub always-on; playbook de release vive em `docs/crypto-overlay.md` + skills `alan-workflow` / `alan-workflow-ambientes`.

## Goals / Non-Goals

**Goals:**

- Runbook canônico do caminho `release-*` para archive quando proteção de `develop` recusa push, inclusive com pacote só Homologado.
- Contrato normativo: `pre` em `release-*` PASS sem archive em `origin/develop`.
- Closeout explícito: após merge em `main`, sync `main → develop` (PR ou merge) antes do `post` final / promoção a `Pronto`.

**Non-Goals:**

- Remover ou enfraquecer branch protection / `qa-gate` em `develop`.
- Automerge, auto-push ou mutação de refs pelo `release-guard` (permanece read-only).
- Card #618 (blocker de `pre` por ref local `develop` com archive não publicado) — escopo separado.
- Mudar produto, CI workflows, ou política de quando Homologado autoriza `main`.
- Dual-write do playbook completo no stub `AGENTS.md`.

## Decisions

### D1 — Documentar o terceiro caminho no overlay + alan-workflow (não no always-on)

O caminho canônico de closeout quando push em `develop` falha por proteção (`qa-gate` ou equivalente), **mesmo** com `develop` só Homologado:

1. Criar `release-YYYY-MM-DD` a partir de `origin/develop` (ou `main` + cherry-picks homologados, se já for o caso parcial).
2. Commitar o archive OpenSpec (e docs/kaizen do pacote) **nessa** branch.
3. `scripts/release-guard pre` com HEAD em `release-*`.
4. PR `release-* → main`, merge manual.
5. Deploy PROD + evidência (contrato existente).
6. Sync explícito `main → develop` (PR ou merge ff/merge conforme política do repo).
7. `scripts/release-guard post` (reexecutar após o sync se o primeiro `post` falhar por árvores divergentes).
8. Só então `Pronto`.

Atualizar:

- `docs/crypto-overlay.md`: seção Release em lote + bloco de comandos “Publicar com branch de release…” para cobrir **também** proteção de `develop`, não só “não-homologado”.
- `.cursor/skills/alan-workflow/` (e ambientes se citar o fluxo): uma regra curta apontando o mesmo caminho e o sync `main → develop`.
- `AGENTS.md`: no máximo reforçar “release → overlay”; sem playbook completo.

**Alternativa rejeitada:** exigir admin bypass / desligar `qa-gate` para archive — quebra o gate de integração e não é aceite do PO.

### D2 — `pre` em `release-*` não exige archive em `origin/develop`

Normativo em `release-worktree-hygiene`:

- Com `current_branch` matching `release-*`, `scripts/release-guard pre` MUST NOT emitir blocker cujo remédio seja “publique o archive em `origin/develop` primeiro”.
- MUST NOT tratar a ausência do archive (ou da change ainda ativa) em `origin/develop` como falha do `pre` quando o conteúdo está (ou será) no HEAD `release-*` do pacote.
- Comportamentos já existentes que sustentam isso (skip da branch corrente `release-*` no inventário local; warn-only de drift local develop fora de `develop`) MUST permanecer; se apply encontrar regressão, corrigir no guard sem ampliar escopo ao #618.

**Alternativa rejeitada:** forçar archive em `develop` via PR `card → develop` só para passar `qa-gate` antes da release — duplica CI e atrasa closeout sem ganho de segurança do lote já Homologado.

### D3 — Sync `main → develop` explícito no closeout

O `post` já exige `origin/develop` e `origin/main` com o mesmo commit ou ancestor+árvores idênticas. Após archive via `release-* → main`, as árvores divergem até o sync. O runbook MUST:

- Nomear o passo “sync `main → develop`” (PR ou merge) como obrigatório no closeout desse caminho.
- Orientar reexecutar `release-guard post` após o sync quando o primeiro `post` falhar por árvores diferentes.
- Não tratar o sync como opcional “quando necessário” sem critério — no caminho archive-via-`release-*` ele é necessário para PASS do `post`.

**Alternativa rejeitada:** relaxar o `post` para aceitar archive só em `main` — esconderia develop desatualizada e reabriria duplicata ativa+arquivada (#428).

### Fora de escopo (reafirmação)

- #618, #579, #625, mudança de branch protection.
- Autodelete de branches pelo guard.

## Risks / Trade-offs

- [Operadores usam `release-*` por default mesmo quando push em develop funcionaria] → Mitigação: runbook mantém `develop → main` como caminho feliz quando o push do archive em `develop` passa; `release-*` é o fallback obrigatório sob proteção.
- [Sync `main → develop` esquecido → `post` FAIL / change ativa+arquivada] → Mitigação: passo numerado + exemplo de comando no overlay; reexecutar `post` após sync.
- [Confusão com #618] → Mitigação: design/tasks citam #618 como out-of-scope; não “consertar” local `develop` neste card.
- [Docs só no overlay; agente não carrega] → Mitigação: skill `alan-workflow` aponta o caminho; stub AGENTS já manda carregar overlay em release.

## Migration Plan

1. Apply após `Pronto para Dev`: editar overlay + skill; ajustar `release-guard` só se evidência mostrar FAIL indevido.
2. Validar com cenário sintético ou replay documental: `pre` em `release-*` com archive só no HEAD local/remoto da release, `origin/develop` sem archive → PASS.
3. Rollback: reverter docs/guard; sem migração de dados.

## Open Questions

- Nenhum bloqueante. Forma exata do sync (PR `main → develop` vs merge local+push) fica a critério do operador desde que `origin/develop` e `origin/main` fiquem com árvores idênticas antes do `post` final.

## Critérios de aceite (do issue)

- Runbook documenta `release-*` quando push em `develop` é recusado por proteção, mesmo com `develop` só Homologado.
- `release-guard pre` a partir de `release-*` PASS sem exigir archive já em `origin/develop`.
- Após merge em `main`, sync `main → develop` explícito no closeout para o `post` ver árvores idênticas.

## Implementação (somente `Status=Pronto para Dev`)

1. Atualizar `docs/crypto-overlay.md` (regra + bloco de comandos) e skill `alan-workflow`.
2. Confirmar/ajustar `scripts/release-guard pre` conforme D2; evidência PASS/FAIL.
3. Não tocar board Status neste card de Design; apply separado.

## Design Critique

**Critic:** Independent Design Critic (Task isolada, read-only)  
**Alvo:** `proposal.md` + `design.md` + `specs/**` + `tasks.md` (change `card-617-release-archive-via-release-branch`)  
**UI impact:** `none`  
**Prototype:** N/A — justificado (runbook/closeout + `release-guard pre` em `release-*`; sem superfície visual do produto)  
**Impeccable Brief / Critique / Audit / Trace:** N/A — justificado (`UI impact: none`; pipeline visual não se aplica)

### Escopo vs aceite
- Os 3 critérios do #617 estão cobertos por Goals, D1–D3, specs e tasks: (1) runbook `release-*` sob proteção de `develop` com pacote só Homologado; (2) `pre` em `release-*` sem exigir archive em `origin/develop`; (3) sync `main → develop` explícito antes do `post` final.
- Non-goals corretos: não enfraquecer `qa-gate`, não relaxar `post`, não expandir ao #618, sem dual-write de playbook no stub `AGENTS.md`.

### Regressão
- Alternativas rejeitadas (bypass de proteção; forçar PR archive→develop só para CI; relaxar `post`) preservam o gate de integração e o contrato de árvores idênticas / anti-duplicata ativa+arquivada.
- Spec `release-worktree-hygiene` preserva comportamentos existentes de `release-*`.

### Risco operacional
- **P2 (aceito para apply):** D1 não deve substituir a ordem canônica #518; apply insere o terceiro caminho + sync obrigatório no overlay/skill existentes.
- **P2 (aceito para apply):** eliminar dual message do overlay no caminho archive-via-`release-*`.
- **nit:** evidência do `pre` PASS isola ausência em `origin/develop`; não misturar com blocker de ref local `develop` (#618).

### Pendências não bloqueantes
- P2×2 e nits acima — tratar no apply (tasks 1.x / 3.x), sem reabrir design.

**Design Agent verdict: PASS**
