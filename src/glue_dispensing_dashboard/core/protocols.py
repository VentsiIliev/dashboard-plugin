"""
Protocol classes (structural interfaces) for every external dependency.

No other dashboard file needs to import from communication_layer,
modules.shared, or frontend.core at module level — these protocols
define the shape of what's expected.

Message schemas
---------------
CellWeightMessage : plain float
    Grams of glue remaining in the cell (e.g. 3421.5).

CellStateMessage : dict
    {
        "cell_id":       int,
        "current_state": str,          # "ready" | "low_weight" | "empty" | "error" | ...
        "previous_state": str | None,
        "reason":        str,
        "weight":        float | None,
        "timestamp":     str,          # ISO-8601
        "details":       dict,
    }
"""

from __future__ import annotations

from typing import Optional, runtime_checkable, Protocol


@runtime_checkable
class ControllerServiceProtocol(Protocol):
    def send_request(self, endpoint: str, payload: Optional[dict] = None) -> Optional[dict]:
        ...


@runtime_checkable
class ControllerProtocol(Protocol):
    controller_service: ControllerServiceProtocol

    def handle(self, endpoint: str, payload: Optional[dict] = None) -> None:
        ...


@runtime_checkable
class GlueCellProtocol(Protocol):
    id: int
    glueType: str
    capacity: float


@runtime_checkable
class GlueCellManagerProtocol(Protocol):
    def getCellById(self, cell_id: int) -> Optional[GlueCellProtocol]:
        ...

    def getAllCells(self) -> list[GlueCellProtocol]:
        ...


@runtime_checkable
class CellStateManagerProtocol(Protocol):
    def get_cell_state(self, cell_id: int) -> Optional[str]:
        ...


@runtime_checkable
class CellWeightMonitorProtocol(Protocol):
    def get_cell_weight(self, cell_id: int) -> Optional[float]:
        ...
