from PyQt6.QtCore import pyqtSignal

try:
    from frontend.core.shared.base_widgets.AppWidget import AppWidget
except ImportError:
    # Fallback for standalone / test mode
    from PyQt6.QtWidgets import QWidget as AppWidget

try:
    from ..core.container import DashboardContainer
except ImportError:
    from container import DashboardContainer

try:
    from ..ui.DashboardWidget import DashboardWidget
except ImportError:
    from DashboardWidget import DashboardWidget

try:
    from ..adapter.DashboardAdapter import DashboardAdapter
except ImportError:
    from DashboardAdapter import DashboardAdapter


class DashboardAppWidget(AppWidget):
    """
    Entry point: wires DashboardWidget (Level 1) + DashboardAdapter (Level 2)
    and exposes signals to the parent application.

    Construction::

        # Minimal (standalone / test)
        widget = DashboardAppWidget()

        # Full integration (parent app)
        container = DashboardContainer(
            controller=my_controller,
            glue_cell_manager=GlueCellsManagerSingleton.get_instance(),
            cell_state_manager=fetcher.state_manager,
            cell_weight_monitor=fetcher.state_monitor,
        )
        widget = DashboardAppWidget(container=container, parent=self)

        # Backward-compat shim (controller only)
        widget = DashboardAppWidget(controller=my_controller, parent=self)
    """

    LOGOUT_REQUEST = pyqtSignal()
    start_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    clean_requested = pyqtSignal()
    reset_errors_requested = pyqtSignal()
    mode_toggle_requested = pyqtSignal(str)

    def __init__(self, container: DashboardContainer = None, parent=None, controller=None):
        # Backward-compat: accept bare controller and wrap it in a container
        if container is None and controller is not None:
            container = DashboardContainer(controller=controller)
        self._container = container or DashboardContainer()
        super().__init__("Dashboard", parent)

    def setup_ui(self):
        super().setup_ui()

        # 1. Create the pure UI layer
        self._dashboard = DashboardWidget(config=self._container.config)

        # 2. Create the adapter and connect it
        self._adapter = DashboardAdapter(self._dashboard, self._container)
        self._adapter.connect()

        # 3. Forward user-action signals to the parent app
        self._dashboard.start_requested.connect(self.start_requested.emit)
        self._dashboard.stop_requested.connect(self.stop_requested.emit)
        self._dashboard.pause_requested.connect(self.pause_requested.emit)
        self._dashboard.clean_requested.connect(self.clean_requested.emit)
        self._dashboard.reset_errors_requested.connect(self.reset_errors_requested.emit)
        self._dashboard.mode_toggle_requested.connect(self.mode_toggle_requested.emit)

        # 4. Place in layout (replace AppWidget placeholder)
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
