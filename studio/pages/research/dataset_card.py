from tkinter import ttk


class DatasetCard(ttk.Frame):
    def __init__(self, parent, dataset, on_select) -> None:
        super().__init__(parent, style="Card.TFrame", padding=18)
        self.dataset = dataset
        self.columnconfigure(0, weight=1)

        ttk.Label(
            self,
            text=f"{dataset.symbol} {dataset.timeframe}",
            style="CardTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text=f"{dataset.candles:,} candles",
            style="CardBody.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Label(
            self,
            text=f"{dataset.start_date} -> {dataset.end_date}",
            style="CardBody.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            self,
            text=f"Quality: {dataset.quality}",
            style="CardBody.TLabel",
        ).grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Label(
            self,
            text=f"Missing candles: {dataset.missing_candles:,}",
            style="CardBody.TLabel",
        ).grid(row=4, column=0, sticky="w", pady=(4, 14))

        ttk.Button(
            self,
            text="Select Dataset",
            style="Studio.TButton",
            command=lambda: on_select(dataset),
        ).grid(row=5, column=0, sticky="w")

