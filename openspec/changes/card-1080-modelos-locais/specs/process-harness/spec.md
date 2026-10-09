## MODIFIED Requirements

### Requirement: dsh plugin sanitizes rejected reasoning effort on every model request
For newly managed dsh children, the plugin SHALL validate the captured supported selection on each request and SHALL NOT silently replace missing, off, none or incompatible effort with high. Required effort missing SHALL fail visibly. Valid selected effort SHALL be forwarded exactly; unsupported effort SHALL NOT be invented. Existing root/child sessions SHALL retain their birth contract. Write deny, grill deny, cordis restrictions and existing bounded error handling SHALL remain. Selection logic MUST NOT enter decide(), vendor the host, or use native settings as a pin channel.

#### Scenario: Invalid effort on managed child
- **WHEN** a request lacks its required captured effort or proposes an incompatible value
- **THEN** the adapter reports refusal instead of sending high as a substitute

### Requirement: dsh child agentCtx sanitizes reasoning effort outside installModelSelection
The existing agent-created attachment and per-child agent.ctx request guards SHALL protect every request of a continuable child, including contexts that do not inherit parent listeners. For newly managed children they SHALL reapply/validate the immutable birth selection outside runtime stripping, without rereading operational choices for that living child. Attachment MUST NOT throw synchronously. Error listeners, rejected-run diagnostics and existing unrelated guards SHALL remain; no host package SHALL be vendored.

#### Scenario: Child after machine edit
- **WHEN** a continuing child's agent.ctx requests again after the machine selection changes
- **THEN** the request retains its captured supported effort instead of receiving the new choice or a high default
