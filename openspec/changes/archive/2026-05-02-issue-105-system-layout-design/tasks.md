## 1. System Mapping

- [x] 1.1 Map current global shell, navigation, shared UI components, and compatibility CSS that control system layout.
- [x] 1.2 Identify `DESIGN.md` tokens that can be safely adapted to an operational crypto workspace.

## 2. Global Design System

- [x] 2.1 Rebase global CSS variables, body background, page shells, shared cards, forms, tables, buttons, and utility classes on the `DESIGN.md` visual system.
- [x] 2.2 Update `Layout.tsx` so authenticated routes inherit the standardized Binance dark shell instead of the old decorative background.
- [x] 2.3 Update `AppNav.tsx` to use the new pill/sidebar/account/mobile visual treatment while preserving admin filtering and navigation behavior.
- [x] 2.4 Update shared UI components (`Button`, `Card`, `Input`, `Sidebar`) to use tokenized classes that match the system layout.
- [x] 2.5 Correct remaining scoped layouts on Monitor and Signals History to inherit the Binance system surfaces.

## 3. Validation

- [x] 3.1 Run frontend build.
- [x] 3.2 Run relevant navigation/layout E2E checks.
- [x] 3.3 Run browser/visual smoke validation for desktop and mobile representative routes.
- [x] 3.4 Run `/opsx:verify` equivalent via `openspec` and record evidence.
- [x] 3.5 Run `./restart` after validation.
- [x] 3.6 Re-run frontend build, focused E2E, visual smoke, and `./restart` after dark-screen correction.
- [x] 3.7 Reimplement after Alan updated `DESIGN.md` from warm/Mastercard language to Binance dark/yellow language.

Note: use the local `crypto-frontend` skill for frontend quality and visual validation.
