### Requirement: Workflow runtime MUST persist stable pull order per stage
The runtime workflow model MUST store enough ordering information to return a stable, user-controlled card sequence within each active stage.

#### Scenario: Persist reorder in runtime
- **WHEN** the user changes the order of two cards in the same stage
- **THEN** the runtime workflow state MUST persist that new relative order
- **AND** later Kanban reads MUST reflect the same ordering automatically

### Requirement: Ordered columns MUST guide operational pull behavior
The visible order of cards in a column MUST be treated as the intended pull sequence for agents/operators working that stage.

#### Scenario: Agent reads ordered queue
- **GIVEN** multiple cards are available in the same stage
- **WHEN** an agent/operator consults the Kanban/runtime queue
- **THEN** the topmost eligible card SHOULD be interpreted as the next preferred item to pull
- **AND** lower cards SHOULD be treated as lower priority unless blocked or explicitly skipped
