import threading

try:
    from ..managers import DatasetManager
    from .progress import TaskProgress
    from .task import GenerateFeaturesTask, LoadDatasetTask, ProgressCallback, Task
except ImportError:
    from managers import DatasetManager
    from workflow.progress import TaskProgress
    from workflow.task import GenerateFeaturesTask, LoadDatasetTask, ProgressCallback, Task


class WorkflowManager:
    def __init__(self, dataset_manager: DatasetManager | None = None) -> None:
        self.dataset_manager = dataset_manager or DatasetManager()
        self.progress_callbacks: list[ProgressCallback] = []
        self.completion_callbacks: list[ProgressCallback] = []

    def add_progress_callback(self, callback: ProgressCallback) -> None:
        self.progress_callbacks.append(callback)

    def add_completion_callback(self, callback: ProgressCallback) -> None:
        self.completion_callbacks.append(callback)

    def scan_datasets(self):
        return self.dataset_manager.scan_datasets()

    def load_dataset(self, dataset_name: str):
        task = LoadDatasetTask(self.dataset_manager, dataset_name)
        return self.execute_task(task)

    def get_dataset_statistics(self, dataset_name: str) -> dict:
        return self.dataset_manager.get_statistics(dataset_name)

    def validate_dataset(self, dataset_name: str) -> dict:
        return self.dataset_manager.validate_dataset(dataset_name, update_metadata=True)

    def assign_dataset_to_project(self, project, dataset_name: str):
        self.load_dataset(dataset_name)
        return self.dataset_manager.assign_dataset_to_project(project, dataset_name)

    def create_feature_generation_task(self, project_path, dataset_path, selected_features, feature_engine):
        return GenerateFeaturesTask(project_path=project_path, dataset_path=dataset_path, selected_features=selected_features, feature_engine=feature_engine)

    def execute_task(self, task: Task):
        task.add_progress_callback(self._emit_progress)
        result = task.execute()
        self._emit_completion(TaskProgress(task.name, task.status, "Task completed", task.progress))
        return result

    def execute_task_async(self, task: Task, on_done=None):
        def runner() -> None:
            try:
                result = self.execute_task(task)
            except Exception as error:
                self._emit_completion(TaskProgress(task.name, task.status, str(error), task.progress))
                if on_done is not None:
                    on_done(None, error)
                return
            if on_done is not None:
                on_done(result, None)

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        return thread

    def _emit_progress(self, progress: TaskProgress) -> None:
        for callback in self.progress_callbacks:
            callback(progress)

    def _emit_completion(self, progress: TaskProgress) -> None:
        for callback in self.completion_callbacks:
            callback(progress)

