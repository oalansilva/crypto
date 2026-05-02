## Context

`ProfilePage` already dispatches a success toast after `PUT /users/me` succeeds. The global toaster is mounted in `App.tsx`, but the current `ToastViewport` renders an empty fixed container and the actual toast nodes are rendered outside that container, so the confirmation can be missed or appear in the normal document flow.

## Goals / Non-Goals

**Goals:**
- Render toast messages in a fixed, visible viewport above app content.
- Keep existing `useToast` call sites working without API changes.
- Add a focused E2E regression for the profile save flow.

**Non-Goals:**
- Redesign the toast system or introduce Radix/shadcn dependencies.
- Change backend profile APIs or validation rules.
- Add inline profile-only success state unless the shared toast path remains insufficient.

## Decisions

- Update `ToastViewport` to accept and render children, then place mapped toast elements inside it from `Toaster`.
  Rationale: this fixes the shared notification surface while preserving the existing hook and call-site API.
- Position the viewport near the top center and style the toast with the app's dark elevated surface tokens.
  Rationale: this avoids the bottom-right placement that felt disconnected from the workflow.
- Wire the close control to `dismiss(id)`.
  Rationale: the current close button is visual only and does not update toast state.
- Keep the existing profile success copy: "Perfil atualizado" and "Seu nome foi salvo com sucesso."
  Rationale: the issue is visibility, not copy or backend behavior.
- Add Playwright coverage for `/profile` with mocked auth and profile endpoints.
  Rationale: the bug is user-observable and best validated in the browser.

## Risks / Trade-offs

- [Risk] Changing the shared toaster affects all toasts.
  Mitigation: keep markup and classes close to current primitives and validate with the focused profile E2E plus frontend build.
- [Risk] A fixed toast can overlap content on small screens.
  Mitigation: constrain width to the viewport, keep it top-centered, and preserve a compact max width on desktop.
