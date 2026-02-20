"""
GlueAdapter — bridge between DashboardWidget (pure UI) and the glue dispensing system.
"""

from __future__ import annotations

from typing import Callable

try:
    from .MessageBroker import MessageBroker
except ImportError:
    from src.glue_dispensing_dashboard.adapter.MessageBroker import MessageBroker

try:
    from ..core._compat import (
        GlueCellTopics, RobotTopics, VisionTopics, SystemTopics,
    )
except ImportError:
    from src.glue_dispensing_dashboard.core._compat import (
        GlueCellTopics, RobotTopics, VisionTopics, SystemTopics,
    )

try:
    from .ApplicationState import ApplicationState
except ImportError:
    from src.glue_dispensing_dashboard.adapter.ApplicationState import ApplicationState

try:
    from src.dashboard.DashboardWidget import DashboardWidget, ActionButtonConfig, CardConfig
except ImportError:
    from dashboard.DashboardWidget import DashboardWidget
    from dashboard.config import ActionButtonConfig, CardConfig

try:
    from ..core.container import GlueContainer
except ImportError:
    from glue_dispensing_dashboard.core.container import GlueContainer

try:
    from ..core.config import GlueDashboardConfig
except ImportError:
    from glue_dispensing_dashboard.core.config import GlueDashboardConfig

try:
    from ..ui.glue_change_guide_wizard import create_glue_change_wizard
except ImportError:
    from glue_dispensing_dashboard.ui.setupWizard import create_glue_change_wizard

try:
    from ..ui.factories.GlueCardFactory import GlueCardFactory
except ImportError:
    from glue_dispensing_dashboard.ui.factories.GlueCardFactory import GlueCardFactory


