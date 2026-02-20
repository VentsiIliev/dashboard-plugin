from dataclasses import dataclass, field


@dataclass
class DashboardConfig:
    trajectory_width: int = 800
    trajectory_height: int = 450
    card_min_height: int = 75
    card_grid_rows: int = 3
    card_grid_cols: int = 1
    card_grid_min_width: int = 350
    card_grid_max_width: int = 450
    display_fps_ms: int = 30
    trajectory_trail_length: int = 100
    action_grid_rows: int = 2
    action_grid_cols: int = 2
    bottom_section_height: int = 300
    preview_aux_rows: int = 2
    preview_aux_cols: int = 3
    show_placeholders: bool = True
    combo_style: "ComboBoxStyle" = None

    def __post_init__(self):
        if self.combo_style is None:
            try:
                from ..ui.widgets.shared.ComboBoxStyle import ComboBoxStyle
            except ImportError:
                from ComboBoxStyle import ComboBoxStyle
            self.combo_style = ComboBoxStyle()

