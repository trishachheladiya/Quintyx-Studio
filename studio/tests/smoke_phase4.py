"""Phase 4 acceptance smoke tests."""

from __future__ import annotations

import ast
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

STUDIO_ROOT = Path(__file__).resolve().parents[1]
if str(STUDIO_ROOT) not in sys.path:
    sys.path.insert(0, str(STUDIO_ROOT))

from managers.dataset_manager import DATASET_METADATA_FILE, SUPPORTED_DATASETS, DatasetManager
from managers.project_manager import ProjectManager
from models.project import Project
from services.dataset_service import DatasetService
from services.project_service import ProjectService
from workflow import (
    BacktestTask,
    GenerateFeaturesTask,
    GenerateLabelsTask,
    GenerateReportTask,
    LoadDatasetTask,
    ProgressStatus,
    Task,
    TaskProgress,
    ThresholdAnalysisTask,
    TrainModelTask,
    Workflow,
    WorkflowManager,
)


class Phase4SmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.datasets_root = STUDIO_ROOT / "data" / "datasets"
        self.dataset_manager = DatasetManager(self.datasets_root)
        self.workflow_manager = WorkflowManager(self.dataset_manager)

    def test_only_supported_datasets_appear(self) -> None:
        datasets = self.dataset_manager.scan_datasets()
        names = {dataset.name for dataset in datasets}
        self.assertEqual(names, set(SUPPORTED_DATASETS))
        self.assertNotIn("AUDUSD_H1", names)
        self.assertNotIn("XAUUSD_H1", names)

    def test_metadata_generated_from_real_csv(self) -> None:
        for name in SUPPORTED_DATASETS:
            metadata = self.dataset_manager.validate_dataset(name, update_metadata=True)
            metadata_path = self.datasets_root / name / DATASET_METADATA_FILE
            csv_path = self.datasets_root / name / f"{name}.csv"

            self.assertTrue(csv_path.exists(), f"Missing CSV for {name}")
            self.assertTrue(metadata_path.exists(), f"Missing metadata for {name}")
            self.assertGreater(metadata["candles"], 0)
            self.assertIn("symbol", metadata)
            self.assertIn("timeframe", metadata)
            self.assertIn("missing_candles", metadata)
            self.assertIn("duplicates", metadata)
            self.assertIn("quality", metadata)
            self.assertIn("timestamps_sorted", metadata)
            self.assertIn("required_columns", metadata)

            with metadata_path.open("r", encoding="utf-8") as file:
                saved = json.load(file)
            self.assertEqual(saved["candles"], metadata["candles"])
            self.assertEqual(saved["start"], metadata["start"])
            self.assertEqual(saved["end"], metadata["end"])

    def test_dataset_selection_updates_project_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_root = Path(temp_dir) / "Projects"
            project_manager = ProjectManager(projects_root)
            project_service = ProjectService(project_manager)
            dataset_service = DatasetService(
                manager=self.dataset_manager,
                project_service=project_service,
                workflow_manager=self.workflow_manager,
            )

            project = project_service.create_project("SmokeTest", "Phase 4 smoke test project")
            updated = dataset_service.assign_dataset_to_project(project, "EURUSD_H1")

            metadata_path = Path(updated.path) / "project.json"
            with metadata_path.open("r", encoding="utf-8") as file:
                saved = json.load(file)

            self.assertEqual(saved["dataset"], "EURUSD_H1")
            reloaded = project_service.open_project("SmokeTest")
            self.assertEqual(reloaded.dataset, "EURUSD_H1")

    def test_current_dataset_statistics(self) -> None:
        stats = self.dataset_manager.get_statistics("EURUSD_H1")
        expected_keys = {
            "Dataset",
            "Symbol",
            "Timeframe",
            "Candles",
            "Date Range",
            "Missing Candles",
            "Quality",
            "CSV Path",
        }
        self.assertEqual(set(stats.keys()), expected_keys)
        self.assertEqual(stats["Dataset"], "EURUSD_H1")
        self.assertEqual(stats["Symbol"], "EURUSD")
        self.assertEqual(stats["Timeframe"], "H1")

    def test_workflow_manager_and_task_framework(self) -> None:
        self.assertIsNotNone(self.workflow_manager)
        progress_events: list[TaskProgress] = []
        self.workflow_manager.add_progress_callback(progress_events.append)
        dataset = self.workflow_manager.load_dataset("GBPUSD_H1")
        self.assertEqual(dataset.name, "GBPUSD_H1")
        self.assertTrue(any(event.status == ProgressStatus.RUNNING for event in progress_events))
        self.assertTrue(any(event.status == ProgressStatus.COMPLETED for event in progress_events))

        placeholder_tasks = [
            GenerateFeaturesTask(),
            GenerateLabelsTask(),
            TrainModelTask(),
            ThresholdAnalysisTask(),
            BacktestTask(),
            GenerateReportTask(),
        ]
        for task in placeholder_tasks:
            self.assertIsInstance(task, Task)
            with self.assertRaises(NotImplementedError):
                task.run()

        workflow = Workflow("Research Pipeline")
        workflow.add_task(LoadDatasetTask(self.dataset_manager, "USDJPY_H1"))
        self.assertEqual(len(workflow.tasks), 1)

    def test_progress_framework_statuses(self) -> None:
        statuses = {status.value for status in ProgressStatus}
        self.assertEqual(
            statuses,
            {"Queued", "Running", "Completed", "Failed", "Cancelled"},
        )
        progress = TaskProgress("Load Dataset", ProgressStatus.RUNNING, "Reading CSV", 50)
        self.assertEqual(progress.percent, 50)

    def test_gui_never_reads_csv_directly(self) -> None:
        pages_root = STUDIO_ROOT / "pages"
        forbidden = {"csv", "DatasetManager", "ProjectManager"}
        for path in pages_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imports.update(
                node.module.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            )
            violations = forbidden.intersection(imports)
            self.assertFalse(violations, f"{path.name} imports forbidden modules: {violations}")

    def test_service_routes_through_workflow_manager(self) -> None:
        dataset_service = DatasetService(workflow_manager=self.workflow_manager)
        datasets = dataset_service.list_datasets()
        self.assertEqual(len(datasets), 3)
        self.assertIs(dataset_service.workflow_manager, self.workflow_manager)


if __name__ == "__main__":
    unittest.main(verbosity=2)
