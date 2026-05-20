## Context

The current release rules already require inventory of worktrees, branches, stashes, generated output, and `develop`/`main` merge state. The gap is enforcement: agents can complete a release by following the prose partially and still leave hidden work behind.

Recent release cleanup also showed two recurring sources of confusion:
- comparing `develop` to stale local `main` instead of `origin/main`;
- treating stash/backup/worktree preservation as cleanup even when the preserved work remains unclassified.

## Goals / Non-Goals

**Goals:**
- Add one repository command that audits release hygiene consistently.
- Make `pre` and `post` release modes fail when hidden/orphaned work remains.
- Keep official branch comparison remote-first: `origin/develop` and `origin/main`.
- Keep generated/local-only files out of source control.
- Document the guard in `AGENTS.md` as a mandatory release gate.

**Non-Goals:**
- Automatically drop, rewrite, or delete stashes and branches.
- Automatically merge old WIP into product code.
- Change runtime behavior, database schema, APIs, or frontend UX.
- Replace the OpenSpec or GitHub Project release process.

## Decisions

1. Use a small Bash guard at `scripts/release-guard`.
   - Rationale: the checks are Git/file-system operations and should run without project Python dependencies.
   - Alternative considered: Python CLI. Rejected because the guard should work even when virtualenv setup is broken.

2. Provide three modes: `audit`, `pre`, and `post`.
   - Rationale: `audit` lets agents inspect state while developing; `pre` and `post` are strict release gates.
   - Alternative considered: one strict command only. Rejected because the current repo intentionally has legacy stashes that must be reviewed before deletion.

3. Treat stashes as blocking in strict modes.
   - Rationale: stash is invisible to normal branch/worktree review and is the main source of orphaned work.
   - Alternative considered: allow named stashes. Rejected for release closure because named but stale stashes still hide unmerged code.

4. Use remote refs for release merge comparison.
   - Rationale: local `main` can be stale and create false "not merged" alerts.
   - Alternative considered: force local `main` to update. Rejected because release verification only needs authoritative remote state.

## Risks / Trade-offs

- Existing legacy stashes will make `pre` and `post` fail until classified. Mitigation: use `audit` for inventory and require explicit Alan approval before dropping anything.
- Network access is needed for the freshest remote comparison. Mitigation: the guard fetches with `git fetch --prune origin` and fails if fetch fails in strict modes.
- A tracked ignored file may be legitimate configuration. Mitigation: remove generated/local files from the index while keeping local copies ignored.

## Migration Plan

1. Add `scripts/release-guard`.
2. Update `AGENTS.md` release and worktree rules to require the guard.
3. Remove tracked generated/local-only files from the index.
4. Validate with `audit` mode now, and document that strict modes fail while legacy stashes remain.
