## Context

Card #222 is a frontend UX change for beta onboarding. The app already has a protected shell, primary navigation, Monitor and Favorites as core workflows, and a responsible product disclaimer on Monitor/Login. There is no persistent, user-accessible explanation of the recommended first-use journey.

## Goals / Non-Goals

**Goals:**
- Give a new user an obvious starting path on first access, beginning with Favorites instead of wallet setup.
- Make Help accessible later through navigation.
- Explain Monitor and Favorites with concise Portuguese copy.
- Keep guidance inside the product and aligned with `DESIGN.md`.
- Add focused automated coverage.

**Non-Goals:**
- Create a full course, video hosting, external documentation, or support automation.
- Change signal, backtest, metric, favorite, or monitor business rules.
- Send external messages or automate beta invitations.
- Add backend persistence for guide dismissal.

## Decisions

- Use a persistent `/help` route plus a local dismissible first-use panel in the protected layout.
  - Rationale: covers first access and later lookup without backend migration.
  - Alternative considered: modal tour. Rejected for now because it blocks trading workflow and increases interaction complexity.
- Store dismissal in `localStorage`.
  - Rationale: sufficient for a beta guidance prompt and reversible by clearing browser storage.
  - Alternative considered: user-profile preference. Rejected because it requires backend/model changes outside the card's current value.
- Use concise panels instead of long documentation.
  - Rationale: the app is an operational trading workspace; first viewport should stay focused on actions and status.
- Put Binance wallet setup after Monitor as optional guidance.
  - Rationale: the updated user story says the user must reach strategy selection and monitoring before any wallet configuration.
- Use existing design tokens/classes and lucide icons.
  - Rationale: preserves the Binance-inspired system layout in `DESIGN.md`.

## Risks / Trade-offs

- First-use state is per browser, not per account -> acceptable for beta; Help remains permanently available.
- Extra copy can crowd small screens -> mitigate with compact sections, wrapping layout, and responsive tests.
- Overexplaining signals could sound like recommendation -> copy explicitly frames the product as decision support, not financial advice or guaranteed result.
