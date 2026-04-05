# Design: Onchain SignalCard MVP

## Goal

Provide a minimal UI direction for the onchain signal feature so DEV can implement the frontend slice without blocking on a missing design artifact.

## UX Direction

- Surface the feature as a dedicated `/signals/onchain` view
- Keep the first version separate from the existing general signals page
- Prioritize readability over dense analytics
- Show one primary decision per card: `BUY`, `SELL`, or `HOLD`

## Signal Card Structure

Each signal card should display:

1. Token / asset name
2. Chain badge
3. Primary signal badge (`BUY`, `SELL`, `HOLD`)
4. Confidence score (`0-100`)
5. Short breakdown of the strongest drivers
6. Timestamp of last update

## Visual Rules

- Confidence above `70`: positive emphasis
- Confidence from `40` to `70`: neutral emphasis
- Confidence below `40`: warning emphasis
- Breakdown details may start as simple text rows instead of advanced charts

## MVP Scope

- List view with filters for token, chain, and confidence threshold
- Responsive layout for desktop and mobile
- No advanced visualization requirement for the first pass
- No requirement for pixel-perfect prototype before backend work starts

## Implementation Notes

- Backend phases are not blocked by this file
- If DEV reaches the frontend phase, this document is the minimum design contract
- If the UI needs richer exploration later, that should be handled as a refinement, not as missing approval
