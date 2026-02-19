from typing import Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame

try:
    from .GlueMeterWidget import GlueMeterWidget
except ImportError:
    try:
        from ..widgets.GlueMeterWidget import GlueMeterWidget
    except ImportError:
        from GlueMeterWidget import GlueMeterWidget


class GlueMeterCard(QFrame):
    """
    Pure UI composite: title header + state indicator dot + glue-type label
    + "Change" button + GlueMeterWidget.

    Has zero knowledge of MessageBroker, topics, or any external system.
    Call the typed setter API to update the display.
    """

    change_glue_requested = pyqtSignal(int)  # emits cell index

    def __init__(self, label_text: str, index: int, capacity_grams: float = 5000.0):
        super().__init__()
        self.label_text = label_text
        self.index = index
        self.card_index = index  # backward-compat alias
        self.meter_widget = GlueMeterWidget(index, capacity_grams=capacity_grams)
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Public setter API (called by DashboardWidget)                      #
    # ------------------------------------------------------------------ #

    def set_weight(self, grams: float) -> None:
        self.meter_widget.set_weight(grams)

    def set_state(self, state_str: str) -> None:
        self._update_indicator(state_str)
        self.meter_widget.set_state(state_str)

    def set_glue_type(self, glue_type: Optional[str]) -> None:
        self.glue_type_label.setText(f"🧪 {glue_type}" if glue_type else "No glue configured")

    def initialize_display(self, initial_state: Optional[dict], glue_type: Optional[str]) -> None:
        if initial_state:
            self.set_state(initial_state.get("current_state", "unknown"))
        if glue_type:
            self.set_glue_type(glue_type)

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _update_indicator(self, state_str: str) -> None:
        """Update the state indicator circle colour based on *state_str*."""
        state_config = {
            "unknown":       {"color": "#808080", "text": "Unknown"},
            "initializing":  {"color": "#FFA500", "text": "Initializing..."},
            "ready":         {"color": "#28a745", "text": "Ready"},
            "low_weight":    {"color": "#ffc107", "text": "Low Weight"},
            "empty":         {"color": "#dc3545", "text": "Empty"},
            "error":         {"color": "#d9534f", "text": "Error"},
            "disconnected":  {"color": "#6c757d", "text": "Disconnected"},
        }
        cfg = state_config.get(str(state_str).lower(), state_config["unknown"])
        self.state_indicator.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                color: {cfg['color']};
                background-color: white;
                border: 2px solid {cfg['color']};
                border-radius: 20px;
                padding: 5px;
            }}
        """)
        self.state_indicator.setToolTip(cfg["text"])

    def _build_ui(self) -> None:
        self.dragEnabled = True
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.title_label = QLabel(self.label_text)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 10px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #905BA9, stop:1 #7a4d8f);
                border-radius: 5px;
            }
        """)
        header_layout.addWidget(self.title_label, 1)

        self.state_indicator = QLabel("●")
        self.state_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_indicator.setFixedSize(40, 40)
        self.state_indicator.setToolTip("Initializing...")
        self.state_indicator.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #808080;
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 20px;
                padding: 5px;
            }
        """)
        header_layout.addWidget(self.state_indicator, 0)
        main_layout.addLayout(header_layout)

        # Info section
        info_widget = QFrame()
        info_widget.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_layout.setSpacing(10)

        self.glue_type_label = QLabel("🧪 Loading...")
        self.glue_type_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.glue_type_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #2c3e50;
                padding: 4px 8px;
                background-color: transparent;
            }
        """)
        info_layout.addWidget(self.glue_type_label, 1)

        self.change_glue_button = QPushButton("⚙ Change")
        self.change_glue_button.clicked.connect(lambda: self.change_glue_requested.emit(self.index))
        self.change_glue_button.setFixedHeight(32)
        self.change_glue_button.setStyleSheet("""
            QPushButton {
                background-color: #905BA9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #7a4d8f; }
            QPushButton:pressed { background-color: #643f75; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
        """)
        info_layout.addWidget(self.change_glue_button)
        main_layout.addWidget(info_widget)

        # Meter
        main_layout.addWidget(self.meter_widget)
        self.meter_widget.setStyleSheet("""
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 10px;
        """)

        main_layout.addStretch()

        self.setStyleSheet("""
            GlueMeterCard {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
            }
        """)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow

    app = QApplication([])
    main_window = QMainWindow()
    main_window.setWindowTitle("GlueMeterCard Test")
    main_window.setGeometry(100, 100, 400, 300)
    card = GlueMeterCard("Test Glue Meter", 1)
    main_window.setCentralWidget(card)
    main_window.show()
    app.exec()
