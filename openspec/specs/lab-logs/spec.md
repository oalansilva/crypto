# lab-logs Specification

## Purpose
TBD - created by archiving change lab-realtime-logs. Update Purpose after archive.
## Requirements
### Requirement: Stream Logs Endpoint
**Description:** The system SHALL provide an SSE endpoint to stream logs from a running Lab step.

#### Scenario: Connect to log stream
- **GIVEN** a Lab run is in progress with step `combo_optimization`
- **WHEN** the frontend connects to `/api/lab/{run_id}/logs/stream`
- **THEN** the server opens an SSE connection
- **AND** the server sends log lines as they are generated

### Requirement: Log Display Panel
**Description:** The system MUST display a collapsible log panel in the Lab UI during step execution.

#### Scenario: Open log panel
- **GIVEN** the Lab is showing a running step
- **WHEN** the user clicks the "Ver Logs" button
- **THEN** a panel expands showing the live log stream
- **AND** logs auto-scroll to show the latest entries

#### Scenario: Collapse log panel
- **GIVEN** the log panel is expanded during step execution
- **WHEN** the user toggles the "Ver Logs" control to close the panel
- **THEN** the panel collapses in the Lab UI
- **AND** the live stream subscription is released until the panel is reopened

### Requirement: Log Format Consistency
**Description:** The system SHALL use the same log format and styling as the existing combo configuration logs.

#### Scenario: Consistent log appearance
- **GIVEN** logs are being displayed in the Lab
- **WHEN** comparing with combo configuration logs
- **THEN** both use the same timestamp format
- **AND** both use the same color coding for log levels
- **AND** both use the same monospace font family

### Requirement: Log Persistence
**Description:** The system MUST store logs so they can be viewed after step completion.

#### Scenario: View logs after completion
- **GIVEN** a Lab step has completed
- **WHEN** the user opens the logs panel
- **THEN** all logs from that step are displayed
- **AND** new logs are no longer added (connection closed)

