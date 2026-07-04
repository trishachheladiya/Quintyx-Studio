try:
    from ..managers import DatasetManager
    from ..models import Dataset, Project
    from .project_service import ProjectService
except ImportError:
    from managers import DatasetManager
    from models import Dataset, Project
    from services.project_service import ProjectService


class DatasetService:
    def __init__(self, manager: DatasetManager | None = None, project_service: ProjectService | None = None) -> None:
        self.manager = manager or DatasetManager()
        self.project_service = project_service or ProjectService()

    def list_datasets(self) -> list[Dataset]:
        return self.manager.scan_datasets()

    def get_dataset(self, name: str) -> Dataset:
        return self.manager.load_dataset(name, validate=True)

    def get_statistics(self, name: str) -> dict:
        return self.manager.get_statistics(name)

    def validate_dataset(self, name: str) -> dict:
        return self.manager.validate_dataset(name, update_metadata=True)

    def assign_dataset_to_project(self, project: Project, dataset_name: str) -> Project:
        updated_project = self.manager.assign_dataset_to_project(project, dataset_name)
        return self.project_service.update_project_metadata(updated_project)
