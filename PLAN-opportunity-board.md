# PLAN-opportunity-board - Strategy Monitoring & Alerts

> **Status**: APPROVED
> **Mode**: PLANNING
> **Agent**: project-planner

## Overview
Implement a "Strategy Monitoring" feature (Opportunity Board) that analyzes a user's saved favorite strategies and visualizes their proximity to entry signals on the Daily (1D) timeframe.

**Problem**: Users miss entries because they cannot monitor all their favorite strategies 24/7.
**Solution**: A backend engine that calculates "Signal Proximity" and a frontend dashboard that ranks opportunities.

## Project Type
**WEB + BACKEND** (Full Stack)
- Agents: `backend-specialist` (API/Logic), `frontend-specialist` (UI/Dashboard).

## Success Criteria
1. **Accuracy**: "Approaching" logic correctly identifies setups within defined thresholds (e.g. <1% from MA).
2. **Performance**: API returns opportunities for 10-20 favorites in under 2 seconds.
3. **UX**: Dashboard clearly distinguishes between "Active Signal", "Approaching", and "Neutral".

## Tech Stack
- **Backend**: Python, FastAPI, Pandas-TA (for proximity calc).
- **Frontend**: React, TailwindCSS (for Dashboard).
- **Database**: SQLite (existing) to fetch Favorites.

## File Structure
```
backend/
  app/
    services/
      opportunity_service.py       # [NEW] Proximity logic engine
    routes/
      opportunity_routes.py        # [NEW] GET /opportunities
    strategies/
      combos/
        proximity_analyzer.py      # [NEW] Heuristic logic extraction

frontend/
  src/
    pages/
      MonitorPage.tsx              # [NEW] Dashboard Page
    components/
      monitor/
        OpportunityCard.tsx        # [NEW] Individual Strategy Card
```

## Task Breakdown

### Phase 1: Backend Implementation (P1)
**Agent**: `backend-specialist`

#### Task 1.1: Create Proximity Logic Engine
- **Input**: DataFrame + Strategy Params (MA lengths, etc.)
- **Output**: `proximity_analyzer.py` with `analyze_proximity(df, params)` function returning status (SIGNAL, NEAR, FAR) and metrics (distance %).
- **Verify**: Unit test with mock DF where price is 0.5% below MA. Expect "NEAR".

#### Task 1.2: Implement Opportunity Service
- **Input**: User Favorites List
- **Output**: `opportunity_service.py` that loops favorites, fetches 1D data, calls analyzer.
- **Verify**: Call `get_opportunities` with 1 favorite. Returns dict with status.

#### Task 1.3: Create API Endpoint
- **Input**: `GET /api/opportunities` request.
- **Output**: JSON response with list of ranked opportunities.
- **Verify**: `curl localhost:8000/api/opportunities` returns 200 OK and JSON list.

### Phase 2: Frontend Implementation (P2)
**Agent**: `frontend-specialist`

#### Task 2.1: Create Opportunity Card Component
- **Input**: `Opportunity` interface (Symbol, Strategy Name, Status, Metrics).
- **Output**: `OpportunityCard.tsx` showing visual badge and key data.
- **Verify**: Visual check. Green badge for Signal, Yellow for Near.

#### Task 2.2: Build Monitor Dashboard Page
- **Input**: `MonitorPage.tsx` structure.
- **Output**: Page fetching API data and mapping to Grid of Cards.
- **Verify**: Page loads, fetches data, displays cards.

### Phase 3: Integration & Polish (P3)
**Agent**: `frontend-specialist` + `backend-specialist`

#### Task 3.1: Sort & Filter Logic
- **Input**: Raw list of opportunities.
- **Output**: Sort by "Status Priority" (Signal > Near > Far).
- **Verify**: Signals appear at top of list.

#### Task 3.2: Error Handling & Loading States
- **Input**: API failure / Slow network.
- **Output**: Skeleton loaders and Error Toasts.
- **Verify**: Disconnect backend, refresh page. See clean error message.

## Phase X: Verification
- [ ] Lint Check (`npm run lint`, `flake8`)
- [ ] Security Scan (No exposed secrets)
- [ ] Build Check (`npm run build`)
- [ ] E2E Test (User opens Monitor -> Sees Opportunities)
- [ ] Manual Check: Verify "Approaching" math on a live chart (e.g. TradingView) vs Dashboard.
