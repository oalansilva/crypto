## Why

5/5 cards da release 2026-08-11 foram para `Homologado` (e depois `Pronto`) sem o comentário padrão de evidência "Homologado por Alan na develop." — recorrência da F-5 da auditoria 08-09 (F-2 em 08-11). A transição por arraste/chat no board não passa pelo helper `post-card-evidence-comment.sh --transition homologado`, e o `release-guard` não valida essa evidência no closeout.

## What Changes

- `release-guard post` com `RELEASE_CARDS` exportado: detecta card `Homologado`/`Pronto` sem comentário de homologação (warn em `audit`, blocker em `post`).
- Helper `post-card-evidence-comment.sh` passa a suportar post retroativo `--transition homologado` com `--dry-run` validável (template `Homologado por Alan na develop.` já existe; garantir dry-run e dedupe por transição).
- Release 2026-08-11 fechada com 5/5 comentários de homologação postados de forma retroativa (cards 456, 457, 458, 463, 464).
- `AGENTS.md` atualizado para tornar obrigatório o post do comentário de homologação na transição para `Homologado`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `documental-board-evidence-validation`: `release-guard post/audit` deve validar comentário de homologação nos cards `Homologado`/`Pronto` do pacote (`RELEASE_CARDS`).
- `card-close-evidence-integrity`: helper de comentário de evidência deve suportar `--transition homologado` retroativo com dry-run e dedupe.

## Impact

- Affected files: `scripts/release-guard`, `scripts/post-card-evidence-comment.sh`, `AGENTS.md`, `docs/kaizen-log.md` (evidência do fechamento retroativo).
- Affected workflow: closeout de release/lote; transição `Done -> Homologado`.
- No runtime API, database ou frontend behavior changes.
