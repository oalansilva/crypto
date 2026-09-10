## ADDED Requirements

### Requirement: Sale blocked by an open protective stop offers removal in the sell flow
When a Spot sale as operation is blocked by an open protective Spot stop SELL on the symbol, the sell flow MUST offer Remover stop there with its own explicit confirmation. After removal, the sale MUST follow the normal flow (new preview, review, confirmation). Removal MUST never submit the sale on its own.

#### Scenario: Blocked sale offers removal in place
- **WHEN** the user attempts `Vender 100%` for a Posicionado (HOLD) symbol and the preview/submission fails signalling balance locked by an open protective stop
- **THEN** the sell panel MUST show that the sale is blocked by the open stop and MUST offer Remover stop without leaving the sell flow

#### Scenario: Removal inside the sell flow requires its own confirmation
- **WHEN** the user activates Remover stop from the blocked-sale state
- **THEN** the UI MUST show a confirmation identifying the stop (quantity, stop price, limit price, origin — app labeled explicitly e.g. "criada no app (Farol)", externa keeps its label) before calling the cancel API
- **AND** opening the confirmation MUST move focus to it (focusable container `tabindex="-1"` or primary button) with an adequate accessible signal (`role="group"` + `aria-label`, trigger `aria-expanded`/`aria-controls`); closing it (Voltar or confirmar) MUST return focus to the trigger (or to the next step when the trigger is gone)
- **AND** cancelling that confirmation MUST keep the sale unsubmitted

#### Scenario: After removal the sale follows the normal flow
- **WHEN** the stop has been removed from the blocked-sale state
- **THEN** the panel MUST return to sale entry and REQUIRE a fresh preview, review and explicit sale confirmation before submitting anything

#### Scenario: Removal never sells alone
- **WHEN** the user confirms Remover stop inside the sell flow
- **THEN** the system MUST cancel only the stop order and MUST NOT submit the sale

#### Scenario: Non-stop sale failures do not offer removal
- **WHEN** a sale fails for a reason other than an open protective stop (e.g. lot/notional filters, credentials, connectivity)
- **THEN** the UI MUST NOT offer Remover stop and MUST keep the existing failure path
