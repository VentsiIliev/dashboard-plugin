"""
Centralized import fallback chains for the glue dashboard plugin.
"""

try:
    from communication_layer.api.v1.topics import GlueCellTopics
except ImportError:
    from ..adapter.topics import GlueCellTopics

try:
    from communication_layer.api.v1.topics import RobotTopics
except ImportError:
    from ..adapter.topics import RobotTopics

try:
    from communication_layer.api.v1.topics import VisionTopics
except ImportError:
    from ..adapter.topics import VisionTopics

try:
    from communication_layer.api.v1.topics import SystemTopics
except ImportError:
    from ..adapter.topics import SystemTopics

try:
    from communication_layer.api.v1.topics import UITopics
except ImportError:
    from ..adapter.topics import UITopics


__all__ = [
    "GlueCellTopics",
    "RobotTopics",
    "VisionTopics",
    "SystemTopics",
    "UITopics",
]

