try:
    from ..widgets.GlueMeterCard import GlueMeterCard
    from ...core.config import DashboardConfig
except ImportError:
    from widgets.GlueMeterCard import GlueMeterCard
    from config import DashboardConfig


class GlueCardFactory:
    """
    Factory for creating configured GlueMeterCard instances.

    The optional *container* is used only for capacity lookup at card-creation
    time.  When container is None, config.default_cell_capacity_grams is used.
    """

    def __init__(self, config: DashboardConfig, container=None):
        self.config = config
        self.container = container

    def create_glue_card(self, index: int, label_text: str) -> GlueMeterCard:
        """Create a GlueMeterCard with the appropriate capacity."""
        if self.container is not None:
            capacity = self.container.get_cell_capacity(index)
        else:
            capacity = self.config.default_cell_capacity_grams
        return GlueMeterCard(label_text, index, capacity_grams=capacity)
