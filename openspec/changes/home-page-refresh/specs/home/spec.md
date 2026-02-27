<artifact id="specs" change="home-page-refresh" schema="spec-driven">

<task>
Create the specs artifact for change "home-page-refresh".
Detailed specifications for the change
</task>

<project_context>
<!-- This is background information for you. Do NOT include this in your output. -->
Purpose: Build a cryptocurrency backtester to fetch historical data, simulate trading strategies, and visualize performance (ROI, Drawdown).

Tech Stack:
- Python 3.x
- pandas (Data manipulation)
- ccxt (Crypto data fetching)
- matplotlib (Visualization)

Project Conventions:
- PEP 8
- Type hinting for all function signatures
- Docstrings for all classes and methods

Architecture Patterns:
- Modular design: DataLoader, Strategy, Backtester, Visualization
- Strategy Pattern for different trading strategies

External Dependencies:
- CCXT (Exchange APIs)
</project_context>

<dependencies>
Read these files for context before creating this artifact:

<dependency id="proposal" status="done">
  <path>/root/.openclaw/workspace/crypto/openspec/changes/home-page-refresh/proposal.md</path>
  <description>Initial proposal document outlining the change</description>
</dependency>
</dependencies>

<output>
Write to: /root/.openclaw/workspace/crypto/openspec/changes/home-page-refresh/specs/**/*.md
</output>

<instruction>
Create specification files that define WHAT the system should do.

Create one spec file per capability listed in the proposal's Capabilities section.
- New capabilities: use the exact kebab-case name from the proposal (specs/<capability>/spec.md).
- Modified capabilities: use the existing spec folder name from openspec/specs/<capability>/ when creating the delta spec at specs/<capability>/spec.md.

Delta operations (use ## headers):
- **ADDED Requirements**: New capabilities
- **MODIFIED Requirements**: Changed behavior - MUST include full updated content
- **REMOVED Requirements**: Deprecated features - MUST include **Reason** and **Migration**
- **RENAMED Requirements**: Name changes only - use FROM:/TO: format

Format requirements:
- Each requirement: `### Requirement: <name>` followed by description
- Use SHALL/MUST for normative requirements (avoid should/may)
- Each scenario: `#### Scenario: <name>` with WHEN/THEN format
- **CRITICAL**: Scenarios MUST use exactly 4 hashtags (`####`). Using 3 hashtags or bullets will fail silently.
- Every requirement MUST have at least one scenario.

MODIFIED requirements workflow:
1. Locate the existing requirement in openspec/specs/<capability>/spec.md
2. Copy the ENTIRE requirement block (from `### Requirement:` through all scenarios)
3. Paste under `## MODIFIED Requirements` and edit to reflect new behavior
4. Ensure header text matches exactly (whitespace-insensitive)

Common pitfall: Using MODIFIED with partial content loses detail at archive time.
If adding new concerns without changing existing behavior, use ADDED instead.

Example:
```
## ADDED Requirements

### Requirement: User can export data
The system SHALL allow users to export their data in CSV format.

#### Scenario: Successful export
- **WHEN** user clicks "Export" button
- **THEN** system downloads a CSV file with all user data

## REMOVED Requirements

### Requirement: Legacy export
**Reason**: Replaced by new export system
**Migration**: Use new export endpoint at /api/v2/export
```

Specs should be testable - each scenario is a potential test case.
</instruction>

<template>
<!-- Use this as the structure for your output file. Fill in the sections. -->
## ADDED Requirements

### Requirement: <!-- requirement name -->
<!-- requirement text -->

#### Scenario: <!-- scenario name -->
- **WHEN** <!-- condition -->
- **THEN** <!-- expected outcome -->
</template>

<success_criteria>
<!-- To be defined in schema validation rules -->
</success_criteria>

<unlocks>
Completing this artifact enables: tasks
</unlocks>

</artifact>
