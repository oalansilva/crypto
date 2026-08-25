# workflow-projects-lockdown Specification

## Purpose
List and create workflow projects only for admins on GET, and never return database connection strings or internal paths in the HTTP DTO.

## Requirements

### Requirement: GET /api/workflow/projects requires admin
`GET /api/workflow/projects` SHALL use the same admin criterion as the rest of the API (`get_current_admin` / `ADMIN_EMAILS`). It SHALL NOT remain a public list of `wf_projects` rows.

#### Scenario: Anonymous caller is 401
- **WHEN** a client calls `GET /api/workflow/projects` without a valid session or token
- **THEN** the response SHALL be 401
- **AND** the body SHALL NOT contain a connection string or `root_directory`

#### Scenario: Authenticated non-admin is 403
- **WHEN** an authenticated user whose email is not in `ADMIN_EMAILS` calls `GET /api/workflow/projects`
- **THEN** the response SHALL be 403
- **AND** the body SHALL NOT contain a connection string or `root_directory`

#### Scenario: Admin lists projects
- **WHEN** an admin calls `GET /api/workflow/projects`
- **THEN** the response SHALL be 200
- **AND** each item SHALL include `id`, `slug`, and `name`

### Requirement: Project HTTP DTO omits secrets and internal path
The HTTP DTO for a workflow project (`ProjectOut` and the same shape on `POST /api/workflow/projects`) SHALL omit `database_url`, `workflow_database_url`, and `root_directory`. Those columns MAY remain on the Postgres row and in runtime seed; they SHALL NOT appear as JSON keys (not null).

#### Scenario: Admin GET has no secret keys
- **WHEN** an admin receives 200 from `GET /api/workflow/projects`
- **THEN** each item MAY include `frontend_url`, `backend_url`, and `tech_stack`
- **AND** the keys `database_url`, `workflow_database_url`, and `root_directory` SHALL NOT exist on the object

#### Scenario: POST response is redacted while the row keeps URLs
- **WHEN** an authenticated caller `POST /api/workflow/projects` with `database_url`, `workflow_database_url`, or `root_directory` in the body
- **THEN** the response SHALL be 200
- **AND** the response SHALL NOT include those three keys
- **AND** the `wf_projects` row SHALL still store the URLs for runtime

#### Scenario: Other Project serializers share the cut
- **WHEN** any other HTTP serializer mirrors a `Project` row
- **THEN** it SHALL use the same field cut as `ProjectOut`

### Requirement: POST /api/workflow/projects stays actor-authenticated
`POST /api/workflow/projects` SHALL remain behind `get_workflow_actor` (any logged-in actor). This card SHALL NOT replace that dependency with `get_current_admin`.

#### Scenario: POST still requires a workflow actor
- **WHEN** an unauthenticated client `POST /api/workflow/projects`
- **THEN** the response SHALL NOT be 200
- **AND** a caller with `get_workflow_actor` SHALL still be able to create a project as today, with a redacted response body

### Requirement: ProjectSelector sends credentials
The Kanban `ProjectSelector` SHALL send the authenticated credential on `GET` of workflow projects. A non-admin SHALL see load failure, not a public list.

#### Scenario: Admin Kanban lists by slug and name
- **WHEN** an authenticated admin opens the Kanban selector
- **THEN** the request SHALL include the app auth credential
- **AND** the options SHALL use project slug/name

#### Scenario: Non-admin does not get a public list
- **WHEN** a non-admin (or anonymous) session hits the selector GET
- **THEN** the UI SHALL show the existing load-failure state
- **AND** SHALL NOT render a public catalog of projects from this endpoint

### Requirement: Out-of-scope workflow GETs are unchanged
This card SHALL NOT change auth on `GET /api/workflow/kanban/*`, `GET .../changes`, scheduler, or health, except that those responses SHALL NOT leak the full `Project` row secrets if they currently do not.

#### Scenario: Other GETs are not the lockdown target
- **WHEN** this change ships
- **THEN** auth behavior of Kanban/changes GETs other than `/projects` SHALL remain as before unless a serializer would echo `database_url` / `workflow_database_url` / `root_directory`, in which case those keys SHALL be omitted
