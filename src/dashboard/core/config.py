from dataclasses import dataclass, field


@dataclass
class DashboardConfig:
    glue_meters_count: int = 3
    trajectory_width: int = 800
    trajectory_height: int = 450
    card_min_height: int = 75
    glue_cards_min_width: int = 350
    glue_cards_max_width: int = 450
    default_cell_capacity_grams: float = 5000.0
    display_fps_ms: int = 30
    trajectory_trail_length: int = 100
    bottom_grid_rows: int = 2
    bottom_grid_cols: int = 3
    combo_style: "ComboBoxStyle" = None

    def __post_init__(self):
        if self.combo_style is None:
            try:
                from ..ui.widgets.shared.ComboBoxStyle import ComboBoxStyle
            except ImportError:
                from ComboBoxStyle import ComboBoxStyle
            self.combo_style = ComboBoxStyle()
