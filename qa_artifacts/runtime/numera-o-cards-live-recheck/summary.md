# QA recheck — numera-o-cards

Result: FAIL

## API live
- `/api/workflow/kanban/changes?project_slug=crypto`
  - change `numera-o-cards` still has no `card_number` field in the board payload.
- `/api/workflow/projects/crypto/changes/numera-o-cards`
  - change payload still has no `card_number` field.

## UI live
- Board `/kanban`: `#16` did not appear on the visible board card.
- Drawer `/kanban`: `#16` did appear after opening the card details.
- After reload: board still did not show `#16`.

## Verdict
- Blocker remains in live runtime because API + board are still inconsistent with the expected fix.
- Keep change in `QA`.

## Evidence
- Board payload: http://72.60.150.140:5173/qa-artifacts/runtime/numera-o-cards-live-recheck/01-board.json
- Change payload: http://72.60.150.140:5173/qa-artifacts/runtime/numera-o-cards-live-recheck/02-change.json
- Runtime summary: http://72.60.150.140:5173/qa-artifacts/runtime/numera-o-cards-live-recheck/summary.md
- UI initial board: http://72.60.150.140:5173/qa-artifacts/playwright/numera-o-cards-live-recheck/01-board-initial.png
- UI drawer open: http://72.60.150.140:5173/qa-artifacts/playwright/numera-o-cards-live-recheck/02-drawer-open.png
- UI board after reload: http://72.60.150.140:5173/qa-artifacts/playwright/numera-o-cards-live-recheck/03-board-after-reload.png
- UI summary JSON: http://72.60.150.140:5173/qa-artifacts/playwright/numera-o-cards-live-recheck/summary.json
