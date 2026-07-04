import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

try:
    from ..models import Dataset, Project
except ImportError:
    from models import Dataset, Project


DATASET_METADATA_FILE = "metadata.json"
REQUIRED_COLUMNS = ("time", "open", "high", "low", "close", "volume")
SUPPORTED_DATASETS = ("EURUSD_H1", "GBPUSD_H1", "USDJPY_H1")


class DatasetValidationError(ValueError):
    pass


class DatasetManager:
    def __init__(self, datasets_root: Path | None = None) -> None:
        if datasets_root is None:
            datasets_root = Path(__file__).resolve().parents[1] / "data" / "datasets"
        self.datasets_root = datasets_root

    def scan_datasets(self) -> list[Dataset]:
        if not self.datasets_root.exists():
            self.datasets_root.mkdir(parents=True, exist_ok=True)
            return []

        datasets: list[Dataset] = []
        for dataset_name in SUPPORTED_DATASETS:
            dataset_path = self.datasets_root / dataset_name
            if dataset_path.is_dir():
                try:
                    datasets.append(self.load_dataset(dataset_name, rebuild_metadata=True))
                except (OSError, json.JSONDecodeError, DatasetValidationError):
                    continue
        return datasets

    def load_dataset(self, name: str, rebuild_metadata: bool = False, validate: bool | None = None) -> Dataset:
        if name not in SUPPORTED_DATASETS:
            raise DatasetValidationError(f"Unsupported dataset: {name}")

        if validate is not None:
            rebuild_metadata = validate

        dataset_path = self.datasets_root / name
        metadata_path = dataset_path / DATASET_METADATA_FILE
        csv_path = self._csv_path(name)

        if rebuild_metadata or not metadata_path.exists():
            metadata = self.validate_dataset(name, update_metadata=True)
        else:
            with metadata_path.open("r", encoding="utf-8") as file:
                metadata = json.load(file)

        file_size = csv_path.stat().st_size if csv_path.exists() else 0
        return Dataset.from_metadata(name, str(csv_path), metadata, file_size)

    def validate_dataset(self, name: str, update_metadata: bool = True) -> dict:
        if name not in SUPPORTED_DATASETS:
            raise DatasetValidationError(f"Unsupported dataset: {name}")

        dataset_path = self.datasets_root / name
        csv_path = self._csv_path(name)
        metadata_path = dataset_path / DATASET_METADATA_FILE

        if not csv_path.exists():
            raise DatasetValidationError(f"CSV file missing: {name}")

        symbol, timeframe = self._parse_dataset_name(name)
        stats = self._calculate_csv_statistics(csv_path, timeframe)
        metadata = {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": stats["candles"],
            "start": stats["start"],
            "end": stats["end"],
            "missing_candles": stats["missing_candles"],
            "duplicates": stats["duplicates"],
            "required_columns": stats["required_columns"],
            "nan_values": stats["nan_values"],
            "timestamps_sorted": stats["timestamps_sorted"],
            "quality": self._quality_rating(stats),
            "timezone": "UTC",
            "validation_errors": stats["validation_errors"],
        }

        if update_metadata:
            with metadata_path.open("w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=2)
        return metadata

    def get_statistics(self, name: str) -> dict:
        dataset = self.load_dataset(name)
        return {
            "Dataset": dataset.name,
            "Symbol": dataset.symbol,
            "Timeframe": dataset.timeframe,
            "Candles": f"{dataset.candles:,}",
            "Date Range": f"{dataset.start_date} -> {dataset.end_date}",
            "Missing Candles": f"{dataset.missing_candles:,}",
            "Quality": dataset.quality,
            "CSV Path": dataset.path,
        }

    def assign_dataset_to_project(self, project: Project, dataset_name: str) -> Project:
        dataset = self.load_dataset(dataset_name, rebuild_metadata=True)
        project.dataset = dataset.to_project_reference()
        return project

    def _calculate_csv_statistics(self, csv_path: Path, timeframe: str) -> dict:
        timestamps = []
        duplicates = 0
        nan_values = 0
        validation_errors = []
        seen_timestamps = set()

        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            sample = file.read(4096)
            file.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters="\t,;")
            reader = csv.DictReader(file, dialect=dialect)
            headers = reader.fieldnames or []
            column_map = self._column_map(headers)
            missing_columns = [column for column in REQUIRED_COLUMNS if column not in column_map]

            if missing_columns:
                validation_errors.append(f"Missing required columns: {', '.join(missing_columns)}")

            for row in reader:
                timestamp = self._row_timestamp(row, column_map)
                if timestamp is None:
                    nan_values += 1
                    continue

                if timestamp in seen_timestamps:
                    duplicates += 1
                seen_timestamps.add(timestamp)
                timestamps.append(timestamp)

                for logical_column in ("open", "high", "low", "close", "volume"):
                    source_column = column_map.get(logical_column)
                    value = row.get(source_column, "").strip() if source_column else ""
                    if value == "":
                        nan_values += 1

        timestamps_sorted = timestamps == sorted(timestamps)
        if not timestamps_sorted:
            validation_errors.append("Timestamps are not sorted")
        if duplicates:
            validation_errors.append("Duplicate timestamps found")
        if nan_values:
            validation_errors.append("Missing or NaN values found")

        missing_candles = self._missing_candles(sorted(set(timestamps)), timeframe)
        return {
            "candles": len(timestamps),
            "start": self._date_text(min(timestamps)) if timestamps else "",
            "end": self._date_text(max(timestamps)) if timestamps else "",
            "missing_candles": missing_candles,
            "duplicates": duplicates,
            "required_columns": {
                "expected": list(REQUIRED_COLUMNS),
                "present": [column for column in REQUIRED_COLUMNS if column in column_map],
                "missing": missing_columns,
            },
            "nan_values": nan_values,
            "timestamps_sorted": timestamps_sorted,
            "validation_errors": validation_errors,
        }

    def _column_map(self, headers: list[str]) -> dict[str, str]:
        normalized = {self._normalize_header(header): header for header in headers}
        column_map = {}

        if "date" in normalized and "time_source" in normalized:
            column_map["date"] = normalized["date"]
            column_map["time"] = normalized["time_source"]
        elif "time" in normalized:
            column_map["time"] = normalized["time"]

        direct_columns = {
            "open": ("open",),
            "high": ("high",),
            "low": ("low",),
            "close": ("close",),
            "volume": ("volume", "tickvol", "vol"),
        }
        for logical_name, candidates in direct_columns.items():
            for candidate in candidates:
                if candidate in normalized:
                    column_map[logical_name] = normalized[candidate]
                    break
        return column_map

    def _row_timestamp(self, row: dict, column_map: dict[str, str]) -> datetime | None:
        date_column = column_map.get("date")
        time_column = column_map.get("time")
        if date_column and time_column:
            date_text = row.get(date_column, "").strip()
            time_text = row.get(time_column, "").strip()
            return self._parse_timestamp(f"{date_text} {time_text}")
        if time_column:
            return self._parse_timestamp(row.get(time_column, "").strip())
        return None

    def _parse_timestamp(self, value: str) -> datetime | None:
        for fmt in ("%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    def _missing_candles(self, timestamps: list[datetime], timeframe: str) -> int:
        if len(timestamps) < 2:
            return 0

        step = self._timeframe_delta(timeframe)
        missing = 0
        for previous, current in zip(timestamps, timestamps[1:]):
            expected = previous + step
            while expected < current:
                if self._is_expected_market_time(expected):
                    missing += 1
                expected += step
        return missing

    def _is_expected_market_time(self, timestamp: datetime) -> bool:
        return timestamp.weekday() < 5

    def _timeframe_delta(self, timeframe: str) -> timedelta:
        if timeframe.upper().endswith("H"):
            return timedelta(hours=int(timeframe[:-1]))
        if timeframe.upper().endswith("M"):
            return timedelta(minutes=int(timeframe[:-1]))
        return timedelta(hours=1)

    def _quality_rating(self, stats: dict) -> str:
        if stats["required_columns"]["missing"] or not stats["timestamps_sorted"] or stats["duplicates"] or stats["nan_values"]:
            return "Invalid"
        if stats["candles"] == 0:
            return "Invalid"

        missing_ratio = stats["missing_candles"] / stats["candles"]
        if missing_ratio == 0:
            return "Excellent"
        if missing_ratio <= 0.005:
            return "Good"
        if missing_ratio <= 0.02:
            return "Fair"
        return "Poor"

    def _csv_path(self, name: str) -> Path:
        return self.datasets_root / name / f"{name}.csv"

    def _parse_dataset_name(self, name: str) -> tuple[str, str]:
        symbol, timeframe = name.rsplit("_", 1)
        return symbol, timeframe

    def _date_text(self, value: datetime) -> str:
        return value.date().isoformat()

    def _normalize_header(self, header: str) -> str:
        raw = header.strip()
        text = raw.lower().replace("<", "").replace(">", "")
        if raw.upper() == "<TIME>":
            return "time_source"
        return text
