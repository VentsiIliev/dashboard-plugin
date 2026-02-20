"""
GlueDashboardConfig — configuration specific to the glue dispensing dashboard.
"""

from __future__ import annotations
from dataclasses import dataclass

try:
    from dashboard.core.config import DashboardConfig
except ImportError:
    from src.dashboard.config import DashboardConfig


@dataclass
class GlueDashboardConfig(DashboardConfig):
    """
    Configuration for the glue dispensing dashboard.

    Extends DashboardConfig with glue-specific defaults.
    Override any field to customize the glue dashboard layout.
    """

    # THIS CURRENTLY INHERITS THE DEFAULT VALUES FROM DashboardConfig !
    # AND EXTENDS IT BY ADDING GLUE-SPECIFIC FIELDS BELOW.
    default_cell_capacity_grams: float = 5000.0



