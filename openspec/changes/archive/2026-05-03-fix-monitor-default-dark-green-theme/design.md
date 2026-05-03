## Context

The archived `monitor-dark-green-theme` change and current specs define `dark-green` as the Monitor default. Card #100 shows the QA path can still observe `monitor-theme--black` on first load, so the client must treat missing or invalid global theme data as `dark-green`.

## Goals / Non-Goals

**Goals:**

- Keep `dark-green` as the Monitor fallback theme.
- Preserve `black` only when it is explicitly stored as the global preference.
- Validate the default and persistence paths with existing E2E tests.

**Non-Goals:**

- Add new themes.
- Change Monitor layout, palette tokens, or backend API shape.
- Archive or release this change before Alan homologates it.

## Decisions

- Use the existing `DEFAULT_MONITOR_THEME` and `normalizeMonitorTheme` helpers as the single frontend fallback path.
- Keep theme state derived from `preferences[__global__].theme`; do not introduce separate local UI state.
- Validate with `monitor-theme.spec.ts` because it reproduces both initial default and persisted global preference behavior.

## Risks / Trade-offs

- Existing user data with `theme: black` remains respected. This is intentional so the fix does not erase explicit preferences.
- If backend returns stale `black` for `__global__`, the frontend will still show black because that is a valid stored preference. Backend cleanup is out of scope for this card.
