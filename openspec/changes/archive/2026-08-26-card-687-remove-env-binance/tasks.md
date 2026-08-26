## 1. Gitignore allowlist

- [x] 1.1 Add `.env.*` to root `.gitignore` (keep existing `.env` / `backend/.env` entries as needed)
- [x] 1.2 Allowlist tracked examples so they are not ignored: `.env.binance.example`, `.env.docker.example`, and package examples via `!**/.env.example` or explicit `!backend/.env.example` + `!frontend/.env.example`
- [x] 1.3 Verify with `git check-ignore -v`: a probe like `.env.probe` is ignored; the four examples are not ignored; root `.env` remains ignored

## 2. Remove tracked .env.binance from tip

- [x] 2.1 `git rm --cached .env.binance` (do not recommit secret values; do not recreate the file as canonical home)
- [x] 2.2 Confirm working-tree/index: path untracked or absent from index; examples still tracked
- [ ] 2.3 Open/update PR so merge into develop yields empty `git ls-tree origin/develop -- .env.binance`
  <!-- Apply: index deletion staged (`D .env.binance`); no commit/push in Apply child — parent opens PR after commit. -->

## 3. Runtime / systemd verification (no product code change)

- [x] 3.1 Confirm `backend/app/config.py` still loads only `backend/.env` and root `.env` — no edit that adds `.env.binance`
- [x] 3.2 Confirm `ops/systemd/*.service` have no `EnvironmentFile`/`source` of `.env.binance` — do not add one
- [x] 3.3 Do not edit `backend/**` or `frontend/src/**` product code for this card

## 4. Ops closeout (human; reuse current keys; no rotation)

- [ ] 4.1 If `BINANCE_API_KEY` / `BINANCE_API_SECRET` still live only in local `.env.binance`, copy the **existing** values into root `.env` on DEV and PROD (do **not** generate new Binance key pairs)
  <!-- Apply verify (names only): worktree root `.env` missing; local `.env.binance` has both key NAMES present; backend/.env missing. Human must migrate values to DEV/PROD root `.env`. -->
- [ ] 4.2 Stop using local `.env.binance` as source of truth; prefer deleting or ignoring the local file after migration
  <!-- Apply: path now gitignored via `.env.*`; WT file may remain until human deletes after migration. -->
- [x] 4.3 Do **not** revoke old keys; do **not** require Binance API rejection evidence; do **not** run new-key smoke AC5
  <!-- Apply compliance: no key generation/revoke/smoke performed. -->
- [ ] 4.4 After merge: record `git ls-tree origin/develop -- .env.binance` empty; note that `origin/main` may still have the path until release (accepted under Alan T6)
  <!-- Human/post-merge evidence. -->
- [ ] 4.5 Done when: develop tip clean + gitignore blocks new `.env.<name>` except allowlisted examples + ops uses root `.env` with current keys (no rotation gate)
  <!-- Apply portion of gitignore/index done; tip-clean + ops home migration await commit/merge + human 4.1–4.2. -->
