# Proposal: Migrate to Database-Driven Strategy Configuration

## Problem Statement

Currently, the system has a hybrid approach to combo strategies:
- **Pre-built templates**: Hard-coded as Python classes in `backend/app/strategies/combos/`
- **Example templates**: Stored in database with JSON configuration

This creates several issues:
1. **Code deployment required** for new strategies
2. **Inconsistent architecture** between pre-built and examples
3. **Limited flexibility** - users can't easily customize pre-built strategies
4. **Optimization schema duplication** - `get_optimization_schema()` exists only in Python classes

## Proposed Solution

Migrate to a **100% database-driven architecture** where:
- All strategies (pre-built, examples, custom) are stored in `combo_templates` table
- Optimization schemas are stored as JSON in the database
- Python code only **interprets** configuration (no hard-coded strategies)
- Pre-built strategies become "seed data" with `is_prebuilt=1` flag

## Benefits

### For Users
- ✅ **No code deployment** needed to create/modify strategies
- ✅ **Consistent experience** across all template types
- ✅ **Easy customization** of pre-built strategies via UI
- ✅ **Version control** of strategies in database
- ✅ **Sharing strategies** via JSON export/import

### For Developers
- ✅ **Simpler codebase** - remove 6 Python strategy classes
- ✅ **Easier testing** - strategies are data, not code
- ✅ **Faster iteration** - modify strategies without code changes
- ✅ **Better separation** of concerns (engine vs. configuration)

## High-Level Design

### Database Schema Enhancement

```sql
ALTER TABLE combo_templates ADD COLUMN optimization_schema JSON;
```

**Example optimization_schema:**
```json
{
  "ema_fast": {
    "min": 5,
    "max": 20,
    "step": 1,
    "default": 9
  },
  "rsi_period": {
    "min": 7,
    "max": 21,
    "step": 1,
    "default": 14
  }
}
```

### Migration Strategy

1. **Phase 1**: Add `optimization_schema` column to database
2. **Phase 2**: Migrate 6 pre-built strategies to database as seed data
3. **Phase 3**: Update `ComboService` to load all strategies from database
4. **Phase 4**: Remove hard-coded Python strategy classes
5. **Phase 5**: Update `ComboOptimizer` to read schema from database

### Backward Compatibility

- Existing example templates work as-is (already in database)
- API endpoints remain unchanged
- Frontend requires no changes
- Migration script handles data transformation

## User Review Required

> [!IMPORTANT]
> **Breaking Change**: This removes the hard-coded Python strategy classes. After migration, all strategies will be database-driven.

> [!WARNING]
> **Data Migration**: Requires running migration script to populate database with pre-built strategies.

## Implementation Phases

### Phase 1: Database Schema (Low Risk)
- Add `optimization_schema` JSON column
- Update migration script
- Backward compatible

### Phase 2: Seed Pre-built Strategies (Medium Risk)
- Convert 6 Python classes to JSON seed data
- Populate database with pre-built strategies
- Mark with `is_prebuilt=1` flag

### Phase 3: Update Service Layer (High Risk)
- Modify `ComboService.get_template_metadata()` to read from DB only
- Remove `PREBUILT_TEMPLATES` dictionary
- Update `ComboOptimizer` to use DB schema

### Phase 4: Cleanup (Low Risk)
- Delete Python strategy class files
- Update documentation
- Remove unused imports

## Validation Plan

### Automated Tests
- Unit tests for database schema
- Integration tests for strategy loading
- Optimization tests with DB-driven schemas

### Manual Verification
- Verify all 6 pre-built strategies work from database
- Test optimization with DB schemas
- Confirm UI displays strategies correctly

## Rollback Plan

If issues arise:
1. Revert database migration
2. Restore Python strategy classes from git
3. Revert service layer changes

Database backup recommended before migration.

## Timeline Estimate

- **Phase 1**: 1 hour (schema + migration script)
- **Phase 2**: 2 hours (convert 6 strategies to JSON)
- **Phase 3**: 3 hours (service layer refactoring)
- **Phase 4**: 1 hour (cleanup)
- **Testing**: 2 hours

**Total**: ~9 hours

## Success Criteria

- ✅ All 6 pre-built strategies work from database
- ✅ Optimization uses DB-driven schemas
- ✅ No Python strategy class files remain
- ✅ All existing tests pass
- ✅ Documentation updated

## Related Changes

This change builds upon:
- `add-indicator-combinations` (current combo system)

This change enables future:
- Visual strategy builder UI
- Strategy marketplace/sharing
- A/B testing of strategies
- Strategy versioning system
