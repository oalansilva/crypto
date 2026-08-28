## ADDED Requirements

### Requirement: Guard normalizes the dsh native dialect
`scripts/process-fsm/` SHALL normalize hook stdin so `decide()` is client-agnostic across four dialects. In addition to Cursor (`tool_name` / `tool_input`), Grok (`toolName` / `toolInput`), and OpenCode `{ tool, args }` with `filePath` / `patchText` / `command`, the normalizer MUST accept the native dsh payload `{ tool, args }` as a fourth dialect whose write path key is `file_path` and whose shell key is `command`. Canonical dsh write tools SHALL include `write` and `edit`. Canonical dsh shell tool SHALL include `bash`. Path extraction MUST use `args.file_path` for `write`/`edit`. For `bash`, path extraction MUST use `args.command` with the same mutation classification as other shell dialects (`tee`, `>`, Status `item-edit`). Mutating `str_replace_editor` (`command` `create`, `str_replace`, or `insert`) MUST be classified as a product write via **`extract_paths(args.path)`** when that path matches `product_globs`. Apply MUST put those mutate commands on the write-path extraction branch (`PATH_KEYS` already includes `path`) and MUST NOT treat `args.command` (`str_replace` / `create` / `insert` / `view`) as a shell `_command()` — that path today yields `extract_paths==[]` and allow. Apply MUST NOT dump the whole tool into `WRITE_TOOLS`: that would extract `path` on `view` and then `bool(command)` would make `view` of `backend/` `write_produto`. Classify by `args.command`: mutate → `extract_paths(args.path)`; `view` → do not extract as a write. Goldens for mutate MUST assert `extract_paths()` (not only deny, so they do not collapse with empty-path). The editor is mounted on preset **`sdk-minimal`**; default `dsh web` (web-app overlay) disables `tool-str-replace-editor`. `str_replace_editor` `command` `view` MUST NOT be classified as a product write solely because `path` matches `product_globs`. A dsh `edit`/`write` of a `product_globs` path with `q_git=develop` MUST take the same `write_produto` path as a Cursor `Write` and as an OpenCode `edit` with `filePath`. Unknown tools remain class #611: allow. `cwd` MAY come from plugin directory / worktree when the envelope omits `cwd`.

#### Scenario: dsh write of product on develop is denied
- **WHEN** stdin is a native dsh envelope `{ "tool": "write", "args": { "file_path": "backend/app/tasks/discovery_tasks.py" } }` and `q_git=develop`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: dsh edit of frontend on develop is denied
- **WHEN** stdin is `{ "tool": "edit", "args": { "file_path": "frontend/src/x.tsx" } }` and `q_git=develop`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: dsh bash tee onto backend is denied
- **WHEN** stdin is `{ "tool": "bash", "args": { "command": "echo x | tee backend/app/main.py" } }` and I1 does not hold
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: dsh OpenSpec write in Design on card branch is allowed
- **WHEN** stdin is dsh `edit` of a path under `openspec/changes/` and `status` is `Design` and `q_git` matches `card-<id>-*`
- **THEN** the Guard returns `permission: allow` and `decision: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path

#### Scenario: Four dialects deny the same product path
- **WHEN** Cursor `Write`, Grok `write` (`file_path`), OpenCode `edit` (`filePath`), and dsh `write` (`file_path`) target the same overlay product path with `q_git=develop`
- **THEN** all four return `permission: deny` and `decision: deny`

#### Scenario: Unknown dsh tool remains allow
- **WHEN** stdin is `{ "tool": "grep", "args": {} }` with no extractable product path
- **THEN** the Guard returns `permission: allow` (class #611)

#### Scenario: str_replace_editor mutate of product on develop is denied
- **WHEN** stdin is `{ "tool": "str_replace_editor", "args": { "command": "str_replace", "path": "backend/app/main.py", "old_str": "a", "new_str": "b" } }` and `q_git=develop`
- **THEN** `extract_paths()` equals `["backend/app/main.py"]`
- **AND** the Guard returns `permission: deny` and `decision: deny`
- **AND** the deny is `write_produto`, not empty-path

#### Scenario: str_replace_editor insert of product on develop is denied
- **WHEN** stdin is `{ "tool": "str_replace_editor", "args": { "command": "insert", "path": "backend/app/main.py", "insert_line": 1, "new_str": "x" } }` and `q_git=develop`
- **THEN** `extract_paths()` equals `["backend/app/main.py"]`
- **AND** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: str_replace_editor mutate of OpenSpec in Design is allowed
- **WHEN** stdin is `{ "tool": "str_replace_editor", "args": { "command": "str_replace", "path": "openspec/changes/card-782-dsh-adapter/design.md", "old_str": "a", "new_str": "b" } }` with `status` `Design` and `q_git` matching `card-782-*`
- **THEN** `extract_paths()` equals `["openspec/changes/card-782-dsh-adapter/design.md"]`
- **AND** the Guard returns `permission: allow` and `decision: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path

