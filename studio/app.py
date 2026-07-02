try:
    from .main_window import QuintyxStudioApp
except ImportError:
    from main_window import QuintyxStudioApp


def main() -> None:
    app = QuintyxStudioApp()
    app.mainloop()


if __name__ == "__main__":
    main()
