## ADDED Requirements

### Requirement: Backend MUST stop exposing Lab-specific runtime endpoints
The backend MUST stop exposing HTTP endpoints, runtime helpers, and trace/log streaming surfaces that exist only to support the Lab workflow.

#### Scenario: Client requests a former Lab endpoint
- **WHEN** a client calls a former `/api/lab` endpoint or a Lab-specific log/trace surface
- **THEN** the backend MUST NOT execute a Lab run
- **AND** the Lab-specific route surface is no longer available as a supported product capability
