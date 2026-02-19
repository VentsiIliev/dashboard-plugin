from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QCheckBox, QRadioButton,
                             QButtonGroup, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QColor, QIcon
import sys

try:
    from .widgets.shared.MaterialButton import MaterialButton
except ImportError:
    from MaterialButton import MaterialButton


class WizardStep(QWizardPage):
    """Base class for wizard steps with image and text support"""

    def __init__(self, title, subtitle, description, image_path=None):
        super().__init__()
        self.setTitle(title)
        self.setSubTitle(subtitle)

        layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #e0e0e0;
                border: 2px dashed #999;
                border-radius: 8px;
            }
        """)

        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("📷 Image Placeholder")
            font = QFont()
            font.setPointSize(14)
            self.image_label.setFont(font)

        layout.addWidget(self.image_label)

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("QLabel { margin: 15px 0; line-height: 1.5; font-size: 16px; }")
        layout.addWidget(description_label)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        layout.addStretch()
        self.setLayout(layout)


class WelcomeStep(WizardStep):
    def __init__(self):
        super().__init__(
            title="Glue Change Guide",
            subtitle="Welcome to the Glue Change Wizard",
            description="This wizard will guide you through the process of changing the glue container. Click Next to continue.",
        )


class OpenDrawerStep(WizardStep):
    def __init__(self):
        super().__init__(
            title="Step 1: Open Drawer",
            subtitle="Open the glue container drawer",
            description="Locate and carefully open the drawer containing the glue container.",
        )


class DisconnectHoseStep(WizardStep):
    def __init__(self):
        super().__init__(
            title="Step 2: Disconnect Hose",
            subtitle="Disconnect the hose from the glue container",
            description="Carefully disconnect the hose from the current glue container. Make sure to avoid any spills.",
        )


class PlaceNewContainerStep(WizardStep):
    def __init__(self):
        super().__init__(
            title="Step 3: Place New Glue Container",
            subtitle="Place the new glue container in the drawer",
            description="Remove the old glue container and place the new one in its position.",
        )


class ConnectHoseStep(WizardStep):
    def __init__(self):
        super().__init__(
            title="Step 4: Connect Hose",
            subtitle="Connect the hose to the new container",
            description="Securely connect the hose to the new glue container. Ensure the connection is tight.",
        )


class CloseDrawerStep(WizardStep):
    def __init__(self):
        super().__init__(
            title="Step 5: Close Drawer",
            subtitle="Close the glue container drawer",
            description="Carefully close the drawer. Make sure everything is secured properly.",
        )


class SelectGlueTypeStep(WizardStep):
    """Select glue type step — glue type names are injected, not fetched here."""

    def __init__(self, glue_type_names: Optional[list] = None):
        super().__init__(
            title="Step 6: Select Glue Type",
            subtitle="Select the type of the new glue",
            description="Choose the type of glue you have installed from the options below.",
        )

        glue_label = QLabel("Select Glue Type:")
        glue_label.setStyleSheet("font-weight: bold; margin-top: 10px; font-size: 16px;")
        self.content_layout.addWidget(glue_label)

        self.glue_group = QButtonGroup(self)
        self.radio_buttons = []

        names = glue_type_names or []

        if not names:
            error_label = QLabel("⚠️ No glue types configured!")
            error_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px; padding: 10px;")
            self.content_layout.addWidget(error_label)

            instruction_label = QLabel(
                "Please configure glue types in:\n"
                "1. Glue Cell Settings (assign types to cells)\n"
                "2. Or register custom glue types\n\n"
                "Wizard cannot continue without glue type configuration."
            )
            instruction_label.setStyleSheet(
                "font-size: 12px; padding: 10px; background-color: #fff3cd; border-radius: 5px;"
            )
            instruction_label.setWordWrap(True)
            self.content_layout.addWidget(instruction_label)
            return

        for idx, glue_type_name in enumerate(names):
            radio = QRadioButton(glue_type_name)
            radio.setStyleSheet("font-size: 14px;")
            if idx == 0:
                radio.setChecked(True)
            self.glue_group.addButton(radio, idx)
            self.radio_buttons.append(radio)
            self.content_layout.addWidget(radio)

    def get_selected_glue_type(self) -> Optional[str]:
        for radio in self.radio_buttons:
            if radio.isChecked():
                return radio.text()
        return self.radio_buttons[0].text() if self.radio_buttons else None


class SummaryStep(WizardStep):
    def __init__(self):
        super().__init__(
            title="Summary",
            subtitle="Glue change completed",
            description="Review the completed steps and the selected glue type.",
        )
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setStyleSheet("font-size: 14px;")
        self.content_layout.addWidget(self.summary_text)

    def initializePage(self):
        glue_page = self.wizard().page(6)
        glue_type = glue_page.get_selected_glue_type()
        summary = f"""
<b>Glue Change Steps Completed:</b><br>
✓ Drawer opened<br>
✓ Hose disconnected from old container<br>
✓ New glue container placed<br>
✓ Hose connected to new container<br>
✓ Drawer closed<br><br>
<b>Selected Glue Type:</b> {glue_type}
        """
        self.summary_text.setHtml(summary)


class SetupWizard(QWizard):
    """
    Main wizard for guiding the user through a glue container change.

    Pass *glue_type_names* to inject available glue types (from DashboardContainer).
    """

    def __init__(self, glue_type_names: Optional[list] = None):
        super().__init__()
        self.setWindowTitle("Glue Change Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(600, 500)

        # Use a path relative to this file — no hardcoded Windows paths
        icon_path = Path(__file__).parent.parent / "resources" / "logo.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            logo_pixmap = QPixmap(str(icon_path))
            self.setPixmap(
                QWizard.WizardPixmap.LogoPixmap,
                logo_pixmap.scaled(60, 60,
                                   Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation),
            )

        self.addPage(WelcomeStep())             # page 0
        self.addPage(OpenDrawerStep())          # page 1
        self.addPage(DisconnectHoseStep())      # page 2
        self.addPage(PlaceNewContainerStep())   # page 3
        self.addPage(ConnectHoseStep())         # page 4
        self.addPage(CloseDrawerStep())         # page 5
        self.addPage(SelectGlueTypeStep(glue_type_names))  # page 6
        self.addPage(SummaryStep())             # page 7

        self.button(QWizard.WizardButton.FinishButton).clicked.connect(self.on_finish)
        self.customize_buttons()

    def on_finish(self):
        selected_type = self.get_selected_glue_type()
        print(f"Glue change completed! Selected: {selected_type}")

    def get_selected_glue_type(self) -> Optional[str]:
        glue_page = self.page(6)
        return glue_page.get_selected_glue_type()

    def customize_buttons(self):
        back_btn = self.button(QWizard.WizardButton.BackButton)
        next_btn = self.button(QWizard.WizardButton.NextButton)
        cancel_btn = self.button(QWizard.WizardButton.CancelButton)
        finish_btn = self.button(QWizard.WizardButton.FinishButton)

        self.setButton(QWizard.WizardButton.BackButton, MaterialButton(back_btn.text()))
        self.setButton(QWizard.WizardButton.NextButton, MaterialButton(next_btn.text()))
        self.setButton(QWizard.WizardButton.CancelButton, MaterialButton(cancel_btn.text()))
        self.setButton(QWizard.WizardButton.FinishButton, MaterialButton(finish_btn.text()))


def main():
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
