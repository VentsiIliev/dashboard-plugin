from PyQt6.QtCore import pyqtSignal

try:
    from frontend.core.shared.base_widgets.AppWidget import AppWidget
except ImportError:
    from PyQt6.QtWidgets import QWidget as AppWidget

try:
    from ..core.container import GlueContainer
except ImportError:
    from dashboard.glue.core.container import GlueContainer

try:
    from src.dashboard.ui.DashboardWidget import DashboardWidget
except ImportError:
    from dashboard.ui.DashboardWidget import DashboardWidget

try:
    from ..adapter.GlueAdapter import GlueAdapter
except ImportError:
    from dashboard.glue.adapter.GlueAdapter import GlueAdapter

try:
    from src.dashboard.ui.DashboardWidget import ActionButtonConfig
except ImportError:
    from dashboard.ui.DashboardWidget import ActionButtonConfig


class GlueAppWidget(AppWidget):
    """
    Entry point: wires DashboardWidget (Level 1) + GlueAdapter (Level 2)
    and exposes signals to the parent application.
    """

    LOGOUT_REQUEST = pyqtSignal()
    start_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    action_requested = pyqtSignal(str)

    def __init__(self, container: GlueContainer = None, parent=None, controller=None):
        if container is None and controller is not None:
            container = GlueContainer(controller=controller)
        self._container = container or GlueContainer()
        super().__init__("Dashboard", parent)

    def setup_ui(self):
        super().setup_ui()

        built_cards = GlueAdapter.build_cards(self._container)

        self._dashboard = DashboardWidget(
            config=GlueAdapter.CONFIG,
            action_buttons=GlueAdapter.ACTION_BUTTONS,
            cards=built_cards,
        )

        self._adapter = GlueAdapter(self._dashboard, self._container)
        self._adapter.connect()

        self._dashboard.start_requested.connect(self.start_requested.emit)
        self._dashboard.stop_requested.connect(self.stop_requested.emit)
        self._dashboard.pause_requested.connect(self.pause_requested.emit)
        self._dashboard.action_requested.connect(self.action_requested.emit)

        try:
            layout = self.layout()
            old_content = layout.itemAt(layout.count() - 1).widget()
            layout.removeWidget(old_content)
            old_content.deleteLater()
        except Exception:
            pass
        try:
            self.layout().addWidget(self._dashboard)
        except Exception:
            pass

    def closeEvent(self, event):
        self._adapter.disconnect()
        super().closeEvent(event)
        self.LOGOUT_REQUEST.emit()

    def clean_up(self):
        self._adapter.disconnect()
        if hasattr(super(), "clean_up"):
            super().clean_up()


# Backward-compat alias
DashboardAppWidget = GlueAppWidget

