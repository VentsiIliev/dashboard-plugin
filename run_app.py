#!/usr/bin/env python3
"""
Full-stack runner — DashboardWidget + DashboardAdapter + DashboardContainer.
Exercises the complete three-layer architecture without requiring AppWidget.

    python run_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow
from dashboard.ui.DashboardWidget import DashboardWidget
from dashboard.adapter.DashboardAdapter import DashboardAdapter
from dashboard.core.container import DashboardContainer

app = QApplication(sys.argv)

container = DashboardContainer()          # empty container — all optional deps are None
dashboard = DashboardWidget(config=container.config)
adapter = DashboardAdapter(dashboard, container)
adapter.connect()                          # subscriptions live, signals wired

window = QMainWindow()
window.setWindowTitle("Dashboard — full stack (no AppWidget)")
window.setCentralWidget(dashboard)
window.resize(1400, 800)
window.show()

sys.exit(app.exec())
