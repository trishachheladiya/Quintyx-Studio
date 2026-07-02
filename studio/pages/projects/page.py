from tkinter import ttk

try:
    from ..base import Page
except ImportError:
    from pages.base import Page


class ProjectsPage(Page):
    title = "Projects"
    subtitle = "Project workspace shell."

    def __init__(self, parent) -> None:
        super().__init__(parent)

        ttk.Label(
            self.content,
            text="Projects",
            style="SurfaceTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.content,
            text="Project architecture will live here in a later phase.",
            style="SurfaceBody.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

