# Capability: Lab Real-time Logs

## Overview
Permitir visualização de logs em tempo real durante a execução de steps no Lab, proporcionando transparência e melhor experiência ao usuário.

## ADDED Requirements

### Requirement: Stream Logs Endpoint
**Description:** The system SHALL provide an SSE endpoint to stream logs from a running Lab step.

#### Scenario: Connect to log stream
**Given** a Lab run is in progress with step `combo_optimization`
**When** the frontend connects to `/api/lab/{run_id}/logs/stream`
**Then** the server opens an SSE connection
**And** sends log lines as they are generated

### Requirement: Log Display Panel
**Description:** The system MUST display a collapsible log panel in the Lab UI during step execution.

#### Scenario: Open log panel
**Given** the Lab is showing a running step
**When** the user clicks the "Ver Logs" button
**Then** a panel expands showing the live log stream
**And** logs auto-scroll to show the latest entries

### Requirement: Log Format Consistency
**Description:** The system SHALL use the same log format and styling as the existing combo configuration logs.

#### Scenario: Consistent log appearance
**Given** logs are being displayed in the Lab
**When** comparing with combo configuration logs
**Then** both use the same timestamp format
**And** both use the same color coding for log levels
**And** both use the same monospace font family

### Requirement: Log Persistence
**Description:** The system MUST store logs so they can be viewed after step completion.

#### Scenario: View logs after completion
**Given** a Lab step has completed
**When** the user opens the logs panel
**Then** all logs from that step are displayed
**And** new logs are no longer added (connection closed)

## MODIFIED Requirements

(None)

## REMOVED Requirements

(None)
