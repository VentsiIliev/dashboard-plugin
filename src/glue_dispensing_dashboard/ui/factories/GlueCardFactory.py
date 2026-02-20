try:
    from ..widgets.GlueMeterCard import GlueMeterCard
    from ...core.config import GlueDashboardConfig
except ImportError:
    from glue_dispensing_dashboard.ui.widgets.GlueMeterCard import GlueMeterCard
    from glue_dispensing_dashboard.core.config import GlueDashboardConfig


class GlueCardFactory:
    def __init__(self, config: GlueDashboardConfig, container=None):
        self.config = config
        self.container = container

    def create_glue_card(self, index: int, label_text: str) -> GlueMeterCard:
        if self.container is not None:
            capacity = self.container.get_cell_capacity(index)
        else:
            capacity = self.config.default_cell_capacity_grams
        return GlueMeterCard(label_text, index, capacity_grams=capacity)

