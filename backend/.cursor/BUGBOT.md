# Review rules — backend

Included when the reviewed diff touches `backend/`.

- Keep FastAPI routes thin; business rules stay in services/repositories.
- `DATABASE_URL` / `WORKFLOW_DATABASE_URL` remain PostgreSQL. No SQLite fallback in runtime or QA.
- Auth, credentials, wallet, and trading paths are sensitive: flag missing validation, secret leakage, and untested mutations.
- If this tree changes and there is no update under `backend/**/test*` or `backend/tests/**`, add a blocking finding titled "Missing tests for backend changes" unless the PR is docs/harness-only inside backend comments.
