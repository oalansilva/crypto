# Tasks — remover /signals/onchain

## PO Tasks

- [x] Consolidate the refinement input into final removal scope.
- [x] Define explicit acceptance criteria for route, navigation, permissions, and internal references.
- [x] Publish review artifacts for the next stage.

## DESIGN Tasks

- [x] No prototype needed. DESIGN registrado como decisão de remoção sem impacto de nova UX; ver `openspec/changes/remover-signals-onchain/design.md`.

## DEV Tasks

- [x] Remove the `/signals/onchain` route and any direct page wiring.
- [x] Remove menus, links, CTAs, shortcuts, and visible entry points that lead to `/signals/onchain`.
- [x] Remove or adjust capability guards, permissions, internal integrations, and copy tied to `/signals/onchain`.
- [x] Confirm no adjacent signals flow regresses after the removal.

## QA Tasks

- [x] Validate that `/signals/onchain` is no longer reachable through visible navigation.
- [x] Validate direct access and known saved links do not reopen the removed flow.
- [x] Validate adjacent signals areas still work after permission and reference cleanup.
- [x] Attach evidence for impacted entry points and any regression checks performed.

QA evidence captured on 2026-04-20:
- `./backend/.venv/bin/python -m pytest backend/tests/integration/test_ai_dashboard_dynamic.py -q` -> `7 passed`
- `npm --prefix frontend run build` -> passed
- `rg -n "signals/onchain|OnchainSignalsPage|OnchainBacktestPage|OnchainSignalCard|sectionErrors\\.onchain|build_onchain_snapshot" backend/app frontend/src backend/tests frontend/tests` -> no runtime references in the removed flow surface; remaining matches are limited to the standalone on-chain service and its own tests
