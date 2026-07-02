import tkinter as tk
from tkinter import ttk

try:
    from ..base import Page
except ImportError:
    from pages.base import Page


class SettingsPage(Page):
    title = "Settings"
    subtitle = "Application preferences."

    def __init__(self, parent, get_theme, set_theme, save_settings) -> None:
        super().__init__(parent)
        self.get_theme = get_theme
        self.set_theme = set_theme
        self.save_settings = save_settings
        self.theme_choice = tk.StringVar(value=self.get_theme())

        ttk.Label(
            self.content,
            text="Theme",
            style="SurfaceTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(self.content, style="Surface.TFrame")
        controls.grid(row=1, column=0, sticky="w", pady=(14, 0))

        ttk.Radiobutton(
            controls,
            text="Dark",
            value="dark",
            variable=self.theme_choice,
            style="Studio.TRadiobutton",
            command=self.apply_selected_theme,
        ).grid(row=0, column=0, sticky="w", padx=(0, 18))

        ttk.Radiobutton(
            controls,
            text="Light",
            value="light",
            variable=self.theme_choice,
            style="Studio.TRadiobutton",
            command=self.apply_selected_theme,
        ).grid(row=0, column=1, sticky="w")

        ttk.Button(
            self.content,
            text="Save Settings",
            style="Studio.TButton",
            command=self.save_settings,
        ).grid(row=2, column=0, sticky="w", pady=(24, 0))

    def apply_selected_theme(self) -> None:
        self.set_theme(self.theme_choice.get())

    def refresh_theme(self, palette: dict[str, str]) -> None:
        super().refresh_theme(palette)
        self.theme_choice.set(self.get_theme())

