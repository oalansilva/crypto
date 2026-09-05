## ADDED Requirements

### Requirement: Citation-vs-role grill deny ships as product patch pin
This change SHALL ship in product `oalansilva/covenant-flow` as a patch tag (not a schema major). Live overlay/pin-tests are `v1.1.6`. Sibling [#817](https://github.com/oalansilva/crypto/issues/817) (`card-817-dsh-reasoning-effort`) also expects `v1.1.7` and changes the same nucleus (`dsh_plugin_lib.js` and `.dsh/plugin/process-fsm-guard.js`: grill → `dsh_reasoning_effort_spawn` → cordis → `runGuard`, plus `agent/request` / `agent/request-error`). Apply SHALL `gh api repos/oalansilva/covenant-flow/tags` **and** rebase the product on the tag/tip that already exists. Apply MUST NOT pin from base `v1.1.6` after the sibling (that clobbers the sibling sanitizer/gate). The fallback next unused patch covers the **number** only, not rebase/merge. Pin-tests SHALL bump to **this** card's tag after that rebase and MUST NOT hardcode `v1.1.7` in a vacuum. If `v1.1.7` is still free and the tip is still `v1.1.6`, Apply MAY tag `v1.1.7`; if #817 already took it, Apply SHALL use the next unused patch and MUST NOT bump major. `SCHEMA_MAJOR` SHALL remain 1. Apply SHALL commit the updated `isGrillShapedSpawn` helper and goldens in `scripts/process-fsm/test_dsh_grill_spawn.py` on top of the rebased tip, then `implantar --pin` of **this** card's tag on Cripto. Overlay SHALL record `pin` as that tag. `clients.dsh.auto` SHALL remain `false`. `AGENTS.md` MUST NOT gain a line for this rule. The canonical T1 comment text MUST NOT change. Cursor and Grok grill spawn MUST remain allowed. Client skins under `.grok/` `.dsh/` `.opencode/` for `grill-card` MUST stay at most 8 non-empty body lines. Apply MUST NOT revert `dsh_reasoning_effort_spawn` or the `agent/request` listeners.

#### Scenario: Pin materializes the citation-vs-role deny on Cripto
- **WHEN** overlay is valid and `implantar --pin` of this card's tag completes on Cripto
- **THEN** `scripts/process-fsm/dsh_plugin_lib.js` distinguishes grill papel from citation
- **AND** overlay contains `pin:` equal to **this** card's tag after rebase (not a hardcoded `v1.1.7` in a vacuum)
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1
- **AND** grill-card stubs under `.grok/` `.dsh/` `.opencode/` remain at most 8 non-empty body lines
- **AND** if the rebased tip already contained `dsh_reasoning_effort_spawn` or `agent/request`, those remain after pin

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is this card's patch after `gh api` tags and rebase on the existing tip
- **AND** it is not `v2.0.0`
- **AND** `deepseek-ai/deepseek-harness` is still not vendored
- **AND** `process-fsm.yaml` is unchanged by this pin
- **AND** `scripts/process-fsm/guard.py` source still does not contain `grill-card`, `dsh_grill_spawn`, or `isGrillShapedSpawn`

#### Scenario: Pin from v1.1.6 must not clobber sibling #817
- **WHEN** origin already has a tag/tip from #817 on the same nucleus
- **THEN** Apply rebases onto that tag/tip before committing this card's helper
- **AND** Apply MUST NOT `implantar --pin` a tree based on `v1.1.6` that omits `dsh_reasoning_effort_spawn`
- **AND** the next unused patch number MAY be used only after that rebase
