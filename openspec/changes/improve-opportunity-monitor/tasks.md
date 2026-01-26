# Tasks: Simplify Opportunity Monitor

## 1. Backend Simplification
- [ ] 1.1 Update `opportunity_service.py` to return simplified model:
  - [ ] 1.1.1 Add `is_holding` boolean field (true if last signal was buy and no exit)
  - [ ] 1.1.2 Add `distance_to_next_status` field (distance to exit if holding, distance to entry if not)
  - [ ] 1.1.3 Remove complex status logic, keep only hold detection
- [ ] 1.2 Update API response model in `opportunity_routes.py`:
  - [ ] 1.2.1 Update `OpportunityResponse` to include `is_holding` and `distance_to_next_status`
  - [ ] 1.2.2 Remove or deprecate complex `status` field (keep for backward compatibility initially)

## 2. Frontend Simplification
- [ ] 2.1 Update `types.ts`:
  - [ ] 2.1.1 Add `is_holding: boolean`
  - [ ] 2.1.2 Add `distance_to_next_status: number`
  - [ ] 2.1.3 Keep `status` field for migration period but mark as deprecated
- [ ] 2.2 Simplify `OpportunityCard.tsx`:
  - [ ] 2.2.1 Replace status badge with simple HOLD/WAIT badge (green/gray)
  - [ ] 2.2.2 Show distance as "X% to exit" or "X% to entry" based on `is_holding`
  - [ ] 2.2.3 Update progress bar to show distance to next status
  - [ ] 2.2.4 Simplify color scheme: green for HOLD, gray for WAIT
- [ ] 2.3 Simplify `MonitorPage.tsx`:
  - [ ] 2.3.1 Remove status-based filtering UI
  - [ ] 2.3.2 Keep only distance-based sorting (default: closest first)
  - [ ] 2.3.3 Add optional sort by symbol
  - [ ] 2.3.4 Group visually: HOLD positions at top (or separate section), WAIT below
  - [ ] 2.3.5 Remove complex status grouping logic

## 3. Testing & Verification
- [ ] 3.1 Test with strategies in HOLD state
- [ ] 3.2 Test with strategies waiting for entry
- [ ] 3.3 Verify distance calculations are correct
- [ ] 3.4 Verify sorting by distance works correctly
- [ ] 3.5 Manual verification: Compare with actual chart positions
