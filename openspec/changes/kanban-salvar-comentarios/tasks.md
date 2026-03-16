# Tasks: Fix Disabled Save Button for Comments

## Task List

### Task 1: Fix Author Field Pre-population (Frontend)
**Type:** Bug Fix  
**Priority:** High  
**Estimate:** Small  

- [ ] Modify `KanbanPage.tsx` to pre-fill the author field with a default value
- [ ] Use a sensible default like "User" or retrieve from a user profile if available
- [ ] Ensure the localStorage save/load still works for subsequent visits

**Suggested Code Change:**
```tsx
// Before:
const [author, setAuthor] = useState(() => localStorage.getItem('kanban.commentAuthor') || '')

// After:
const [author, setAuthor] = useState(() => localStorage.getItem('kanban.commentAuthor') || 'User')
```

### Task 2: Add Visual Indicator for Required Fields (Frontend)
**Type:** UX Improvement  
**Priority:** Medium  
**Estimate:** Small  

- [ ] Add a placeholder text to the author input field (e.g., "Your name")
- [ ] Consider adding a subtle asterisk or label indicating the field is required

### Task 3: Backend: Make Author Optional (Optional Enhancement)
**Type:** Enhancement  
**Priority:** Low  
**Estimate:** Medium  

- [ ] Modify `CoordinationCommentCreateRequest` in `/backend/app/routes/coordination.py` to make `author` optional
- [ ] Add a default value handler on the backend (e.g., "Anonymous")
- [ ] Update API tests if applicable

**Suggested Code Change:**
```python
class CoordinationCommentCreateRequest(BaseModel):
    author: str = "Anonymous"  # Default value
    body: str = Field(max_length=2000)
```

### Task 4: Verify Fix (QA)
**Type:** Validation  
**Priority:** High  
**Estimate:** Small  

- [ ] Test on desktop browser: Open a Kanban card, verify "Comentar" button is enabled
- [ ] Test on mobile browser: Verify same behavior
- [ ] Test with empty author field: Verify fallback works
- [ ] Test after clearing localStorage: Verify default author is used

---

## Implementation Order

1. **Task 1** - Primary fix (enables button by defaulting author)
2. **Task 2** - UX improvement (makes it clearer what's needed)
3. **Task 3** - Optional backend enhancement (future-proofing)
4. **Task 4** - Validation

## Notes

- The issue is not device-specific (desktop vs mobile) - the same code runs on both
- The root cause is simply that the author field starts empty on first use
- The simplest fix is pre-filling the author with a default value
