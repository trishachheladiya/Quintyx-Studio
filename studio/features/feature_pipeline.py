from __future__ import annotations

import pandas as pd

try:
    from .feature_registry import FeatureRegistry
except ImportError:
    from features.feature_registry import FeatureRegistry


class FeaturePipeline:
    def __init__(self, registry: FeatureRegistry | None = None) -> None:
        self.registry = registry or FeatureRegistry()

    def build_features(self, frame: pd.DataFrame, selected_features: list[str], progress_callback=None) -> pd.DataFrame:
        if frame.empty:
            raise ValueError("The dataset is empty")

        unique_features = list(dict.fromkeys(selected_features))
        if len(unique_features) != len(selected_features):
            raise ValueError("Duplicate feature names are not allowed")

        if not unique_features:
            raise ValueError("No features selected")

        feature_frame = frame.copy()
        total = len(unique_features)
        for index, feature_name in enumerate(unique_features, start=1):
            if progress_callback is not None:
                progress_callback(feature_name, index, total)
            calculator = self.registry.get_calculator(feature_name)
            feature_frame[feature_name] = calculator.calculate(feature_frame)
        return feature_frame
