## ADDED Requirements

### Requirement: Terminal routes cover the complete authorized workflow
The Codex terminal workflow SHALL support creation and refinement, human prioritization, Design and independent critique, human approval, Apply, independent Review, QA, integration, homologation or non-homologation, and explicitly requested release. Interactive TUI and terminal exec principal routes MUST be tracked separately, including their dedicated exec Review coordinator. App/IDE and other clients MUST remain outside this delivery. An unsupported terminal route MUST remain an explicit blocker within this card rather than be transferred to App/IDE scope.

#### Scenario: Interactive workflow reaches a human decision
- **WHEN** a terminal card reaches T1, T7, T15 or T18
- **THEN** the workflow preserves the human gate and waits for Alan's existing authorized action without changing Status on his behalf
- **AND** silence or generic implementation wording does not authorize advancement

#### Scenario: Exec needs an answer
- **WHEN** an exec principal needs a refinement answer or human decision
- **THEN** it returns the question and a native-session checkpoint and continues only after an explicit answer with state revalidated
- **AND** absence of a demonstrated native continuation capability blocks that route without inventing an answer or switching interface silently

### Requirement: Fresh sessions discover evidence and bind natively
The workflow SHALL work from new sessions in source and card worktrees and from resumed sessions without relying silently on private implementation-worktree files. It MUST identify the active native root before dependent work. Shell workdir or a root argument MUST NOT count as native rebind. Automated rebind MUST require observed native capability; otherwise the workflow MUST provide the precise native resume action to the operator and continue validation after it occurs.

#### Scenario: Source to card worktree
- **WHEN** Design requires a card worktree while the native chat remains in source
- **THEN** the workflow prepares the worktree and preserves existing work but refuses dependent Design work until native turn metadata confirms the destination
- **AND** a supported operator resume of the same UUID is distinguished from automated preparation

#### Scenario: Fresh destination has no local qualification files
- **WHEN** a new worktree has no private local qualification but an intact compatible capability proof is discoverable
- **THEN** that proof is revalidated at its original source and current contextual qualification is independently checked or prepared
- **AND** copied receipts never establish the new context

### Requirement: Authorized preparation is orchestrated with bounded recovery
The principal SHALL conduct already-authorized native diagnostics, collection, qualification and preflight retry when preparation is missing. Diagnostics MUST remain separate from product work and transitions. Recovery MUST preserve Status, artifacts, captures and failure evidence, stop repeated identical failures after one automatic retry with unchanged sources, and report the exact cause and next action. Human trust MUST NOT be recorded by the agent.

#### Scenario: Missing contextual proof after resume
- **WHEN** preparation finds current-context proof missing and diagnostics are already authorized
- **THEN** the principal conducts the native diagnostic for that scope, verifies it, and retries the pending preflight
- **AND** it does not end with generic instructions for manual essays or count diagnostic completion as stage completion

#### Scenario: Interrupted child retains useful work
- **WHEN** a child is interrupted or lacks valid returned payload
- **THEN** the stage remains unsuccessful and artifacts and original failure are retained
- **AND** any required new birth obtains fresh selection and proof instead of inheriting the old success or retuning a divergent child

### Requirement: Native stage identity and refinement dialogue are preserved
Delegated stages SHALL execute in native isolated children using per-birth local model and effort selection, verified identity, card/root/role binding and completed status with payload. The principal MUST orchestrate without performing delegated work as fallback. Refinement MUST relay questions and explicit answers in the card's same chat and update only the bound card in its live allowed state.

#### Scenario: Reproduce the refinement incident
- **WHEN** the authorized #1117 case is exercised
- **THEN** the workflow first checks its live state, diagnoses the original pre-birth refusal, and runs refinement only if that state still permits it
- **AND** a changed state is reported without moving the card backwards for an essay

#### Scenario: Child identity or selection differs
- **WHEN** the native child's observed identity, model, effort or context differs from its capture or expected binding
- **THEN** no stage success is accepted and the principal does not replace the child with its own work

