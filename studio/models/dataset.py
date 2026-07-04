from dataclasses import dataclass


@dataclass
class Dataset:
    name: str
    symbol: str
    timeframe: str
    path: str
    start_date: str
    end_date: str
    candles: int
    missing_candles: int
    quality: str
    timezone: str
    file_size: int

    @classmethod
    def from_metadata(cls, name: str, path: str, metadata: dict, file_size: int) -> "Dataset":
        return cls(
            name=name,
            symbol=metadata.get("symbol", ""),
            timeframe=metadata.get("timeframe", ""),
            path=path,
            start_date=metadata.get("start", ""),
            end_date=metadata.get("end", ""),
            candles=int(metadata.get("candles") or 0),
            missing_candles=int(metadata.get("missing_candles", metadata.get("missing", 0)) or 0),
            quality=metadata.get("quality", "Unknown"),
            timezone=metadata.get("timezone", "UTC"),
            file_size=file_size,
        )

    def to_project_reference(self) -> str:
        return self.name
