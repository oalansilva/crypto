# Design: kaizen-bulk-archive-terminal-changes

## Context

- ~33 changes OpenSpec de cards terminais (`Pronto`/`Cancelado`) de abr-jul/2026 permanecem ativas em `openspec/changes/` com 4/4 artifacts done (auditoria 2026-08-09, F-3).
- O archive é hoje etapa manual no fechamento de lote; mudanças completas de cards terminais que "escaparam" do lote não são detectadas por nenhum check.
- `openspec validate --all` continua funcional, mas o escopo de changes ativas fica poluído com trabalho já concluído.

## Goals / Non-Goals

- Goals: rodar `/opsx:bulk-archive` (via `openspec archive` por change) para as ~33 changes completas de cards terminais; adicionar check no guard `post`/`audit` para change completa de card terminal ainda ativa; `openspec validate --all` verde após o archive.
- Non-Goals: não arquivar changes de cards não terminais; não mexer em specs de capabilities já sincronizadas; não alterar o fluxo OpenSpec da CLI.

## Decisions

- **D1 — Archive via CLI OpenSpec (bulk-archive)**: executar `openspec archive --change <name>` (ou bulk-archive via skill) para cada change elegível, na ordem, com sync de delta specs quando o artefato indicar; usar `openspec status --change <name> --json` antes para confirmar 4/4 done.
  - Rationale: caminho canônico da CLI; preserva evidência por change.
  - Alternativa: `mv` manual — rejeitada: perderia sync de specs e validação da CLI (regra do AGENTS.md exige skill/CLI; archive manual só como exceção operacional se a CLI falhar, com registro).
- **D2 — Elegibilidade por card terminal**: para cada change ativa, mapear o card vinculado (nome `card-<id>-*`, `issue-<id>-*` ou referência em proposal) e verificar o status do card no board (`gh project item-list`); elegível = 4/4 done + card em `Pronto` ou `Cancelado`. Changes sem card vinculado (ex.: `add-*`, `collect-*`) exigem classificação manual (integrar/arquivar com evidência de conclusão).
  - Rationale: evita arquivar change em andamento; regra do card #458.
- **D3 — Check no guard (post/audit)**: adicionar seção "OpenSpec terminal changes" que lista changes ativas com 4/4 done cujo card é `Pronto`/`Cancelado`: `audit` → warn; `post` → blocker exigindo archive/classificação.
  - Rationale: enforcement contínuo; sem isso o problema recria na próxima release.
  - Alternativa: check apenas no closeout manual — rejeitada (mesmo motivo do guard existente: disciplina manual não é enforcement).
- **D4 — Validação final**: após archive, rodar `openspec validate --all`; se falhar por changes antigas fora do escopo, validar as changes afetadas como evidência parcial e classificar antes do fechamento do card (regra AGENTS.md).
- **D5 — Guarda de rede**: o check do guard consulta o board via `gh`; se `gh` falhar, fail-closed no post (não silenciar) — padrão já usado na seção "Board fields".

## Risks / Trade-offs

- [Change com artifacts done mas código nunca integrado (card Pronto por engano)] → elegibilidade exige card terminal; se o card está Pronto, o conteúdo foi publicado (regra de Pronto exige deploy); risco baixo. Changes com dúvida ficam para classificação manual.
- [Sync de delta specs gerar conflito com specs ativas] → seguir instrução da CLI (`openspec instructions` para archive); em conflito, resolver manualmente com registro.
- [Bulk-archive falhar no meio (CLI/skill)] → exceção operacional registrada: archive manual de cada change restante com evidência, conforme AGENTS.md.
- [validate --all quebrar por outra change não relacionada] → não bloqueia o archive; evidência parcial + classificação da sujeira.

## Migration Plan

1. Para cada change elegível: `openspec status --change` → `openspec archive` (sync de specs quando aplicável) → mover para `openspec/changes/archive/YYYY-MM-DD-<change>/`.
2. Adicionar seção "OpenSpec terminal changes" ao `scripts/release-guard` (post/audit).
3. Atualizar `AGENTS.md` (regra de validação OpenSpec global) com a nova checagem.
4. Rodar `openspec validate --all` e `scripts/release-guard audit`.
5. Rollback: restaurar diretórios do archive para `openspec/changes/` (git) e reverter diff do guard.
6. Sem runtime/DB/migração.

## Open Questions

- Nenhuma; changes sem card vinculado e não concluídas ficam como classificação manual (não arquivadas).

## Design Critique

- UI impact: **none** — mudança 100% tooling/processo (archive OpenSpec + scripts/release-guard + AGENTS.md); nenhuma superfície visual do produto é criada ou alterada.
- Impeccable: **N/A** — sem UI; justificativa: não há interface, componente ou fluxo visual envolvido.
- Prototype Validation: **N/A** — sem protótipo HTML; superfície de validação é `openspec validate --all` + saída do guard.
- Critérios de aceite verificáveis: (1) bulk-archive conclui sem blockers; (2) guard post detecta changes completas de cards terminais ativas (warn/blocker); (3) `openspec validate --all` verde após archive.
- Design Agent verdict: **PASS** — D1-D5 definem elegibilidade, archive canônico e enforcement sem ambiguidade; nenhum achado bloqueante (produto/UX/a11y não aplicáveis).