#### Scenario: str_replace_editor view of product is not write_produto
- **WHEN** stdin is `{ "tool": "str_replace_editor", "args": { "command": "view", "path": "backend/app/main.py" } }` and `q_git=develop`
- **THEN** the Guard returns `permission: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path

#### Scenario: workflow tool remains allow
- **WHEN** stdin is `{ "tool": "workflow", "args": { "script": "return 1", "meta": { "name": "x", "description": "y" } } }` with `q_git=develop`
- **THEN** the Guard returns `permission: allow` (class #611)

### Requirement: Empty dsh write file_path is not allow
When the canonical tool is dsh `write` or `edit`, a missing or empty `args.file_path` MUST NOT return allow. The Guard MUST deny (same class as OpenCode empty `filePath` / `apply_patch` without extractable path: not the missing-path early-return allow used for unknown tools). Mutating `str_replace_editor` (`create` / `str_replace` / `insert`) with empty `path` MUST deny empty-path **and** `extract_paths()` MUST be empty. Cursor/Grok envelopes whose tool is not in that write set keep the existing missing-path behavior except Status-edit and sidecar mutation. The empty_path reason string MUST name canonical write tools with an extractable path, not only “OpenCode write/edit/apply_patch”.

#### Scenario: write with empty file_path is denied
- **WHEN** stdin is `{ "tool": "write", "args": { "file_path": "" } }`
- **THEN** the Guard returns `permission: deny` and `decision: deny`
- **AND** it MUST NOT take the missing-path early-return allow

#### Scenario: edit with empty file_path is denied
- **WHEN** stdin is `{ "tool": "edit", "args": { "file_path": "" } }`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: str_replace_editor create with empty path is denied
- **WHEN** stdin is `{ "tool": "str_replace_editor", "args": { "command": "create", "path": "", "file_text": "x" } }`
- **THEN** `extract_paths()` is empty
- **AND** the Guard returns `permission: deny` and `decision: deny`
- **AND** it MUST NOT take the missing-path early-return allow
- **AND** the reason is empty_path, not a shell parse of `args.command`

#### Scenario: str_replace_editor insert with empty path is denied
- **WHEN** stdin is `{ "tool": "str_replace_editor", "args": { "command": "insert", "path": "", "insert_line": 1, "new_str": "x" } }`
- **THEN** `extract_paths()` is empty
- **AND** the Guard returns `permission: deny` and `decision: deny`
- **AND** the reason is empty_path

### Requirement: dsh plugin denies on Guard deny without throw
The dsh adapter SHALL live in `.dsh/plugin/` as Cordis `apply(ctx)` JS and SHALL serialize `{ tool: exec.name, args: exec.arguments }`, invoke the same `scripts/process-fsm/guard.py` / `decide()`, and return `{ kind: 'deny', reason }` when `permission`/`decision` is deny, **without** calling `next()`. dsh MUST NOT be treated as honoring OpenCode throw or Cursor stdout-only JSON as the Cordis decision. Allow MUST call `next()`. Write-like tools without a parseable `decide()` JSON MUST deny `fail_closed` (not `next()`, not throw). Detector hooks MUST NOT share this deny path. `process_event` remains the only Status mover; dsh `bash` with Status `item-edit` MUST deny via this path.

#### Scenario: Plugin deny on illegal product write
- **WHEN** the plugin receives `tools/pre-execute` for `edit` of `backend/` with `q_git=develop`
- **THEN** it calls `decide()` with the native envelope
- **AND** it returns `{ kind: 'deny', reason }` (does not throw, does not `next()`)

#### Scenario: Plugin does not deny on Design OpenSpec write
- **WHEN** the plugin receives `tools/pre-execute` for `edit` of `openspec/changes/` with `status=Design` and `q_git=card-<id>-*`
- **THEN** it calls `next()`

#### Scenario: Write-like without decide JSON is fail-closed
- **WHEN** `write` or `edit` runs and `guard.py` yields no parseable JSON
- **THEN** the plugin returns `{ kind: 'deny' }` with reason `fail_closed`
- **AND** it does not throw

### Requirement: dsh restricts Cordis self-modification tools
The dsh Guard plugin SHALL deny model-facing Cordis lifecycle tools that can mount or unmount plugins in the live process: `cordis_define`, `cordis_run`, `cordis_stop`, and `cordis_undefine` (and any `exec.name` starting with `cordis_` except `cordis_inspect_list`, `cordis_inspect_query`, and `cordis_inspect_self`). Inspect tools remain class #611. The web bundle MAY omit the model-facing `dsh-tool-cordis` row; the restrict MUST still apply when those tools are present.

#### Scenario: cordis_define is denied
- **WHEN** `tools/pre-execute` receives `exec.name` `cordis_define`
- **THEN** the plugin returns `{ kind: 'deny', reason }`
- **AND** it does not `next()`

#### Scenario: cordis inspect remains allow
- **WHEN** stdin is `{ "tool": "cordis_inspect_list", "args": {} }`
- **THEN** the Guard returns `permission: allow` (class #611)
