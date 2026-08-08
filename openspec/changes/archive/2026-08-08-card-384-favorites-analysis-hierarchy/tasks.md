## 1. Development Gate

- [x] 1.1 Confirm that Alan approved the current `design.md` and prototype by moving card #384 from `Aprovação de Design` to `Pronto para Dev`
- [x] 1.2 Move card #384 to `Em desenvolvimento` and run the OpenSpec apply instructions before changing production code

## 2. Result Page Hierarchy

- [x] 2.1 Refactor `ComboResultsPage` to render the decision summary, permanent rules, chart, technical disclosure, signal history and trades in the specified order
- [x] 2.2 Remove the duplicated winning-configuration parameter grid while preserving every canonical value in the technical disclosure
- [x] 2.3 Add the responsive strategy identity and metrics summary with complete wrapping for long descriptions
- [x] 2.4 Translate remaining legacy result-page labels to approved Portuguese equivalents

## 3. Transparency Ownership

- [x] 3.1 Refactor `StrategyTransparencyPanel` as the only detailed presentation of indicator function, participation, configuration, effective parameters and availability
- [x] 3.2 Refactor `StrategyChartSurface` to keep series identity and reference-candle values without rendering a second complete technical manifest
- [x] 3.3 Preserve entry, exit and risk rules in `StrategyRuleOverview` without parameter-card duplication
- [x] 3.4 Implement localized unavailable states for missing manifest, candles, timestamped series and Monitor synchronization

## 4. Responsive and Accessibility Verification

- [x] 4.1 Add or update component tests proving each technical heading and effective parameter has one visual owner
- [x] 4.2 Add desktop and mobile Playwright coverage for description wrapping, technical disclosure, chart controls, trades and no horizontal page overflow
- [x] 4.3 Verify keyboard order, focus visibility, accessible names, 44 px mobile targets and WCAG AA contrast
- [x] 4.4 Update intentional visual baselines on Linux and review only generated diffs

## 5. Delivery Evidence

- [x] 5.1 Run focused frontend tests, build, OpenSpec change validation and `openspec validate --all`
- [x] 5.2 Run `/opsx:verify`, update this checklist and record any justified deviations
- [x] 5.3 Move the card through `Code Review` and `QA`, obtain green `qa-gate` and Playwright visual checks, and integrate the reviewed SHA into `develop`
- [x] 5.4 Run `./restart`, validate the served Favorites analysis URL and only then move card #384 to `Done`

## 6. Feedback After Technical Completion

- [x] 6.1 Clarify the permanent-rules heading and helper text without changing the strategy meaning
- [x] 6.2 Make the results-page operation disclosure event-specific, with the label `Ver decisão da operação` and no repeated permanent-rule overview
- [x] 6.3 Preserve the shared Monitor presentation and add focused regression coverage for both contexts
- [x] 6.4 Re-run review, QA, integration into `develop`, restart and served-URL validation while keeping card #384 in `Done`

## 7. Remove Legacy Copy From Shared Surfaces

- [x] 7.1 Replace the shared `StrategyRuleOverview` defaults so the legacy title and helper text have zero occurrences in production source
- [x] 7.2 Apply `Ver decisão da operação` and event-specific disclosure content to Monitor as well as Favorites
- [x] 7.3 Update functional and visual coverage for Favoritos and Monitor, including explicit absence assertions for the legacy copy
- [x] 7.4 Re-run review, QA, integration into `develop`, restart and served-runtime validation while keeping card #384 in `Done`

## 8. Remove Per-Operation Decision Disclosure

- [x] 8.1 Remove `TradeExplanationDisclosure` from desktop and mobile operation rows in Favoritos and Monitor without changing operation facts or payload contracts
- [x] 8.2 Remove the now-unused disclosure component and add regression assertions that `Ver decisão da operação` and its panels are absent
- [x] 8.3 Update and review affected visual baselines for Favoritos and Monitor, then run focused tests, build and all OpenSpec validations
- [x] 8.4 Re-run Code Review, QA, integration into `develop`, restart and served-runtime validation while keeping card #384 in `Done`

## 9. Remove Duplicate Signal History and Normal-State Copy

