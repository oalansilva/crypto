## MODIFIED Requirements

### Requirement: Shell writes use the same deny as Write
`.cursor/hooks.json` SHALL register `beforeShellExecution` on the same Guard adapter. That hook SHALL apply the same deny as `Write` for commands classified as mutating a `product_globs` path (shell redirection, `tee`, `sed -i`, copy/move onto a product path). Commands that only read or test product trees (`pytest`, `ruff`, `git status`) MUST be allowed. Commands classified as Project Status `item-edit` / Status GraphQL MUST be denied (card #612).

When classifying shell redirection or `tee`, the Guard MUST use the **redirect/`tee` target**, not any product path merely cited elsewhere in the command. If every redirect/`tee` target in the command is exactly `/dev/null` or a path under `/tmp` (including `/tmp` itself), the Guard MUST NOT treat the command as a product write solely because the command string also mentions a `product_globs` path. If any redirect/`tee` target resolves to a `product_globs` path (relative to envelope `cwd`, or absolute mapped into the repo product prefixes outside `/tmp` and `/dev/null`), the Guard MUST apply the same product deny as `Write` when I1 does not hold. Non-redirect mutations (`sed -i`, `perl -i`, `cp`, `mv`, `install`) keep the existing product-path extraction behavior. The bash fallback in `.cursor/hooks/process-fsm-guard.sh` MUST apply the same null/`/tmp` allowlist before promoting a cited product path. `git commit`, `git push`, and `./restart` remain out of scope.

#### Scenario: Redirect onto backend
- **WHEN** `beforeShellExecution` stdin has `command` that redirects or `tee`s onto `backend/app/main.py` and I1 does not hold
- **THEN** permission is `deny`

#### Scenario: Pytest is not a write
- **WHEN** `command` is `pytest backend/ -q` (or equivalent test runner) without a mutation token
- **THEN** permission is `allow`

#### Scenario: Null redirect with product path cited is not a product write
- **WHEN** `beforeShellExecution` stdin `command` cites a `product_globs` path (for example under `backend/` or `frontend/src/`) and every redirect or `tee` target is `/dev/null` or under `/tmp`, and Status is outside I1 (for example `Todo` or `Design`)
- **THEN** permission is `allow`
- **AND** the Guard MUST NOT classify the command as `write_produto` solely due to the cited product path

#### Scenario: Tmp redirect with product path cited is not a product write
- **WHEN** `command` cites a `product_globs` path and redirects or `tee`s only onto a path under `/tmp` (for example `> /tmp/out.log` or `tee /tmp/out.log`)
- **THEN** permission is `allow` for the product-write rule even when I1 does not hold

#### Scenario: Real product redirect still denied outside I1
- **WHEN** `command` redirects or `tee`s onto a `product_globs` path (relative or absolute mapped into the repo product tree) and I1 does not hold
- **THEN** permission is `deny`
