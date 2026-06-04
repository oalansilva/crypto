## 1. Frontend Environment Source

- [x] 1.1 Create a centralized frontend helper that resolves `DEV` or `PROD` from `VITE_APP_ENV`, `VITE_ENVIRONMENT`, and Vite mode.
- [x] 1.2 Keep the helper safe for public UI by exposing only label, kind, and display metadata.
- [x] 1.3 Configure the local restart build to pass a branch-aware `VITE_APP_ENV` default.
- [x] 1.4 Make the restart stop phase reliably clear stale preview processes on the configured frontend port before serving the rebuilt bundle.

## 2. Authenticated Shell UI

- [x] 2.1 Add a reusable environment indicator component using `DESIGN.md` tokens and compact shell styling.
- [x] 2.2 Mount the indicator in desktop authenticated navigation.
- [x] 2.3 Mount the indicator in mobile authenticated navigation and mobile drawer context.

## 3. Validation

- [x] 3.1 Validate OpenSpec status and strict validation for `card-257-env-indicator`.
- [x] 3.2 Run frontend build.
- [x] 3.3 Validate rendered DEV and PROD indicator states through stable DOM selectors.
- [x] 3.4 Run Codex review on the exact diff before commit/integration.

## Notes

- Use project skills when applicable: `alan-workflow`, `github-project-board`, OpenSpec skills, and frontend/design validation against `DESIGN.md`.
