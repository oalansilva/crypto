## 1. Investigation

- [x] 1.1 Confirm runtime PostgreSQL `combo_templates` count and sample rows without exposing secrets.
- [x] 1.2 Confirm `/api/combos/templates` response shape and count against the same runtime database.
- [x] 1.3 Confirm the Combo UI uses the documented endpoint and identify whether the defect is backend, runtime data, or UI handling.

## 2. Implementation

- [x] 2.1 Fix the template listing path so valid runtime PostgreSQL templates are returned with `name`, `description`, and `is_readonly`.
- [x] 2.2 Preserve the existing `prebuilt`, `examples`, and `custom` buckets and avoid SQLite operational fallback.
- [x] 2.3 Apply `DESIGN.md` UI rules if frontend changes are required.

## 3. Validation

- [x] 3.1 Add or update focused backend regression tests for non-empty template listing.
- [x] 3.2 Run OpenSpec validation for `card-252-combo-templates`.
- [x] 3.3 Run focused backend/frontend checks proportional to the changed files.
- [x] 3.4 Validate the served runtime API and Combo UI/DOM show the non-zero template count.
- [ ] 3.5 Move the card through Code Review to Done tecnico only after review, integration in `develop`, `./restart`, and runtime evidence.

Note: use project skills when applicable; `alan-workflow`, `openspec-new-change`, and `openspec-ff-change` were used for this planning package.
