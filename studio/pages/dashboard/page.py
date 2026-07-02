from tkinter import ttk

try:
    from ..base import Page
except ImportError:
    from pages.base import Page


class DashboardPage(Page):
    title = "Dashboard"
    subtitle = "A clear starting point for the studio."

    def __init__(self, parent) -> None:
        super().__init__(parent)

        ttk.Label(
            self.content,
            text="Quintyx Studio is ready.",
            style="SurfaceTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.content,
            text="Navigation, page hosting, theme state, and persistence are active.",
            style="SurfaceBody.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

