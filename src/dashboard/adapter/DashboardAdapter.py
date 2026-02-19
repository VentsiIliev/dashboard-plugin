"""
DashboardAdapter — the single bridge between DashboardWidget (pure UI)
and the external system (MessageBroker + application services).

This is the ONLY place in the dashboard plugin that:
  * imports MessageBroker and topic constants
  * calls broker.subscribe() / broker.unsubscribe()
  * connects DashboardWidget output signals to actual system actions

Lifecycle::

    adapter = DashboardAdapter(dashboard, container)
    adapter.connect() # all subscriptions live, all signals wired
    # ... in use ...
    adapter.disconnect() # all subscriptions removed, signals disconnected
"""

from __future__ import annotations

from typing import Callable

try:
    from src.dashboard.adapter.MessageBroker import MessageBroker
except ImportError:
    from MessageBroker import MessageBroker

try:
    from ..core._compat import (
        GlueCellTopics, RobotTopics, VisionTopics, SystemTopics,
    )
except ImportError:
    from _compat import (
        GlueCellTopics, RobotTopics, VisionTopics, SystemTopics,
    )

try:
    from .ApplicationState import ApplicationState
except ImportError:
    from ApplicationState import ApplicationState

try:
    from ..ui.DashboardWidget import DashboardWidget
except ImportError:
    from DashboardWidget import DashboardWidget

try:
    from ..core.container import DashboardContainer
except ImportError:
    from container import DashboardContainer

try:
    from ..ui.setupWizard import SetupWizard
except ImportError:
    from setupWizard import SetupWizard


