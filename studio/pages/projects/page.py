from tkinter import messagebox, ttk

try:
    from ..base import Page
    from .dialogs import NewProjectDialog, RenameProjectDialog
    from .widgets import ProjectCard, ScrollFrame
    from ...utils.validators import ValidationError
except ImportError:
    from pages.base import Page
    from pages.projects.dialogs import NewProjectDialog, RenameProjectDialog
    from pages.projects.widgets import ProjectCard, ScrollFrame
    from utils.validators import ValidationError


class ProjectsPage(Page):
    title = "Projects"
    subtitle = "Create, open, and manage research projects."

    def __init__(self, parent, project_service, on_project_opened=None) -> None:
        super().__init__(parent)
        self.project_service = project_service
        self.on_project_opened = on_project_opened
        self.projects = []

        self.content.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self.content, style="Surface.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        toolbar.columnconfigure(1, weight=1)

        ttk.Button(
            toolbar,
            text="+ New Project",
            style="Studio.TButton",
            command=self.open_new_project_dialog,
        ).grid(row=0, column=0, sticky="w")

        self.status = ttk.Label(toolbar, text="", style="SurfaceBody.TLabel")
        self.status.grid(row=0, column=1, sticky="e")

        self.project_list = ScrollFrame(self.content)
        self.project_list.grid(row=1, column=0, sticky="nsew")

        self.load_projects()

    def load_projects(self) -> None:
        try:
            self.projects = self.project_service.list_projects()
        except OSError as error:
            messagebox.showerror("Projects", str(error))
            self.projects = []
        self.render_projects()

    def render_projects(self) -> None:
        for child in self.project_list.inner.winfo_children():
            child.destroy()

        if not self.projects:
            ttk.Label(
                self.project_list.inner,
                text="No projects yet.",
                style="SurfaceBody.TLabel",
            ).grid(row=0, column=0, sticky="w", padx=2, pady=2)
        else:
            for index, project in enumerate(self.projects):
                card = ProjectCard(
                    self.project_list.inner,
                    project,
                    on_open=self.open_project,
                    on_rename=self.open_rename_project_dialog,
                    on_delete=self.confirm_delete_project,
                )
                card.grid(row=index, column=0, sticky="ew", pady=(0, 12))
                self.project_list.inner.columnconfigure(0, weight=1)

        count = len(self.projects)
        self.status.configure(text=f"{count} project{'s' if count != 1 else ''}")

    def open_new_project_dialog(self) -> None:
        dialog = NewProjectDialog(self)
        self.wait_window(dialog)
        if dialog.result is None:
            return

        try:
            self.project_service.create_project(dialog.result["name"], dialog.result["description"])
        except (OSError, ValidationError) as error:
            messagebox.showerror("New Project", str(error))
            return

        self.load_projects()

    def open_project(self, project) -> None:
        try:
            opened_project = self.project_service.open_project(project.name)
        except (OSError, ValidationError) as error:
            messagebox.showerror("Open Project", str(error))
            return

        if self.on_project_opened is not None:
            self.on_project_opened(opened_project)
        self.load_projects()

    def open_rename_project_dialog(self, project) -> None:
        dialog = RenameProjectDialog(self, project)
        self.wait_window(dialog)
        if dialog.result is None:
            return

        try:
            self.project_service.rename_project(
                project.name,
                dialog.result["name"],
                description=dialog.result["description"],
            )
        except (OSError, ValidationError) as error:
            messagebox.showerror("Rename Project", str(error))
            return

        self.load_projects()

    def confirm_delete_project(self, project) -> None:
        confirmed = messagebox.askyesno(
            "Delete Project",
            f"Delete '{project.name}'? This removes the project folder.",
        )
        if not confirmed:
            return

        try:
            self.project_service.delete_project(project.name)
        except (OSError, ValidationError) as error:
            messagebox.showerror("Delete Project", str(error))
            return

        self.load_projects()

    def refresh_theme(self, palette: dict[str, str]) -> None:
        super().refresh_theme(palette)
        if hasattr(self, "project_list"):
            self.project_list.refresh_theme(palette)
