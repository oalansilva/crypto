# Proposal: Fix Disabled Save Button for Comments on Kanban Cards

## Problem Statement

Users cannot save comments on Kanban cards via desktop because the "Comentar" (Save/Post) button remains disabled. This prevents users from adding comments to cards, which is a critical feature for collaboration.

**Reported Issue (Portuguese):** "Não consigo salvar comentários via desktop nos cards o botão esta desabilitado"

## Root Cause Analysis

After reviewing the frontend code in `KanbanPage.tsx`, the "Comentar" button is disabled based on three conditions:

```tsx
disabled={createComment.isPending || !author.trim() || !body.trim()}
```

1. **`createComment.isPending`** - True when the mutation is in progress (expected behavior)
2. **`!author.trim()`** - True when the author field is empty
3. **`!body.trim()`** - True when the comment body is empty

The issue occurs because:

- The author field attempts to load from `localStorage.getItem('kanban.commentAuthor')` but defaults to an empty string if not set
- On first use (or after clearing browser data), no author is persisted, leaving the field empty
- With an empty author field, the button stays disabled regardless of whether the comment body has content
- Users may not realize they need to manually enter an author name each time

## Proposed Solution

**Option A (Recommended):** Pre-fill the author field with a sensible default
- Use the user's display name or a default like "User" or "Anonymous"
- Still allow manual editing if needed

**Option B:** Make the author field optional on the backend
- Modify the `CoordinationCommentCreateRequest` schema to make `author` optional
- Default to a system value (e.g., "Anonymous" or use a timestamp-based identifier)

**Option C:** Add a placeholder/prompt in the author field
- Make it more obvious that the author field is required
- Add inline validation messages

## Impact Assessment

- **Frontend Changes:** Minimal - mainly UI text and default values
- **Backend Changes:** Optional - if making author optional
- **Breaking Changes:** None - this is a bug fix
- **User Experience:** Significantly improved - users can post comments without manually entering author each time

## Files Involved

- `/frontend/src/pages/KanbanPage.tsx` - Comment form component
- `/backend/app/routes/coordination.py` - Optional: backend schema modification

## Acceptance Criteria

1. User can post a comment on a Kanban card without manually entering an author
2. The "Comentar" button is enabled when the comment body has content (assuming author is auto-filled)
3. If author is left empty, a sensible default is used or a clear prompt is shown
4. No regression in existing functionality
