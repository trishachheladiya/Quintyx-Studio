from dataclasses import dataclass, field

try:
    from .task import Task
except ImportError:
    from task import Task


@dataclass
class Workflow:
    name: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

