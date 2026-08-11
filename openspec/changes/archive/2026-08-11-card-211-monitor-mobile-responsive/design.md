## Context

The Monitor page currently renders its content inside a table and, at mobile widths, still applies a forced minimum width to the signals grid. That causes horizontal overflow and makes the screen hard to use on phones. The page already has a detailed `OpportunityCard` component that can serve as the mobile surface without changing the underlying Monitor logic.

## Goals / Non-Goals

**Goals:**
- Make `/monitor` usable on phone-sized viewports.
- Show each opportunity in a full card layout on mobile.
- Preserve existing desktop behavior.
- Keep the current opportunity actions and chart entry points available on mobile.

**Non-Goals:**
- Change Monitor filtering, opportunity ranking, or backend APIs.
- Redesign the desktop Monitor table.
- Change chart logic beyond making the page reachable and usable from mobile.

## Decisions

- Reuse `OpportunityCard` as the mobile presentation layer instead of building a second card component.
- Hide the desktop table entirely on narrow screens and render a dedicated mobile card list.
- Normalize spacing, button wrapping, and grid columns inside the detail surface for screens `<= 740px`.

## Risks / Trade-offs

- Rendering both table rows and mobile cards from the same data creates duplicated JSX paths. Mitigation: keep behavior identical by reusing the same props and opportunity component.
- Mobile-only CSS changes can regress desktop spacing if selectors are too broad. Mitigation: scope all layout overrides to the existing mobile breakpoint and Monitor namespace.
