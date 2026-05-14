## 1. Backend Closed Beta Access

- [x] 1.1 Add closed-beta registration guards using `BETA_PUBLIC_REGISTRATION_ENABLED` and `BETA_INVITED_EMAILS`.
- [x] 1.2 Preserve login for active existing users and blocked-user rejection.
- [x] 1.3 Document beta access configuration and admin-created user flow.

## 2. Frontend Login

- [x] 2.1 Remove visible public `Criar Conta` mode from the login page.
- [x] 2.2 Keep login and forgot-password flow intact.
- [x] 2.3 Add focused frontend coverage that `/login` does not show public registration.

## 3. Tests

- [x] 3.1 Add backend unit coverage for unauthorized registration, invited registration, explicit public-registration override, login success, and missing-user login denial.
- [x] 3.2 Run focused backend auth tests.
- [x] 3.3 Run focused frontend build/E2E validation.

## 4. Delivery

- [x] 4.1 Run OpenSpec validation for `card-76-beta-access-control`.
- [x] 4.2 Run `openspec validate --all`.
- [ ] 4.3 Integrate in `develop`, run `./restart`, comment evidence, and move card #76 to `Done`.
