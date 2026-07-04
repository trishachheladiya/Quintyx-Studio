import json
from pathlib import Path

try:
    from ..models import Dataset, Project
except ImportError:
    from models import Dataset, Project


DATASET_METADATA_FILE = "metadata.json"
DATASET_DATA_FILE = "data.parquet"
REQUIRED_COLUMNS = ("time", "open", "high", "low", "close", "volume")


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
        for dataset_path in sorted(self.datasets_root.iterdir(), key=lambda item: item.name.lower()):
            if dataset_path.is_dir():
                try:
                    datasets.append(self.load_dataset(dataset_path.name, validate=False))
                except (OSError, json.JSONDecodeError, DatasetValidationError):
                    continue
        return datasets

    def load_dataset(self, name: str, validate: bool = False) -> Dataset:
        dataset_path = self.datasets_root / name
        metadata_path = dataset_path / DATASET_METADATA_FILE
        data_path = dataset_path / DATASET_DATA_FILE

        if not metadata_path.exists():
            raise DatasetValidationError(f"Dataset metadata missing: {name}")

        with metadata_path.open("r", encoding="utf-8") as file:
            metadata = json.load(file)

        if validate:
            metadata = self.validate_dataset(name, update_metadata=True)

        file_size = data_path.stat().st_size if data_path.exists() else 0
        return Dataset.from_metadata(name, str(dataset_path), metadata, file_size)

    def validate_dataset(self, name: str, update_metadata: bool = True) -> dict:
        dataset_path = self.datasets_root / name
        metadata_path = dataset_path / DATASET_METADATA_FILE
        data_path = dataset_path / DATASET_DATA_FILE

        if not metadata_path.exists():
            raise DatasetValidationError(f"Dataset metadata missing: {name}")

        with metadata_path.open("r", encoding="utf-8") as file:
            metadata = json.load(file)

        results = {
            "file_exists": data_path.exists(),
            "metadata_exists": metadata_path.exists(),
            "required_columns_present": False,
            "timestamps_sorted": None,
            "duplicates": None,
            "missing_timestamps": metadata.get("missing", 0),
            "nan_values": None,
            "validation_status": "not_validated",
            "validation_errors": [],
        }

        if not data_path.exists():
            results["validation_status"] = "invalid"
            results["validation_errors"].append("data.parquet is missing")
            metadata = self._merge_validation(metadata, results, update_metadata, metadata_path)
            return metadata

        column_results = self._validate_parquet_file(data_path, metadata)
        results.update(column_results)
        if results["validation_errors"]:
            results["validation_status"] = "invalid"
            metadata["quality"] = "Invalid"
        else:
            results["validation_status"] = "valid"
            metadata["quality"] = metadata.get("quality", "Excellent")

        return self._merge_validation(metadata, results, update_metadata, metadata_path)

    def get_statistics(self, name: str) -> dict:
        dataset = self.load_dataset(name)
        return {
            "Dataset": dataset.symbol,
            "Timeframe": dataset.timeframe,
            "Candles": f"{dataset.candles:,}",
            "Coverage": f"{dataset.start_date}-{dataset.end_date}",
            "Missing Candles": f"{dataset.missing_candles:,}",
            "Quality": dataset.quality,
            "Timezone": dataset.timezone,
            "File Size": self._format_file_size(dataset.file_size),
        }

    def assign_dataset_to_project(self, project: Project, dataset_name: str) -> Project:
        dataset = self.load_dataset(dataset_name)
        project.dataset = dataset.to_project_reference()
        return project

    def _validate_parquet_file(self, data_path: Path, metadata: dict) -> dict:
        pyarrow_result = self._validate_with_pyarrow(data_path, metadata)
        if pyarrow_result is not None:
            return pyarrow_result

        pandas_result = self._validate_with_pandas(data_path, metadata)
        if pandas_result is not None:
            return pandas_result

        return {
            "required_columns_present": False,
            "timestamps_sorted": None,
            "duplicates": None,
            "missing_timestamps": metadata.get("missing", 0),
            "nan_values": None,
            "validation_errors": ["No Parquet engine available to validate data.parquet"],
        }

    def _validate_with_pyarrow(self, data_path: Path, metadata: dict) -> dict | None:
        try:
            import pyarrow.parquet as pq
        except ImportError:
            return None

        try:
            parquet_file = pq.ParquetFile(data_path)
            columns = parquet_file.schema.names
        except Exception as error:
            return self._invalid_result(metadata, f"Unable to read Parquet schema: {error}")

        errors = self._column_errors(columns)
        if errors:
            return self._result(metadata, False, None, None, None, errors)

        try:
            table = parquet_file.read(columns=list(REQUIRED_COLUMNS))
            frame = table.to_pandas()
            return self._validate_frame(frame, metadata)
        except Exception as error:
            return self._invalid_result(metadata, f"Unable to validate Parquet rows: {error}")

    def _validate_with_pandas(self, data_path: Path, metadata: dict) -> dict | None:
        try:
            import pandas as pd
        except ImportError:
            return None

        try:
            frame = pd.read_parquet(data_path)
        except Exception as error:
            return self._invalid_result(metadata, f"Unable to read Parquet file: {error}")

        columns = list(frame.columns)
        errors = self._column_errors(columns)
        if errors:
            return self._result(metadata, False, None, None, None, errors)

        return self._validate_frame(frame, metadata)

    def _validate_frame(self, frame, metadata: dict) -> dict:
        errors = []
        time_series = frame["time"]
        timestamps_sorted = bool(time_series.is_monotonic_increasing)
        duplicates = int(time_series.duplicated().sum())
        nan_values = int(frame[list(REQUIRED_COLUMNS)].isna().sum().sum())

        if not timestamps_sorted:
            errors.append("Timestamps are not sorted")
        if duplicates:
            errors.append("Duplicate timestamps found")
        if nan_values:
            errors.append("NaN values found")

        return self._result(metadata, True, timestamps_sorted, duplicates, nan_values, errors)

    def _column_errors(self, columns: list[str]) -> list[str]:
        missing = [column for column in REQUIRED_COLUMNS if column not in columns]
        if missing:
            return [f"Missing required columns: {', '.join(missing)}"]
        return []

    def _invalid_result(self, metadata: dict, error: str) -> dict:
        return self._result(metadata, False, None, None, None, [error])

    def _result(
        self,
        metadata: dict,
        required_columns_present: bool,
        timestamps_sorted,
        duplicates,
        nan_values,
        errors: list[str],
    ) -> dict:
        return {
            "required_columns_present": required_columns_present,
            "timestamps_sorted": timestamps_sorted,
            "duplicates": duplicates,
            "missing_timestamps": metadata.get("missing", 0),
            "nan_values": nan_values,
            "validation_errors": errors,
        }

    def _merge_validation(self, metadata: dict, results: dict, update_metadata: bool, metadata_path: Path) -> dict:
        metadata["validation"] = results
        if results.get("validation_status") == "invalid":
            metadata["quality"] = "Invalid"
        if update_metadata:
            with metadata_path.open("w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=2)
        return metadata

    def _format_file_size(self, size: int) -> str:
        if size <= 0:
            return "0 B"
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f} {unit}"
            size = size / 1024
        return f"{size:.1f} TB"
