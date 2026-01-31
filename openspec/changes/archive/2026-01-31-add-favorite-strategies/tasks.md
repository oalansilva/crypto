# Tasks

1.  Backend: Data Layer
    -   Define SQLAlchemy model `FavoriteStrategy` in `backend/app/models/favorite.py`.
    -   Create migration script (or update `init_db.py` for SQLite).
    -   Validate model schema matches requirements (name, symbol, timeframe, parameters, metrics).
2.  Backend: API Layer
    -   Implement `GET /api/favorites` (List).
    -   Implement `POST /api/favorites` (Create).
    -   Implement `DELETE /api/favorites/{id}` (Delete).
    -   Add Pydantic schemas in `backend/app/schemas/favorite.py`.
3.  Frontend: Favorites Dashboard
    -   Create `FavoritesDashboard.tsx` page.
    -   Implement fetching and displaying the list of favorites.
    -   Implement "Delete" action.
4.- [x] Create reusable "Save to Favorites" button component (`frontend/src/components/SaveFavoriteButton.tsx`)
    - [x] Input modal for Name/Notes
    - [x] API integration
- [x] Add Save button to Optimization Results
    - [x] `frontend/src/components/optimization/ParameterOptimizationResults.tsx`
    - [x] Pass `timeframe` prop correctly
- [x] Develop "Saved Strategies" Dashboard Page
    - [x] List favorites (`GET /api/favorites/`)
    - [x] Delete functionality
- [x] Implement Re-run Logic
    - [x] Redirect to optimization page with pre-filled parameters
- [x] Develop Comparison View
    - [x] Select multiple strategies
    - [x] Side-by-side comparison table

## 4. Verification
- [x] Verify saving a strategy works
- [x] Verify listing favorites works
- [x] Verify re-running a strategy populates the form correctly
- [x] Verify comparison view shows correct datact parameters.
