## 1. Development Gate

- [ ] 1.1 Confirm that Alan approved the current `design.md` and prototype by moving card #384 from `Aprovação de Design` to `Pronto para Dev`
- [ ] 1.2 Move card #384 to `Em desenvolvimento` and run the OpenSpec apply instructions before changing production code

## 2. Result Page Hierarchy

- [ ] 2.1 Refactor `ComboResultsPage` to render the decision summary, permanent rules, chart, technical disclosure, signal history and trades in the specified order
- [ ] 2.2 Remove the duplicated winning-configuration parameter grid while preserving every canonical value in the technical disclosure
- [ ] 2.3 Add the responsive strategy identity and metrics summary with complete wrapping for long descriptions
- [ ] 2.4 Translate remaining legacy result-page labels to approved Portuguese equivalents

## 3. Transparency Ownership

- [ ] 3.1 Refactor `StrategyTransparencyPanel` as the only detailed presentation of indicator function, participation, configuration, effective parameters and availability
- [ ] 3.2 Refactor `StrategyChartSurface` to keep series identity and reference-candle values without rendering a second complete technical manifest
- [ ] 3.3 Preserve entry, exit and risk rules in `StrategyRuleOverview` without parameter-card duplication
- [ ] 3.4 Implement localized unavailable states for missing manifest, candles, timestamped series and Monitor synchronization

## 4. Responsive and Accessibility Verification

- [ ] 4.1 Add or update component tests proving each technical heading and effective parameter has one visual owner
- [ ] 4.2 Add desktop and mobile Playwright coverage for description wrapping, technical disclosure, chart controls, trades and no horizontal page overflow
- [ ] 4.3 Verify keyboard order, focus visibility, accessible names, 44 px mobile targets and WCAG AA contrast
- [ ] 4.4 Update intentional visual baselines on Linux and review only generated diffs

## 5. Delivery Evidence

- [ ] 5.1 Run focused frontend tests, build, OpenSpec change validation and `openspec validate --all`
- [ ] 5.2 Run `/opsx:verify`, update this checklist and record any justified deviations
- [ ] 5.3 Move the card through `Code Review` and `QA`, obtain green `qa-gate` and Playwright visual checks, and integrate the reviewed SHA into `develop`
- [ ] 5.4 Run `./restart`, validate the served Favorites analysis URL and only then move card #384 to `Done`
