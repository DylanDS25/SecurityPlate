"""Pruebas para el procesamiento de imagen de Semana 09."""

import unittest

import numpy as np

from src.semana09_vision import analizar_imagen, generar_reporte, preparar_imagen


class Semana09VisionTests(unittest.TestCase):
    def setUp(self) -> None:
        image = np.full((160, 240, 3), 225, dtype=np.uint8)
        image[45:115, 60:180] = 25
        image[60:100, 80:100] = 230
        image[60:100, 120:140] = 230
        image[60:100, 160:170] = 230
        self.image = image

    def test_analysis_returns_threshold_edges_and_regions(self) -> None:
        result = analizar_imagen(self.image, sigma=1.6)

        self.assertGreater(result["threshold"], 0)
        self.assertEqual(result["edges"].shape, self.image.shape[:2])
        self.assertEqual(result["mask"].shape, self.image.shape[:2])
        self.assertGreaterEqual(result["region_count"], 3)
        self.assertEqual(len(result["sigma_comparison"]), 3)

    def test_invalid_sigma_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            analizar_imagen(self.image, sigma=0)

    def test_large_image_is_resized_and_report_is_generated(self) -> None:
        large_image = np.zeros((1900, 2400, 3), dtype=np.uint8)
        prepared = preparar_imagen(large_image)
        result = analizar_imagen(prepared)
        report = generar_reporte(result, "data/imagen_proyecto.png")

        self.assertEqual(max(prepared.shape[:2]), 1800)
        self.assertIn("Umbral Otsu", report)
        self.assertIn("Regiones conectadas", report)
        self.assertIn("sigma", report)


if __name__ == "__main__":
    unittest.main()