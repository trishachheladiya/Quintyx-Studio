import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from ..projects.widgets import ScrollFrame
    from ...features import FeatureRegistry
    from .dataset_card import DatasetCard
except ImportError:
    from pages.projects.widgets import ScrollFrame
    from features import FeatureRegistry
    from pages.research.dataset_card import DatasetCard


class DatasetLibrary(ttk.Frame):
    def __init__(self, parent, dataset_service, feature_service, get_current_project, set_current_project) -> None:
        super().__init__(parent, style="Surface.TFrame")
        self.dataset_service = dataset_service
        self.feature_service = feature_service
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

        self.feature_panel = ttk.Frame(self, style="Card.TFrame", padding=18)
        self.feature_panel.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(18, 0))
        self.feature_panel.columnconfigure(0, weight=1)
        ttk.Label(self.feature_panel, text="Feature Selection", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.feature_registry = FeatureRegistry()
        self.feature_vars: dict[str, tk.BooleanVar] = {}
        self.feature_checkbuttons: list[ttk.Checkbutton] = []
        row_index = 1
        for category in ("Trend", "Momentum", "Volatility", "Returns", "Price Structure", "Price Action", "Time"):
            ttk.Label(self.feature_panel, text=category, style="CardBody.TLabel").grid(row=row_index, column=0, sticky="w", pady=(12, 4))
            row_index += 1
            for definition in sorted(self.feature_registry.get_definitions_by_category().get(category, []), key=lambda item: item.name):
                variable = tk.BooleanVar(value=definition.name in {"EMA20", "EMA50", "RSI14", "ATR14", "Return1", "Body", "Hour"})
                self.feature_vars[definition.name] = variable
                checkbutton = ttk.Checkbutton(self.feature_panel, text=definition.name, variable=variable)
                checkbutton.grid(row=row_index, column=0, sticky="w", padx=(12, 0))
                self.feature_checkbuttons.append(checkbutton)
                row_index += 1

        self.generate_button = ttk.Button(self.feature_panel, text="Generate Features", style="Studio.TButton", command=self.generate_features)
        self.generate_button.grid(row=row_index, column=0, sticky="w", pady=(14, 0))

        self.preview_frame = ttk.Frame(self, style="Card.TFrame", padding=18)
        self.preview_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(14, 0))
        self.preview_frame.columnconfigure(0, weight=1)
        ttk.Label(self.preview_frame, text="Generation Preview", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.preview_text = tk.Text(self.preview_frame, height=10, wrap="none", borderwidth=0, highlightthickness=0)
        self.preview_text.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.preview_scrollbar = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_scrollbar.grid(row=1, column=1, sticky="ns")
        self.preview_text.configure(yscrollcommand=self.preview_scrollbar.set)
        self.preview_frame.grid_remove()

        self.progress_frame = ttk.Frame(self, style="Surface.TFrame")
        self.progress_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self.progress_frame.columnconfigure(0, weight=1)
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="",
            style="SurfaceBody.TLabel",
        )
        self.progress_label.grid(row=0, column=0, sticky="w")
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode="determinate",
            maximum=100,
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.progress_frame.grid_remove()

        self.dataset_service.add_progress_callback(self._on_task_progress)
        self.dataset_service.add_completion_callback(self._on_task_completion)

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

    def generate_features(self) -> None:
        project = self.get_current_project()
        if project is None:
            messagebox.showinfo("Feature Generation", "Open a project before generating features.")
            return
        if not project.dataset:
            messagebox.showinfo("Feature Generation", "Select a dataset before generating features.")
            return

        selected_features = [name for name, variable in self.feature_vars.items() if variable.get()]
        if not selected_features:
            messagebox.showinfo("Feature Generation", "Select at least one feature to generate.")
            return

        self.generate_button.configure(state="disabled")
        self.preview_frame.grid_remove()
        self.progress_frame.grid()
        self.progress_label.configure(text="Queued: waiting for workflow")
        self.progress_bar["value"] = 0

        try:
            self.feature_service.generate_features(
                project_path=project.path,
                dataset_path=self.dataset_service.get_dataset(project.dataset).path,
                selected_features=selected_features,
                on_complete=self._on_generation_complete,
            )
        except (OSError, ValueError) as error:
            self.generate_button.configure(state="normal")
            self.progress_frame.grid_remove()
            messagebox.showerror("Feature Generation", str(error))
            return

        self.progress_label.configure(text="Queued: workflow started")

    def _on_generation_complete(self, result, error) -> None:
        def update_ui() -> None:
            self.generate_button.configure(state="normal")
            if error:
                self.progress_frame.grid_remove()
                messagebox.showerror("Feature Generation", str(error))
                return

            self.progress_frame.grid_remove()
            self.preview_frame.grid()
            self.preview_text.delete("1.0", tk.END)
            output_path = Path(result["output_path"]) if result else None
            if output_path and output_path.exists():
                self._render_preview(output_path)
                self.progress_label.configure(text=f"Completed: {result['rows']} rows -> {result['generated_features']} features")
            else:
                self.preview_text.insert("1.0", "No preview available.")

        self.after(0, update_ui)

    def _render_preview(self, output_path: Path) -> None:
        try:
            with output_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                rows = list(reader)
        except OSError:
            self.preview_text.insert("1.0", "Preview unavailable.")
            return

        if len(rows) <= 1:
            self.preview_text.insert("1.0", "No data rows available.")
            return

        preview_rows = rows[:11]
        text = "\n".join("\t".join(row) for row in preview_rows)
        self.preview_text.insert("1.0", text)

    def refresh_theme(self, palette: dict[str, str]) -> None:
        self.dataset_list.refresh_theme(palette)

    def _on_task_progress(self, progress) -> None:
        self.after(0, lambda: self._update_progress(progress))

    def _on_task_completion(self, progress) -> None:
        self.after(0, lambda: self._update_progress(progress, completed=True))

    def _update_progress(self, progress, completed: bool = False) -> None:
        self.progress_frame.grid()
        self.progress_label.configure(text=f"{progress.task_name}: {progress.message} ({progress.status.value})")
        self.progress_bar["value"] = progress.percent
        if completed:
            self.after(3000, self._hide_progress)

    def _hide_progress(self) -> None:
        self.progress_frame.grid_remove()
        self.progress_bar["value"] = 0
        self.progress_label.configure(text="")
