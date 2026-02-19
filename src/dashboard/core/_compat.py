"""
Centralized import fallback chains for the dashboard plugin.

All triple-try/except ImportError chains for external dependencies live here.
Other files import from this module instead of repeating the fallback logic.
"""

try:
    from communication_layer.api.v1.topics import GlueCellTopics
except ImportError:
    try:
        from src.dashboard.adapter.topics import GlueCellTopics
    except ImportError:
        from src.dashboard.adapter.topics import GlueCellTopics

try:
    from communication_layer.api.v1.topics import RobotTopics
except ImportError:
    try:
        from src.dashboard.adapter.topics import RobotTopics
    except ImportError:
        from src.dashboard.adapter.topics import RobotTopics

try:
    from communication_layer.api.v1.topics import VisionTopics
except ImportError:
    try:
        from src.dashboard.adapter.topics import VisionTopics
    except ImportError:
        from src.dashboard.adapter.topics import VisionTopics

try:
    from communication_layer.api.v1.topics import SystemTopics
except ImportError:
    try:
        from src.dashboard.adapter.topics import SystemTopics
    except ImportError:
        from src.dashboard.adapter.topics import SystemTopics

try:
    from communication_layer.api.v1.topics import UITopics
except ImportError:
    try:
        from src.dashboard.adapter.topics import UITopics
    except ImportError:
        from src.dashboard.adapter.topics import UITopics


__all__ = [
    "GlueCellTopics",
    "RobotTopics",
    "VisionTopics",
    "SystemTopics",
    "UITopics",

]
