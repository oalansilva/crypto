## Context

Favorites can open a cached strategy result on `/combo/results`, while Monitor can open a chart modal for the same strategy. Both surfaces rendered visible parameter objects directly, so internal keys and raw values leaked into the trader-facing UI when the strategy was not protected.

## Goals / Non-Goals

**Goals:**
- Use one shared frontend formatter for common strategy parameter labels and values.
- Apply the formatter to Favorites result charts and Monitor chart details.
- Preserve protected-user redaction.
- Keep the fix UI-only; no API payload or database changes.

**Non-Goals:**
- Rename backend fields.
- Change optimization, scoring, saved favorite payloads, or monitor signal logic.
- Translate every possible custom parameter beyond the known keys in this correction.

## Decisions

- Add a shared `strategyParameters` frontend helper instead of duplicating label maps in each component.
- Keep unknown parameter labels readable by replacing underscores with spaces, so custom strategy parameters remain visible without hard failures.
- Format percentage-like numeric values defensively: values between -1 and 1 are displayed as percentages, while values already expressed as percentages stay in percent scale.
- Add `data-testid` selectors to parameter containers so E2E assertions can target the intended UI block without coupling to surrounding chart text.

## Risks / Trade-offs

- New custom keys can still appear in English if they are not in the label map. Mitigation: fallback remains readable, and future keys can be added centrally.
- `long` and `short` are translated as `Compra` and `Venda` for trader readability. Mitigation: this matches the existing signal language used elsewhere in the product.
