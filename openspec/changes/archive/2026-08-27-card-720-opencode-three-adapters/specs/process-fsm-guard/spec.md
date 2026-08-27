## ADDED Requirements

### Requirement: Guard normalizes the OpenCode native dialect
`scripts/process-fsm/` SHALL normalize hook stdin so `decide()` is client-agnostic across three dialects. In addition to Cursor (`tool_name` / `tool_input`) and Grok (`toolName` / `toolInput`), the normalizer MUST accept the native OpenCode payload `{ tool, args }` as a third dialect. Canonical OpenCode write tools SHALL include `write`, `edit`, and `apply_patch`. Canonical OpenCode shell tool SHALL include `bash`. Path extraction MUST use `args.filePath` for `write`/`edit`. For `apply_patch`, path extraction MUST parse `args.patchText` markers observed on OpenCode 1.18.18: `*** Add File:`, `*** Update File:`, `*** Delete File:`, and `*** Move to:` (issue shorthand “Move File” maps to live `*** Move to:`; `*** Move to:` yields the **destination** path). `extract_paths()` SHALL return every marker path in order. `decide()` SHALL classify each extracted path and treat the envelope as `write_produto` when **any** path matches `product_globs`. For `bash`, path extraction MUST use `args.command` with the same mutation classification as other shell dialects (`tee`, `>`, Status `item-edit`). `cwd` MAY come from plugin `directory` / `worktree` when the envelope omits `cwd`. An OpenCode `edit`/`write` of a `product_globs` path with `q_git=develop` MUST take the same `write_produto` path as a Cursor `Write`. Unknown tools remain class #611: allow. The bash fallback MUST parse `tool`/`args`/`filePath`/`patchText`; missing native keys is not an allow token for those canonical OpenCode write tools.

#### Scenario: OpenCode edit of product on develop is denied
- **WHEN** stdin is a native OpenCode envelope `{ "tool": "edit", "args": { "filePath": "backend/app/tasks/discovery_tasks.py" } }` and `q_git=develop`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: OpenCode apply_patch of product on develop is denied
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "*** Begin Patch\n*** Update File: backend/app/main.py\n*** End Patch" } }` and `q_git=develop`
- **THEN** `extract_paths()` equals `["backend/app/main.py"]`
- **AND** the Guard returns `permission: deny` and `decision: deny`
- **AND** the deny is `write_produto`, not empty-path

#### Scenario: OpenCode apply_patch OpenSpec path from patchText is allowed
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "*** Begin Patch\n*** Add File: openspec/changes/card-720-opencode-three-adapters/design.md\n*** End Patch" } }` with no `filePath`, `status` is `Design`, and `q_git` matches `card-720-*`
- **THEN** `extract_paths()` equals `["openspec/changes/card-720-opencode-three-adapters/design.md"]`
- **AND** the Guard returns `permission: allow` and `decision: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path

#### Scenario: OpenCode apply_patch Move to product dest is denied
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "*** Begin Patch\n*** Update File: docs/note.md\n*** Move to: backend/app/moved.py\n*** End Patch" } }` and `q_git=develop`
- **THEN** `extract_paths()` contains `backend/app/moved.py`
- **AND** the Guard returns `permission: deny` and `decision: deny`
- **AND** a parse that only kept `docs/note.md` MUST NOT be treated as passing this scenario

#### Scenario: OpenCode bash tee onto backend is denied
- **WHEN** stdin is `{ "tool": "bash", "args": { "command": "echo x | tee backend/app/main.py" } }` and I1 does not hold
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: OpenCode OpenSpec write in Design on card branch is allowed
- **WHEN** stdin is OpenCode `edit` of a path under `openspec/changes/` and `status` is `Design` and `q_git` matches `card-<id>-*`
- **THEN** the Guard returns `permission: allow` and `decision: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path

#### Scenario: Unknown OpenCode tool remains allow
- **WHEN** stdin is `{ "tool": "grep", "args": {} }` with no extractable product path
- **THEN** the Guard returns `permission: allow` (class #611)

### Requirement: Empty OpenCode write path is not allow
When the canonical tool is OpenCode `write`, `edit`, or `apply_patch`, a missing `filePath`, empty `patchText`, or `patchText` with no extractable path MUST NOT return allow. The Guard MUST deny (not take the missing-path early-return allow used for unknown tools). Cursor/Grok envelopes whose tool is not in that OpenCode write set keep the existing missing-path behavior except Status-edit and sidecar mutation.

#### Scenario: apply_patch with empty patchText is denied
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "" } }`
- **THEN** the Guard returns `permission: deny` and `decision: deny`
- **AND** it MUST NOT take the missing-path early-return allow

#### Scenario: apply_patch without extractable path is denied
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "*** Begin Patch\n*** End Patch" } }`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: edit with empty filePath is denied
- **WHEN** stdin is `{ "tool": "edit", "args": { "filePath": "" } }`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

### Requirement: OpenCode plugin throws on Guard deny
The OpenCode adapter SHALL live in `.opencode/plugin/` as auto-loaded JS (or TS) and SHALL serialize the native `{ tool, args }` object, invoke the same `scripts/process-fsm/guard.py` / `decide()`, and **throw** when `permission`/`decision` is deny. OpenCode 1.18.18 MUST NOT be treated as honoring stdout JSON `{permission, decision}`. Allow MUST NOT throw. Detector hooks MUST NOT share this throw path. `process_event` remains the only Status mover; OpenCode `bash` with Status `item-edit` MUST throw via this deny.

#### Scenario: Plugin throw on illegal product write
- **WHEN** the plugin receives `tool.execute.before` for `edit` of `backend/` with `q_git=develop`
- **THEN** it calls `decide()` with the native envelope
- **AND** it throws (does not return JSON `{permission: deny}` as the OpenCode decision)

#### Scenario: Plugin does not throw on Design OpenSpec write
- **WHEN** the plugin receives `tool.execute.before` for `edit` of `openspec/changes/` with `status=Design` and `q_git=card-<id>-*`
- **THEN** it does not throw
