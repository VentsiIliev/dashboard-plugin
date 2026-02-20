#!/usr/bin/env python3
"""
Bare-bone runner — DashboardWidget only (Level 1, pure UI).
No broker, no adapter, no application state.  Good for styling / layout work.

    python run_ui.py

Keyboard shortcuts:
    L - Cycle language (localization test)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

from dashboard.DashboardWidget import DashboardWidget
from localization import TranslationManager


class UITestWindow(QMainWindow):
    def __init__(self, translation_manager: TranslationManager):
        super().__init__()
        self.translation_manager = translation_manager
        self.available_languages = translation_manager.get_available_languages()
        self.lang_index = 0

        self.dashboard = DashboardWidget()
        self.setCentralWidget(self.dashboard)
        self.setWindowTitle("DashboardWidget — bare UI | L=cycle language")
        self.resize(1280, 1024)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_L:
            self.lang_index = (self.lang_index + 1) % len(self.available_languages)
            lang = self.available_languages[self.lang_index]
            self.translation_manager.load_language(lang)
            print(f"🌐 Language switched to: {lang.native_name} ({lang.code})")
        else:
            super().keyPressEvent(event)


app = QApplication(sys.argv)
_translations_dir = Path(__file__).parent / "src/glue_dispensing_dashboard/localization/translations"
translation_manager = TranslationManager(app, translations_dir=_translations_dir, file_prefix="glue")

window = UITestWindow(translation_manager)
window.show()

print("L — cycle language")

sys.exit(app.exec())
