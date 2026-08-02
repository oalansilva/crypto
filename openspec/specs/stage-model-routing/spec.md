# stage-model-routing Specification

## Purpose

Define fixed, fail-closed Codex model routing by delivery stage for the Cripto Farol project.

## Requirements

### Requirement: The workflow MUST route fixed models by stage
The Codex workflow MUST use `gpt-5.6-sol` with `high` reasoning for Design/OpenSpec and QA, and MUST use `gpt-5.6-luna` with `max` reasoning for development, Code Review, and release. The routing MUST be determined by the operational stage and MUST NOT vary by task complexity.

#### Scenario: Design and OpenSpec start
- **WHEN** a card is prepared in Design or its planning artifacts are created or refined
- **THEN** the Sol High primary session performs the work

#### Scenario: Development starts after approval
- **WHEN** a card is in `Pronto para Dev` and moves to `Em desenvolvimento`
- **THEN** the workflow spawns the exact Luna Max implementer profile for `/opsx:apply`, implementation, and focused tests

#### Scenario: Reviewed implementation enters QA
- **WHEN** Code Review has accepted the exact diff and the reviewed SHA is available
- **THEN** the Sol High primary session reassumes execution for `/opsx:verify` and QA acceptance

#### Scenario: Release is explicitly requested
- **WHEN** Alan explicitly requests a release containing homologated cards
- **THEN** the workflow spawns the exact Luna Max release profile to conduct the release checklist

### Requirement: Code Review MUST use an independent Luna thread after activation
After the project-scoped profiles are versioned and loaded, Code Review MUST run in a new Luna Max thread spawned with `fork_turns="none"`, distinct from the implementation thread, and whose observed sandbox is read-only. The reviewer MUST inspect the exact diff and MUST NOT implement its own fixes. The bootstrap change that installs these profiles uses the explicit static-acceptance exception below.

#### Scenario: Post-activation implementation becomes reviewable
- **WHEN** a task started after profile activation has an implementation diff and focused evidence ready
- **THEN** the workflow spawns the exact Luna Max reviewer with `fork_turns="none"`, no implementation conversation history, and a self-contained review packet

#### Scenario: Post-activation reviewer isolation is not enforced
- **WHEN** a post-activation Luna reviewer's observed sandbox is not read-only or cannot be observed
- **THEN** Code Review remains blocked and the workflow MUST NOT claim an accepted review

### Requirement: Model routing MUST fail closed
Every routed stage MUST require the exact configured agent name, model, reasoning effort, and applicable sandbox. Missing, stale, conflicting, unavailable, or unobservable routing evidence MUST block the stage without fallback.

#### Scenario: Expected profile is unavailable
- **WHEN** the client does not expose the exact profile required for the stage
- **THEN** the workflow stops that stage and reports the configuration blocker

#### Scenario: Model or effort differs
- **WHEN** runtime evidence differs from the profile's required model or reasoning effort
- **THEN** the workflow rejects the lane and MUST NOT substitute Terra, a built-in agent, or another effort

#### Scenario: Public runtime metadata is incomplete
- **WHEN** spawn details omit agent type, model, effort, sandbox policy type, or permission profile type
- **THEN** the workflow uses the exact-thread local allowlisted inspector and blocks if required values remain missing, ambiguous, or conflicting

### Requirement: Routing evidence MUST be safe and auditable
Each spawned stage MUST capture agent type, model, reasoning effort, sandbox policy type, and permission profile type from public details or the allowlisted local fallback. Public handoffs MUST NOT expose thread ids, rollout paths, prompts, messages, environment values, tokens, or arbitrary runtime payloads.

#### Scenario: Spawned lane returns work
- **WHEN** the orchestrator evaluates the lane report
- **THEN** it verifies the required routing fields and records only the safe allowlisted evidence in the handoff

### Requirement: Bootstrap acceptance MUST use static contract validation
The change that installs the project-scoped profiles MUST be accepted through reproducible parsing and assertions of the exact TOML profiles, models, reasoning efforts, sandboxes, stage rules, skill metadata, model catalog and OpenSpec. The model-catalog check MUST read the Codex cache at `${CODEX_HOME:-$HOME/.codex}/models_cache.json` and prove that `gpt-5.6-sol` exposes `high` and `gpt-5.6-luna` exposes `max` in `supported_reasoning_levels`. It MUST NOT require pre-spawning every lane or changing server security configuration.

