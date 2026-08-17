# Design: kaizen-guard-branch-inventory

## Context

- O guard atual (card #422) inventaria só refs órfãs `runtime-*/rollback-*/release-post-*/sync-*/preserve/*` e worktrees; branches `change-*/card-*/release-*` ficam fora do inventário.
- Dívida real: ~14 refs de cards terminais de releases anteriores (08-03, mai-jul) e branches locais órfãs nunca classificadas/limpas.
- O closeout atual lista "Branches limpas: <lista ou pendência>" no comentário de Pronto, mas sem enforcement.

## Goals / Non-Goals

- Goals: guard `post`/`audit` inventaria branches locais e remotas `change-*/card-*/release-*`; classificação obrigatória (integrada/preservada) ou deleção no closeout; dívida antiga classificada/limpa.
- Non-Goals: não mudar a semântica de `develop`/`main`; não criar branch de release automática; não alterar o fluxo de cards.

## Decisions

- **D1 — Inventário por prefixo com `git for-each-ref`**: estender a seção "Orphan refs" do `scripts/release-guard` (post/audit) para listar `refs/heads/change-*`, `refs/heads/card-*`, `refs/heads/release-*` (locais) e `refs/remotes/origin/change-*`, `refs/remotes/origin/card-*`, `refs/remotes/origin/release-*` (remotas), mostrando se o branch já está mergeado em `origin/develop`/`origin/main` (reusa lógica existente das linhas 220-240).
  - Rationale: um único comando, saída uniforme com o inventário de órfãos atual, sem dependência nova.
  - Alternativa: gh/API do GitHub — rejeitada (mais lento, requer rede; git local basta).
- **D2 — Classificação obrigatória em post**: para cada branch do inventário, exigir estado explícito: `mergeado` (já em origin/develop ou origin/main → classificar como deletável após Pronto), `preservar` (worktree/branch com WIP não mergeado → blocker exigindo classificação). Em `post` estrito, branch não classificado/deletável não deletado é blocker.
  - Rationale: fail-closed consistente com o guard atual.
- **D3 — Closeout checklist no guard**: adicionar sub-seção "Package branch cleanup" que valida, com `RELEASE_CARDS`/`RELEASE_BRANCHES` (novo env opcional), que as branches do pacote foram deletadas (local e remota) depois que os cards foram para `Pronto`; sem env, lista todas as `change-*/card-*` como pendência de classificação.
  - Rationale: aproveita o padrão `RELEASE_CARDS` já usado para campos do board; evita inventar estado novo.
- **D4 — Tratamento da dívida**: a dívida de 08-03 e branches locais órfãs são classificadas nesta implementação: deletar `change-*`/`card-*` locais e remotas já mergeadas em `origin/develop`/`origin/main` (após confirmação no inventário); `preserve/*` segue preservada. Nenhuma deleção acontece sem `origin/develop`/`origin/main` terem o commit (regra de comparação oficial).
  - Observação: a limpeza real da dívida é execução de closeout (passo 2 do critério de aceite), feita no mesmo card ou no fechamento de release, com autorização já dada pelo card kaizen.

## Risks / Trade-offs

- [Deletar branch remota ainda referenciada em PR aberto] → antes de `git push origin --delete`, o script valida que não existe PR aberto com a branch como head (via `gh pr list --head`), e falha com classificação se houver.
- [Branches com prefixo parecido (ex.: `release-2026-08-03-kaizen` já arquivada vs nova)] → inventário mostra SHA e estado de merge; classificação é explícita por branch.
- [Worktree em branch change-* com WIP] → reutiliza o bloco de worktrees existente: WIP não commitado em branch de worktree é blocker no closeout.

## Migration Plan

1. Estender `scripts/release-guard` (seção post/audit) com inventário e classificação `change-*/card-*/release-*` + sub-seção "Package branch cleanup".
2. Atualizar `AGENTS.md` (higiene Git/worktree/stash e release em lote) com a exigência de deleção das branches do pacote após `Pronto`.
3. Rodar `scripts/release-guard audit` para validar saída sem alteração de estado; classificar/limpar a dívida identificada com evidência.
4. Rollback: reverter o diff do guard; comportamento antigo (sem inventário) volta.
5. Sem runtime/DB/migração.

## Open Questions

- Nenhuma.

## Design Critique

- UI impact: **none** — mudança 100% tooling/processo (scripts/release-guard + AGENTS.md); nenhuma superfície visual do produto é criada ou alterada.
- Impeccable: **N/A** — sem UI; justificativa: não há interface, componente ou fluxo visual envolvido.
- Prototype Validation: **N/A** — sem protótipo HTML; superfície de validação é a saída do próprio `release-guard audit/post`.
- Critérios de aceite verificáveis: (1) guard post lista branches change-*/card-*/release-* locais e remotas com classificação obrigatória; (2) closeout exige deleção das branches do pacote após Pronto; (3) dívida 08-03 e branches locais órfãs classificadas/limpas.
- Design Agent verdict: **PASS** — D1-D4 definem inventário, classificação e closeout sem ambiguidade; nenhum achado bloqueante (produto/UX/a11y não aplicáveis).

