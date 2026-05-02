## Context

Card #105 targets system-wide layout consistency using `DESIGN.md`. The current source design is Binance-inspired, and this app is a trading/crypto operations tool; the implementation must translate that financial-platform language into a dense workspace instead of creating a marketing page.

Current frontend state:
- `Layout.tsx` owns the authenticated shell and dark decorative background.
- `AppNav.tsx` owns desktop sidebar, mobile header/drawer, account menu, admin-only menu filtering, and page title.
- `index.css` defines global tokens plus cross-screen compatibility overrides for legacy page classes.
- Several pages already use shared `.page-card`, `.page-card-muted`, `.eyebrow`, `.app-page`, and tokenized colors.

## Goals / Non-Goals

**Goals:**
- Make the app shell, nav, cards, panels, forms, tables, and common controls read as one visual system.
- Adapt `DESIGN.md` tokens: near-black canvas, dark elevated card surfaces, Binance yellow primary action/accent, compact 4-12px radii, flat hairlines, trading green/red semantics, and financial number typography.
- Preserve operational density, dashboard scanability, and existing admin/user route behavior.
- Keep changes mostly in shared shell/CSS/components so the standard applies broadly.

**Non-Goals:**
- Rebuild every page component from scratch.
- Add decorative marketing heroes, orbital imagery, or non-workflow filler.
- Change backend APIs, auth, permissions, routes, or database behavior.
- Archive or commit this change before Alan homologates it.

## Decisions

- Rebase global CSS variables instead of rewriting every page.
  - Rationale: most screens already reference `var(--text-*)`, `var(--bg-*)`, `.page-card`, `.glass`, and `.app-page` selectors.
  - Alternative considered: page-by-page refactor; rejected for first pass because it increases risk and blast radius.

- Keep a sidebar workspace shell, but restyle it with pill/card language from `DESIGN.md`.
  - Rationale: trading workflows need persistent navigation and dense screen space; a floating marketing nav would reduce usability.
  - Alternative considered: top-only floating pill nav; rejected because admin/account routes and desktop density would suffer.

- Use Binance yellow as the primary accent and keep green/red only for semantic market states.
  - Rationale: matches `DESIGN.md` while preserving financial meaning for gain/loss and status.
  - Alternative considered: replacing all semantic colors; rejected because it would reduce trading clarity.

- Update shared UI components to token-based classes.
  - Rationale: new and existing component usage should inherit the same surface, radius, and typography defaults.

## Risks / Trade-offs

- [Risk] Some page-specific Tailwind classes may still force old dark colors. -> Mitigation: add targeted compatibility selectors in `index.css` and validate representative routes.
- [Risk] A dark global system can hide legacy dark-on-dark overrides if applied naively. -> Mitigation: keep explicit elevated surfaces and verify build plus browser smoke.
- [Risk] Existing E2E tests may assert old color classes. -> Mitigation: run relevant layout/navigation tests and update only when product contract changed.

## Migration Plan

1. Update global tokens and app shell.
2. Update navigation and shared UI components.
3. Add compatibility overrides for common legacy surface/text classes.
4. Validate build and representative E2E/browser routes.
5. Keep change uncommitted and move card to `Done` only after verification plus `./restart`.

## Open Questions

- Full page-by-page visual parity can become follow-up work if Alan wants exact `DESIGN.md` treatment on every specialty screen.
