#!/usr/bin/env python3
"""
Full-stack runner — DashboardWidget + DashboardAdapter + DashboardContainer.
Exercises the complete three-layer architecture without requiring AppWidget.

    python run_app.py

Keyboard shortcuts for testing:
    W - Publish test weight to cell 1
    S - Publish test state to cell 1
    G - Publish test glue type to cell 1
    A - Cycle application state
    T - Publish trajectory point
    L - Cycle language (localization test)
    Space - Toggle auto-test mode
"""
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar
from PyQt6.QtCore import QTimer, Qt, QEvent
from PyQt6.QtGui import QKeyEvent

import numpy as np

from localization import TranslationManager, Language
from glue_dispensing_dashboard.app.GlueDashboardAppWidget import GlueDashboardAppWidget
from glue_dispensing_dashboard.adapter.GlueAdapter import GlueAdapter
from glue_dispensing_dashboard.core.container import GlueContainer
from external_dependencies.MessageBroker import MessageBroker
from external_dependencies.topics import GlueCellTopics, SystemTopics, RobotTopics, VisionTopics
from external_dependencies.ApplicationState import ApplicationState


class TestPublisher:
    """Test message publisher for verifying MessageBroker subscriptions."""

    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self.app_states = list(ApplicationState)
        self.current_state_idx = 0
        self.weight_values = {1: 5000.0, 2: 4500.0, 3: 4000.0}
        self.glue_types = ["PUR Hotmelt", "EVA Adhesive", "Silicone"]

    def publish_test_weight(self, cell_id: int = 1):
        """Publish a random weight value to a cell."""
        weight = random.uniform(0, 5000)
        self.weight_values[cell_id] = weight
        topic = GlueCellTopics.cell_weight(cell_id)
        self.broker.publish(topic, weight)
        print(f"📊 Published weight {weight:.1f}g to cell {cell_id}")

    def publish_test_state(self, cell_id: int = 1):
        """Publish a test state to a cell."""
        states = ["ready", "initializing", "low_weight", "empty", "error", "disconnected"]
        state = random.choice(states)
        topic = GlueCellTopics.cell_state(cell_id)
        self.broker.publish(topic, {"current_state": state})
        print(f"🔔 Published state '{state}' to cell {cell_id}")

    def publish_test_glue_type(self, cell_id: int = 1):
        """Publish a test glue type to a cell."""
        glue_type = random.choice(self.glue_types)
        topic = GlueCellTopics.cell_glue_type(cell_id)
        self.broker.publish(topic, glue_type)
        print(f"🧪 Published glue type '{glue_type}' to cell {cell_id}")

    def cycle_application_state(self):
        """Cycle through application states."""
        self.current_state_idx = (self.current_state_idx + 1) % len(self.app_states)
        state = self.app_states[self.current_state_idx]
        self.broker.publish(SystemTopics.APPLICATION_STATE, state.value)
        print(f"⚙️  Published application state: {state.value}")

    def publish_trajectory_point(self):
        """Publish a random trajectory point."""
        x = random.randint(50, 590)
        y = random.randint(50, 310)
        self.broker.publish(RobotTopics.TRAJECTORY_POINT, {"x": x, "y": y})
        print(f"📍 Published trajectory point: ({x}, {y})")

    def publish_test_image(self):
        """Publish a test image."""
        img = np.random.randint(0, 255, (360, 640, 3), dtype=np.uint8)
        self.broker.publish(VisionTopics.LATEST_IMAGE, {"image": img})
        print(f"🖼️  Published test image")

    def run_auto_test(self):
        """Run a sequence of test messages."""
        for cell_id in [1, 2, 3]:
            self.publish_test_weight(cell_id)

        self.publish_test_state(1)
        self.publish_test_glue_type(1)
        self.publish_trajectory_point()


