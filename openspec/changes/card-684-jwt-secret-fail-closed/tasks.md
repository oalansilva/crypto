## 1. Resolver fail-closed

- [x] 1.1 Create a single `resolve_jwt_secret()` (new small module, e.g. `app.jwt_secret`) that reads `os.getenv("JWT_SECRET")` with no default, strips whitespace, and raises `RuntimeError` (message names `JWT_SECRET`, never the value) for unset, empty/whitespace, equal to `dev-secret-change-in-production`, or length &lt; 32
- [x] 1.2 Point `app.routes.auth`, `app.middleware.authMiddleware`, and `app.services.oos_promotion_proof` at that resolver so all three share the same criterion and boot fails on import when invalid
- [x] 1.3 Confirm no remaining `os.getenv("JWT_SECRET", "<known default>")` in those runtime modules

## 2. Tests

- [x] 2.1 In `backend/tests/conftest.py`, assign `os.environ["JWT_SECRET"]` (not `setdefault`) to a ≥ 32 test secret that is not the known default, **before** `from app.config import get_settings`
- [x] 2.2 Add unit tests for unset, empty/whitespace, known default, length &lt; 32 (fail) and a valid secret (pass); each failure `RuntimeError` names `JWT_SECRET` and does not contain the candidate
- [x] 2.3 Add a test that an HS256 access token signed with the known default is 401 on `get_current_user` / `get_current_admin` when the process uses a valid secret
- [x] 2.4 Replace short `unit-test-secret` monkeypatches and drop the known-default fallback in `test_oos_promotion_proof_digest` helpers `_expired_proof` / `_proof_with_purpose`
- [x] 2.5 Run the focused backend unit tests for auth, JWT resolver, and OOS proof

## 3. Scripts and example env

- [x] 3.1 Remove the known-default fallback from `scripts/card_262_*` and `scripts/card_277_*` (fail or require explicit env; not runtime)
- [x] 3.2 Document `JWT_SECRET` in the backend env example with a placeholder (not the known default, not a real secret)

## 4. Rotation and closeout (no secret in git/chat)

- [ ] 4.1 Before DEV `./restart` at Done: ensure a strong `JWT_SECRET` exists in the DEV backend `.env` (generate if invalid) without printing the value; evidence = key present + backend up
- [x] 4.2 Leave PROD `.env` rotation for the release of this card, not Done
- [x] 4.3 Confirm systemd units still source the backend `.env` and do not add `JWT_SECRET` to `Environment=`