### Requirement: Review launches automatically under effective read-only permissions
The writable principal SHALL automatically launch a dedicated exec read-only coordinator that spawns two distinct native named reviewers in the same turn. Both reviewers MUST receive the same materialized exact diff and digest, demonstrate deny/readback and full reading, and return complete independent findings. The coordinator MUST only orchestrate. The principal MUST collect and persist evidence and require verify-wave and checklist success before committing, without manual permission switching.

#### Scenario: Product Review succeeds
- **WHEN** the card is in Code Review with a fresh authoritative stage check and a fixed product diff
- **THEN** principal launch, coordinator identity, read-only interval, two native births, full diff reading and payload returns are verified as one chain
- **AND** verify-wave and the checklist run after collection in the writable principal

#### Scenario: Permission or coverage is incompatible
- **WHEN** a reviewer can write the probe target, misses a diff chunk, has a different SHA, or the coordinator stage proof has expired
- **THEN** the wave is refused with the specific cause and unchanged product bytes where denial is expected
- **AND** no profile declaration, process exit code or diagnostic wave substitutes for product Review

#### Scenario: Correction and non-homologation return
- **WHEN** Review requires correction or Alan performs T18 with the required visible reason
- **THEN** the workflow follows the existing correction ceiling and residual rules, or resumes development on the same card from current develop without repeating T8 after T18
- **AND** P0 stops the column and no third Review cycle is invented

### Requirement: Live acceptance is incremental without waiving final proof
The delivery SHALL publish a sanitized acceptance matrix for every workflow stage and both terminal principal routes, including new and resumed sessions, positive and negative cases, source references, card/state, SHA/pin and consuming-gate results. Fixtures and diagnostics MUST be separate from live stage proof. Done técnico MUST NOT mean full-flow delivery. Post-QA human decisions and explicitly authorized release SHALL append evidence to the same acceptance commitment without making future release proof a precommit dependency or exempting it from full-flow acceptance.

#### Scenario: Technical integration precedes release authorization
- **WHEN** implementation, Review and QA pass but Alan has not requested release
- **THEN** normal technical integration may proceed with remaining matrix cells explicitly pending
- **AND** no release runs and no integral-delivery claim is made

#### Scenario: Full-flow claim is evaluated
- **WHEN** any mandatory terminal stage, route, return or consuming gate remains blocked or lacks real evidence
- **THEN** full-flow delivery remains unproven even if implementation tasks and fixtures pass
- **AND** the remaining acceptance work stays traceable to #1130

### Requirement: Release uses existing authorization and environment contracts
Terminal release SHALL require Alan's explicit release request, eligible homologated cards, the observed execution selection for the principal, existing fecho-lote obligations and release guards. It MUST use the consumer overlay for migration/build/restart/health, archive and integration rules, Kaizen, branch hygiene and main-to-develop sync where required. Pronto MUST require post PASS after actual publication and validated deployment.

#### Scenario: Authorized release produces final evidence
- **WHEN** Alan explicitly requests a release of an eligible package
- **THEN** the terminal workflow collects the real release sequence, published SHA, deployment and public health evidence, Kaizen and final guard results
- **AND** only the existing fechar_release event after post PASS can complete the release transition

#### Scenario: Homologation without publication request
- **WHEN** a card is Homologado but no explicit release request exists
- **THEN** terminal support remains available but archive, publication and production operations are not authorized by this card

### Requirement: Distribution and historical scope remain auditable
Generic changes SHALL be distributed from nucleus to consumer with recorded revision/pin and verified manifests, keeping human trust separate. Public evidence MUST exclude private transcripts, control values and sentinels. #1098 and #1128 SHALL receive traceable reconciliation preserving historical outcomes and locating all remaining terminal acceptance in #1130.

#### Scenario: Consumer receives a new pin
- **WHEN** updated generic support is installed into the consumer
- **THEN** source and consumer revisions and manifest integrity are recorded and required human trust review remains explicit
- **AND** old diagnostic evidence is neither upgraded to full delivery nor silently copied into a new execution context
