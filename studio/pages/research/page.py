from tkinter import ttk

try:
    from ..base import Page
except ImportError:
    from pages.base import Page


class ResearchPage(Page):
    title = "Research"
    subtitle = "Research workspace shell."

    def __init__(self, parent) -> None:
        super().__init__(parent)

        ttk.Label(
            self.content,
            text="Research",
            style="SurfaceTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.content,
            text="No research tools are implemented in Phase 1.",
            style="SurfaceBody.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

