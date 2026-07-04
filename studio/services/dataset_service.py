try:
    from ..managers import DatasetManager
    from ..models import Dataset, Project
    from ..workflow import WorkflowManager
    from .project_service import ProjectService
except ImportError:
    from managers import DatasetManager
    from models import Dataset, Project
    from workflow import WorkflowManager
    from services.project_service import ProjectService


class DatasetService:
    def __init__(
        self,
        manager: DatasetManager | None = None,
        project_service: ProjectService | None = None,
        workflow_manager: WorkflowManager | None = None,
    ) -> None:
        self.workflow_manager = workflow_manager or WorkflowManager(manager or DatasetManager())
        self.project_service = project_service or ProjectService()

    def list_datasets(self) -> list[Dataset]:
        return self.workflow_manager.scan_datasets()

    def get_dataset(self, name: str) -> Dataset:
        return self.workflow_manager.load_dataset(name)

    def get_statistics(self, name: str) -> dict:
        return self.workflow_manager.get_dataset_statistics(name)

    def validate_dataset(self, name: str) -> dict:
        return self.workflow_manager.validate_dataset(name)

    def assign_dataset_to_project(self, project: Project, dataset_name: str) -> Project:
        updated_project = self.workflow_manager.assign_dataset_to_project(project, dataset_name)
        return self.project_service.update_project_metadata(updated_project)

    def add_progress_callback(self, callback) -> None:
        self.workflow_manager.add_progress_callback(callback)

    def add_completion_callback(self, callback) -> None:
        self.workflow_manager.add_completion_callback(callback)
