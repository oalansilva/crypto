## 1. Identify source of the label

- [ ] 1.1 Locate the Playground UI component that renders the “New Backtest” label (component/page route)
- [ ] 1.2 Confirm whether the label comes from i18n translations, a shared constant, or inline text

## 2. Implement copy change

- [ ] 2.1 Update the label text to exactly “New Backtest2” in the single source of truth
- [ ] 2.2 Verify no other screens are unintentionally affected (search usage of the string/key)

## 3. Tests and verification

- [ ] 3.1 Add/update a frontend test (or existing UI test) asserting the Playground primary action label is “New Backtest2”
- [ ] 3.2 Manually verify in the Playground UI that the label displays correctly and the click behavior remains unchanged

## 4. Quality gates

- [ ] 4.1 Run relevant format/lint/typecheck steps for the frontend (if present)
- [ ] 4.2 Ensure the change matches the spec requirement and does not introduce functional behavior changes

## 5. Notes

- [ ] 5.1 Use project skills under `.codex/skills` when applicable (frontend, tests, debugging, architecture)
