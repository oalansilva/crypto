## ADDED Requirements

### Requirement: Guard judges the real write destination of shell commands
The Guard SHALL resolve the destination of shell redirections (`>`, `>>`, `tee`) to an absolute path before classifying a command as a product write: a destination outside the repository (for example the session scratchpad or `/tmp`) SHALL NOT be a product write, and `>`/`>>` inside the body of a heredoc SHALL be treated as text, not as a redirection. A redirection into the repository SHALL keep being judged as today (R33, finding 39 of #1101).

#### Scenario: Redirect to the scratchpad
- **WHEN** a Bash command in a card without product-write permission redirects output to a file in the session scratchpad
- **THEN** the Guard allows it

#### Scenario: Append marker inside a heredoc
- **WHEN** a Bash command writes a heredoc to a scratchpad file and the heredoc body contains `>>`
- **THEN** the Guard allows it

#### Scenario: Redirect into the repository
- **WHEN** a Bash command redirects output to `backend/x.py` on `develop`
- **THEN** the Guard denies it with the same reason as today
