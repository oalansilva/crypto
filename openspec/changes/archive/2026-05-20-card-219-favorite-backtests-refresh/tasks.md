## Tasks

- [x] Add persistence fields for favorite automatic refresh status.
- [x] Implement internal favorite backtest refresh service using saved favorite configuration.
- [x] Start and stop the refresh loop from the runtime worker.
- [x] Expose refresh metadata through the Favorites API and UI.
- [x] Add focused backend tests for refresh success/failure and worker wiring.
- [x] Run OpenSpec validation, backend tests, and frontend build.
- [x] Reject stale candle refresh results so delisted/inactive pairs do not appear successfully updated.
- [x] Prepare required market data before running favorite backtest recalculation.
- [x] Prioritize recent tail candle updates before older missing-history backfill.
