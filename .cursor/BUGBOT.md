# Review rules — Cripto Farol

Project rules for the local `diff-reviewer` (and for Cursor Bugbot / `/review-bugbot` if Alan later enables them). `.cursor/rules/*.mdc` do **not** replace this file.

## Base branch

Integration branch is `develop`, not `main`. Closing review compares `origin/develop...HEAD` on the card branch. Never after squash into `develop`.

## Product constraints

- PostgreSQL is mandatory for runtime, QA, and workflow. Do not introduce SQLite as an operational database.
- Do not skip Design, Aprovação de Design, or Pronto para Dev. `implemente` is not approval.
- Never commit secrets, tokens, `.env`, or credentials.
- If `backend/**` changes, accompanying tests (or an explicit classified gap) are required.
- If UI changes, Playwright visual coverage is required unless Alan left `qa-visual-skip` plus `QA visual dispensado por Alan.` with a non-empty `Motivo:`.

## Review stance

Flag only defects introduced by the diff (correctness, security, performance, maintainability). Do not nitpick style. Do not rewrite product UI. Autofix MUST NOT commit onto the existing PR branch.

The paid Bugbot product is Off on purpose (cost). Local reviewers are the Code Review gate.
