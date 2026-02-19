"""
DashboardContainer — the ONLY place where cross-boundary lazy imports happen.

All fields are Optional so the dashboard degrades gracefully in
standalone / test mode (no parent-app modules required).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Callable

try:
    from .config import DashboardConfig
except ImportError:
    from config import DashboardConfig

try:
    from .protocols import (
        ControllerProtocol,
        GlueCellManagerProtocol,
        CellStateManagerProtocol,
        CellWeightMonitorProtocol,
    )
except ImportError:
    from protocols import (
        ControllerProtocol,
        GlueCellManagerProtocol,
        CellStateManagerProtocol,
        CellWeightMonitorProtocol,
    )


@dataclass
class DashboardContainer:
    controller: Optional[ControllerProtocol] = None
    glue_cell_manager: Optional[GlueCellManagerProtocol] = None
    cell_state_manager: Optional[CellStateManagerProtocol] = None
    cell_weight_monitor: Optional[CellWeightMonitorProtocol] = None
    config: DashboardConfig = field(default_factory=DashboardConfig)

    # ------------------------------------------------------------------ #
    #  Convenience shortcuts                                               #
    # ------------------------------------------------------------------ #

    @property
    def controller_service(self):
        """Shortcut to controller.controller_service, or None."""
        if self.controller is not None and hasattr(self.controller, "controller_service"):
            return self.controller.controller_service
        return None

    # ------------------------------------------------------------------ #
    #  Lazy cross-boundary helpers                                         #
    # ------------------------------------------------------------------ #

    def camera_feed_callback(self) -> Optional[Callable[[], None]]:
        """Return a zero-arg callable that triggers a camera frame update."""
        if self.controller is None:
            return None
        try:
            from communication_layer.api.v1.endpoints import camera_endpoints
            return lambda: self.controller.handle(camera_endpoints.UPDATE_CAMERA_FEED)
        except Exception:
            return None

    def get_cell_capacity(self, cell_id: int) -> float:
        """
        Return the configured capacity (grams) for *cell_id*.

        Makes one RPC call per cell; falls back to
        config.default_cell_capacity_grams on any failure.
        """
        if self.controller_service is None:
            return self.config.default_cell_capacity_grams
        try:
            from communication_layer.api.v1.endpoints import glue_endpoints
            response = self.controller_service.send_request(
                glue_endpoints.GLUE_CELLS_CONFIG_GET
            )
            if response and response.get("status") == "success":
                cells_data = response.get("data", {})
                if isinstance(cells_data, dict) and "cells" in cells_data:
                    cells = cells_data["cells"]
                elif isinstance(cells_data, list):
                    cells = cells_data
                else:
                    cells = []
                for cell in cells:
                    if isinstance(cell, dict) and cell.get("id") == cell_id:
                        return float(cell.get("capacity", self.config.default_cell_capacity_grams))
        except Exception:
            pass
        return self.config.default_cell_capacity_grams

    def get_cell_initial_state(self, cell_id: int) -> Optional[dict]:
        """Return the current CellStateMessage dict for *cell_id*, or None."""
        if self.cell_state_manager is None:
            return None
        try:
            import datetime
            current_state = self.cell_state_manager.get_cell_state(cell_id)
            if current_state is None:
                return None
            weight = None
            if self.cell_weight_monitor is not None:
                weight = self.cell_weight_monitor.get_cell_weight(cell_id)
            return {
                "cell_id": cell_id,
                "current_state": str(current_state),
                "previous_state": None,
                "reason": "Initial state on subscription",
                "weight": weight,
                "timestamp": datetime.datetime.now().isoformat(),
                "details": {},
            }
        except Exception:
            return None

    def get_cell_glue_type(self, cell_id: int) -> Optional[str]:
        """Return the glue type string for *cell_id*, or None."""
        if self.glue_cell_manager is None:
            return None
        try:
            cell = self.glue_cell_manager.getCellById(cell_id)
            if cell is not None and hasattr(cell, "glueType"):
                return cell.glueType
        except Exception:
            pass
        return None

    def get_all_glue_types(self) -> list[str]:
        """Return all known glue-type names (for the setup wizard)."""
        if self.glue_cell_manager is None:
            return []
        try:
            return [c.glueType for c in self.glue_cell_manager.getAllCells() if hasattr(c, "glueType")]
        except Exception:
            return []
