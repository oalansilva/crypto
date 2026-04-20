# Proposal: Remove /signals/onchain

## Change Type

- change

## User Story

As a crypto user
I want `/signals/onchain` to be removed from the product
So that the experience no longer exposes an unsupported or unwanted capability

## Value Proposition

- Reduces product surface and maintenance overhead
- Prevents users from reaching a deprecated flow
- Lowers regression risk by removing stale navigation and capability references

## Scope In

- Remove the `/signals/onchain` route
- Remove menus, links, CTAs, shortcuts, and saved-entry references that point to `/signals/onchain`
- Remove or adjust permissions, guards, internal integrations, and copy tied to this capability
- Preserve stability of adjacent signals flows after the removal

## Scope Out

- No replacement screen for `/signals/onchain`
- No redirect or temporary fallback flow
- No redesign of unrelated signals experiences
- No broad cleanup outside proven dependency points

## Dependencies

- Mapping of all known entry points to `/signals/onchain`
- Validation of permissions and internal references before merge

## Risks

- Hidden entry points may keep exposing the removed flow
- Saved links or internal integrations may break if references are not cleaned up
- Capability/permission leftovers may create regressions in adjacent signals flows

## Acceptance Criteria

1. Given a user navigates through the application, when they inspect menus and visible entry points, then there is no link or CTA to `/signals/onchain`.
2. Given a direct route hit or known saved link to `/signals/onchain`, when it is triggered after the change, then the removed flow is not available and other product areas remain stable.
3. Given permissions, guards, or internal integrations previously referenced `/signals/onchain`, when the change is deployed, then those references are removed or adjusted without breaking other signals capabilities.
4. Given QA validates the affected areas, when evidence is collected, then the removal is confirmed with no navigation regression in impacted entry points.

## Notes for Delivery

- Treat this as full capability removal, not a route-only cleanup.
- DESIGN is not required unless a hidden UI dependency appears during implementation.
