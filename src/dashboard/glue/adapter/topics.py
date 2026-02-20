"""
Centralized Topic Definitions for the glue dispensing application.
"""

from enum import Enum


class TopicCategory:
    @classmethod
    def all_topics(cls) -> list[str]:
        return [getattr(cls, attr) for attr in dir(cls)
                if not attr.startswith('_') and not callable(getattr(cls, attr))]


class SystemTopics(TopicCategory):
    SYSTEM_STATE = "system/state"
    SYSTEM_MODE_CHANGE = "system/mode-change"
    CURRENT_PROCESS = "system/current-process"
    OPERATION_STATE = "application/operation/state"
    APPLICATION_STATE = "application/state"


class RobotTopics(TopicCategory):
    SERVICE_STATE = "robot-service/state"
    TRAJECTORY_START = "robot/trajectory/start"
    TRAJECTORY_STOP = "robot/trajectory/stop"
    TRAJECTORY_BREAK = "robot/trajectory/break"
    TRAJECTORY_UPDATE_IMAGE = "robot/trajectory/updateImage"
    TRAJECTORY_POINT = "robot/trajectory/point"
    ROBOT_CALIBRATION_LOG = "robot/calibration/log"
    ROBOT_CALIBRATION_START = "robot/calibration/start"
    ROBOT_CALIBRATION_STOP = "robot/calibration/stop"
    ROBOT_CALIBRATION_IMAGE = "robot/calibration/image"
    ROBOT_STATE = "robot/state"


class VisionTopics(TopicCategory):
    SERVICE_STATE = "vision-service/state"
    LATEST_IMAGE = "vision-system/latest-image"
    FPS = "vision-system/fps"
    CALIBRATION_IMAGE_CAPTURED = "vision-system/calibration-image-captured"
    BRIGHTNESS_REGION = "vision-system/brightness-region"
    THRESHOLD_REGION = "vision-system/threshold"
    CALIBRATION_FEEDBACK = "vision-system/calibration-feedback"
    THRESHOLD_IMAGE = "vision-system/threshold-image"
    AUTO_BRIGHTNESS = "vision-system/auto-brightness"
    AUTO_BRIGHTNESS_START = "vison-auto-brightness"
    AUTO_BRIGHTNESS_STOP = "vison-auto-brightness"
    TRANSFORM_TO_CAMERA_POINT = "vision-system/transform-to-camera-point"


class GlueCellTopics(TopicCategory):
    CELL_1_WEIGHT = "glue/cell/1/weight"
    CELL_2_WEIGHT = "glue/cell/2/weight"
    CELL_3_WEIGHT = "glue/cell/3/weight"
    CELL_1_STATE = "glue/cell/1/state"
    CELL_2_STATE = "glue/cell/2/state"
    CELL_3_STATE = "glue/cell/3/state"
    CELL_1_GLUE_TYPE = "glue/cell/1/glue-type"
    CELL_2_GLUE_TYPE = "glue/cell/2/glue-type"
    CELL_3_GLUE_TYPE = "glue/cell/3/glue-type"

    @staticmethod
    def cell_weight(cell_id: int) -> str:
        return f"glue/cell/{cell_id}/weight"

    @staticmethod
    def cell_state(cell_id: int) -> str:
        return f"glue/cell/{cell_id}/state"

    @staticmethod
    def cell_glue_type(cell_id: int) -> str:
        return f"glue/cell/{cell_id}/glue-type"


class SystemTopicsExtended(TopicCategory):
    pass


class UITopics(TopicCategory):
    LANGUAGE_CHANGED = "Language"

