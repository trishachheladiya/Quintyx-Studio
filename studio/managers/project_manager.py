import json
from datetime import datetime
from pathlib import Path
import shutil

try:
    from ..models import Project
    from ..utils.filesystem import PROJECT_DIRECTORIES, PROJECT_METADATA_FILE
    from ..utils.validators import ValidationError, validate_project_name
except ImportError:
    from models import Project
    from utils.filesystem import PROJECT_DIRECTORIES, PROJECT_METADATA_FILE
    from utils.validators import ValidationError, validate_project_name


class ProjectManager:
    def __init__(self, projects_root: Path | None = None) -> None:
        if projects_root is None:
            projects_root = Path(__file__).resolve().parents[2] / "Projects"
        self.projects_root = projects_root

    def create_project(self, name: str, description: str) -> Project:
        project_name = validate_project_name(name)
        self.projects_root.mkdir(parents=True, exist_ok=True)
        project_path = self.projects_root / project_name

        if project_path.exists():
            raise ValidationError("A project with this name already exists.")

        created_at = self._timestamp()
        project_path.mkdir()
        for directory in PROJECT_DIRECTORIES:
            (project_path / directory).mkdir()

        project = Project(
            name=project_name,
            description=description.strip(),
            path=str(project_path),
            version="1.0",
            created_at=created_at,
            last_opened=created_at,
            status="created",
            dataset=None,
        )
        self._write_metadata(project)
        return project

    def delete_project(self, name: str) -> None:
        project = self.load_project(name)
        shutil.rmtree(project.path)

    def rename_project(self, current_name: str, new_name: str) -> Project:
        project = self.load_project(current_name)
        new_project_name = validate_project_name(new_name)
        new_path = self.projects_root / new_project_name

        if new_path.exists() and new_project_name != project.name:
            raise ValidationError("A project with this name already exists.")

        old_path = Path(project.path)
        if new_project_name != project.name:
            old_path.rename(new_path)
            project.path = str(new_path)

        project.name = new_project_name
        project.last_opened = self._timestamp()
        self._write_metadata(project)
        return project

    def open_project(self, name: str) -> Project:
        project = self.load_project(name)
        project.last_opened = self._timestamp()
        self._write_metadata(project)
        return project

    def load_project(self, name: str) -> Project:
        project_name = validate_project_name(name)
        project_path = self.projects_root / project_name
        metadata_path = project_path / PROJECT_METADATA_FILE

        if not metadata_path.exists():
            raise FileNotFoundError(f"Project metadata not found: {project_name}")

        with metadata_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        project = Project.from_dict(data, str(project_path))
        self.validate_structure(project)
        return project

    def scan_projects(self) -> list[Project]:
        if not self.projects_root.exists():
            self.projects_root.mkdir(parents=True, exist_ok=True)
            return []

        projects: list[Project] = []
        for path in sorted(self.projects_root.iterdir(), key=lambda item: item.name.lower()):
            if path.is_dir() and (path / PROJECT_METADATA_FILE).exists():
                try:
                    projects.append(self.load_project(path.name))
                except (OSError, json.JSONDecodeError, ValidationError):
                    continue
        return projects

    def update_metadata(self, project: Project) -> Project:
        self.validate_structure(project)
        self._write_metadata(project)
        return project

    def validate_structure(self, project: Project) -> bool:
        project_path = Path(project.path)
        if not project_path.exists() or not project_path.is_dir():
            raise FileNotFoundError(f"Project folder not found: {project.name}")
        if not (project_path / PROJECT_METADATA_FILE).exists():
            raise FileNotFoundError(f"Project metadata not found: {project.name}")
        for directory in PROJECT_DIRECTORIES:
            child = project_path / directory
            if not child.exists() or not child.is_dir():
                raise FileNotFoundError(f"Project folder is incomplete: {directory}")
        return True

    def _write_metadata(self, project: Project) -> None:
        metadata_path = Path(project.path) / PROJECT_METADATA_FILE
        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(project.to_metadata(), file, indent=2)

    def _timestamp(self) -> str:
        return datetime.now().replace(microsecond=0).isoformat()
