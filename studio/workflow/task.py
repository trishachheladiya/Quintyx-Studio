from dataclasses import dataclass, field
from typing import Any, Callable

try:
    from .progress import ProgressStatus, TaskProgress
except ImportError:
    from progress import ProgressStatus, TaskProgress


ProgressCallback = Callable[[TaskProgress], None]


@dataclass
class Task:
    name: str
    status: ProgressStatus = ProgressStatus.QUEUED
    progress: int = 0
    result: Any = None
    error: str = ""
    callbacks: list[ProgressCallback] = field(default_factory=list)

    def add_progress_callback(self, callback: ProgressCallback) -> None:
        self.callbacks.append(callback)

    def emit(self, status: ProgressStatus, message: str = "", percent: int | None = None) -> None:
        self.status = status
        if percent is not None:
            self.progress = percent
        progress = TaskProgress(self.name, self.status, message, self.progress)
        for callback in self.callbacks:
            callback(progress)

    def run(self):
        raise NotImplementedError

    def execute(self):
        self.emit(ProgressStatus.RUNNING, f"{self.name} started", 0)
        try:
            self.result = self.run()
        except Exception as error:
            self.error = str(error)
            self.emit(ProgressStatus.FAILED, self.error, self.progress)
            raise
        self.emit(ProgressStatus.COMPLETED, f"{self.name} completed", 100)
        return self.result


class LoadDatasetTask(Task):
    def __init__(self, dataset_manager, dataset_name: str) -> None:
        super().__init__("Load Dataset")
        self.dataset_manager = dataset_manager
        self.dataset_name = dataset_name

    def run(self):
        self.emit(ProgressStatus.RUNNING, "Reading dataset CSV metadata", 25)
        dataset = self.dataset_manager.load_dataset(self.dataset_name, rebuild_metadata=True)
        self.emit(ProgressStatus.RUNNING, "Dataset metadata ready", 75)
        return dataset


class GenerateFeaturesTask(Task):
    def __init__(self) -> None:
        super().__init__("Generate Features")


class GenerateLabelsTask(Task):
    def __init__(self) -> None:
        super().__init__("Generate Labels")


class TrainModelTask(Task):
    def __init__(self) -> None:
        super().__init__("Train Model")


class ThresholdAnalysisTask(Task):
    def __init__(self) -> None:
        super().__init__("Threshold Analysis")


class BacktestTask(Task):
    def __init__(self) -> None:
        super().__init__("Backtest")


class GenerateReportTask(Task):
    def __init__(self) -> None:
        super().__init__("Generate Report")

