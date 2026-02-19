# Dashboard Plugin Refactor Plan

## Context

The dashboard is a PyQt6 plugin for a glue-dispensing robotics application. It is functional but suffers from:
- Widgets knowing about `MessageBroker` and topics
- Lifecycle management relying on `__del__`
- Subscriptions scattered across many files
- Tight coupling to parent-app imports
- Hardcoded magic numbers everywhere

---

## Architecture: Three Levels of Abstraction

```
┌─────────────────────────────────────────────────────────────┐
│  Level 3 — Entry Point                                      │
│  DashboardAppWidget                                         │
│  Builds container, creates adapter + UI, exposes signals    │
│  to parent application                                      │
└──────────────┬──────────────────────────────────────────────┘
               │ owns
┌──────────────▼──────────────────────────────────────────────┐
│  Level 2 — Adapter Layer                                    │
│  DashboardAdapter                                           │
│  • Subscribes to MessageBroker topics                       │
│  • Routes broker messages → DashboardWidget setter methods  │
│  • Connects DashboardWidget output signals → system calls   │
│  • Single place for ALL subscribe/unsubscribe               │
└──────────────┬──────────────────────────────────────────────┘
               │ holds reference to
┌──────────────▼──────────────────────────────────────────────┐
│  Level 1 — UI Layer                                         │
│  DashboardWidget (facade)                                   │
│  • Composes child widgets                                   │
│  • Exposes typed setter API: set_cell_weight(), set_state() │
│  • Emits user-action signals: start_requested, etc.         │
│  • Zero knowledge of broker, topics, or external system     │
└──────────────┬──────────────────────────────────────────────┘
               │ composes
       ┌───────┼───────────────┐
       ▼       ▼               ▼
  GlueMeterCard  ControlButtonsWidget  RobotTrajectoryWidget
  (pure UI)      (pure UI)             (pure UI)
       │
       ▼
  GlueMeterWidget
  (pure UI)
```

> **Rule:** No file in `widgets/` imports `MessageBroker`, topic strings, or any external system module.  
> All `broker.subscribe()` / `broker.unsubscribe()` calls live exclusively in `DashboardAdapter`.

---

## Files That Do NOT Change

- `MessageBroker.py` — well-designed, weak refs, auto-cleanup
- `topics.py` — complete topic registry
- `ApplicationState.py` — simple enum
- `localization/` (entire directory) — already has proper DI + mixin pattern
- `widgets/DashboardCard.py`, `MaterialButton.py`, `ComboBoxStyle.py`, `Drawer.py` — pure UI

---

## Implementation Steps

### Step 1 — `config/dashboard_styles.py`: Expose all hardcoded values

Add missing fields so every hardcoded value has one configurable home:

```python
@dataclass
class DashboardConfig:
    glue_meters_count: int = 3
    trajectory_width: int = 800
    trajectory_height: int = 450
    card_min_height: int = 75
    glue_cards_min_width: int = 350
    glue_cards_max_width: int = 450
    default_cell_capacity_grams: float = 5000.0   # was hardcoded in GlueMeterWidget
    display_fps_ms: int = 30                       # was hardcoded in RobotTrajectoryWidget
    trajectory_trail_length: int = 100             # was hardcoded in TrajectoryManager
    bottom_grid_rows: int = 2                      # was magic number in DashboardLayoutManager
    bottom_grid_cols: int = 3                      # was magic number in DashboardLayoutManager
    combo_style: "ComboBoxStyle" = None

    def __post_init__(self):
        if self.combo_style is None:
            from .ComboBoxStyle import ComboBoxStyle
            self.combo_style = ComboBoxStyle()
```

**File:** `src/dashboard/ui/config/dashboard_styles.py`

---

### Step 2 — NEW `protocols.py`: External dependency contracts

`@runtime_checkable` Protocol classes for every external dependency. No other dashboard file needs to import from `communication_layer`, `modules.shared`, or `frontend.core` at module level.