class GlueAdapter:
    """Bridge between DashboardWidget (pure UI) and the glue dispensing system."""

    BUTTON_CONFIG: dict = {
        ApplicationState.IDLE:         {"start": True,  "stop": False, "pause": False, "pause_text": "Pause"},
        ApplicationState.STARTED:      {"start": False, "stop": True,  "pause": True,  "pause_text": "Pause"},
        ApplicationState.PAUSED:       {"start": False, "stop": True,  "pause": True,  "pause_text": "Resume"},
        ApplicationState.INITIALIZING: {"start": False, "stop": False, "pause": False, "pause_text": "Pause"},
        ApplicationState.CALIBRATING:  {"start": False, "stop": False, "pause": False, "pause_text": "Pause"},
        ApplicationState.STOPPED:      {"start": False, "stop": False, "pause": False, "pause_text": "Pause"},
        ApplicationState.ERROR:        {"start": False, "stop": True,  "pause": False, "pause_text": "Pause"},
    }

    ACTION_BUTTONS: list = [
        ActionButtonConfig(action_id="reset_errors", label="Reset Errors", enabled=True, row=1, col=0),
        ActionButtonConfig(action_id="mode_toggle",  label="Pick And Spray", row_span=1, col_span=2),  # Wider button
        ActionButtonConfig(action_id="clean",        label="Clean"),
    ]

    CARDS: list = [
        CardConfig(card_id=1, label="Glue 1"),
        CardConfig(card_id=2, label="Glue 2"),
        CardConfig(card_id=3, label="Glue 3"),
    ]

    CONFIG: GlueDashboardConfig = GlueDashboardConfig()

    _MODE_TOGGLE_LABELS = ("Pick And Spray", "Spray Only")

    @classmethod
    def build_cards(cls, container: GlueContainer) -> list:
        factory = GlueCardFactory(cls.CONFIG, container)
        return [
            (factory.create_glue_card(cfg.card_id, cfg.label), cfg.card_id, cfg.row, cfg.col)
            for cfg in cls.CARDS
        ]

    def __init__(self, dashboard: DashboardWidget, container: GlueContainer):
        self._dashboard = dashboard
        self._container = container
        self._broker = MessageBroker()
        self._subscriptions: list[tuple[str, Callable]] = []
        self._mode_toggle_index: int = 0

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

    def _subscribe_broker_to_ui(self) -> None:
        for cfg in self.CARDS:
            i = cfg.card_id
            self._sub(GlueCellTopics.cell_weight(i), self._make_weight_handler(i))
            self._sub(GlueCellTopics.cell_state(i),  self._make_state_handler(i))
            self._sub(GlueCellTopics.cell_glue_type(i), self._make_glue_type_handler(i))

        self._sub(SystemTopics.APPLICATION_STATE, self._on_app_state)
        self._sub(RobotTopics.TRAJECTORY_UPDATE_IMAGE, self._dashboard.set_trajectory_image)
        self._sub(VisionTopics.LATEST_IMAGE,           self._dashboard.set_trajectory_image)
        self._sub(RobotTopics.TRAJECTORY_POINT,        self._dashboard.update_trajectory_point)
        self._sub(RobotTopics.TRAJECTORY_BREAK,        self._dashboard.break_trajectory)
        self._sub(RobotTopics.TRAJECTORY_STOP,         self._dashboard.disable_trajectory_drawing)
        self._sub(RobotTopics.TRAJECTORY_START,        self._dashboard.enable_trajectory_drawing)

    def _make_weight_handler(self, cell_id: int) -> Callable:
        return lambda grams: self._dashboard.set_cell_weight(cell_id, grams)

    def _make_state_handler(self, cell_id: int) -> Callable:
        def on_state(msg):
            state = (msg.get("current_state", "unknown") if isinstance(msg, dict) else str(msg))
            self._dashboard.set_cell_state(cell_id, state)
        return on_state

    def _make_glue_type_handler(self, cell_id: int) -> Callable:
        return lambda glue_type: self._dashboard.set_cell_glue_type(cell_id, glue_type)

    def _connect_ui_signals_to_system(self) -> None:
        d = self._dashboard
        d.start_requested.connect(self._on_start)
        d.stop_requested.connect(self._on_stop)
        d.pause_requested.connect(self._on_pause)
        d.action_requested.connect(self._on_action)
        for card in d._cards.values():
            card.change_glue_requested.connect(self._on_glue_type_change)

    def _disconnect_ui_signals(self) -> None:
        try:
            d = self._dashboard
            d.start_requested.disconnect(self._on_start)
            d.stop_requested.disconnect(self._on_stop)
            d.pause_requested.disconnect(self._on_pause)
            d.action_requested.disconnect(self._on_action)
            for card in d._cards.values():
                card.change_glue_requested.disconnect(self._on_glue_type_change)
        except RuntimeError:
            pass

    def _on_app_state(self, state_data) -> None:
        try:
            if isinstance(state_data, dict):
                state = ApplicationState(state_data["state"])
            else:
                state = ApplicationState(state_data)
        except (KeyError, ValueError):
            return
        config = self.BUTTON_CONFIG.get(state)
        if config:
            self._dashboard.set_start_enabled(config["start"])
            self._dashboard.set_stop_enabled(config["stop"])
            self._dashboard.set_pause_enabled(config["pause"])
            self._dashboard.set_pause_text(config["pause_text"])

    def _on_start(self):
        print(f"Start Pressed")

    def _on_stop(self):
        print(f"Stop Pressed")

    def _on_pause(self):
        print(f"Pause Pressed")

    def _on_action(self, action_id: str) -> None:
        if action_id == "mode_toggle":
            self._mode_toggle_index = 1 - self._mode_toggle_index
            new_label = self._MODE_TOGGLE_LABELS[self._mode_toggle_index]
            self._dashboard.set_action_button_text("mode_toggle", new_label)
            self._broker.publish(SystemTopics.SYSTEM_MODE_CHANGE, new_label)
            print(f"Mode Toggled to {new_label}")
        elif action_id == "clean":
            print(f"Clean Pressed")
        elif action_id == "reset_errors":
            print(f"Reset Errors Pressed")

    def _on_glue_type_change(self, cell_id: int):
        wizard = create_glue_change_wizard(glue_type_names=self._container.get_all_glue_types())
        wizard.setWindowTitle(f"Change Glue for Cell {cell_id}")
        result = wizard.exec()
        if result == 1:
            # Get the selection step (page index 6)
            selection_page = wizard.page(6)
            selected_glue_type = selection_page.get_selected_option() if hasattr(selection_page, 'get_selected_option') else None
            if selected_glue_type:
                self._dashboard.set_cell_glue_type(cell_id, selected_glue_type)

    def _initialize_display(self) -> None:
        for cfg in self.CARDS:
            i = cfg.card_id
            initial_state = self._container.get_cell_initial_state(i)
            glue_type = self._container.get_cell_glue_type(i)
            if initial_state:
                self._dashboard.set_cell_state(i, initial_state.get("current_state", "unknown"))
            if glue_type:
                self._dashboard.set_cell_glue_type(i, glue_type)

    def _sub(self, topic: str, callback: Callable) -> None:
        self._broker.subscribe(topic, callback)
        self._subscriptions.append((topic, callback))


# Backward-compat alias
DashboardAdapter = GlueAdapter

