"""Pruebas de integracion para reconocimiento de caracteres de SecurityPlate."""

from pathlib import Path
import csv
import json
import sqlite3
import tempfile
import unittest

import networkx as nx
from PIL import Image

from src.semana08_reconocimiento import (
    DATABASE_PATH,
    CLASS_MAP_PATH,
    METRICS_PATH,
    MODEL_PATH,
    ONTOLOGY_PATH,
    REPORT_PATH,
    RecortesYOLO,
    predict,
)


class Semana08IntegrationTests(unittest.TestCase):
    def test_predict_persists_evidence_and_ontology_instance(self) -> None:
        dataset = RecortesYOLO("test")
        image_tensor, actual_id, _ = dataset[0]
        crop_path = Path(tempfile.gettempdir()) / "securityplate_test_character.png"
        pixels = (image_tensor.squeeze(0).numpy() * 255).astype("uint8")
        Image.fromarray(pixels).save(crop_path)

        prediction = predict(crop_path, actual_class_id=actual_id)

        self.assertTrue(MODEL_PATH.is_file())
        self.assertTrue(DATABASE_PATH.is_file())
        self.assertTrue(ONTOLOGY_PATH.is_file())
        self.assertEqual(prediction["class_id"] >= 0, True)
        self.assertGreaterEqual(prediction["probability"], 0.0)
        self.assertLessEqual(prediction["probability"], 1.0)

        with sqlite3.connect(DATABASE_PATH) as connection:
            row = connection.execute(
                """SELECT categoria_real_id, prediccion_id, probabilidad, particion
                   FROM predicciones WHERE id = ?""",
                (prediction["registro_id"],),
            ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], actual_id)
        self.assertEqual(row[1], prediction["class_id"])
        self.assertEqual(row[3], "inferencia")

        graph = nx.read_graphml(ONTOLOGY_PATH)
        self.assertIn(f"prediccion_{prediction['registro_id']}", graph)
        self.assertIn(f"evidencia_{prediction['registro_id']}", graph)
        relations = {
            edge_data["relacion"] for _, _, edge_data in graph.edges(data=True)
        }
        self.assertIn("registra", relations)
        self.assertIn("asigna_categoria_a", relations)

    def test_training_artifacts_are_consistent(self) -> None:
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        test_sample_count = metrics["samples"]["test"]
        predictions_path = METRICS_PATH.parent / "predicciones_test.csv"

        self.assertTrue(MODEL_PATH.is_file())
        self.assertTrue(REPORT_PATH.is_file())
        self.assertTrue(CLASS_MAP_PATH.is_file())
        with CLASS_MAP_PATH.open(encoding="utf-8", newline="") as file:
            class_rows = list(csv.reader(file))
        self.assertEqual(metrics["classes"], len(class_rows) - 1)

        with predictions_path.open(encoding="utf-8", newline="") as file:
            prediction_rows = list(csv.DictReader(file))
        self.assertEqual(len(prediction_rows), test_sample_count)
        self.assertTrue(
            all(row["ejecucion_id"] == metrics["run_id"] for row in prediction_rows)
        )

        with sqlite3.connect(DATABASE_PATH) as connection:
            database_count = connection.execute(
                "SELECT COUNT(*) FROM predicciones WHERE ejecucion_id = ? AND particion = ?",
                (metrics["run_id"], "test"),
            ).fetchone()[0]
        self.assertEqual(database_count, test_sample_count)

        graph = nx.read_graphml(ONTOLOGY_PATH)
        concept_count = sum(
            data.get("tipo") == "concepto" for _, data in graph.nodes(data=True)
        )
        self.assertGreaterEqual(concept_count, 5)
        self.assertGreaterEqual(graph.number_of_edges(), 5)


if __name__ == "__main__":
    unittest.main()