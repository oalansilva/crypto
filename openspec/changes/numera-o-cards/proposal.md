# Proposal — numera-o-cards

## Why

On the Kanban board, cards are currently identified mainly by title and slug. As the board grows, it becomes harder to reference a specific card quickly in chat, QA evidence, and operational coordination.

Users asked for an automatic sequential code for each Kanban card (for example `#1`, `#2`, `#3`) so cards can be located and referenced faster.

## What Changes

- assign each card a stable human-friendly sequential number
- show the number in the Kanban card surface and detail view
- persist the number in the runtime/workflow layer so reloads keep the same identifier
- expose the number in board/query payloads used by the UI and automation
- ensure newly created cards receive the next available number automatically

## Scope

This change covers:
- numbering for runtime Kanban cards/changes
- display of the number in the board UI and related detail surfaces
- runtime/API support for reading the number
- automatic assignment for new cards

This change does not cover:
- manual renumbering
- per-column numbering
- renumbering based on reorder or workflow stage
- replacing the existing slug/change id

## Outcome

After this change, every board card has a simple visible number that stays stable over time, improving communication, QA references, and operational pull-order discussions.
