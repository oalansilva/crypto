## 1. Operational Tooling

- [x] 1.1 Add a PostgreSQL-only beta user cleanup script with dry-run/apply modes.
- [x] 1.2 Default allowed emails to `o.alan.silva@gmail.com` and `o2.alan.silva@gmail.com`.
- [x] 1.3 Emit safe masked evidence and refuse non-PostgreSQL URLs.

## 2. Execution

- [x] 2.1 Run dry-run/list evidence before cleanup.
- [x] 2.2 Apply cleanup against the target runtime database.
- [x] 2.3 Re-run evidence after cleanup and confirm only allowed users remain active.

## 3. Validation

- [x] 3.1 Run focused tests for the cleanup script.
- [x] 3.2 Run OpenSpec validation for `card-135-remove-test-users`.
- [x] 3.3 Run `openspec validate --all`.

## 4. Delivery

- [x] 4.1 Commit branch, integrate in `develop`, run `./restart`.
- [x] 4.2 Comment evidence on card #135 and move it to `Done`.
