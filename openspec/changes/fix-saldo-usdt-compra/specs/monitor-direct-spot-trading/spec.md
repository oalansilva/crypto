## MODIFIED Requirements

### Requirement: Purchase uses a user-entered USDT amount
The direct purchase SHALL submit a Binance Spot `BUY MARKET` order using `quoteOrderQty` equal to the confirmed USDT amount entered by the user, and SHALL validate the amount against the current available free USDT balance correctly populated from the authenticated user's Binance account. A balance that is not yet loaded or fails to load SHALL NOT be treated as zero for validation purposes.

#### Scenario: Confirm a valid purchase amount
- **WHEN** the user enters a positive USDT amount within the available free USDT balance and confirms the purchase
- **THEN** the backend SHALL submit `BUY MARKET` with that amount as `quoteOrderQty`
- **AND** the order SHALL use the authenticated user's Binance credentials

#### Scenario: Reject invalid purchase amount
- **WHEN** the USDT amount is empty, non-numeric, non-positive, above the free USDT balance, or below/above an applicable symbol notional filter
- **THEN** the UI and backend SHALL reject the request before order submission with an actionable message

#### Scenario: Purchase allowed with sufficient free USDT balance
- **WHEN** the user enters a USDT amount that is at or below the currently loaded free USDT balance
- **THEN** the backend SHALL NOT raise `Saldo livre em USDT insuficiente` solely because the balance field was unpopulated, missing or stale in the preview payload
- **AND** the backend SHALL re-read the current free USDT balance from Binance before submission

#### Scenario: Balance loading failure is explicit, not zero
- **WHEN** the free USDT balance cannot be loaded from Binance before a purchase validation
- **THEN** the system SHALL surface an explicit loading or failure state in the UI and SHALL NOT treat the missing balance as zero USDT
- **AND** the purchase validation SHALL fail closed with a clear balance-availability message rather than an insufficient-balance message

### Requirement: Direct orders validate exchange rules and fail closed
The backend SHALL validate the current symbol status, supported order type, quote/base assets, balances and applicable `MARKET_LOT_SIZE`, `LOT_SIZE`, `MIN_NOTIONAL` and `NOTIONAL` rules before submitting an order. Credentials SHALL require Spot Trade permission and SHALL never fall back to system-wide exchange secrets. Balance validation SHALL use the same free-balance source and semantics as the balance surfaced to the user in the trading surface, so the UI and backend never diverge on what free USDT is available.

#### Scenario: Missing or read-only credentials
- **WHEN** Binance credentials are missing, invalid or lack Spot Trade permission
- **THEN** the request SHALL fail closed with guidance to configure a trade-capable key in Meu Perfil
- **AND** the guidance SHALL never request withdraw permission

#### Scenario: Symbol or balance changes before confirmation completes
- **WHEN** the symbol becomes unavailable or the relevant free balance changes between setup and final submission
- **THEN** the backend SHALL use current Binance data, reject stale invalid values, and return the updated reason without submitting an unsafe order

#### Scenario: Balance source mismatch is prevented
- **WHEN** the trading surface displays a free USDT balance for a purchase
- **THEN** the displayed value SHALL match the free USDT balance source used by backend validation for that user
- **AND** balances that are not tradeable Spot free USDT (e.g. Simple Earn or locked funds) SHALL NOT be presented as available for purchase

#### Scenario: Sensitive data is protected
- **WHEN** any direct order succeeds or fails
- **THEN** API keys, secrets, signatures, raw signed URLs and private Binance payloads SHALL NOT be returned to the frontend or written to user-visible logs/errors

### Requirement: Real orders require an explicit review and confirmation
The UI SHALL separate order setup from final confirmation and SHALL make the real, market-priced and potentially irreversible nature of the operation unambiguous. The review SHALL always display the available free USDT balance or an explicit loading/failure state; an empty balance field SHALL NOT accompany an insufficient-balance validation error.

#### Scenario: Review purchase before submission
- **WHEN** the user advances from a valid purchase amount
- **THEN** the confirmation SHALL show symbol, `Comprar`, entered USDT amount, available USDT balance, indicative asset quantity, market-price variation warning and the final confirmation action

#### Scenario: Review sale before submission
- **WHEN** the user advances to sell
- **THEN** the confirmation SHALL show symbol, `Vender 100%`, refreshed free base-asset balance, indicative USDT value, possible residual/fee notice, market-price variation warning and the final confirmation action

#### Scenario: Review shows balance always
- **WHEN** the review step renders the available USDT balance
- **THEN** the UI SHALL display either the numeric free balance or an explicit `carregando`/`indisponível` state
- **AND** the UI SHALL NOT show an empty balance label together with an insufficient-balance error

#### Scenario: Cancel confirmation
- **WHEN** the user cancels or closes the confirmation
- **THEN** no order SHALL be submitted and the user SHALL return to a safe Monitor state
