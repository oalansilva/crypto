## ADDED Requirements

### Requirement: Design page is not a deny of OpenSpec
`page()` SHALL keep compiling the Moore page from `.cursor/process-fsm.yaml` `context_file[q]` without listing `enabled_tools`. When `bound_card` is issue N and `q` is `Design` on `card-<id>-*`, `additional_context` MUST contain the yaml `context_file[Design]` stub (synthesize + not re-interview + `OpenSpec/protótipo allow` + `Write produto deny`), MUST be at most 20 lines, and MUST NOT contain the token `enabled_tools`. The page MUST still list `enabled_events` for Design. This requirement MUST NOT change `UNBOUND_PAGE`, `unread_page()`, or the paging schema. Unit tests MUST inject `status_provider` and MUST NOT call GitHub.

#### Scenario: Design page carries the OpenSpec allow carve-out
- **WHEN** `page()` is invoked with injected `status_provider` returning `Design` and a bound card on `card-<id>-*`
- **THEN** `additional_context` contains `sintetizar`
- **AND** it contains `não reentrevistar`
- **AND** it contains `OpenSpec/protótipo allow`
- **AND** it contains `Write produto deny`
- **AND** it contains `q=Design`
- **AND** it has at most 20 lines

#### Scenario: Design page does not list enabled_tools
- **WHEN** `page()` is invoked with injected `status_provider` returning `Design` and a bound card on `card-<id>-*`
- **THEN** `additional_context` does not contain `enabled_tools`
- **AND** it contains `enabled_events`
- **AND** `unread_page()` is unchanged by this change
- **AND** `UNBOUND_PAGE` is unchanged by this change
