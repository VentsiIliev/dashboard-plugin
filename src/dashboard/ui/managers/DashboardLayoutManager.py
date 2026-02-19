from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt
from typing import List

try:
    from ..widgets.shared.MaterialButton import MaterialButton
except ImportError:
    from MaterialButton import MaterialButton


class DashboardLayoutManager:
    def __init__(self, parent_widget: QWidget, config):
        self.parent = parent_widget
        self.config = config
        self.main_layout = QVBoxLayout(parent_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

    def setup_complete_layout(self, trajectory_widget, glue_cards: List[QWidget],
                              control_buttons: QWidget, clean_button: MaterialButton,
                              reset_errors_button: MaterialButton,
                              mode_toggle_button: MaterialButton) -> None:
        top_section = self._create_top_section(trajectory_widget, glue_cards)
        bottom_section = self._create_bottom_section(
            control_buttons, clean_button, reset_errors_button, mode_toggle_button
        )
        self.main_layout.addLayout(top_section, stretch=2)
        self.main_layout.addLayout(bottom_section, stretch=1)

    def _create_top_section(self, trajectory_widget, glue_cards: List[QWidget]) -> QHBoxLayout:
        top_section = QHBoxLayout()
        top_section.setSpacing(10)
        preview_container = self._create_preview_container(trajectory_widget)
        top_section.addWidget(preview_container, stretch=2)
        glue_container = self._create_glue_cards_container(glue_cards)
        top_section.addWidget(glue_container, stretch=1)
        return top_section

    def _create_preview_container(self, trajectory_widget) -> QWidget:
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)
        trajectory_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        trajectory_widget.setMinimumHeight(300)
        trajectory_widget.setMaximumWidth(1200)
        preview_layout.addWidget(trajectory_widget)
        return preview_widget

    def _create_glue_cards_container(self, glue_cards: List[QWidget]) -> QWidget:
        glue_cards_widget = QWidget()
        glue_cards_layout = QVBoxLayout(glue_cards_widget)
        glue_cards_layout.setContentsMargins(0, 0, 0, 0)
        glue_cards_layout.setSpacing(8)
        for card in glue_cards:
            card.setMinimumHeight(self.config.card_min_height)
            card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            glue_cards_layout.addWidget(card)
        glue_cards_layout.addStretch()
        glue_cards_widget.setMinimumWidth(self.config.glue_cards_min_width)
        glue_cards_widget.setMaximumWidth(self.config.glue_cards_max_width)
        return glue_cards_widget

    def _create_bottom_section(self, control_buttons: QWidget,
                               clean_btn: MaterialButton,
                               reset_errors_button: MaterialButton,
                               mode_toggle_button: MaterialButton) -> QVBoxLayout:
        bottom_section = QVBoxLayout()
        bottom_section.setSpacing(10)

        placeholders_container = QWidget()
        placeholders_layout = QGridLayout(placeholders_container)
        placeholders_layout.setSpacing(15)
        placeholders_layout.setContentsMargins(0, 0, 0, 0)

        rows = self.config.bottom_grid_rows
        cols = self.config.bottom_grid_cols

        # Slot assignment map for the bottom grid.
        # Entries that are None become placeholder frames.
        # (row, col) -> widget | None
        slot_map = {}
        for row in range(rows):
            for col in range(cols):
                slot_map[(row, col)] = None  # default: placeholder

        # Control buttons span rows 0-1 in the last column
        last_col = cols - 1
        slot_map[(0, last_col)] = ("span", control_buttons, rows, 1)
        for row in range(1, rows):
            slot_map[(row, last_col)] = "skip"  # occupied by span

        # Mode toggle: row 1, col 0
        if rows > 1:
            slot_map[(1, 0)] = mode_toggle_button

        # Clean button: row 1, col 1 (middle column if it exists)
        if rows > 1 and cols > 2:
            slot_map[(1, 1)] = clean_btn

        for (row, col), entry in slot_map.items():
            if entry == "skip":
                continue
            elif entry is None:
                placeholder = self._create_placeholder(row * cols + col + 1)
                placeholders_layout.addWidget(placeholder, row, col)
            elif isinstance(entry, tuple) and entry[0] == "span":
                _, widget, row_span, col_span = entry
                placeholders_layout.addWidget(widget, row, col, row_span, col_span)
            else:
                placeholders_layout.addWidget(entry, row, col)

        bottom_section.addWidget(placeholders_container)
        return bottom_section

    def _create_placeholder(self, number: int) -> QFrame:
        placeholder_frame = QFrame()
        placeholder_frame.setMinimumHeight(120)
        placeholder_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(placeholder_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        return placeholder_frame
