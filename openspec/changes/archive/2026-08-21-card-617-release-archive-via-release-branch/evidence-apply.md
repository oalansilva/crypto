# Apply evidence — card #617

Date: 2026-08-21

## 2.1 / 2.2 / 3.1 — `release-guard pre` sem exigir archive em `origin/develop`

Static inspection of `scripts/release-guard` (no code change in this card; #618 out of scope):

- `unpublished_is_code_pr` (≈314–332): when `current_branch` matches `release-*`, diff base is `origin/main...HEAD`, not `origin/develop`. Archive committed only on the release tip is visible to `pre` without being on `origin/develop`.
- No message/string in the script prescribe “publique archive em develop primeiro” / equivalent (repo-wide `rg` on `scripts/release-guard`).
- Local-branches section skips the current `release-*` branch; drift of local `develop` vs `origin/develop` is warn-only when HEAD is not `develop` (blocker only when `current_branch == develop`). Residual local-`develop` ahead case remains #618.

Conclusion: D2 already holds in current guard; apply did not modify `scripts/release-guard`.

## 3.2 — Runbook cites sync + re-run `post`

Verified in:

- `docs/crypto-overlay.md` — terceiro caminho (#617), ordem #518 passo **5b**, bloco Caso B com sync → `post`
- `.cursor/skills/alan-workflow/SKILL.md` — seção Release

## 3.3 — OpenSpec validate

```text
openspec validate card-617-release-archive-via-release-branch
→ Change 'card-617-release-archive-via-release-branch' is valid
```
