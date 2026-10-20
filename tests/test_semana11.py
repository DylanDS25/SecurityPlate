"""Pruebas del benchmark de modelos de Semana 11."""

import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from src import semana11_benchmark as benchmark


class Semana11BenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.X_train = np.array(
            [
                [0.0, 0.0],
                [0.1, 0.0],
                [0.0, 0.1],
                [1.0, 1.0],
                [0.9, 1.0],
                [1.0, 0.9],
            ],
            dtype=np.float32,
        )
        self.y_train = np.array([0, 0, 0, 1, 1, 1])
        self.X_test = np.array([[0.05, 0.05], [0.95, 0.95]], dtype=np.float32)
        self.y_test = np.array([0, 1])

    def test_benchmark_runs_all_models_three_times_on_shared_split(self) -> None:
        results = benchmark.ejecutar_benchmark(
            self.X_train, self.y_train, self.X_test, self.y_test, repeats=3
        )

        self.assertEqual(len(results), 9)
        self.assertEqual(
            {result["modelo"] for result in results},
            {"logistic_regression", "random_forest", "mlp"},
        )
        self.assertEqual(
            {result["ejecucion"] for result in results},
            {1, 2, 3},
        )
        self.assertTrue(all(0 <= result["accuracy"] <= 1 for result in results))
        self.assertTrue(all(result["fit_seconds"] > 0 for result in results))

    def test_benchmark_requires_three_runs_and_matching_labels(self) -> None:
        with self.assertRaisesRegex(ValueError, "al menos 3"):
            benchmark.ejecutar_benchmark(
                self.X_train, self.y_train, self.X_test, self.y_test, repeats=2
            )
        with self.assertRaisesRegex(ValueError, "mismo tamaño"):
            benchmark.ejecutar_benchmark(
                self.X_train, self.y_train[:-1], self.X_test, self.y_test
            )

    def test_summary_and_decision_prefer_fast_model_within_accuracy_tolerance(self) -> None:
        results = [
            {"modelo": "best", "ejecucion": 1, "accuracy": 0.90, "fit_seconds": 10.0},
            {"modelo": "best", "ejecucion": 2, "accuracy": 0.90, "fit_seconds": 10.0},
            {"modelo": "fast", "ejecucion": 1, "accuracy": 0.895, "fit_seconds": 1.0},
            {"modelo": "fast", "ejecucion": 2, "accuracy": 0.895, "fit_seconds": 1.0},
        ]

        summaries = benchmark.resumir_resultados(results)

        self.assertEqual(benchmark.seleccionar_modelo(summaries), "fast")
        self.assertAlmostEqual(summaries["best"]["std_accuracy"], 0.0)

    def test_csv_contains_each_model_and_run(self) -> None:
        results = benchmark.ejecutar_benchmark(
            self.X_train, self.y_train, self.X_test, self.y_test, repeats=3
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "benchmark.csv"
            with patch.object(benchmark, "BENCHMARK_PATH", output):
                benchmark.guardar_benchmark(results)
            with output.open(encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 9)
        self.assertEqual(
            set(rows[0]),
            {"modelo", "ejecucion", "accuracy", "fit_seconds", "convergido"},
        )
        self.assertEqual({row["ejecucion"] for row in rows}, {"1", "2", "3"})

    def test_adr_documents_project_scope_and_test_split_limitations(self) -> None:
        results = [
            {"modelo": "logistic_regression", "ejecucion": 1, "accuracy": 0.8, "fit_seconds": 1.0},
            {"modelo": "random_forest", "ejecucion": 1, "accuracy": 0.85, "fit_seconds": 2.0},
            {
                "modelo": "mlp",
                "ejecucion": 1,
                "accuracy": 0.84,
                "fit_seconds": 3.0,
                "convergido": False,
            },
        ]

        report = benchmark.generar_adr(results, 100, 30, 50, 48)

        self.assertIn("recortes anotados de caracteres", report)
        self.assertIn("48 de 50 clases", report)
        self.assertIn("no reconstruye la cadena OCR", report)
        self.assertIn("mlp: 1 ejecucion(es) sin converger", report)
        self.assertIn("decisión", report.lower())


if __name__ == "__main__":
    unittest.main()
