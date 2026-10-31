## ADDED Requirements

### Requirement: Step 1 saves the landing lead
The landing lead endpoint SHALL save a lead as soon as the visitor submits step 1 with a name and a valid e-mail. Step 2 (WhatsApp, crypto level, main difficulty) SHALL be optional and SHALL only enrich the same lead. The lead SHALL keep every field the form asks for: name, e-mail, WhatsApp, crypto level, main difficulty, origin, and the sanitized attribution (UTM parameters, referrer without query, landing path, first-seen time).

#### Scenario: Visitor leaves after step 1
- **WHEN** a visitor submits step 1 with name and e-mail and closes the page
- **THEN** the system SHALL have one lead stored with that name and e-mail
- **AND** WhatsApp, level and difficulty SHALL be empty for that lead

#### Scenario: Visitor completes step 2
- **WHEN** a visitor who saved step 1 submits step 2 with WhatsApp, level and difficulty
- **THEN** the system SHALL store those fields in the same lead
- **AND** it SHALL NOT create a second lead for that e-mail

#### Scenario: Step 2 fields are all optional
- **WHEN** a visitor submits step 2 with every field empty, or skips step 2
- **THEN** the lead from step 1 SHALL stay stored
- **AND** the endpoint SHALL NOT reject the submission for a missing WhatsApp, level or difficulty

#### Scenario: Same e-mail submits step 1 again
- **WHEN** step 1 arrives for an e-mail that already has a lead
- **THEN** the system SHALL update that lead instead of creating a duplicate
- **AND** it SHALL keep fields from an earlier step 2 that the new submission does not carry

### Requirement: Landing lead response stays neutral and creates no account
The landing lead endpoint SHALL answer every accepted submission with the same neutral response, whether or not the e-mail already has a lead, an account or an invite. It SHALL NOT create an account, SHALL NOT consume an invite and SHALL keep recording the lead audit event, as required by `beta-lead-access-hardening`.

#### Scenario: E-mail of an existing account
- **WHEN** step 1 arrives for an e-mail that already has an app account
- **THEN** the response SHALL be the same as for a new e-mail
- **AND** no account SHALL be created or changed

### Requirement: Alan is notified of each new lead
The system SHALL send Alan a Telegram message, through the existing Cripto Farol bot, for each new landing lead, with name, e-mail and origin. When step 2 arrives, it SHALL send a follow-up with WhatsApp, level and difficulty. A notification failure SHALL NOT fail or undo the lead submission.

#### Scenario: New lead
- **WHEN** a new lead is saved at step 1
- **THEN** Alan SHALL receive one Telegram message identifying it as a new lead with name, e-mail and origin

#### Scenario: Lead completes step 2
- **WHEN** step 2 enriches a lead
- **THEN** Alan SHALL receive one follow-up Telegram message with WhatsApp, level and difficulty for that lead

#### Scenario: Telegram is unavailable
- **WHEN** the Telegram send fails or no admin has a linked Telegram chat
- **THEN** the lead SHALL still be stored and the visitor SHALL still see the success state
- **AND** the failure SHALL be logged without the lead's personal data

### Requirement: Honest success and error messages
The landing form SHALL tell the visitor only what actually happens. The step 1 button SHALL NOT say "Garantir minha vaga". After step 1 the form SHALL confirm the registration is saved and offer step 2 as optional, with a way to skip it. The final state SHALL say the registration was received and that the visitor will be called when the next wave opens, and SHALL NOT promise an e-mail.

#### Scenario: Success state
- **WHEN** the visitor finishes or skips step 2
- **THEN** the form SHALL show "Recebemos seu cadastro." and "Vamos te chamar quando abrir a próxima leva do beta."
- **AND** the page SHALL NOT mention an access e-mail, an e-mail to check, or a guaranteed seat

#### Scenario: Step 1 fails
- **WHEN** the lead endpoint fails at step 1
- **THEN** the form SHALL stay on step 1 and show "Não conseguimos salvar agora. Tente de novo em alguns minutos."

#### Scenario: Step 2 fails
- **WHEN** the lead endpoint fails at step 2
- **THEN** the form SHALL say the registration is already saved and offer to retry or skip

### Requirement: Seat counter endpoint is removed
The public `GET /api/leads/stats` endpoint and the 50-seat constant SHALL be removed, since the landing no longer shows a count of registrations or seats.

#### Scenario: Stats endpoint after the change
- **WHEN** a client calls `GET /api/leads/stats`
- **THEN** the backend SHALL NOT return a count of accounts or seats

### Requirement: Keyboard submit and focus follow the active form step
Pressing Enter (or the phone keyboard's "Go") in a step 1 field SHALL do exactly what the "Entrar na lista do beta" button does: validate name and e-mail, save step 1 with the name, and show step 2. It SHALL NOT send step 2. Pressing Enter in a step 2 field SHALL send step 2. After step 1 is saved, focus SHALL move to the step 2 title, not to a step 2 input.

#### Scenario: Enter on step 1 = "Entrar na lista do beta"
- **WHEN** a visitor fills name and e-mail and presses Enter in the e-mail field
- **THEN** the form SHALL send step 1 with the name and e-mail and show step 2
- **AND** it SHALL NOT send a step 2 submission nor skip step 2
- **AND** the funnel SHALL record `lead_step1_completed` and no step 2 event

#### Scenario: Enter on an empty step 1
- **WHEN** a visitor presses Enter in step 1 with name or e-mail empty or invalid
- **THEN** the form SHALL stay on step 1 and show the field validation
- **AND** nothing SHALL be sent

#### Scenario: Focus after step 1
- **WHEN** step 1 is saved
- **THEN** focus SHALL move to the step 2 title ("Cadastro salvo. Quer contar um pouco sobre você? É opcional.")
- **AND** the phone keyboard SHALL NOT open by itself over "Pular esta etapa"
