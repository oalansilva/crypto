## Context

Card #103 asks to refactor the Wallet page from the attached `Carteira.html` template. The existing React page already owns the relevant API calls, credential management, filters, sorting, CSV export, and responsive row/card switch. The change is primarily a frontend layout refactor, not a backend contract change.

## Goals / Non-Goals

**Goals:**
- Match the supplied Wallet template structure inside the existing React application.
- Preserve the existing read-only Binance API and credential behavior.
- Keep the screen dense, scannable, and usable for repeated balance inspection.
- Preserve responsive desktop table and mobile card behavior.

**Non-Goals:**
- Add new Binance trading, withdrawal, or mutation behavior.
- Store or reveal secrets beyond the existing masked-key behavior.
- Rework global navigation or unrelated Monitor screens.

## Decisions

- Keep implementation in `ExternalBalancesPage.tsx` instead of adding a parallel static template. This preserves live data, auth, toasts, and route behavior.
- Use local utility classes and small helper functions rather than copying the static CSS files wholesale. This avoids a second design system and keeps the repo's Tailwind/Vite conventions.
- Add allocation share and KPI summaries in the UI from existing balance fields. This avoids backend changes because all required values are already present or derivable from the visible rows.
- Keep CSV export via the existing window event path and add a visible export button in the Wallet page. This exposes existing behavior without expanding the API.

## Risks / Trade-offs

- Template parity can drift because the final UI is React/Tailwind, not the static HTML/CSS. Mitigation: visual validation via browser screenshot.
- Existing E2E selectors may rely on old text or structure. Mitigation: run wallet-specific E2E and update only if the product contract changed.
- Live Binance credentials may be absent in local QA. Mitigation: preserve empty/error states and rely on mocked E2E where available.
