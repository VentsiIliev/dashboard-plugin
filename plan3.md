# Plan: Generic Dashboard / Glue Dispensing Separation

## Context

The dashboard plugin mixes two concerns in one flat package:
- A generic dashboard framework (trajectory view, start/stop/pause, configurable grid layout)
- A glue dispensing application (GlueMeterCards, broker subscriptions to glue-cell topics, ApplicationState, SetupWizard)

The goal is a clean sub-package split so the generic dashboard can be reused without pulling in any glue-specific code.

---

## Target Directory Structure

```
src/dashboard/
├── core/                        # GENERIC — unchanged
│   ├── config.py               # DashboardConfig
│   ├── protocols.py            # Protocol interfaces (kept generic)
│   ├── IconLoader.py
│   └── _compat.py              # DELETED (moved to glue/core/)
├── ui/                          # GENERIC — unchanged
│   ├── DashboardWidget.py      # ActionButtonConfig, CardConfig, DashboardWidget
│   ├── managers/DashboardLayoutManager.py
│   └── widgets/
│       ├── ControlButtonsWidget.py
│       ├── RobotTrajectoryWidget.py
│       └── shared/  (MaterialButton, DashboardCard, ComboBoxStyle, Drawer)
├── styles.py                    # GENERIC — unchanged
│
└── glue/                        # NEW — glue dispensing specific
    ├── __init__.py
    ├── adapter/
    │   ├── __init__.py
    │   ├── GlueAdapter.py      # was adapter/DashboardAdapter.py (class renamed GlueAdapter)
    │   ├── ApplicationState.py # moved from adapter/
    │   ├── MessageBroker.py    # moved from adapter/
    │   └── topics.py           # moved from adapter/
    ├── app/
    │   ├── __init__.py
    │   └── GlueAppWidget.py    # was app/DashboardAppWidget.py (class renamed GlueAppWidget)
    ├── core/
    │   ├── __init__.py
    │   ├── container.py        # was core/container.py (class renamed GlueContainer)
    │   └── _compat.py          # was core/_compat.py
    └── ui/
        ├── __init__.py
        ├── setupWizard.py      # moved from ui/
        ├── factories/
        │   ├── __init__.py
        │   └── GlueCardFactory.py  # moved from ui/factories/
        └── widgets/
            ├── __init__.py
            ├── GlueMeterCard.py    # moved from ui/widgets/
            └── GlueMeterWidget.py  # moved from ui/widgets/
```

**Old locations deleted after move:**
- `adapter/` (entire folder)
- `app/` (entire folder)
- `core/container.py`, `core/_compat.py`
- `ui/setupWizard.py`
- `ui/factories/` (entire folder)
- `ui/widgets/GlueMeterCard.py`, `ui/widgets/GlueMeterWidget.py`

---

## Implementation Steps

### 1. Create `glue/` sub-package skeleton

Create `__init__.py` files for all new directories:
- `src/dashboard/glue/__init__.py`
- `src/dashboard/glue/adapter/__init__.py`
- `src/dashboard/glue/app/__init__.py`
- `src/dashboard/glue/core/__init__.py`
- `src/dashboard/glue/ui/__init__.py`
- `src/dashboard/glue/ui/factories/__init__.py`
- `src/dashboard/glue/ui/widgets/__init__.py`

### 2. Move + rename files (create new, delete old)

| Old path | New path | Class rename |
|---|---|---|
| `adapter/DashboardAdapter.py` | `glue/adapter/GlueAdapter.py` | `DashboardAdapter → GlueAdapter` |
| `adapter/ApplicationState.py` | `glue/adapter/ApplicationState.py` | — |
| `adapter/MessageBroker.py` | `glue/adapter/MessageBroker.py` | — |
| `adapter/topics.py` | `glue/adapter/topics.py` | — |
| `app/DashboardAppWidget.py` | `glue/app/GlueAppWidget.py` | `DashboardAppWidget → GlueAppWidget` |
| `core/container.py` | `glue/core/container.py` | `DashboardContainer → GlueContainer` |
| `core/_compat.py` | `glue/core/_compat.py` | — |
| `ui/setupWizard.py` | `glue/ui/setupWizard.py` | — |
| `ui/factories/GlueCardFactory.py` | `glue/ui/factories/GlueCardFactory.py` | — |
| `ui/widgets/GlueMeterCard.py` | `glue/ui/widgets/GlueMeterCard.py` | — |
| `ui/widgets/GlueMeterWidget.py` | `glue/ui/widgets/GlueMeterWidget.py` | — |

### 3. Update imports in each moved file

