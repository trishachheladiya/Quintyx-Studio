from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pandas as pd

try:
    from ..features.feature_engine import FeatureEngine
    from .progress import ProgressStatus, TaskProgress
except ImportError:
    from features.feature_engine import FeatureEngine
    from workflow.progress import ProgressStatus, TaskProgress


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
    def __init__(self, project_path: str | Path | None = None, dataset_path: str | Path | None = None, selected_features: list[str] | None = None, feature_engine=None) -> None:
        super().__init__("Generate Features")
        self.project_path = Path(project_path) if project_path is not None else None
        self.dataset_path = Path(dataset_path) if dataset_path is not None else None
        self.selected_features = selected_features or []
        self.feature_engine = feature_engine or FeatureEngine()

    def run(self):
        if self.project_path is None or self.dataset_path is None:
            raise ValueError("Project path and dataset path are required")
        if not self.selected_features:
            raise ValueError("At least one feature must be selected")

        self.emit(ProgressStatus.RUNNING, "Preparing feature generation", 10)
        features_frame = self.feature_engine.generate_features(
            self.dataset_path,
            self.selected_features,
            progress_callback=self._report_feature_progress,
        )
        output_dir = self.project_path / "features"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "features.csv"

        self.emit(ProgressStatus.RUNNING, "Saving engineered features", 80)
        features_frame.to_csv(output_path, index=False)

        result = {
            "output_path": str(output_path),
            "rows": int(len(features_frame)),
            "generated_features": int(len(self.selected_features)),
            "preview": features_frame.head(10).to_dict(orient="records"),
        }
        return result

    def _report_feature_progress(self, feature_name: str, index: int, total: int) -> None:
        percent = int(10 + (index / max(total, 1)) * 70)
        self.emit(ProgressStatus.RUNNING, f"Calculating {feature_name}", percent)


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