- `ControllerServiceProtocol` — `.send_request(endpoint, payload) -> Optional[dict]`
- `ControllerProtocol` — `.controller_service`, `.handle(endpoint, payload)`
- `GlueCellProtocol` — `.id: int`, `.glueType: str`, `.capacity: float`
- `GlueCellManagerProtocol` — `.getCellById(id)`, `.getAllCells()`
- `CellStateManagerProtocol` — `.get_cell_state(cell_id) -> Optional[str]`
- `CellWeightMonitorProtocol` — `.get_cell_weight(cell_id) -> Optional[float]`

Also document message schemas:
- `CellWeightMessage` — plain `float` (grams). Fixes wrong docstring in `GlueMeterWidget`.
- `CellStateMessage` — `dict`: `{cell_id, current_state, previous_state, reason, weight, timestamp, details}`

**File:** `src/dashboard/ui/protocols.py` *(new)*

---

### Step 3 — NEW `container.py`: DI container

`DashboardContainer` dataclass — the **only** place cross-boundary lazy imports happen.

All fields are `Optional` (dashboard degrades gracefully in standalone/test mode):
- `controller`, `glue_cell_manager`, `cell_state_manager`, `cell_weight_monitor`, `config`

Methods:
- `controller_service` property — shortcut to `controller.controller_service`
- `camera_feed_callback()` — lazy-imports `camera_endpoints`, returns zero-arg callable
- `get_cell_capacity(cell_id)` — lazy-imports `glue_endpoints`, makes RPC call once per cell, falls back to `config.default_cell_capacity_grams`
- `get_cell_initial_state(cell_id)` — returns full `CellStateMessage` dict or `None`
- `get_cell_glue_type(cell_id)` — returns glue type string or `None`
- `get_all_glue_types()` — for the setup wizard

**File:** `src/dashboard/ui/container.py` *(new)*

---

### Step 4 — NEW `_compat.py`: Centralize import fallback chains

Replace all 3-level `try/except ImportError` chains with a single import from `_compat`:

```python
from ._compat import GlueCellTopics, SystemTopics, ApplicationState
```

Handles: `GlueCellTopics`, `RobotTopics`, `VisionTopics`, `SystemTopics`, `UITopics`, `ApplicationState` — tries parent-app path first, falls back to local.

Triple-fallback chains removed from: `localization/translator.py`, and any other file still containing them after widget cleanup below.

**File:** `src/dashboard/ui/_compat.py` *(new)*

---

### Step 5 — `widgets/GlueMeterWidget.py`: Pure UI widget

**Remove entirely:** All `MessageBroker` imports, topic imports, `_fetch_cell_capacity()`, `__del__`, `closeEvent` broker calls, `controller_service` parameter.

New constructor:
```python
def __init__(self, id: int, parent=None, capacity_grams: float = 5000.0):
    self.max_volume_grams = capacity_grams  # injected — no HTTP call
```

Public setter API:
```python
def set_weight(self, grams: float) -> None: ...
def set_state(self, state: str) -> None: ...  # accepts plain string
```

**File:** `src/dashboard/ui/widgets/GlueMeterWidget.py`

---

### Step 6 — `widgets/GlueMeterCard.py`: Pure UI composite

**Remove entirely:** All `MessageBroker` imports, `GlueCellTopics` imports (+ triple-fallback chains), `GlueDataFetcher` / `GlueCellsManagerSingleton` imports (+ triple-fallback chains), `subscribe()`, `unsubscribe()`, `__del__`, `closeEvent` broker calls, `fetch_initial_state()`, `load_current_glue_type()`.

New constructor:
```python
def __init__(self, label_text: str, index: int, capacity_grams: float = 5000.0):
    # No controller_service, no broker, no topics
    self.meter_widget = GlueMeterWidget(index, capacity_grams=capacity_grams)
```

Public setter API:
```python
def set_weight(self, grams: float) -> None:
    self.meter_widget.set_weight(grams)

def set_state(self, state_str: str) -> None:
    self._update_indicator(state_str)
    self.meter_widget.set_state(state_str)

def set_glue_type(self, glue_type: str) -> None:
    self.glue_type_label.setText(glue_type or "No glue configured")

def initialize_display(self, initial_state: Optional[dict], glue_type: Optional[str]) -> None:
    if initial_state:
        self.set_state(initial_state.get('current_state', 'unknown'))
    if glue_type:
        self.set_glue_type(glue_type)
```

