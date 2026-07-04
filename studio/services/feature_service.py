from __future__ import annotations

from pathlib import Path

try:
    from ..features import FeatureEngine
    from ..workflow import WorkflowManager
except ImportError:
    from features import FeatureEngine
    from workflow import WorkflowManager


class FeatureService:
    def __init__(self, workflow_manager: WorkflowManager | None = None) -> None:
        self.workflow_manager = workflow_manager or WorkflowManager()
        self.feature_engine = FeatureEngine()

    def generate_features(self, project_path: str | Path, dataset_path: str | Path, selected_features: list[str], on_complete=None):
        task = self.workflow_manager.create_feature_generation_task(
            project_path=project_path,
            dataset_path=dataset_path,
            selected_features=selected_features,
            feature_engine=self.feature_engine,
        )
        return self.workflow_manager.execute_task_async(task, on_done=on_complete)

    def add_progress_callback(self, callback) -> None:
        self.workflow_manager.add_progress_callback(callback)

    def add_completion_callback(self, callback) -> None:
        self.workflow_manager.add_completion_callback(callback)
