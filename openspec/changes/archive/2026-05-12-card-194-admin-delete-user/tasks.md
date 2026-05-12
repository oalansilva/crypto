## 1. Backend

- [x] 1.1 Add the admin delete-user request/response contract and route.
- [x] 1.2 Record `user_deleted` audit evidence before deleting the user row.
- [x] 1.3 Block self-deletion for the logged-in admin user.

## 2. Frontend

- [x] 2.1 Add a delete action to the existing Admin Users workflow using `$crypto-frontend` conventions.
- [x] 2.2 Require a reason and browser confirmation before sending the delete request.
- [x] 2.3 Refresh the list and clear selected user state after deletion.

## 3. Validation

- [x] 3.1 Add backend tests for successful deletion and self-delete block.
- [x] 3.2 Run focused backend tests, frontend build, and OpenSpec validation.
