## Why

In the 2026-08-09 kaizen release (421-440), every closed card received duplicated evidence comments ("Implementação concluída" twice, 14:04Z and 14:05Z) for the same commit/PR, varying only in the format used to reference it (URL vs "PR N (sha)"). This was the second occurrence of the same duplication (previously F-5 of #438), which pollutes the card timeline and weakens evidence auditability.

## What Changes

- Add a helper script (`scripts/post-card-evidence-comment.sh`) that checks for an existing evidence comment for the same transition + commit ref before posting a new one.
- The helper dedupes by card number, transition type (Done/Homologado/Pronto), and commit ref; if an equivalent comment already exists, it reports the existing comment instead of posting a duplicate.
- Keep the exact comment templates from `AGENTS.md` so evidence format stays canonical.
- Document the helper usage in `AGENTS.md` (comentários obrigatórios no Kanban).

## Capabilities

### New Capabilities

- `card-evidence-comments`: deduplicated evidence comments per card transition, keyed by transition type + commit ref.

### Modified Capabilities

None.

## Impact

- Affected files: `scripts/post-card-evidence-comment.sh` (new), `AGENTS.md` (usage docs).
- Affected workflow: card closure comments for Done/Homologado/Pronto, batch releases.
- No runtime API, database, or frontend behavior changes.
