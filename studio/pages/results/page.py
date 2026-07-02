from tkinter import ttk

try:
    from ..base import Page
except ImportError:
    from pages.base import Page


class ResultsPage(Page):
    title = "Results"
    subtitle = "Results workspace shell."

    def __init__(self, parent) -> None:
        super().__init__(parent)

        ttk.Label(
            self.content,
            text="Results",
            style="SurfaceTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.content,
            text="Result views will be added after the research architecture exists.",
            style="SurfaceBody.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

