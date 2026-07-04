from dataclasses import dataclass
from enum import Enum


class ProgressStatus(str, Enum):
    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


@dataclass
class TaskProgress:
    task_name: str
    status: ProgressStatus
    message: str = ""
    percent: int = 0

