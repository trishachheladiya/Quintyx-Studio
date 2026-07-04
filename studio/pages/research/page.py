try:
    from ..base import Page
    from .dataset_page import DatasetLibrary
except ImportError:
    from pages.base import Page
    from pages.research.dataset_page import DatasetLibrary


class ResearchPage(Page):
    title = "Research"
    subtitle = "Browse and assign project datasets."

    def __init__(self, parent, dataset_service, feature_service, get_current_project, set_current_project) -> None:
        super().__init__(parent)
        self.content.rowconfigure(0, weight=1)

        self.dataset_library = DatasetLibrary(
            self.content,
            dataset_service,
            feature_service,
            get_current_project,
            set_current_project,
        )
        self.dataset_library.grid(row=0, column=0, sticky="nsew")

    def refresh_data(self) -> None:
        if hasattr(self, "dataset_library"):
            self.dataset_library.refresh_data()

    def refresh_theme(self, palette: dict[str, str]) -> None:
        super().refresh_theme(palette)
        if hasattr(self, "dataset_library"):
            self.dataset_library.refresh_theme(palette)
