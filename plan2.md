# Dashboard Plugin — Layered Directory Restructure

## Context

All code currently lives flat under `src/dashboard/ui/`. This obscures the three-level
architecture (entry point → adapter → pure UI) and mixes infrastructure (broker, topics,
config) with UI widgets. The goal is to make the folder structure mirror the actual data
flow, so a reader can understand the architecture just from the directory tree.

---

## Target Structure

```
src/dashboard/
├── __init__.py                          [CREATE — empty]
├── resources/                           [unchanged]
│
├── app/                                 [CREATE — Level 3: entry point]
│   ├── __init__.py
│   └── DashboardAppWidget.py            [MOVE from ui/]
│
├── adapter/                             [CREATE — Level 2: broker bridge]
│   ├── __init__.py
│   └── DashboardAdapter.py              [MOVE from ui/]
│
├── ui/                                  [Level 1: pure UI — keep, restructure]
│   ├── __init__.py
│   ├── DashboardWidget.py               [stays — update imports]
│   ├── setupWizard.py                   [stays — update imports]
│   ├── mixins.py                        [stays — update imports]
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── GlueMeterWidget.py           [stays — no import changes needed]
│   │   ├── GlueMeterCard.py             [stays — no import changes]
│   │   ├── ControlButtonsWidget.py      [stays — update imports]
│   │   ├── RobotTrajectoryWidget.py     [stays — no import changes]
│   │   └── shared/                      [CREATE — pure UI primitives used across widgets]
│   │       ├── __init__.py
│   │       ├── DashboardCard.py         [MOVE from ui/widgets/]
│   │       ├── MaterialButton.py        [MOVE from ui/]
│   │       ├── ComboBoxStyle.py         [MOVE from ui/]
│   │       └── Drawer.py               [MOVE from ui/]
│   ├── factories/
│   │   ├── __init__.py
│   │   └── GlueCardFactory.py           [stays — update imports]
│   └── managers/
│       ├── __init__.py
│       └── DashboardLayoutManager.py    [stays — update imports]
│
├── core/                                [CREATE — shared infrastructure, no UI]
│   ├── __init__.py
│   ├── config.py                        [MOVE+RENAME from ui/config/dashboard_styles.py]
│   ├── container.py                     [MOVE from ui/]
│   ├── protocols.py                     [MOVE from ui/]
│   ├── _compat.py                       [MOVE from ui/]
│   ├── MessageBroker.py                 [MOVE from ui/]
│   ├── topics.py                        [MOVE from ui/]
│   ├── ApplicationState.py              [MOVE from ui/]
│   ├── Language.py                      [MOVE from ui/]
│   ├── LanguageResourceLoader.py        [MOVE from ui/ — fix LANGUAGES_DIR path]
│   └── IconLoader.py                    [MOVE from ui/]
│
└── localization/                        [MOVE from ui/localization/]
    ├── __init__.py                      [update cross-package imports]
    ├── container.py                     [unchanged — Language fallback already present]
    ├── keys.py                          [unchanged — no internal imports]
    ├── mixins.py                        [unchanged — self-contained]
    ├── translator.py                    [update: ..X → ..core.X]
    ├── widgets.py                       [update: ..Drawer → ..ui.widgets.shared.Drawer]
    └── MIGRATION_GUIDE.md
```

**Files deleted from `ui/` after move:**  
`DashboardAppWidget.py`, `DashboardAdapter.py`, `config/` (folder),
`container.py`, `protocols.py`, `_compat.py`, `MessageBroker.py`,
`topics.py`, `ApplicationState.py`, `Language.py`, `LanguageResourceLoader.py`,
`IconLoader.py`, `MaterialButton.py`, `ComboBoxStyle.py`, `Drawer.py`,
`widgets/DashboardCard.py`, `localization/` (folder), `localization.py` (empty stub)

---

## Import Change Map

### `app/DashboardAppWidget.py`

| Old | New |
|---|---|
| `from .container import DashboardContainer` | `from ..core.container import DashboardContainer` |
| `from .DashboardWidget import DashboardWidget` | `from ..ui.DashboardWidget import DashboardWidget` |
| `from .DashboardAdapter import DashboardAdapter` | `from ..adapter.DashboardAdapter import DashboardAdapter` |

---

### `adapter/DashboardAdapter.py`

| Old | New |
|---|---|
| `from .MessageBroker import MessageBroker` | `from ..core.MessageBroker import MessageBroker` |
| `from ._compat import ...` | `from ..core._compat import ...` |
| `from .DashboardWidget import DashboardWidget` | `from ..ui.DashboardWidget import DashboardWidget` |
| `from .container import DashboardContainer` | `from ..core.container import DashboardContainer` |
| `from .setupWizard import SetupWizard` | `from ..ui.setupWizard import SetupWizard` |

---

### `ui/DashboardWidget.py`

| Old | New |
|---|---|
| `from .localization import TranslationKeys` | `from ..localization import TranslationKeys` |
| `from .MaterialButton import MaterialButton` | `from .widgets.shared.MaterialButton import MaterialButton` |
| `from .config.dashboard_styles import DashboardConfig` | `from ..core.config import DashboardConfig` |
| `from .widgets.DashboardCard import DashboardCard` | `from .widgets.shared.DashboardCard import DashboardCard` |

---

### `ui/setupWizard.py`

| Old | New |
|---|---|
| `from .MaterialButton import MaterialButton` | `from .widgets.shared.MaterialButton import MaterialButton` |
| `icon_path = Path(__file__).parent.parent / "resources"` | `icon_path = Path(__file__).parents[2] / "resources"` (goes up to `src/dashboard/`) |

