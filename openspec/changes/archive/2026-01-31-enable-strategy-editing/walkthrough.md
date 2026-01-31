# Walkthrough: Strategy Editor & Cloning

This detailed walkthrough covers the new Strategy Editor and Cloning features implemented to allow users to customize their combo strategies.

## ✨ New Features

### 1. Strategy Editor
Users can now edit the optimization parameters of their strategies directly from the UI.

- **Visual Mode**: Form-based editing for `min`, `max`, and `step` values of each parameter.
- **Advanced Mode**: Full JSON editor (using Monaco Editor) for power users to modify the underlying schema directly.
- **Validation**: Real-time validation prevents invalid ranges (e.g., Min > Max).

### 2. Strategy Cloning
To preserve the integrity of pre-built strategies (like `multi_ma_crossover`), we implemented a "Copy on Write" mechanism.

- **Read-Only**: System templates are marked as read-only.
- **Clone Action**: Users can clone any template to create a custom, editable copy.
- **Flow**: Clicking "Edit" on a read-only template automatically prompts to clone.

### 3. Backend Enhancements
- **New Endpoints**:
    - `PUT /api/combos/meta/{template_name}`: Update template metadata and schema.
    - `POST /api/combos/meta/{template_name}/clone`: Clone a template.
    - `DELETE /api/combos/meta/{template_name}`: Delete a custom template.
- **Validation**: Improved Pydantic schemas and backend validation logic.

## 🛠️ Technical Implementation

### Frontend (`ComboEditPage.tsx`)
The editor page provides a dual-mode interface.

```tsx
// Mode Toggle
<div className="bg-black/40 p-1 rounded-lg flex items-center border border-white/10">
    <button onClick={() => setAdvancedMode(false)} ...>Visual</button>
    <button onClick={() => setAdvancedMode(true)} ...>JSON</button>
</div>
```

### Backend (`ComboService.py`)
We added methods to handle the cloning and updating logic safely.

```python
def clone_template(self, source_name: str, new_name: str) -> Dict[str, Any]:
    # ...
    # Mark as custom (not prebuilt, not example)
    cursor.execute("""
        INSERT INTO combo_templates (...)
        VALUES (?, ?, 0, 0, ...)
    """, ...)
```

## ✅ Verification Results

We ran an automated integration test script (`integration_test.py`) that verified the entire lifecycle:

1. **List**: Confirmed `is_readonly` flags are correct.
2. **Clone**: Successfully cloned `multi_ma_crossover` to a new name.
3. **Update**: Modified `sma_medium` range via API and verified persistence.
4. **Backtest**: Executed a backtest using the *modified* template, confirming the backend uses the updated parameters.
5. **Serialization**: Validated that all API responses key fields correctly, handling Timestamp and Numpy types.

All tests passed successfully.

## 📸 Usage Guide

1. Navigate to **"Combo Strategies"** from the home page.
2. Identify strategies by their icons:
    - 🔒 **Lock**: Read-only (System)
    - 🔓 **Unlock**: Editable (Custom)
3. Click the **Edit (Pencil)** icon on a custom strategy to modify it.
4. Click the **Clone (Copy)** icon on any strategy to duplicate it.
5. In the editor, adjust parameters and click **Save**.
