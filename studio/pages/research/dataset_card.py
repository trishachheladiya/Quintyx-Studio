from tkinter import ttk


class DatasetCard(ttk.Frame):
    def __init__(self, parent, dataset, on_select) -> None:
        super().__init__(parent, style="Card.TFrame", padding=18)
        self.dataset = dataset
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Dataset", style="CardBody.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text=dataset.name,
            style="CardTitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        ttk.Label(self, text="Candles", style="CardBody.TLabel").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Label(
            self,
            text=f"{dataset.candles:,}",
            style="CardTitle.TLabel",
        ).grid(row=3, column=0, sticky="w", pady=(2, 0))
        ttk.Label(self, text="Date Range", style="CardBody.TLabel").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Label(
            self,
            text=f"{dataset.start_date} -> {dataset.end_date}",
            style="CardTitle.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(2, 0))
        ttk.Label(self, text="Missing Candles", style="CardBody.TLabel").grid(row=6, column=0, sticky="w", pady=(10, 0))
        ttk.Label(
            self,
            text=f"{dataset.missing_candles:,}",
            style="CardTitle.TLabel",
        ).grid(row=7, column=0, sticky="w", pady=(2, 0))
        ttk.Label(self, text="Quality", style="CardBody.TLabel").grid(row=8, column=0, sticky="w", pady=(10, 0))
        ttk.Label(
            self,
            text=dataset.quality,
            style="CardTitle.TLabel",
        ).grid(row=9, column=0, sticky="w", pady=(2, 14))

        ttk.Button(
            self,
            text="Select Dataset",
            style="Studio.TButton",
            command=lambda: on_select(dataset),
        ).grid(row=10, column=0, sticky="w")

