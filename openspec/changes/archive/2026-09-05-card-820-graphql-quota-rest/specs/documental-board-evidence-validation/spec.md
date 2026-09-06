## ADDED Requirements

### Requirement: Card evidence comments are listed over REST
`scripts/post-card-evidence-comment.sh` SHALL list existing issue comments via REST `GET /repos/<owner>/<repo>/issues/<n>/comments` (paginate as needed). It MUST NOT call `gh issue view --json comments` (GraphQL). If the REST list fails or returns invalid JSON, the script MUST refuse to post (fail-closed), unchanged from today's fail-closed posture. GraphQL remaining=0 MUST NOT block this REST list. Dedup by transition marker and commit ref remains.

#### Scenario: Comments fetch uses REST
- **WHEN** the script loads comments for card N before posting evidence
- **THEN** it calls REST `/issues/N/comments`
- **AND** the script source MUST NOT contain `gh issue view --json comments`

#### Scenario: REST comments failure stays fail-closed
- **WHEN** the REST comments list fails or is not a JSON array of comment objects
- **THEN** the script errors and MUST NOT post a new comment

#### Scenario: GraphQL quota 0 does not block REST comments
- **WHEN** GraphQL headers remaining=0 and REST comments GET succeeds
- **THEN** the script may read comments and post when the marker/SHA rules allow
