# improve-wallet-screen (prototype)

Static HTML/CSS/JS prototype for **Wallet / External Balances** (`/external/balances`).

Goals:
- scan-first hierarchy (Total + as_of timestamp)
- mobile-friendly (cards) + desktop table
- search, filters (locked-only + dust threshold), sorting
- visible states: default, empty, loading, error (toast)

Open:
- `frontend/public/prototypes/improve-wallet-screen/index.html`

Notes for DEV:
- JS uses fake data; real implementation should map API fields into the same UI structure.
- PnL is explicitly shown as **partial** (backend only computes for top N symbols).