---

### `ui/mixins.py`

| Old | New |
|---|---|
| `from .localization import TranslationKeys as Message` | `from ..localization import TranslationKeys as Message` |
| `from .container import get_app_translator` | `from ..localization.container import get_app_translator` |
| `from .translator import AppTranslator` | `from ..localization.translator import AppTranslator` |

---

### `ui/widgets/ControlButtonsWidget.py`

| Old | New |
|---|---|
| `from .._compat import ApplicationState` | `from ...core._compat import ApplicationState` |
| `from ..localization import TranslationKeys` | `from ...localization import TranslationKeys` |
| `from ..mixins import TranslatableWidget` | `from ..mixins import TranslatableWidget` *(unchanged)* |
| `from ..MaterialButton import MaterialButton` | `from .shared.MaterialButton import MaterialButton` |

---

### `ui/factories/GlueCardFactory.py`

| Old | New |
|---|---|
| `from ..config.dashboard_styles import DashboardConfig` | `from ...core.config import DashboardConfig` |
| `from ..widgets.GlueMeterCard import GlueMeterCard` | unchanged |

---

### `ui/managers/DashboardLayoutManager.py`

| Old | New |
|---|---|
| `from ..MaterialButton import MaterialButton` | `from ..widgets.shared.MaterialButton import MaterialButton` |

---

### `core/config.py` (was `ui/config/dashboard_styles.py`)

- Replace top-level `from ..ComboBoxStyle import ComboBoxStyle` with lazy import in `__post_init__`:

```python
def __post_init__(self):
    if self.combo_style is None:
        try:
            from ..ui.widgets.shared.ComboBoxStyle import ComboBoxStyle
        except ImportError:
            from ComboBoxStyle import ComboBoxStyle
        self.combo_style = ComboBoxStyle()
```

---

### `core/container.py`

| Old | New |
|---|---|
| `from .config.dashboard_styles import DashboardConfig` | `from .config import DashboardConfig` |
| `from .protocols import ...` | unchanged |

---

### `core/_compat.py`

All `from .topics import X` / `from .ApplicationState import X` — **unchanged** (same package).

---

### `core/LanguageResourceLoader.py`

Fix `LANGUAGES_DIR` — `BASE_DIR` is now `core/`, not `ui/`:

```python
# OLD
LANGUAGES_DIR = BASE_DIR / "languages"

# NEW
LANGUAGES_DIR = BASE_DIR.parent / "ui" / "languages"
```

---

### `localization/translator.py`

| Old (fallback chain) | New |
|---|---|
| `from ..topics import UITopics` | `from ..core.topics import UITopics` |
| `from ..MessageBroker import MessageBroker` | `from ..core.MessageBroker import MessageBroker` |
| `from ..LanguageResourceLoader import LanguageResourceLoader` | `from ..core.LanguageResourceLoader import LanguageResourceLoader` |
| `from ..Language import Language` | `from ..core.Language import Language` |

---

### `localization/widgets.py`

| Old | New |
|---|---|
| `from ..Drawer import Drawer` | `from ..ui.widgets.shared.Drawer import Drawer` |

---

### `localization/__init__.py`

Scan for any `from ..X` or `from ..Y` lines and redirect to `from ..core.X` / `from ..ui.X` as appropriate.

---

## Implementation Steps

1. **Create package scaffolding** — `__init__.py` files for `app/`, `adapter/`, `core/`, `ui/widgets/shared/`, and root `src/dashboard/`
2. **Move + update infrastructure files to `core/`** — all 9 files listed above. Fix `LanguageResourceLoader.py` path. Update `container.py` and `config.py` imports.
3. **Move `localization/`** from `ui/localization/` → `src/dashboard/localization/`. Update 3 files: `translator.py`, `widgets.py`, `__init__.py`.
4. **Move shared UI primitives to `ui/widgets/shared/`** — `MaterialButton.py`, `ComboBoxStyle.py`, `Drawer.py`, `DashboardCard.py` — no import changes needed inside these files (pure PyQt6).
5. **Move layer files to `app/` and `adapter/`**. Update their imports per the map above.
6. **Update remaining `ui/` files** — `DashboardWidget.py`, `setupWizard.py`, `mixins.py`, `ControlButtonsWidget.py`, `GlueCardFactory.py`, `DashboardLayoutManager.py`.
7. **Delete all old `ui/` source files** listed under "deleted after move".
8. **Verify:**
   - `python -c "from dashboard.app.DashboardAppWidget import DashboardAppWidget"` — no `ImportError`
   - Grep: no `from ..X` (old ui-relative) in `localization/translator.py`
   - Grep: `MessageBroker` appears only in `adapter/DashboardAdapter.py` and `core/` files

---

## Critical Files

| File | Role |
|---|---|
| `app/DashboardAppWidget.py` | Entry point — imports from all 3 layers |
| `adapter/DashboardAdapter.py` | Only broker importer — update 5 imports |
| `ui/DashboardWidget.py` | UI facade — update 4 imports |
| `core/_compat.py` | Fallback chains — no changes needed |
| `core/config.py` | Config dataclass — lazy `ComboBoxStyle` import from `ui/widgets/shared/` |
| `core/LanguageResourceLoader.py` | Fix `LANGUAGES_DIR` path |
| `localization/translator.py` | 4 import path changes |
| `localization/widgets.py` | 1 import path change |

