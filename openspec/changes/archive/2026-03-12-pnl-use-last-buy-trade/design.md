## Design

No dedicated UI redesign is required for this change.

The user-facing impact is behavioral:
- `/external/balances` should continue using the existing layout.
- Only the purchase reference behind displayed PnL changes.
- If the page labels the buy reference explicitly, the displayed value must match the latest buy trade for the asset.

Validation should focus on correctness of numbers rather than new interface structure.
