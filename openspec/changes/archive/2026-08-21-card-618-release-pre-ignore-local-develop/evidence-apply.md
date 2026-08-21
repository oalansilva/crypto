# Apply evidence — card #618

Date: 2026-08-21

## Tests

```text
pytest ...::test_pre_release_branch_skips_local_develop_ahead_without_preserved
pytest ...::test_pre_release_branch_still_blocks_other_unmerged_local
→ 2 passed
```

## Guard

`scripts/release-guard` Local branches: skip `develop` when `mode=pre` and `current_branch` matches `release-*`. Warn diverge (~438) unchanged. No `PRESERVED_BRANCHES=develop` required.
