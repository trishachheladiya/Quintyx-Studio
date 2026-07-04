"""Phase 5 feature engineering smoke tests."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

STUDIO_ROOT = Path(__file__).resolve().parents[1]
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

from features.feature_engine import FeatureEngine
from features.feature_registry import FeatureRegistry
from workflow.task import GenerateFeaturesTask


class Phase5FeatureEngineeringTests(unittest.TestCase):
    def test_feature_registry_exposes_expected_features(self) -> None:
        registry = FeatureRegistry()
        names = registry.get_feature_names()
        self.assertIn("EMA20", names)
        self.assertIn("EMA50", names)
        self.assertIn("RSI14", names)
        self.assertIn("ATR14", names)
        self.assertIn("Return24", names)
        self.assertIn("Day Of Week", names)

    def test_feature_engine_generates_selected_features(self) -> None:
        dataset_path = STUDIO_ROOT / "data" / "datasets" / "EURUSD_H1" / "EURUSD_H1.csv"
        engine = FeatureEngine()
        result = engine.generate_features(dataset_path, ["EMA20", "RSI14", "Body", "Hour"])

        self.assertIn("EMA20", result.columns)
        self.assertIn("RSI14", result.columns)
        self.assertIn("Body", result.columns)
        self.assertIn("Hour", result.columns)
        self.assertGreater(len(result), 0)

    def test_generate_features_task_writes_project_features_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "Demo Project"
            project_path.mkdir(parents=True)
            (project_path / "features").mkdir()

            dataset_path = STUDIO_ROOT / "data" / "datasets" / "EURUSD_H1" / "EURUSD_H1.csv"
            task = GenerateFeaturesTask(
                project_path=project_path,
                dataset_path=dataset_path,
                selected_features=["EMA20", "RSI14", "Body"],
            )
            result = task.run()

            output_path = project_path / "features" / "features.csv"
            self.assertTrue(output_path.exists())
            self.assertEqual(result["output_path"], str(output_path))
            self.assertGreater(result["rows"], 0)
            self.assertEqual(result["generated_features"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
