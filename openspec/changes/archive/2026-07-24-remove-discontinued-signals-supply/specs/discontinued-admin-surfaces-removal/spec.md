## ADDED Requirements

### Requirement: Discontinued admin signal and supply surfaces are removed from the product UI
The application SHALL NOT expose the discontinued admin surfaces `/signals`, `/signals/history`, and `/supply-distribution` as navigable product routes, and SHALL NOT show navigation links to those surfaces.

#### Scenario: Admin navigation no longer lists discontinued surfaces
- **WHEN** an authenticated admin opens the principal navigation
- **THEN** the navigation SHALL NOT include links to `/signals`, `/signals/history`, or `/supply-distribution`
- **AND** remaining admin entries such as Combo and Backfill remain available when applicable

#### Scenario: Discontinued routes are not registered
- **WHEN** a client requests `/signals`, `/signals/history`, or `/supply-distribution` in the SPA router
- **THEN** those paths SHALL NOT render the former Signals, Signals History, or Supply Distribution pages

### Requirement: Exclusive discontinued APIs are no longer exposed
The backend SHALL NOT expose the discontinued product APIs used only by those surfaces: `/api/signals*` and `/api/onchain/glassnode/{asset}/supply-distribution`.

#### Scenario: Signals product API is unavailable
- **WHEN** a client calls a former `/api/signals` endpoint
- **THEN** the request SHALL NOT be served by the removed signals product router as a supported capability

#### Scenario: Supply distribution product API is unavailable
- **WHEN** a client calls `GET /api/onchain/glassnode/BTC/supply-distribution`
- **THEN** the backend SHALL NOT expose the former supply-distribution product handler as a supported capability

### Requirement: Active Monitor and Favorites signal history remain intact
Removing the discontinued admin surfaces MUST NOT remove Monitor/Favorites/Combo opportunity `signal_history` behavior used by charts and trade analysis.

#### Scenario: Monitor opportunity signal history helpers remain
- **WHEN** the discontinued admin Signals pages and `/api/signals` product router are removed
- **THEN** Monitor/Favorites/Combo components that consume opportunity `signal_history` (for example chart markers and `SignalHistoryPanel`) SHALL remain available
