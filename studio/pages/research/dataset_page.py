from tkinter import messagebox, ttk

try:
    from ..projects.widgets import ScrollFrame
    from .dataset_card import DatasetCard
except ImportError:
    from pages.projects.widgets import ScrollFrame
    from pages.research.dataset_card import DatasetCard


class DatasetLibrary(ttk.Frame):
    def __init__(self, parent, dataset_service, get_current_project, set_current_project) -> None:
        super().__init__(parent, style="Surface.TFrame")
        self.dataset_service = dataset_service
        self.get_current_project = get_current_project
        self.set_current_project = set_current_project
        self.datasets = []
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="Dataset Library", style="SurfaceTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.project_label = ttk.Label(self, text="", style="SurfaceBody.TLabel")
        self.project_label.grid(row=0, column=1, sticky="e")

        self.dataset_list = ScrollFrame(self)
        self.dataset_list.grid(row=1, column=0, sticky="nsew", pady=(16, 0), padx=(0, 14))

        self.dashboard = ttk.Frame(self, style="Card.TFrame", padding=18)
        self.dashboard.grid(row=1, column=1, sticky="nsew", pady=(16, 0))
        self.dashboard.columnconfigure(0, weight=1)

        self.refresh_data()

    def refresh_data(self) -> None:
        try:
            self.datasets = self.dataset_service.list_datasets()
        except OSError as error:
            messagebox.showerror("Dataset Library", str(error))
            self.datasets = []

        self.render_cards()
        self.render_dashboard()

    def render_cards(self) -> None:
        for child in self.dataset_list.inner.winfo_children():
            child.destroy()

        if not self.datasets:
            ttk.Label(
                self.dataset_list.inner,
                text="No datasets available.",
                style="SurfaceBody.TLabel",
            ).grid(row=0, column=0, sticky="w")
            return

        for index, dataset in enumerate(self.datasets):
            card = DatasetCard(self.dataset_list.inner, dataset, self.select_dataset)
            card.grid(row=index, column=0, sticky="ew", pady=(0, 12))
            self.dataset_list.inner.columnconfigure(0, weight=1)

    def render_dashboard(self) -> None:
        for child in self.dashboard.winfo_children():
            child.destroy()

        project = self.get_current_project()
        if project is None:
            self.project_label.configure(text="No open project")
            ttk.Label(
                self.dashboard,
                text="Open a project to assign a dataset.",
                style="CardTitle.TLabel",
            ).grid(row=0, column=0, sticky="w")
            return

        self.project_label.configure(text=f"Project: {project.name}")
        ttk.Label(
            self.dashboard,
            text="Selected Dataset",
            style="CardTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        if not project.dataset:
            ttk.Label(
                self.dashboard,
                text="No dataset selected.",
                style="CardBody.TLabel",
            ).grid(row=1, column=0, sticky="w", pady=(8, 0))
            return

        try:
            statistics = self.dataset_service.get_statistics(project.dataset)
        except (OSError, ValueError) as error:
            ttk.Label(
                self.dashboard,
                text=f"Dataset reference could not be loaded: {error}",
                style="CardBody.TLabel",
            ).grid(row=1, column=0, sticky="w", pady=(8, 0))
            return

        for index, (label, value) in enumerate(statistics.items(), start=1):
            ttk.Label(
                self.dashboard,
                text=label,
                style="CardBody.TLabel",
            ).grid(row=index * 2 - 1, column=0, sticky="w", pady=(12 if index == 1 else 8, 0))
            ttk.Label(
                self.dashboard,
                text=str(value),
                style="CardTitle.TLabel",
            ).grid(row=index * 2, column=0, sticky="w")

    def select_dataset(self, dataset) -> None:
        project = self.get_current_project()
        if project is None:
            messagebox.showinfo("Dataset Library", "Open a project before selecting a dataset.")
            return

        try:
            updated_project = self.dataset_service.assign_dataset_to_project(project, dataset.name)
        except (OSError, ValueError) as error:
            messagebox.showerror("Dataset Library", str(error))
            return

        self.set_current_project(updated_project)
        self.refresh_data()

    def refresh_theme(self, palette: dict[str, str]) -> None:
        self.dataset_list.refresh_theme(palette)