class DashboardAdapter:
    """Bridge between DashboardWidget (pure UI) and the external system."""

    BUTTON_CONFIG: dict = {
        ApplicationState.IDLE:         {"start": True,  "stop": False, "pause": False, "pause_text": "Pause"},
        ApplicationState.STARTED:      {"start": False, "stop": True,  "pause": True,  "pause_text": "Pause"},
        ApplicationState.PAUSED:       {"start": False, "stop": True,  "pause": True,  "pause_text": "Resume"},
        ApplicationState.INITIALIZING: {"start": False, "stop": False, "pause": False, "pause_text": "Pause"},
        ApplicationState.CALIBRATING:  {"start": False, "stop": False, "pause": False, "pause_text": "Pause"},
        ApplicationState.STOPPED:      {"start": False, "stop": False, "pause": False, "pause_text": "Pause"},
        ApplicationState.ERROR:        {"start": False, "stop": True,  "pause": False, "pause_text": "Pause"},
    }

    def __init__(self, dashboard: DashboardWidget, container: DashboardContainer):
        self._dashboard = dashboard
        self._container = container
        self._broker = MessageBroker()
        self._subscriptions: list[tuple[str, Callable]] = []

    # ------------------------------------------------------------------ #
    #  Public lifecycle API                                                #
    # ------------------------------------------------------------------ #

    def connect(self) -> None:
        """Subscribe to broker topics and wire all UI signals."""
        self._subscribe_broker_to_ui()
        self._connect_ui_signals_to_system()
        self._initialize_display()

    def disconnect(self) -> None:
        """Remove all broker subscriptions and disconnect UI signals."""
        for topic, callback in reversed(self._subscriptions):
            try:
                self._broker.unsubscribe(topic, callback)
            except Exception:
                pass
        self._subscriptions.clear()
        self._disconnect_ui_signals()

    # ------------------------------------------------------------------ #
    #  Private: broker → UI                                               #
    # ------------------------------------------------------------------ #

    def _subscribe_broker_to_ui(self) -> None:
        config = self._container.config
        for i in range(1, config.glue_meters_count + 1):
            self._sub(GlueCellTopics.cell_weight(i), self._make_weight_handler(i))
            self._sub(GlueCellTopics.cell_state(i),  self._make_state_handler(i))
            self._sub(GlueCellTopics.cell_glue_type(i), self._make_glue_type_handler(i))

        self._sub(SystemTopics.APPLICATION_STATE, self._on_app_state)
        self._sub(RobotTopics.TRAJECTORY_UPDATE_IMAGE,
                  self._dashboard.set_trajectory_image)
        self._sub(VisionTopics.LATEST_IMAGE,
                  self._dashboard.set_trajectory_image)
        self._sub(RobotTopics.TRAJECTORY_POINT,
                  self._dashboard.update_trajectory_point)
        self._sub(RobotTopics.TRAJECTORY_BREAK,
                  self._dashboard.break_trajectory)
        self._sub(RobotTopics.TRAJECTORY_STOP,
                  self._dashboard.disable_trajectory_drawing)
        self._sub(RobotTopics.TRAJECTORY_START,
                  self._dashboard.enable_trajectory_drawing)

    def _make_weight_handler(self, cell_id: int) -> Callable:
        return lambda grams: self._dashboard.set_cell_weight(cell_id, grams)

    def _make_state_handler(self, cell_id: int) -> Callable:
        def on_state(msg):
            state = (msg.get("current_state", "unknown")
                     if isinstance(msg, dict) else str(msg))
            self._dashboard.set_cell_state(cell_id, state)
        return on_state

    def _make_glue_type_handler(self, cell_id: int) -> Callable:
        return lambda glue_type: self._dashboard.set_cell_glue_type(cell_id, glue_type)

    # ------------------------------------------------------------------ #
    #  Private: UI signals → system                                       #
    # ------------------------------------------------------------------ #

    def _connect_ui_signals_to_system(self) -> None:
        d = self._dashboard
        d.start_requested.connect(self._on_start)
        d.stop_requested.connect(self._on_stop)
        d.pause_requested.connect(self._on_pause)
        d.clean_requested.connect(self._on_clean)
        d.reset_errors_requested.connect(self._on_reset_errors)
        d.mode_toggle_requested.connect(self._on_mode_toggle)
        d.glue_type_change_requested.connect(self._on_glue_type_change)

    def _disconnect_ui_signals(self) -> None:
        try:
            d = self._dashboard
            d.start_requested.disconnect(self._on_start)
            d.stop_requested.disconnect(self._on_stop)
            d.pause_requested.disconnect(self._on_pause)
            d.clean_requested.disconnect(self._on_clean)
            d.reset_errors_requested.disconnect(self._on_reset_errors)
            d.mode_toggle_requested.disconnect(self._on_mode_toggle)
            d.glue_type_change_requested.disconnect(self._on_glue_type_change)
        except RuntimeError:
            pass  # widget may already be destroyed

    # ------------------------------------------------------------------ #
    #  Signal handlers                                                     #
    # ------------------------------------------------------------------ #

    def _on_app_state(self, state_data) -> None:
        """Resolve ApplicationState from broker message and push button config to UI."""
        try:
            if isinstance(state_data, dict):
                state = ApplicationState(state_data["state"])
            else:
                state = ApplicationState(state_data)
        except (KeyError, ValueError):
            return
        config = self.BUTTON_CONFIG.get(state)
        if config:
            self._dashboard.apply_button_config(config)

    def _on_start(self):
        pass  # forwarded to the parent app via DashboardAppWidget signal

    def _on_stop(self):
        pass

    def _on_pause(self):
        pass

    def _on_clean(self):
        pass

    def _on_reset_errors(self):
        pass

    def _on_mode_toggle(self, mode: str):
        """Publish mode change to the system bus."""
        self._broker.publish(SystemTopics.SYSTEM_MODE_CHANGE, mode)

    def _on_glue_type_change(self, cell_id: int):
        """Show the glue-change wizard with injected glue type names."""
        wizard = SetupWizard(glue_type_names=self._container.get_all_glue_types())
        wizard.setWindowTitle(f"Change Glue for Cell {cell_id}")
        result = wizard.exec()
        if result == 1:  # QDialog.Accepted
            selected_glue_type = wizard.get_selected_glue_type()
            if selected_glue_type:
                self._dashboard.set_cell_glue_type(cell_id, selected_glue_type)

    # ------------------------------------------------------------------ #
    #  Private: initial display population                                #
    # ------------------------------------------------------------------ #

    def _initialize_display(self) -> None:
        """Populate initial UI state after subscriptions are live."""
        config = self._container.config
        for i in range(1, config.glue_meters_count + 1):
            initial_state = self._container.get_cell_initial_state(i)
            glue_type = self._container.get_cell_glue_type(i)
            if initial_state:
                state_str = initial_state.get("current_state", "unknown")
                self._dashboard.set_cell_state(i, state_str)
            if glue_type:
                self._dashboard.set_cell_glue_type(i, glue_type)

    # ------------------------------------------------------------------ #
    #  Internal helper                                                     #
    # ------------------------------------------------------------------ #

    def _sub(self, topic: str, callback: Callable) -> None:
        self._broker.subscribe(topic, callback)
        self._subscriptions.append((topic, callback))
