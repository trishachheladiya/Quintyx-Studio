import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk

try:
    from .sidebar import Sidebar
    from .services import DatasetService
    from .services import FeatureService
    from .services import ProjectService
    from .pages.dashboard import DashboardPage
    from .pages.projects import ProjectsPage
    from .pages.research import ResearchPage
    from .pages.results import ResultsPage
    from .pages.settings import SettingsPage
except ImportError:
    from sidebar import Sidebar
    from services import DatasetService
    from services import FeatureService
    from services import ProjectService
    from pages.dashboard import DashboardPage
    from pages.projects import ProjectsPage
    from pages.research import ResearchPage
    from pages.results import ResultsPage
    from pages.settings import SettingsPage


SETTINGS_FILE = Path(__file__).with_name("settings.json")


THEMES = {
    "dark": {
        "background": "#111318",
        "surface": "#171a21",
        "surface_alt": "#20242d",
        "border": "#2b303b",
        "text": "#f3f4f6",
        "muted": "#9ca3af",
        "accent": "#5eead4",
        "accent_text": "#061513",
        "button": "#252a34",
        "button_hover": "#303642",
    },
    "light": {
        "background": "#f5f7fa",
        "surface": "#ffffff",
        "surface_alt": "#eef2f6",
        "border": "#d8dee8",
        "text": "#151922",
        "muted": "#637083",
        "accent": "#0f766e",
        "accent_text": "#ffffff",
        "button": "#e8edf4",
        "button_hover": "#dce4ee",
    },
}


class QuintyxStudioApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Quintyx Studio")
        self.geometry("1120x720")
        self.minsize(900, 560)

        self.settings = self.load_settings()
        self.theme_name = self.settings.get("theme", "dark")
        self.palette = THEMES[self.theme_name]
        self.project_service = ProjectService()
        self.workflow_manager = None
        self.dataset_service = None
        self.feature_service = None
        self._build_services()
        self.current_project = None
        self.pages: dict[str, ttk.Frame] = {}
        self.current_page = tk.StringVar(value=self.settings.get("last_page", "Dashboard"))

        self.configure(bg=self.palette["background"])
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.container = ttk.Frame(self, style="App.TFrame")
        self.container.pack(fill="both", expand=True)
        self.container.columnconfigure(1, weight=1)
        self.container.rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self.container, self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.page_host = ttk.Frame(self.container, style="App.TFrame")
        self.page_host.grid(row=0, column=1, sticky="nsew")
        self.page_host.rowconfigure(0, weight=1)
        self.page_host.columnconfigure(0, weight=1)

        self.build_pages()
        self.apply_theme()
        self.show_page(self.current_page.get())

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_services(self) -> None:
        from .workflow import WorkflowManager

        self.workflow_manager = WorkflowManager()
        self.dataset_service = DatasetService(project_service=self.project_service, workflow_manager=self.workflow_manager)
        self.feature_service = FeatureService(workflow_manager=self.workflow_manager)

    def load_settings(self) -> dict[str, str]:
        if not SETTINGS_FILE.exists():
            return {"theme": "dark", "last_page": "Dashboard"}

        try:
            with SETTINGS_FILE.open("r", encoding="utf-8") as file:
                settings = json.load(file)
        except (OSError, json.JSONDecodeError):
            return {"theme": "dark", "last_page": "Dashboard"}

        if settings.get("theme") not in THEMES:
            settings["theme"] = "dark"
        settings.setdefault("last_page", "Dashboard")
        return settings

    def save_settings(self) -> None:
        self.settings["theme"] = self.theme_name
        self.settings["last_page"] = self.current_page.get()
        with SETTINGS_FILE.open("w", encoding="utf-8") as file:
            json.dump(self.settings, file, indent=2)

    def build_pages(self) -> None:
        self.pages = {
            "Dashboard": DashboardPage(self.page_host),
            "Projects": ProjectsPage(
                self.page_host,
                self.project_service,
                on_project_opened=self.set_current_project,
            ),
            "Research": ResearchPage(
                self.page_host,
                self.dataset_service,
                self.feature_service,
                get_current_project=lambda: self.current_project,
                set_current_project=self.set_current_project,
            ),
            "Results": ResultsPage(self.page_host),
            "Settings": SettingsPage(
                self.page_host,
                get_theme=lambda: self.theme_name,
                set_theme=self.set_theme,
                save_settings=self.save_settings,
            ),
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, name: str) -> None:
        if name not in self.pages:
            name = "Dashboard"

        self.current_page.set(name)
        self.pages[name].tkraise()
        self.sidebar.set_active(name)
        if hasattr(self.pages[name], "refresh_data"):
            self.pages[name].refresh_data()
        self.save_settings()

    def set_current_project(self, project) -> None:
        self.current_project = project
        if "Research" in self.pages and hasattr(self.pages["Research"], "refresh_data"):
            self.pages["Research"].refresh_data()

    def set_theme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            return

        self.theme_name = theme_name
        self.palette = THEMES[theme_name]
        self.apply_theme()
        self.save_settings()

    def apply_theme(self) -> None:
        self.configure(bg=self.palette["background"])

        self.style.configure("App.TFrame", background=self.palette["background"])
        self.style.configure("Surface.TFrame", background=self.palette["surface"])
        self.style.configure("Card.TFrame", background=self.palette["surface_alt"])
        self.style.configure("Sidebar.TFrame", background=self.palette["surface"])
        self.style.configure(
            "Title.TLabel",
            background=self.palette["background"],
            foreground=self.palette["text"],
            font=("Segoe UI", 22, "bold"),
        )
        self.style.configure(
            "Body.TLabel",
            background=self.palette["background"],
            foreground=self.palette["muted"],
            font=("Segoe UI", 11),
        )
        self.style.configure(
            "SurfaceTitle.TLabel",
            background=self.palette["surface"],
            foreground=self.palette["text"],
            font=("Segoe UI", 13, "bold"),
        )
        self.style.configure(
            "SurfaceBody.TLabel",
            background=self.palette["surface"],
            foreground=self.palette["muted"],
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "CardTitle.TLabel",
            background=self.palette["surface_alt"],
            foreground=self.palette["text"],
            font=("Segoe UI", 12, "bold"),
        )
        self.style.configure(
            "CardBody.TLabel",
            background=self.palette["surface_alt"],
            foreground=self.palette["muted"],
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Error.TLabel",
            background=self.palette["background"],
            foreground="#ef4444",
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Nav.TButton",
            background=self.palette["surface"],
            foreground=self.palette["muted"],
            borderwidth=0,
            focusthickness=0,
            font=("Segoe UI", 10),
            padding=(18, 12),
            anchor="w",
        )
        self.style.map(
            "Nav.TButton",
            background=[("active", self.palette["surface_alt"])],
            foreground=[("active", self.palette["text"])],
        )
        self.style.configure(
            "ActiveNav.TButton",
            background=self.palette["accent"],
            foreground=self.palette["accent_text"],
            borderwidth=0,
            focusthickness=0,
            font=("Segoe UI", 10, "bold"),
            padding=(18, 12),
            anchor="w",
        )
        self.style.map(
            "ActiveNav.TButton",
            background=[("active", self.palette["accent"])],
            foreground=[("active", self.palette["accent_text"])],
        )
        self.style.configure(
            "Studio.TButton",
            background=self.palette["button"],
            foreground=self.palette["text"],
            borderwidth=0,
            focusthickness=0,
            font=("Segoe UI", 10),
            padding=(14, 9),
        )
        self.style.map(
            "Studio.TButton",
            background=[("active", self.palette["button_hover"])],
            foreground=[("active", self.palette["text"])],
        )
        self.style.configure(
            "Studio.TRadiobutton",
            background=self.palette["background"],
            foreground=self.palette["text"],
            font=("Segoe UI", 10),
        )

        for page in self.pages.values():
            if hasattr(page, "refresh_theme"):
                page.refresh_theme(self.palette)
        self.sidebar.refresh_theme(self.palette)

    def on_close(self) -> None:
        self.save_settings()
        self.destroy()
