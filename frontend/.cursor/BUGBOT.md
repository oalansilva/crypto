# Review rules — frontend

Included when the reviewed diff touches `frontend/`.

- Follow `DESIGN.md` tokens, density, and the authenticated app shell. Do not invent a parallel layout.
- User-visible "validator" copy must remain **Trader**.
- UI changes require Playwright visual coverage (`frontend/tests/e2e/**`) or an auditable Alan dispensation.
- Do not hardcode secrets or Binance credentials in client code.
- Prototypes live in `frontend/public/prototypes/<slug>/` and are not OpenSpec Gist artifacts.
