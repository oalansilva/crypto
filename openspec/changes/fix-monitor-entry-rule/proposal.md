## Why

The /monitor dashboard is marking entries incorrectly, which misleads users about when a strategy should trigger an entry. We need to align the entry signal with the intended crossover + trend rule.

## What Changes

- Fix the entry signal logic to require:
  - crossover **short/long** OR **short/medium**, AND
  - **trend up** (short > long).
- When **trend up is false**, /monitor must measure **distance to entry** using the **short-to-long** pair (red → blue), not the entry pair.
- When **trend up is true**, /monitor should measure entry distance based on **short crossing medium** (red → orange).
- Ensure /monitor displays the corrected entry status based on the rule above.

## Capabilities

### New Capabilities


### Modified Capabilities
- `opportunity-monitor`: Update the entry signal rule used by /monitor.

## Impact

- Backend signal/indicator evaluation for the opportunity monitor.
- Possibly any shared entry-condition utilities used by /monitor.
