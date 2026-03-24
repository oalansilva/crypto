## MODIFIED Requirements

### Requirement: Home is a navigational hub for core workflows
The system MUST present a Home page that acts as the product's daily cockpit, helping users quickly understand the current context, identify the next recommended action, and access the main workflows from a single initial screen.

#### Scenario: User opens Home
- **WHEN** the user navigates to `/`
- **THEN** the system MUST render a first screen with orientation copy, prioritized primary actions, compact status or summary blocks, and contextual sections in addition to workflow shortcuts

#### Scenario: User scans the first screen
- **WHEN** the user views the initial Home viewport on a standard desktop layout
- **THEN** the system MUST expose at least one clear next-step action and enough snapshot context for the user to decide what to do next without first opening another page

### Requirement: Home shows a Quick Actions section
The Home page MUST expose a small set of prioritized primary actions for the most common daily workflows and MUST preserve visible access to supported secondary operational destinations through clearly labeled shortcuts or links.

#### Scenario: User triggers a primary action
- **WHEN** the user selects a primary action such as running a backtest, opening Monitor, or going to Lab
- **THEN** the system MUST navigate to the corresponding destination page

#### Scenario: User looks for a secondary workflow
- **WHEN** the user needs a lower-priority workflow or operational tool from Home
- **THEN** the system MUST provide a visible navigation path to the supported destination without relying on hidden or ambiguous interactions

### Requirement: Home provides basic product orientation
The Home page MUST include concise copy that frames the screen as the user's daily crypto cockpit, explains what the snapshot is for, and suggests an immediate starting path.

#### Scenario: User reads the hero section
- **WHEN** the user views the top portion of Home
- **THEN** the system MUST show short, non-technical orientation copy plus a recommended next action or path

#### Scenario: User interprets snapshot content
- **WHEN** the Home page presents summary or contextual information that is not fully live
- **THEN** the system MUST label or frame that content as a lightweight snapshot rather than implying a fully analytical dashboard

### Requirement: Home content is compact and responsive
The Home layout MUST preserve its information hierarchy on desktop and mobile by keeping orientation and primary actions first, status and summary content next, and contextual sections below without losing readability or action clarity.

#### Scenario: Mobile layout preserves hierarchy
- **WHEN** Home is viewed on a narrow viewport
- **THEN** the system MUST stack sections in priority order and MUST keep primary action labels readable and tappable

#### Scenario: Desktop layout keeps sections distinct
- **WHEN** Home is viewed on a wide viewport
- **THEN** the system MUST keep hero actions, status or summary content, and contextual sections visually distinct so users can scan the page quickly

## ADDED Requirements

### Requirement: Home shows lightweight system status and summary snapshots
The Home page MUST display a compact system status block and summary snapshot cards using data already available to the frontend or explicit fallback content. Each block MUST use deterministic labels and MUST surface loading, success, or fallback states clearly.

#### Scenario: Health status is loading or unavailable
- **WHEN** the status source is still loading or cannot be resolved
- **THEN** the system MUST keep the status section visible and present an explicit loading or fallback state instead of leaving the area blank

#### Scenario: Summary cards use available snapshot data
- **WHEN** the Home page renders summary cards
- **THEN** each card MUST show a stable label and a value or fallback placeholder that the user can interpret without opening another screen

### Requirement: Home includes contextual sections for current focus and recent activity
The Home page MUST provide contextual sections that orient the user around current focus and recent operational activity, with each item exposing descriptive labels and a direct action or destination when relevant.

#### Scenario: User reviews current focus items
- **WHEN** the user opens the contextual focus section
- **THEN** the system MUST show actionable items with enough text, status, or category context for the user to understand why each item matters

#### Scenario: Recent activity data is limited
- **WHEN** live recent-activity data is unavailable or intentionally lightweight
- **THEN** the system MUST preserve the section with explicit snapshot or empty-state content instead of collapsing the area entirely
