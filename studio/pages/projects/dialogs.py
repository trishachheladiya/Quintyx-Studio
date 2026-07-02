import tkinter as tk
from tkinter import ttk

try:
    from ...utils.validators import ValidationError, validate_project_name
except ImportError:
    from utils.validators import ValidationError, validate_project_name


class ProjectDialog(tk.Toplevel):
    def __init__(self, parent, title: str, submit_label: str, initial_name: str = "", initial_description: str = "") -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result: dict[str, str] | None = None

        self.name_var = tk.StringVar(value=initial_name)
        self.description_text: tk.Text | None = None
        self.error_var = tk.StringVar(value="")

        body = ttk.Frame(self, style="App.TFrame", padding=20)
        body.grid(row=0, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)

        ttk.Label(body, text="Project name", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        name_entry = ttk.Entry(body, textvariable=self.name_var, width=44)
        name_entry.grid(row=1, column=0, sticky="ew", pady=(6, 14))

        ttk.Label(body, text="Description", style="Body.TLabel").grid(row=2, column=0, sticky="w")
        self.description_text = tk.Text(body, width=44, height=5, wrap="word")
        self.description_text.grid(row=3, column=0, sticky="ew", pady=(6, 14))
        self.description_text.insert("1.0", initial_description)

        ttk.Label(body, textvariable=self.error_var, style="Error.TLabel").grid(row=4, column=0, sticky="w")

        actions = ttk.Frame(body, style="App.TFrame")
        actions.grid(row=5, column=0, sticky="e", pady=(16, 0))
        ttk.Button(actions, text="Cancel", style="Studio.TButton", command=self.cancel).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions, text=submit_label, style="Studio.TButton", command=self.submit).grid(row=0, column=1)

        self.bind("<Return>", lambda _event: self.submit())
        self.bind("<Escape>", lambda _event: self.cancel())
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        name_entry.focus_set()

    def submit(self) -> None:
        try:
            name = validate_project_name(self.name_var.get())
        except ValidationError as error:
            self.error_var.set(str(error))
            return

        description = ""
        if self.description_text is not None:
            description = self.description_text.get("1.0", "end").strip()

        self.result = {"name": name, "description": description}
        self.destroy()

    def cancel(self) -> None:
        self.result = None
        self.destroy()


class NewProjectDialog(ProjectDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, "New Project", "Create")


class RenameProjectDialog(ProjectDialog):
    def __init__(self, parent, project) -> None:
        super().__init__(
            parent,
            "Rename Project",
            "Rename",
            initial_name=project.name,
            initial_description=project.description,
        )

