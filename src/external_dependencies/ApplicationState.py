from enum import Enum


class ApplicationState(Enum):
    INITIALIZING = "initializing"
    IDLE = "idle"
    PAUSED = "paused"
    STOPPED = "stopped"
    STARTED = "started"
    ERROR = "error"
    CALIBRATING = "calibrating"