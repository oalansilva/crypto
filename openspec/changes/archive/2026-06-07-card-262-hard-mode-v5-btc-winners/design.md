## Context

Issue #262 is a governed execution run, not a production release. The repo already has Favorites, combo optimization/backtest, public strategy descriptions, and favorite refresh/readback flows, but this run has stricter acceptance gates: five new BTC/USDT 1D Long Favorites must be saved sequentially, each one better than all previous winners, and each one visible without fallback public copy.

The active working tree at the original repo path contains unrelated dirty work, so execution uses a clean worktree branch `card-262-hard-mode-v5` from `origin/develop`.

## Goals / Non-Goals

**Goals:**

- Capture a complete T0 snapshot before any candidate generation or save.
- Revalidate current BTC/USDT 1D Long Favorites with Deep Backtest and the required 100 USD / 100% in-out invariants.
- Search, rank, stress, save, and validate up to five sequential winners only when each winner passes novelty, anti-duplicate, anti-dominance, public-name, and readback gates.
- Preserve generated evidence and Pine scripts in versionable repo paths when artifacts are produced.
- Stop with an evidence-backed blocker if the system cannot meet the goal without violating the contract.

**Non-Goals:**

- No production release, `main` merge, or `Homologado` status movement.
- No manual DB row edits as the final solution for public names or Favorite visibility.
- No weakening of capital, sizing, direction, timeframe, Deep Backtest, or sequential superiority constraints.

## Decisions

- Use the card #262 issue as the single evidence log because the goal explicitly forbids technical execution before card traceability exists.
- Store snapshots/reports/Pine under versionable repo paths instead of `/tmp`, because the goal treats generated artifacts as deliverables to preserve.
- Prefer official backend/API surfaces for save/readback/trades and public-name resolution; direct DB inspection is evidence, not a substitute for API/tela validation.
- Treat missing or stale public mapping as a product bug requiring code/test/restart before any affected candidate can count.
- Use a clean worktree branch from `origin/develop` to avoid overwriting unrelated local changes in the original checkout.

## Risks / Trade-offs

- Runtime/API or PostgreSQL may be unavailable -> block before optimizing and report exact failing command/evidence.
- Existing Favorites may already dominate most candidates -> continue until the configured search budget is met before declaring statistical blockage.
- Deep Backtest may be slow -> use bounded cycles and persistent evidence, but do not substitute non-deep results for candidate counts.
- Public mapping may require code changes -> follow branch/OpenSpec/review/commit/develop/restart before counting any save that depends on it.
- The original checkout is dirty -> keep all issue #262 edits inside the dedicated worktree and do not clean or revert unrelated files.
