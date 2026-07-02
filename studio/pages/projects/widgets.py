from datetime import datetime
import tkinter as tk
from tkinter import ttk


def format_created_at(value: str) -> str:
    try:
        created_at = datetime.fromisoformat(value)
    except ValueError:
        return value or "Unknown"

    today = datetime.now().date()
    if created_at.date() == today:
        return "Today"
    return created_at.strftime("%Y-%m-%d")


class ProjectCard(ttk.Frame):
    def __init__(self, parent, project, on_open, on_rename, on_delete) -> None:
        super().__init__(parent, style="Card.TFrame", padding=18)
        self.project = project
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text=project.name, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text=project.description or "No description",
            style="CardBody.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 14))

        ttk.Separator(self).grid(row=2, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(
            self,
            text=f"Created: {format_created_at(project.created_at)}",
            style="CardBody.TLabel",
        ).grid(row=3, column=0, sticky="w")
        ttk.Label(
            self,
            text=f"Status : {project.status.title()}",
            style="CardBody.TLabel",
        ).grid(row=4, column=0, sticky="w", pady=(4, 12))

        ttk.Separator(self).grid(row=5, column=0, sticky="ew", pady=(0, 12))

        actions = ttk.Frame(self, style="Card.TFrame")
        actions.grid(row=6, column=0, sticky="w")
        ttk.Button(actions, text="Open", style="Studio.TButton", command=lambda: on_open(project)).grid(row=0, column=0)
        ttk.Button(actions, text="Rename", style="Studio.TButton", command=lambda: on_rename(project)).grid(
            row=0,
            column=1,
            padx=8,
        )
        ttk.Button(actions, text="Delete", style="Studio.TButton", command=lambda: on_delete(project)).grid(row=0, column=2)


class ScrollFrame(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent, style="Surface.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.inner = ttk.Frame(self.canvas, style="Surface.TFrame")
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._sync_width)

    def refresh_theme(self, palette: dict[str, str]) -> None:
        self.canvas.configure(background=palette["surface"])

    def _sync_scroll_region(self, _event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_width(self, event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

