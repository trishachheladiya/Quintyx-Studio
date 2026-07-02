import tkinter as tk
from tkinter import ttk


class Sidebar(ttk.Frame):
    def __init__(self, parent: tk.Widget, on_select) -> None:
        super().__init__(parent, style="Sidebar.TFrame", width=220)
        self.on_select = on_select
        self.buttons: dict[str, ttk.Button] = {}
        self.pack_propagate(False)

        self.brand = ttk.Label(
            self,
            text="Quintyx\nStudio",
            style="SurfaceTitle.TLabel",
            justify="left",
        )
        self.brand.pack(anchor="w", padx=22, pady=(28, 24))

        for name in ("Dashboard", "Projects", "Research", "Results", "Settings"):
            button = ttk.Button(
                self,
                text=name,
                style="Nav.TButton",
                command=lambda page=name: self.on_select(page),
            )
            button.pack(fill="x", padx=12, pady=3)
            self.buttons[name] = button

        self.footer = ttk.Label(
            self,
            text="Phase 1",
            style="SurfaceBody.TLabel",
        )
        self.footer.pack(side="bottom", anchor="w", padx=22, pady=22)

    def set_active(self, name: str) -> None:
        for page_name, button in self.buttons.items():
            button.configure(style="ActiveNav.TButton" if page_name == name else "Nav.TButton")

    def refresh_theme(self, palette: dict[str, str]) -> None:
        self.configure(style="Sidebar.TFrame")

