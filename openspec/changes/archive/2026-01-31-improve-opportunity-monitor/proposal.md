# Proposal: Simplify Opportunity Monitor - Focus on Hold Status & Distance

## Why
The current opportunity monitor is overly complex with too many status categories (BUY_SIGNAL, BUY_NEAR, EXIT_SIGNAL, EXIT_NEAR, HOLDING, NEUTRAL, etc.). Users need a simple, actionable answer to two key questions:
1. **Is this position currently in HOLD?** (Yes/No)
2. **How many % until the status changes?** (Distance to next signal)

This simplification reduces cognitive load and focuses on what traders actually need to know: whether they have an open position and how close they are to the next actionable signal.

## What Changes
- **Simplified Status Model**: Replace complex status categories with binary `is_holding` (true/false) and `distance_to_next_status` (%)
- **Clear Visual Indicators**: 
  - Green badge = In Hold (open position)
  - Gray badge = Not in Hold (no position)
  - Progress bar showing % remaining until status change
- **Distance Focus**: Always show distance to the next relevant signal:
  - If holding: distance to exit signal
  - If not holding: distance to entry signal
- **Simplified UI**: Remove complex filtering by status types, focus on sorting by distance (closest to signal first)

## Impact
- **Affected specs**: `opportunity-monitor` (simplified capability)
- **Affected code**: 
  - `backend/app/services/opportunity_service.py` - Simplify status calculation to return `is_holding` and `distance_to_next_status`
  - `frontend/src/pages/MonitorPage.tsx` - Simplify UI to show hold status and distance only
  - `frontend/src/components/monitor/OpportunityCard.tsx` - Simplify card to show hold status and distance
  - `frontend/src/components/monitor/types.ts` - Update types to reflect simplified model