**File:** `src/dashboard/ui/widgets/GlueMeterCard.py`

---

### Step 7 — `widgets/ControlButtonsWidget.py`: Pure UI widget

**Remove:** `MessageBroker` import, `SystemTopics` import, `broker.subscribe()` from `__init__`.

**Keep:** `on_system_status_update(state_data)` as a plain public method. The adapter will subscribe it to the broker — the widget doesn't do it itself.

`ApplicationState` imported via `_compat` (needed for button-enable logic only).

**File:** `src/dashboard/ui/widgets/ControlButtonsWidget.py`

---

### Step 8 — `widgets/RobotTrajectoryWidget.py`: Configurable + remove broker imports

Accept `fps_ms` and `trail_length` from config:
```python
def __init__(self, image_width=640, image_height=360,
             fps_ms: int = 30, trail_length: int = 100):
    self.trajectory_manager = TrajectoryManager(trail_length=trail_length)
    self.timer.start(fps_ms)
```

Fix `TrajectoryManager` memory leak — add `maxlen`:
```python
self.trajectory_points = deque(maxlen=trail_length)  # was deque() with no maxlen
```

Remove any remaining broker imports from the widget file.

Public methods are already clean typed callables (`set_image`, `update_trajectory_point`, `break_trajectory`, `enable_drawing`, `disable_drawing`) — the adapter subscribes them.

**File:** `src/dashboard/ui/widgets/RobotTrajectoryWidget.py`

---

### Step 9 — `DashboardWidget.py`: Pure UI facade

`DashboardWidget` is now a pure UI composite that:
1. Composes child widgets and manages layout
2. Exposes a typed setter API (called by the adapter) at the card level
3. Emits user-action signals (consumed by the adapter)
4. Has **zero** knowledge of broker, topics, or container

Constructor accepts only config:
```python
def __init__(self, config: DashboardConfig, parent=None):
    self.config = config
    self.card_factory = GlueCardFactory(config)
```

Typed setter API:
```python
def set_cell_weight(self, cell_id: int, grams: float) -> None:
    if card := self.glue_cards_dict.get(cell_id):
        card.set_weight(grams)

def set_cell_state(self, cell_id: int, state: str) -> None:
    if card := self.glue_cards_dict.get(cell_id):
        card.set_state(state)

def set_cell_glue_type(self, cell_id: int, glue_type: str) -> None:
    if card := self.glue_cards_dict.get(cell_id):
        card.set_glue_type(glue_type)

def set_trajectory_image(self, image) -> None:
    self.trajectory_widget.set_image(image)

def update_trajectory_point(self, point) -> None:
    self.trajectory_widget.update_trajectory_point(point)

def break_trajectory(self, _=None) -> None:
    self.trajectory_widget.break_trajectory()

def enable_trajectory_drawing(self, _=None) -> None:
    self.trajectory_widget.enable_drawing()

def disable_trajectory_drawing(self, _=None) -> None:
    self.trajectory_widget.disable_drawing()

def set_app_state(self, state_data) -> None:
    self.control_buttons.on_system_status_update(state_data)
```

Signals emitted:
- `start_requested`, `stop_requested`, `pause_requested`
- `clean_requested`, `reset_errors_requested`, `mode_toggle_requested`
- `glue_type_change_requested = pyqtSignal(int)` — `cell_id`

**File:** `src/dashboard/ui/DashboardWidget.py`

---

### Step 10 — NEW `DashboardAdapter.py`: The single bridge

The adapter is the **only** place that:
- Imports `MessageBroker` and topic constants for subscription
- Calls `broker.subscribe()` / `broker.unsubscribe()`
- Connects `DashboardWidget` signals to actual system actions

