---
name: crypto-frontend
description: Default frontend skill for the crypto project. Use for any task that creates, edits, reviews, or validates UI in /root/.openclaw/workspace/crypto/frontend, including React components, CSS, responsive layout, charts, dashboards, Monitor screens, Playwright visual checks, and frontend UX polish.
---

# Crypto Frontend

## Operating Rule

Use this skill as the first frontend reference for this repo. Apply it before editing `frontend/` code, reviewing UI changes, or validating a browser-facing workflow.

## Project Fit

- Treat this product as an operational crypto/trading tool, not a marketing site.
- Prefer dense, scannable, utilitarian screens for repeated work: tables, filters, charts, compact panels, clear states.
- Keep Monitor and trading workflows quiet and information-first. Avoid decorative hero sections, oversized copy, ornamental cards, and visual filler.
- Preserve existing component conventions before inventing new layout patterns.
- Use the UI label `Trader` when a validator-like concept appears in copy.

## Frontend Quality Bar

1. Map the current screen/component structure before changing it.
2. Keep the first visible screen usable, not explanatory. Build the actual workflow surface.
3. Use familiar controls:
   - icons for tool actions,
   - segmented controls for modes,
   - toggles or checkboxes for binary settings,
   - selects or menus for option sets,
   - tabs for views,
   - text buttons only for explicit commands.
4. Use `lucide-react` icons when an icon exists in the library.
5. Keep cards for repeated items, modals, and framed tools. Do not nest cards inside cards or turn page sections into floating cards.
6. Keep card radius at 8px or less unless the existing component requires otherwise.
7. Ensure text never overlaps, clips, or depends on viewport-scaled font sizes. Use responsive constraints, wrapping, and stable dimensions.
8. Avoid one-note palettes and default generated UI themes: purple-heavy gradients, beige-only palettes, dark slate-only palettes, decorative orbs, bokeh blobs, and generic SVG hero art.
9. For dashboards, charts, boards, toolbars, tiles, and counters, define stable dimensions with grid tracks, min/max widths, or aspect ratios so loading and hover states do not shift layout.
10. Do not add visible instructional copy about how the UI works unless it is necessary for task completion.

## Implementation Workflow

1. Inspect existing files in `frontend/src`, nearby CSS, tests, and component usage.
2. Identify the user workflow and the smallest UI surface that needs to change.
3. Implement with existing project patterns, components, API helpers, and CSS naming style.
4. Check responsive behavior for desktop and mobile breakpoints when layout changes.
5. For visual or interaction changes, validate with:
   - `npm --prefix frontend run build`
   - relevant Playwright tests in `frontend/tests/*.spec.ts` when present or affected
   - a browser screenshot/manual check when the visual risk is meaningful.
6. Report what changed and which validation passed. If a check was skipped, say why.

## Visual Validation

Use Playwright or browser inspection when a change affects layout, interaction, charts, canvas, responsive behavior, or first-screen composition.

Verify:
- primary content is visible above the fold,
- controls are clickable and not overlapped,
- text fits in buttons, cards, tables, and toolbars,
- charts/canvas/media are nonblank and correctly framed,
- desktop and mobile layouts remain usable.

## Source Guidance

This skill adapts the OpenAI frontend prompt guidance for this repo: build with empathy for the target audience, avoid common generated-UI defaults, use complete controls and states, prefer real workflow surfaces over landing pages, and validate visual output before finishing.
