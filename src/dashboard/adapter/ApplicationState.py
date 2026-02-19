from enum import Enum


class ApplicationState(Enum):
    """Base application states that all robot applications should support"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    PAUSED = "paused"
    STOPPED = "stopped"
    STARTED = "started"
    ERROR = "error"
    CALIBRATING = "calibrating"