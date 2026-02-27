<artifact id="tasks" change="home-page-refresh" schema="spec-driven">

<task>
Create the tasks artifact for change "home-page-refresh".
Implementation checklist with trackable tasks
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

<rules>
<!-- These are constraints for you to follow. Do NOT include this in your output. -->
- Include a short note reminding to use project skills (.codex/skills) when applicable (architecture, tests, debugging, frontend).
</rules>

<dependencies>
Read these files for context before creating this artifact:

<dependency id="specs" status="done">
  <path>/root/.openclaw/workspace/crypto/openspec/changes/home-page-refresh/specs/**/*.md</path>
  <description>Detailed specifications for the change</description>
</dependency>
<dependency id="design" status="done">
  <path>/root/.openclaw/workspace/crypto/openspec/changes/home-page-refresh/design.md</path>
  <description>Technical design document with implementation details</description>
</dependency>
</dependencies>

<output>
Write to: /root/.openclaw/workspace/crypto/openspec/changes/home-page-refresh/tasks.md
</output>

<instruction>
Create the task list that breaks down the implementation work.

**IMPORTANT: Follow the template below exactly.** The apply phase parses
checkbox format to track progress. Tasks not using `- [ ]` won't be tracked.

Guidelines:
- Group related tasks under ## numbered headings
- Each task MUST be a checkbox: `- [ ] X.Y Task description`
- Tasks should be small enough to complete in one session
- Order tasks by dependency (what must be done first?)

Example:
```
## 1. Setup

- [ ] 1.1 Create new module structure
- [ ] 1.2 Add dependencies to package.json

## 2. Core Implementation

- [ ] 2.1 Implement data export function
- [ ] 2.2 Add CSV formatting utilities
```

Reference specs for what needs to be built, design for how to build it.
Each task should be verifiable - you know when it's done.
</instruction>

<template>
<!-- Use this as the structure for your output file. Fill in the sections. -->
## 1. <!-- Task Group Name -->

- [ ] 1.1 <!-- Task description -->
- [ ] 1.2 <!-- Task description -->

## 2. <!-- Task Group Name -->

- [ ] 2.1 <!-- Task description -->
- [ ] 2.2 <!-- Task description -->
</template>

<success_criteria>
<!-- To be defined in schema validation rules -->
</success_criteria>

</artifact>
