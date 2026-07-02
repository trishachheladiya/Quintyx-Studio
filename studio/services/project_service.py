try:
    from ..managers import ProjectManager
    from ..models import Project
    from ..utils.validators import ValidationError, validate_project_name
except ImportError:
    from managers import ProjectManager
    from models import Project
    from utils.validators import ValidationError, validate_project_name


class ProjectService:
    def __init__(self, manager: ProjectManager | None = None) -> None:
        self.manager = manager or ProjectManager()

    def create_project(self, name: str, description: str) -> Project:
        self._ensure_unique_project_name(name)
        return self.manager.create_project(name, description)

    def delete_project(self, name: str) -> None:
        self.manager.delete_project(name)

    def rename_project(self, current_name: str, new_name: str, description: str | None = None) -> Project:
        normalized_new_name = validate_project_name(new_name)
        normalized_current_name = validate_project_name(current_name)
        if normalized_new_name != normalized_current_name:
            self._ensure_unique_project_name(normalized_new_name)
        project = self.manager.rename_project(normalized_current_name, normalized_new_name)
        if description is not None:
            project.description = description.strip()
            project = self.manager.update_metadata(project)
        return project

    def open_project(self, name: str) -> Project:
        return self.manager.open_project(name)

    def list_projects(self) -> list[Project]:
        return self.manager.scan_projects()

    def update_project_metadata(self, project: Project) -> Project:
        return self.manager.update_metadata(project)

    def _ensure_unique_project_name(self, name: str) -> None:
        normalized_name = validate_project_name(name)
        existing_names = {project.name.lower() for project in self.manager.scan_projects()}
        if normalized_name.lower() in existing_names:
            raise ValidationError("A project with this name already exists.")