**`glue/adapter/GlueAdapter.py`** (`. = dashboard.glue.adapter`, `... = dashboard`):
```python
from .MessageBroker import MessageBroker           # unchanged (same package)
from ..core._compat import (GlueCellTopics, ...)   # .. = dashboard.glue
from .ApplicationState import ApplicationState      # unchanged
from ...ui.DashboardWidget import DashboardWidget, ActionButtonConfig, CardConfig  # ... = dashboard
from ..core.container import GlueContainer         # .. = dashboard.glue
from ...core.config import DashboardConfig         # ... = dashboard
from ..ui.setupWizard import SetupWizard           # .. = dashboard.glue
from ..ui.factories.GlueCardFactory import GlueCardFactory
```
Also: rename class `DashboardAdapter → GlueAdapter` throughout. Update `CONFIG`, `ACTION_BUTTONS`, `CARDS`, `BUTTON_CONFIG`, `build_cards`, all methods.  
Update the singleton MessageBroker import fallback:
`from src.dashboard.adapter.MessageBroker` → `from src.dashboard.glue.adapter.MessageBroker`

**`glue/core/container.py`** (`. = dashboard.glue.core`, `... = dashboard`):
```python
from ...core.config import DashboardConfig        # was: from .config
from ...core.protocols import (...)               # was: from .protocols
```
Rename class `DashboardContainer → GlueContainer` throughout.

**`glue/app/GlueAppWidget.py`** (`. = dashboard.glue.app`, `... = dashboard`):
```python
from ..adapter.GlueAdapter import GlueAdapter     # was: from ..adapter.DashboardAdapter
from ..core.container import GlueContainer        # was: from ..core.container
from ...ui.DashboardWidget import DashboardWidget, ActionButtonConfig  # was: from ..ui.DashboardWidget
```
Rename class `DashboardAppWidget → GlueAppWidget`.  
All internal references: `DashboardAdapter → GlueAdapter`, `DashboardContainer → GlueContainer`.

**`glue/ui/factories/GlueCardFactory.py`** (`. = dashboard.glue.ui.factories`, `.... = dashboard`):
```python
from ..widgets.GlueMeterCard import GlueMeterCard  # was: from ..widgets.GlueMeterCard
from ....core.config import DashboardConfig        # was: from ...core.config
```

**`glue/ui/widgets/GlueMeterCard.py`** (`.... = dashboard`):
```python
from .GlueMeterWidget import GlueMeterWidget                          # unchanged
from ....ui.widgets.shared.MaterialButton import MaterialButton       # was: from .shared.MaterialButton
from ....styles import (STATUS_UNKNOWN, ...)                          # was: from ...styles
```

**`glue/ui/widgets/GlueMeterWidget.py`** (`.... = dashboard`):
```python
from ....styles import (ICON_COLOR, STATUS_UNKNOWN, ...)  # was: from ...styles
```

**No import changes needed:**
- `glue/core/_compat.py` — standalone try/except chains
- `glue/adapter/ApplicationState.py`
- `glue/adapter/MessageBroker.py`
- `glue/adapter/topics.py`

**`glue/ui/setupWizard.py`** (`.... = dashboard`):
```python
from ....ui.widgets.shared.MaterialButton import MaterialButton  # was: from .widgets.shared.MaterialButton
from ....styles import (...)                                     # was: from ..styles
```

### 4. Update runner files

**`run_app.py`:**
```python
from dashboard.glue.adapter.GlueAdapter import GlueAdapter
from dashboard.glue.core.container import GlueContainer
# DashboardWidget import unchanged (still dashboard.ui.DashboardWidget)
# built_cards = GlueAdapter.build_cards(container)
# adapter = GlueAdapter(dashboard, container)
```

**`run_ui.py`:**  
Remove the `SetupWizard` import and wizard wiring — `run_ui.py` is a bare-bone runner with no glue dependencies. The `glue_type_change_requested` signal was already removed from `DashboardWidget` in a previous refactor, so this section becomes a no-op.

### 5. Delete old locations

- Delete `src/dashboard/adapter/` (all files moved to `glue/adapter/`)
- Delete `src/dashboard/app/` (all files moved to `glue/app/`)
- Delete `src/dashboard/core/_compat.py` and `src/dashboard/core/container.py`
- Delete `src/dashboard/ui/setupWizard.py`
- Delete `src/dashboard/ui/factories/` (entire folder)
- Delete `src/dashboard/ui/widgets/GlueMeterCard.py` and `GlueMeterWidget.py`

---

## Critical Files (unchanged — do not touch)

- `src/dashboard/core/config.py`
- `src/dashboard/core/protocols.py`
- `src/dashboard/ui/DashboardWidget.py`
- `src/dashboard/ui/managers/DashboardLayoutManager.py`
- `src/dashboard/ui/widgets/ControlButtonsWidget.py`
- `src/dashboard/ui/widgets/RobotTrajectoryWidget.py`
- `src/dashboard/ui/widgets/shared/*`
- `src/dashboard/styles.py`

---

## Verification

1. `python run_ui.py` — bare-bone UI starts with no import errors (uses only `dashboard.ui`, `dashboard.core`, `dashboard.styles`)
2. `python run_app.py` — full stack starts with no import errors (uses `dashboard.glue.*` + generic layers)
3. Confirm no file under `src/dashboard/ui/` or `src/dashboard/core/` imports from `dashboard.glue.*`

