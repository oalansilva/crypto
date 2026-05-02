## ADDED Requirements

### Requirement: Form success feedback is visible
The frontend UI SHALL render success feedback from form submissions in a visible notification surface that is fixed near the top center of the viewport, above the app content.

#### Scenario: Profile update success
- **WHEN** an authenticated user updates and saves "Meu Perfil" successfully
- **THEN** the UI SHALL display a visible confirmation message that the profile was updated

#### Scenario: Shared toast viewport renders messages
- **WHEN** any screen dispatches a toast notification
- **THEN** the notification content SHALL render inside the fixed toast viewport instead of an empty placeholder

#### Scenario: User dismisses a toast
- **WHEN** a notification is visible and the user clicks the close button
- **THEN** the notification SHALL close visually