```python
class DashboardAdapter:
    """
    Bridges DashboardWidget (pure UI) and the external system.

    Lifecycle:
        adapter = DashboardAdapter(dashboard, container)
        adapter.connect()    # all subscriptions live, all signals wired
        # ... in use ...
        adapter.disconnect() # all subscriptions removed, signals disconnected
    """
    def __init__(self, dashboard: DashboardWidget, container: DashboardContainer):
        self._dashboard = dashboard
        self._container = container
        self._broker = MessageBroker()
        self._subscriptions: list[tuple[str, Callable]] = []

    def connect(self) -> None:
        self._subscribe_broker_to_ui()
        self._connect_ui_signals_to_system()
        self._initialize_display()

    def disconnect(self) -> None:
        for topic, callback in reversed(self._subscriptions):
            try:
                self._broker.unsubscribe(topic, callback)
            except Exception:
                pass
        self._subscriptions.clear()
        self._disconnect_ui_signals()
```

> `DashboardMessageManager` is **retired** — its responsibilities are fully covered by `DashboardAdapter`.

**File:** `src/dashboard/ui/DashboardAdapter.py` *(new)*

---

### Step 11 — `factories/GlueCardFactory.py`: Config only, no container

```python
class GlueCardFactory:
    def __init__(self, config: DashboardConfig, container: DashboardContainer):
        self.config = config
        self.container = container  # needed only for capacity lookup at card creation time

    def create_glue_card(self, index: int, label_text: str) -> GlueMeterCard:
        capacity = self.container.get_cell_capacity(index)
        return GlueMeterCard(label_text, index, capacity_grams=capacity)
```

**File:** `src/dashboard/ui/factories/GlueCardFactory.py`

---

### Step 12 — `DashboardAppWidget.py`: Entry point — wires all three levels

```python
class DashboardAppWidget(AppWidget):
    def __init__(self, container: DashboardContainer = None, parent=None, controller=None):
        # Backward compat shim
        if container is None and controller is not None:
            container = DashboardContainer(controller=controller)
        self._container = container or DashboardContainer()
        super().__init__("Dashboard", parent)

    def setup_ui(self):
        super().setup_ui()
        self._dashboard = DashboardWidget(config=self._container.config)
        self._adapter = DashboardAdapter(self._dashboard, self._container)
        self._adapter.connect()
        self._dashboard.start_requested.connect(self.start_requested.emit)
        self._dashboard.stop_requested.connect(self.stop_requested.emit)
        self._dashboard.pause_requested.connect(self.pause_requested.emit)
        self._dashboard.clean_requested.connect(self.clean_requested.emit)
        self._dashboard.reset_errors_requested.connect(self.reset_errors_requested.emit)

    def closeEvent(self, event):
        self._adapter.disconnect()
        super().closeEvent(event)
        self.LOGOUT_REQUEST.emit()

    def clean_up(self):
        self._adapter.disconnect()
        if hasattr(super(), 'clean_up'):
            super().clean_up()
    # REMOVED: __del__, _cleanup_dashboard() 70-line heuristic
```

Remove all module-level imports of `camera_endpoints`, `GlueCellTopics`, `GlueCellsManagerSingleton` (now in container).

**File:** `src/dashboard/ui/DashboardAppWidget.py`

---

### Step 13 — `managers/DashboardLayoutManager.py`: Config-driven grid

Replace `for row in range(2): for col in range(3)` + if/else chains with a declarative slot map driven by `config.bottom_grid_rows` / `config.bottom_grid_cols`.

**File:** `src/dashboard/ui/managers/DashboardLayoutManager.py`

---

### Step 14 — `setupWizard.py`: Inject glue types, fix icon path

```python
class SetupWizard(QWizard):
    def __init__(self, glue_type_names: list[str] = None):
        icon_path = Path(__file__).parent.parent / "resources" / "logo.ico"
        self.setWindowIcon(QIcon(str(icon_path)))
        self.addPage(SelectGlueTypeStep(glue_type_names or []))
```

Remove `GlueCellsManagerSingleton` import and all hardcoded Windows paths.

**File:** `src/dashboard/ui/setupWizard.py`

---

### Step 15 — Parent application update

