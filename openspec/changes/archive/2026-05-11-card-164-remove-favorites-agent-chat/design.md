## Context

`FavoritesDashboard` renders the `/favorites` workflow for strategy curation and analysis. It currently imports `MessageCircle` and `AgentChatModal`, keeps local state for an agent chat modal, and exposes chat buttons in both desktop row actions and mobile card actions for admin users.

`DESIGN.md` keeps this surface dense, operational, and action-focused. Removing the chat action reduces visual noise without changing the canonical Favorites jobs: choosing, ranking, analyzing, and deleting favorite strategies.

## Goals / Non-Goals

**Goals:**
- Remove the visible agent chat action from `/favorites` on desktop and mobile.
- Remove now-unused chat modal state/imports from `FavoritesDashboard`.
- Keep analysis, delete, tier stars, filters, comparison, and navigation unchanged.
- Add E2E coverage that prevents the chat action from returning on `/favorites`.

**Non-Goals:**
- Remove `AgentChatModal` globally.
- Change chat behavior in other screens.
- Change API contracts or favorite persistence.

## Decisions

1. Delete the action instead of hiding it with CSS.
   - Rationale: the product requirement says the option should not be exposed in Favoritos; removing the JSX and state avoids dead interactive code.
   - Alternative considered: `display: none`; rejected because it leaves unused behavior attached to the page.

2. Keep the existing row/card action structure.
   - Rationale: analysis and delete actions already follow the current Favorites layout and DESIGN.md constraints.
   - Alternative considered: restyle the action area; rejected as outside the card scope.

3. Leave `AgentChatModal` component in place.
   - Rationale: the issue only targets the Favorites screen. Other future or existing chat surfaces should not be changed by this card.

## Risks / Trade-offs

- [Risk] Removing the chat button could accidentally remove admin delete action spacing. -> Mitigation: edit only chat-specific import, state, handler, modal, and buttons; preserve delete JSX.
- [Risk] Existing E2E assertions may rely on the action count. -> Mitigation: run focused Favorites E2E and adjust/add assertions for the removed chat action.
