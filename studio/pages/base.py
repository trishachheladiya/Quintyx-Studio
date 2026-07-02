import tkinter as tk
from tkinter import ttk


class Page(ttk.Frame):
    title = ""
    subtitle = ""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, style="App.TFrame", padding=(34, 30))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.heading = ttk.Label(self, text=self.title, style="Title.TLabel")
        self.heading.grid(row=0, column=0, sticky="w")

        self.subheading = ttk.Label(self, text=self.subtitle, style="Body.TLabel")
        self.subheading.grid(row=1, column=0, sticky="w", pady=(8, 28))

        self.content = ttk.Frame(self, style="Surface.TFrame", padding=24)
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)

    def refresh_theme(self, palette: dict[str, str]) -> None:
        self.configure(style="App.TFrame")