```python
from plugins.core.dashboard.ui.container import DashboardContainer

container = DashboardContainer(
    controller=my_controller,
    glue_cell_manager=GlueCellsManagerSingleton.get_instance(),
    cell_state_manager=fetcher.state_manager,
    cell_weight_monitor=fetcher.state_monitor,
)
widget = DashboardAppWidget(container=container, parent=self)
```

---

## Subscription Ownership — Complete Map

All `broker.subscribe()` calls live **only** in `DashboardAdapter._subscribe_broker_to_ui()`.

| Topic | Routes to | Via |
|---|---|---|
| `cell_weight(id)` | `dashboard.set_cell_weight(id, grams)` | weight handler closure |
| `cell_state(id)` | `dashboard.set_cell_state(id, str)` | state handler closure (extracts `current_state` from dict) |
| `cell_glue_type(id)` | `dashboard.set_cell_glue_type(id, type)` | glue type handler closure |
| `APPLICATION_STATE` | `dashboard.set_app_state(data)` | direct |
| `TRAJECTORY_UPDATE_IMAGE` | `dashboard.set_trajectory_image(img)` | direct |
| `LATEST_IMAGE` | `dashboard.set_trajectory_image(img)` | direct |
| `TRAJECTORY_POINT` | `dashboard.update_trajectory_point(pt)` | direct |
| `TRAJECTORY_BREAK` | `dashboard.break_trajectory()` | direct |
| `TRAJECTORY_STOP` | `dashboard.disable_trajectory_drawing()` | direct |
| `TRAJECTORY_START` | `dashboard.enable_trajectory_drawing()` | direct |

---

## Critical Files

| File | Type | Key Role |
|---|---|---|
| `src/dashboard/ui/protocols.py` | NEW | External dependency contracts |
| `src/dashboard/ui/container.py` | NEW | DI container, all lazy cross-boundary imports |
| `src/dashboard/ui/DashboardAdapter.py` | NEW | Single broker+signal bridge, sole mediator |
| `src/dashboard/ui/_compat.py` | NEW | Centralized import fallback chains |
| `src/dashboard/ui/config/dashboard_styles.py` | Modify | Add 5 config fields |
| `src/dashboard/ui/widgets/GlueMeterWidget.py` | Modify | Pure UI: remove broker, typed setters |
| `src/dashboard/ui/widgets/GlueMeterCard.py` | Modify | Pure UI: remove broker/topics/del, typed setters |
| `src/dashboard/ui/widgets/ControlButtonsWidget.py` | Modify | Pure UI: remove self-subscribe |
| `src/dashboard/ui/widgets/RobotTrajectoryWidget.py` | Modify | Accept fps/trail config, fix deque maxlen |
| `src/dashboard/ui/DashboardWidget.py` | Rewrite | Pure UI facade with typed setter API |
| `src/dashboard/ui/DashboardAppWidget.py` | Modify | Wires UI + Adapter + Container, clean lifecycle |
| `src/dashboard/ui/factories/GlueCardFactory.py` | Modify | Uses container for capacity only |
| `src/dashboard/ui/managers/DashboardLayoutManager.py` | Modify | Declarative slot map |
| `src/dashboard/ui/managers/DashboardMessageManager.py` | **Delete** | Superseded by DashboardAdapter |
| `src/dashboard/ui/setupWizard.py` | Modify | Inject glue types, fix icon path |
| Parent app construction site | Modify | Build and pass `DashboardContainer` |

---

## Verification

1. **Grep check:** No `MessageBroker` or topic import in any `widgets/` or `DashboardWidget.py` file
2. **Import check:** `python -c "from src.dashboard.ui.DashboardAppWidget import DashboardAppWidget"` — succeeds without parent-app modules
3. **Standalone test:** `DashboardAppWidget(container=DashboardContainer())` renders correctly with empty/default state
4. **Cleanup check:** After `widget.close()`, `MessageBroker().get_subscriber_count(topic) == 0` for all topics
5. **Config override:** `DashboardConfig(glue_meters_count=2)` renders exactly 2 cards
6. **Full integration:** Parent app with `DashboardContainer(...)` runs real hardware session correctly
