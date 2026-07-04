from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .feature_pipeline import FeaturePipeline
    from .feature_registry import FeatureRegistry
except ImportError:
    from features.feature_pipeline import FeaturePipeline
    from features.feature_registry import FeatureRegistry


class FeatureEngine:
    def __init__(self, registry: FeatureRegistry | None = None) -> None:
        self.registry = registry or FeatureRegistry()
        self.pipeline = FeaturePipeline(self.registry)

    def generate_features(self, dataset_path: str | Path, selected_features: list[str], progress_callback=None) -> pd.DataFrame:
        frame = self._load_dataset(dataset_path)
        self._validate_dataset(frame, selected_features)
        return self.pipeline.build_features(frame, selected_features, progress_callback=progress_callback)

    def _load_dataset(self, dataset_path: str | Path) -> pd.DataFrame:
        path = Path(dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        try:
            frame = pd.read_csv(path, sep=r"\s+", engine="python")
        except Exception:
            frame = pd.read_csv(path, sep=None, engine="python")

        if frame.empty:
            raise ValueError("The selected dataset is empty")

        normalized_columns = {
            column: column.strip().lower().replace("<", "").replace(">", "")
            for column in frame.columns
        }
        frame = frame.rename(columns=normalized_columns)

        if "volume" not in frame.columns:
            for candidate in ("tickvol", "vol"):
                if candidate in frame.columns:
                    frame["volume"] = frame[candidate]
                    break

        if "date" in frame.columns and "time" in frame.columns:
            frame["timestamp"] = pd.to_datetime(frame["date"].astype(str) + " " + frame["time"].astype(str), format="%Y.%m.%d %H:%M:%S", errors="coerce")
        elif "time" in frame.columns:
            frame["timestamp"] = pd.to_datetime(frame["time"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
        else:
            raise ValueError("The dataset needs a recognizable time column")

        if frame["timestamp"].isna().any():
            frame = frame.dropna(subset=["timestamp"])

        frame = frame.sort_values("timestamp").reset_index(drop=True)
        frame["open"] = pd.to_numeric(frame["open"], errors="coerce")
        frame["high"] = pd.to_numeric(frame["high"], errors="coerce")
        frame["low"] = pd.to_numeric(frame["low"], errors="coerce")
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce")
        frame = frame.dropna(subset=["open", "high", "low", "close", "volume"])
        frame = frame.reset_index(drop=True)
        return frame

    def _validate_dataset(self, frame: pd.DataFrame, selected_features: list[str]) -> None:
        missing = {column for column in ("open", "high", "low", "close", "volume") if column not in frame.columns}
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        if len(frame) < 20:
            raise ValueError("The dataset must contain at least 20 candles")

        long_window_features = {"EMA50", "EMA100", "EMA200", "Distance EMA50", "Distance EMA200"}
        required_candles = 0
        for feature_name in selected_features:
            if feature_name not in self.registry.get_feature_names():
                raise ValueError(f"Unsupported feature: {feature_name}")
            if feature_name in long_window_features:
                required_candles = max(required_candles, 200 if feature_name in {"EMA200", "Distance EMA200"} else 100 if feature_name == "EMA100" else 50)
        if required_candles and len(frame) < required_candles:
            raise ValueError(f"The dataset must contain at least {required_candles} candles for the selected long EMA features")
