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
from dashboard.ui.DashboardWidget import DashboardWidget
from dashboard.ui.setupWizard import SetupWizard

app = QApplication(sys.argv)
w = DashboardWidget()
w.setWindowTitle("DashboardWidget — bare UI")
w.resize(1400, 800)

# Wire the wizard so the Change button works without a full adapter
def _launch_wizard(cell_id: int):
    wizard = SetupWizard(glue_type_names=["Type A", "Type B", "Type C"])
    wizard.setWindowTitle(f"Change Glue for Cell {cell_id}")
    if wizard.exec() == 1:
        selected = wizard.get_selected_glue_type()
        if selected:
            w.set_cell_glue_type(cell_id, selected)

w.glue_type_change_requested.connect(_launch_wizard)

w.show()
sys.exit(app.exec())