#### Scenario: Routing profiles are being installed
- **WHEN** the bootstrap change is reviewed before the profiles are versioned and loaded by later tasks
- **THEN** static contract checks and an independent read-only Codex review provide the acceptance evidence

#### Scenario: A profile has no current operational stage
- **WHEN** the release manager is configured but Alan has not authorized a release
- **THEN** the profile is validated statically and MUST NOT be spawned only to produce runtime proof

#### Scenario: Sandbox smoke execution is blocked by host policy
- **WHEN** a pre-activation diagnostic cannot start because of AppArmor, user namespace or sandbox launcher policy
- **THEN** the workflow preserves the server configuration, records the diagnostic as non-acceptance evidence and relies on the static bootstrap contract

#### Scenario: A configured lane is naturally used after activation
- **WHEN** a later task reaches development, Code Review or authorized release and spawns the applicable Luna profile
- **THEN** the workflow collects the safe runtime evidence at that time and applies the normal fail-closed rules to that lane

### Requirement: Every Luna lane MUST use a context-independent spawn packet
The implementer, reviewer, and release manager MUST each be spawned with the exact agent type and `fork_turns="none"`. Each prompt MUST be self-contained and MUST include the card/change, observed gate, branch/worktree, objective, ownership, interfaces, constraints, relevant artifacts or diff/SHA, verification, and required return format.

#### Scenario: Development lane is spawned
- **WHEN** the orchestrator delegates a card in `Em desenvolvimento`
- **THEN** it sends the exact Luna implementer a complete implementation packet without relying on inherited Sol history

#### Scenario: Review lane is spawned
- **WHEN** the orchestrator delegates `Code Review`
- **THEN** it sends the exact Luna reviewer a complete exact-diff packet without implementation history

#### Scenario: Release lane is spawned
- **WHEN** Alan explicitly authorizes release of homologated cards
- **THEN** it sends the exact Luna release manager a complete package/checklist packet without prior conversation history

#### Scenario: Spawn would inherit parent turns
- **WHEN** the runtime cannot create the required Luna lane with `fork_turns="none"`
- **THEN** the stage remains blocked and MUST NOT use a full-history or partial-history fork

### Requirement: Rework MUST preserve stage ownership
Any finding before Done MUST return to the fixed owner of the affected artifact or code and then repeat all downstream gates invalidated by the change.

#### Scenario: Code Review requests a fix
- **WHEN** the Luna reviewer reports a blocking finding
- **THEN** the Luna implementer applies the fix and a new Luna reviewer thread reviews the updated diff before Sol QA

#### Scenario: QA requests a fix
- **WHEN** Sol QA finds a code change required before Done
- **THEN** the card follows `QA -> Em desenvolvimento/Luna -> Code Review/new Luna -> QA/Sol`

#### Scenario: QA requires an OpenSpec correction without design change
- **WHEN** Sol QA finds an OpenSpec correction that does not alter the approved design
- **THEN** Sol High updates and republishes the artifact and repeats affected downstream review and QA evidence

#### Scenario: Rework changes approved design
- **WHEN** any correction changes approved `design.md`, prototype, or design decision
- **THEN** the card returns to `Design/Sol -> Aprovação de Design/Alan` before development resumes

#### Scenario: Release finds a code correction after homologation
- **WHEN** the Luna release manager finds that a Homologado card requires code
- **THEN** release stops, Status remains `Homologado`, and technical work follows Luna implementer, new Luna reviewer, and Sol QA without regressing the card

### Requirement: Model routing MUST preserve human authority
Automatic model routing MUST NOT approve Design, homologate a card, or authorize a release.

#### Scenario: Design evidence is complete
- **WHEN** Sol High completes Design/OpenSpec with a passing critique
- **THEN** the card waits in `Aprovação de Design` until Alan moves it to `Pronto para Dev`

#### Scenario: Technical delivery is Done
- **WHEN** QA and technical integration complete
- **THEN** the card waits for Alan's homologation and no release starts without his explicit request
