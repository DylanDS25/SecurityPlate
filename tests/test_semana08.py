"""Pruebas de integracion para reconocimiento de caracteres de SecurityPlate."""

from pathlib import Path
import sqlite3
import tempfile
import unittest

import networkx as nx
from PIL import Image

from src.semana08_reconocimiento import (
    DATABASE_PATH,
    MODEL_PATH,
    ONTOLOGY_PATH,
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


if __name__ == "__main__":
    unittest.main()