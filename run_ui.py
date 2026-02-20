#!/usr/bin/env python3
"""
Bare-bone runner — DashboardWidget only (Level 1, pure UI).
No broker, no adapter, no application state.  Good for styling / layout work.

    python run_ui.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from dashboard.DashboardWidget import DashboardWidget

app = QApplication(sys.argv)
w = DashboardWidget()
w.setWindowTitle("DashboardWidget — bare UI")
w.resize(1280, 1024)



w.show()
sys.exit(app.exec())
