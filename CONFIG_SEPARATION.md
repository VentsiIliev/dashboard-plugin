# Configuration Separation - Generic vs Glue Dashboard

## Summary

The dashboard configuration has been split into two separate configs:

### 1. **DashboardConfig** (Generic Base)
- **Location**: `src/dashboard/core/config.py`
- **Purpose**: Base configuration for any dashboard type
- **Defaults**: Generic, minimal values suitable for any use case
- **Key changes**:
  - `card_grid_rows: 2` (generic 2x2 grid)
  - `card_grid_cols: 2`
  - `show_placeholders: False` (hidden by default for cleaner look)
  - Smaller trajectory widget (640x360)
  - More conservative dimensions

### 2. **GlueDashboardConfig** (Glue-Specific)
- **Location**: `src/glue_dispensing_dashboard/core/config.py`
- **Purpose**: Configuration specific to glue dispensing dashboard
- **Extends**: `DashboardConfig` (inherits all base fields)
- **Overrides**:
  - `card_grid_rows: 3` (vertical stack for 3 glue meters)
  - `card_grid_cols: 1`
  - `card_min_height: 150` (taller cards for glue meters)
  - `action_grid_rows: 2` / `action_grid_cols: 3` (6 action buttons)
  - `show_placeholders: True` (shown by default for easier config)
  - `default_cell_capacity_grams: 5000.0` (glue-specific)

## Files Updated

1. **`glue_dispensing_dashboard/core/config.py`** (NEW)
   - Created `GlueDashboardConfig` class

2. **`glue_dispensing_dashboard/adapter/GlueAdapter.py`**
   - Import changed: `DashboardConfig` → `GlueDashboardConfig`
   - Type annotation changed: `CONFIG: GlueDashboardConfig`
   - Fallback imports updated to use `glue_dispensing_dashboard`

3. **`glue_dispensing_dashboard/ui/factories/GlueCardFactory.py`**
   - Import changed: `DashboardConfig` → `GlueDashboardConfig`
   - Type hint changed: `config: GlueDashboardConfig`

4. **`dashboard/core/config.py`**
   - Updated to be a generic base class with minimal defaults
   - More conservative values suitable for any dashboard type
   - Added docstring explaining it's a base class

## Usage

**Generic Dashboard:**
```python
from dashboard.core.config import DashboardConfig

config = DashboardConfig()  # Generic defaults
dashboard = DashboardWidget(config=config, ...)
```

**Glue Dashboard:**
```python
from glue_dispensing_dashboard.core.config import GlueDashboardConfig

config = GlueDashboardConfig()  # Glue-specific defaults
dashboard = DashboardWidget(config=config, ...)
```

**Custom Glue Dashboard:**
```python
config = GlueDashboardConfig(
    card_grid_rows=4,  # Override: 4 glue meters instead of 3
    show_placeholders=False,  # Hide placeholders
    trajectory_width=800  # Bigger trajectory view
)
```

## Benefits

1. **Separation of Concerns**: Generic dashboard code doesn't know about glue-specific configs
2. **Extensibility**: Easy to create more specialized configs (e.g., `PickAndPlaceDashboardConfig`)
3. **Inheritance**: Glue config automatically gets updates to base config fields
4. **Type Safety**: Different types make it clear which config is used where
5. **Clear Defaults**: Each use case has appropriate default values

## Migration

Existing code using `GlueAdapter` requires **no changes** - it automatically uses the new `GlueDashboardConfig`.

The `run_app.py` and `run_ui.py` runners continue to work without modification.

