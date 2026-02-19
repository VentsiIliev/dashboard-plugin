from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QSizePolicy


try:
    from .widgets.shared.MaterialButton import MaterialButton
    from .widgets.ControlButtonsWidget import ControlButtonsWidget
    from .widgets.RobotTrajectoryWidget import RobotTrajectoryWidget
    from ..core.config import DashboardConfig
    from .factories.GlueCardFactory import GlueCardFactory
    from .managers.DashboardLayoutManager import DashboardLayoutManager
    from .widgets.shared.DashboardCard import DashboardCard
except ImportError:
    from MaterialButton import MaterialButton
    from widgets.ControlButtonsWidget import ControlButtonsWidget
    from widgets.RobotTrajectoryWidget import RobotTrajectoryWidget
    from config import DashboardConfig
    from factories.GlueCardFactory import GlueCardFactory
    from managers.DashboardLayoutManager import DashboardLayoutManager
    from widgets.DashboardCard import DashboardCard


class CardContainer(QWidget):
    select_card_signal = pyqtSignal(object)

    def __init__(self, columns=3, rows=2):
        super().__init__()
        self.columns = columns
        self.rows = rows
        self.total_cells = columns * rows

        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        for row in range(self.rows):
            self.layout.setRowStretch(row, 1)
            self.layout.setRowMinimumHeight(row, 180)

        for col in range(self.columns):
            self.layout.setColumnStretch(col, 1)
            self.layout.setColumnMinimumWidth(col, 200)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


class DashboardWidget(QWidget):
    """
    Pure UI facade for the dashboard.

    Composes child widgets, exposes a typed setter API (called by the adapter),
    and emits user-action signals (consumed by the adapter).

    Has zero knowledge of MessageBroker, topics, or any external system.
    """

    # User-action signals (adapter connects these to system calls)
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    clean_requested = pyqtSignal()
    reset_errors_requested = pyqtSignal()
    mode_toggle_requested = pyqtSignal(str)
    glue_type_change_requested = pyqtSignal(int)  # cell_id

    def __init__(self, config: DashboardConfig = None, parent=None):
        super().__init__(parent)
        self.config = config or DashboardConfig()
        self.card_factory = GlueCardFactory(self.config)
        self.shared_card_container = CardContainer(columns=1, rows=3)
        self.glue_cards_dict = {}
        self.init_ui()

    # ------------------------------------------------------------------ #
    #  Typed setter API (called by DashboardAdapter)                      #
    # ------------------------------------------------------------------ #

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

    def apply_button_config(self, config: dict) -> None:
        """Called by the adapter with a resolved button config dict."""
        self.control_buttons.apply_button_config(config)

    # ------------------------------------------------------------------ #
    #  UI initialisation                                                   #
    # ------------------------------------------------------------------ #

    def init_ui(self):
        self.layout_manager = DashboardLayoutManager(self, self.config)

        self.trajectory_widget = RobotTrajectoryWidget(
            image_width=self.config.trajectory_width,
            image_height=self.config.trajectory_height,
            fps_ms=self.config.display_fps_ms,
            trail_length=self.config.trajectory_trail_length,
        )

        self.control_buttons = ControlButtonsWidget()
        self.control_buttons.start_clicked.connect(self.start_requested.emit)
        self.control_buttons.stop_clicked.connect(self.stop_requested.emit)
        self.control_buttons.pause_clicked.connect(self.pause_requested.emit)

        self.clean_button = MaterialButton("Clean", font_size=20)
        self.clean_button.clicked.connect(self.clean_requested.emit)

        self.reset_errors_button = MaterialButton("Reset Errors", font_size=20)
        self.reset_errors_button.clicked.connect(self.reset_errors_requested.emit)

        self.mode_toggle_button = MaterialButton("Pick And Spray", font_size=20)
        self.mode_toggle_button.clicked.connect(self._on_mode_toggle)

        glue_cards = []
        for i in range(1, self.config.glue_meters_count + 1):
            card = self._create_glue_card(i, f"Glue {i}")
            glue_cards.append(card)
            self.glue_cards_dict[i] = card

        self.layout_manager.setup_complete_layout(
            self.trajectory_widget,
            glue_cards,
            self.control_buttons,
            self.clean_button,
            self.reset_errors_button,
            self.mode_toggle_button,
        )

    def _create_glue_card(self, index: int, label_text: str):
        card = self.card_factory.create_glue_card(index, label_text)
        card.change_glue_requested.connect(self.glue_type_change_requested.emit)
        return card

    def _on_mode_toggle(self):
        current_text = self.mode_toggle_button.text()
        if current_text == "Pick And Spray":
            new_mode = "Spray Only"
        else:
            new_mode = "Pick And Spray"
        self.mode_toggle_button.setText(new_mode)
        self.mode_toggle_requested.emit(new_mode)


    # ------------------------------------------------------------------ #
    #  Cleanup                                                             #
    # ------------------------------------------------------------------ #

    def clean_up(self):
        """Release resources. Broker subscriptions are managed by DashboardAdapter."""
        pass