- [x] 9.1 Remove the separate signal-history panel and all of its states from Favorites while preserving canonical Monitor signals as graph markers and preserving the Monitor surface
- [x] 9.2 Remove `Série disponível para o timeframe atual.` while preserving unavailable, absent and incompatible series messages
- [x] 9.3 Add focused absence and marker regressions, then run unit, Playwright, visual, build, lint and OpenSpec validation
- [x] 9.4 Re-run Code Review, QA, integration into `develop`, restart and served-runtime validation while keeping card #384 in `Done`

## Verification Notes

- `/opsx:verify` executed on 2026-08-06 with all 5 requirements and 8 scenarios mapped to implementation and automated evidence.
- `/opsx:verify` repeated on 2026-08-07: all 5 requirements and 11 scenarios map to implementation and automated evidence; focused functional tests, the 16-snapshot visual suite, the frontend build and all 146 OpenSpec validations pass. Only the operational integration/runtime task 7.4 remains pending before the served result can be considered complete.
- Operational evidence on 2026-08-07: PR #389 passed every initiated check, including `qa-gate` and Playwright, and was squash-merged into `develop` as `9376731c`; `./restart` built and served `index-Ck8RSED1.js`, `/api/health` returned `ok`, local and public `/favorites` returned HTTP 200, and the served bundle contains the approved labels with zero legacy-copy matches. Card #384 remained in `Done` throughout the correction.
- No functional or API-contract deviation was found. All implementation and operational delivery tasks are complete in `develop`.
- Visual ownership remains scoped to each surface: Favoritos owns its permanent overview above the graph, while shared Monitor and Favoritos operation lists contain only execution facts and render no per-operation disclosure.
- Tasks 5.3 and 5.4 were completed by PR #386, merged into `develop` as `019ef7712ad4538fa5bc2a6d311e8a8fb25b9fc9`, followed by restart and runtime validation.
- Section 6 records copy and disclosure refinements requested after technical completion; the card remains in `Done` under the non-regression status rule.
- `/opsx:verify` repeated before integration on 2026-08-07: all 5 requirements and 9 scenarios mapped to implementation and automated coverage; at that checkpoint, only the post-review integration/restart task 6.4 was pending.
- Feedback refinement merged through PR #387 as `1ace63653d694448b9a8f9d0a8e56ec814e66b6d`; all CI checks passed, `./restart` completed, `/api/health` returned `status: ok`, and the public `/favorites` route served bundle `index-Dy8JaFU-.js` with the updated copy. Task 6.4 is complete and card #384 remained in `Done`.
- Section 8 records Alan's final feedback to remove the per-operation decision control entirely while preserving the operation list and data contracts; the card remains in `Done` under the non-regression rule.
- `/opsx:verify` repeated locally for section 8 on 2026-08-07: all 5 requirements and 11 scenarios map to the implementation; 35 unit tests, 6 focused Playwright scenarios, 16 visual snapshots, the frontend build, focused lint and all 146 OpenSpec validations pass. Only operational task 8.4 remains pending before served-runtime completion.
- Operational evidence for section 8 on 2026-08-07: PR #391 passed every initiated check, including `qa-gate` and Playwright, and was squash-merged into `develop` as `49e3357c`; `./restart` built and served `index-C3GcTgTT.js`, `/api/health` returned `ok`, local and public `/favorites` returned HTTP 200, and the served bundle has zero matches for the removed action/component. Card #384 remained in `Done`.
- Section 9 implements Alan's follow-up feedback: Favoritos consumes Monitor history only as graph markers, removes the duplicate history/sync panel, and omits positive series-availability copy while retaining exceptional states. Local evidence: 35 unit tests, all 20 Favoritos functional scenarios, all 16 visual snapshots, focused lint and the frontend build pass. Only operational task 9.4 remains pending before served-runtime completion.
- Operational evidence for section 9 on 2026-08-07: PR #393 passed every initiated required check, including `qa-gate` and Playwright, and was squash-merged into `develop` as `631c375c`; `deploy-staging` was correctly not applicable because its workflow condition only permits pushes to `develop`. `./restart` built and served `index-k53MGBtS.js`, both local and public `/api/health` returned `ok`, local and public `/favorites` returned HTTP 200, and the served bundle has zero matches for the removed panel/copy while retaining the chart marker contract. Card #384 remained in `Done` throughout the correction.
