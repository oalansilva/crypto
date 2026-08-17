## ADDED Requirements

### Requirement: Agent chat transport is Hermes, not OpenClaw Gateway
The implemented agent-chat backend SHALL use Hermes instead of OpenClaw Gateway WS. The Favorites chat HTTP contract remains; only the transport changes.

#### Scenario: Chat does not use OPENCLAW_GATEWAY
- **WHEN** a chat turn is executed
- **THEN** the backend does not read `OPENCLAW_GATEWAY_URL` or connect to port `18789`