class TestWindow(QMainWindow):
    """Main window with keyboard shortcuts for testing."""

    def __init__(self, dashboard, adapter, test_publisher, translation_manager):
        super().__init__()
        self.dashboard = dashboard
        self.adapter = adapter
        self.test_publisher = test_publisher
        self.translation_manager = translation_manager
        self.available_languages = translation_manager.get_available_languages()
        self.lang_index = 0
        self.auto_test_enabled = False

        self.setWindowTitle("Dashboard — full stack (no AppWidget) — Press SPACE for auto-test")
        self.setCentralWidget(dashboard)
        self.resize(1280, 1024)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready | W=weight | S=state | G=glue | A=app-state | T=point | I=image | R=start | X=stop | C=break | L=language | SPACE=auto")

        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.test_publisher.run_auto_test)

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.adapter.retranslateUi()
        super().changeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key == Qt.Key.Key_W:
            self.test_publisher.publish_test_weight(1)
            self.status_bar.showMessage("Published test weight", 2000)

        elif key == Qt.Key.Key_S:
            self.test_publisher.publish_test_state(1)
            self.status_bar.showMessage("Published test state", 2000)

        elif key == Qt.Key.Key_G:
            self.test_publisher.publish_test_glue_type(1)
            self.status_bar.showMessage("Published test glue type", 2000)

        elif key == Qt.Key.Key_A:
            self.test_publisher.cycle_application_state()
            self.status_bar.showMessage("Cycled application state", 2000)

        elif key == Qt.Key.Key_T:
            self.test_publisher.publish_trajectory_point()
            self.status_bar.showMessage("Published trajectory point", 2000)

        elif key == Qt.Key.Key_I:
            self.test_publisher.publish_test_image()
            self.status_bar.showMessage("Published test image", 2000)

        elif key == Qt.Key.Key_R:
            self.dashboard.enable_trajectory_drawing()
            self.status_bar.showMessage("🟢 Trajectory drawing ENABLED", 2000)
            print("🟢 Trajectory drawing ENABLED")

        elif key == Qt.Key.Key_X:
            self.dashboard.disable_trajectory_drawing()
            self.status_bar.showMessage("🔴 Trajectory drawing DISABLED", 2000)
            print("🔴 Trajectory drawing DISABLED")

        elif key == Qt.Key.Key_C:
            self.dashboard.break_trajectory()
            self.status_bar.showMessage("⚡ Trajectory break inserted", 2000)
            print("⚡ Trajectory break inserted")

        elif key == Qt.Key.Key_L:
            self.lang_index = (self.lang_index + 1) % len(self.available_languages)
            lang = self.available_languages[self.lang_index]
            self.translation_manager.load_language(lang)
            self.status_bar.showMessage(f"Language: {lang.native_name} ({lang.code})", 3000)
            print(f"🌐 Language switched to: {lang.native_name} ({lang.code})")

        elif key == Qt.Key.Key_Space:
            self.auto_test_enabled = not self.auto_test_enabled
            if self.auto_test_enabled:
                self.auto_timer.start(2000)  # Every 2 seconds
                self.status_bar.showMessage("🟢 Auto-test ENABLED (every 2s)", 3000)
                print("\n🟢 Auto-test mode ENABLED - publishing test messages every 2 seconds")
            else:
                self.auto_timer.stop()
                self.status_bar.showMessage("🔴 Auto-test DISABLED", 3000)
                print("\n🔴 Auto-test mode DISABLED")

        else:
            super().keyPressEvent(event)


app = QApplication(sys.argv)

_translations_dir = Path(__file__).parent / "src/glue_dispensing_dashboard/localization/translations"
translation_manager = TranslationManager(app, translations_dir=_translations_dir, file_prefix="glue")

container = GlueContainer()
built_cards = GlueAdapter.build_cards(container)
ui = GlueDashboardAppWidget(
    config=GlueAdapter.CONFIG,
    action_buttons=GlueAdapter.ACTION_BUTTONS,
    cards=built_cards,
)
adapter = GlueAdapter(ui, container)
adapter.connect()

# Enable trajectory drawing by default for testing
ui.enable_trajectory_drawing()

broker = MessageBroker()
test_publisher = TestPublisher(broker)

window = TestWindow(ui, adapter, test_publisher, translation_manager)
window.show()

print("\n" + "="*60)
print("Dashboard Test Runner")
print("="*60)
print("\nKeyboard shortcuts:")
print("  W - Publish test weight to cell 1")
print("  S - Publish test state to cell 1")
print("  G - Publish test glue type to cell 1")
print("  A - Cycle application state")
print("  T - Publish trajectory point")
print("  I - Publish test image")
print("  R - Enable trajectory drawing")
print("  X - Disable trajectory drawing")
print("  C - Break trajectory (start new line)")
print("  L     - Cycle language (localization test)")
print("  SPACE - Toggle auto-test mode (2s interval)")
print("\n" + "="*60 + "\n")

sys.exit(app.exec())
