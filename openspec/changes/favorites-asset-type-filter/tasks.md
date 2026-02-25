## 1. Favorites Filter UI

- [x] 1.1 Add an Asset Type dropdown to the Favorites filter bar with options All/Crypto/Stocks
- [x] 1.2 Ensure the dropdown has default value All and matches the styling of existing filters

## 2. Filtering Logic

- [x] 2.1 Add `assetTypeFilter` state to FavoritesDashboard
- [x] 2.2 Implement filtering rules (Crypto if symbol contains '/', otherwise Stocks)
- [x] 2.3 Apply the filter consistently to both mobile and desktop layouts

## 3. Tests

- [x] 3.1 Add/update a Playwright E2E test to validate the Asset Type dropdown filters the list

## 4. Validation

- [x] 4.1 Run `openspec validate favorites-asset-type-filter --type change`

> Note: Use project skills (.codex/skills) when applicable for frontend work, tests, and verification.
