"""Pruebas del analisis de segmentacion y texturas de Semana 10."""

import base64
from io import BytesIO
import unittest

import numpy as np
from PIL import Image

from src.semana10_texturas import (
    INTENSITY_BINS,
    LBP_POINTS,
    ImageAnalysis,
    MAX_UPLOAD_COUNT,
    analizar_cargas_temporales,
    analizar_imagen,
    generar_reporte,
    serializar_comparacion_temporal,
)


class Semana10TexturasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.first = np.full((100, 100), 20, dtype=np.uint8)
        self.first[15:45, 15:45] = 230
        self.first[60:85, 60:85] = 210

        self.second = np.full((100, 100), 230, dtype=np.uint8)
        self.second[15:45, 15:45] = 20
        self.second[60:85, 60:85] = 40

    def test_analysis_calculates_regions_and_fixed_histogram_features(self) -> None:
        result = analizar_imagen(
            self.first, "Placa A", "Primera placa", "placa_a.jpg"
        )

        self.assertIsInstance(result, ImageAnalysis)
        self.assertGreaterEqual(result.threshold, 20)
        self.assertLess(result.threshold, 230)
        self.assertGreaterEqual(result.region_count, 1)
        self.assertGreaterEqual(result.raw_region_count, result.region_count)
        self.assertGreaterEqual(result.minimum_area, 10)
        self.assertEqual(result.intensity_histogram.size, INTENSITY_BINS)
        self.assertEqual(result.lbp_histogram.size, LBP_POINTS + 2)
        self.assertEqual(result.features.size, 3 + INTENSITY_BINS + LBP_POINTS + 2)
        self.assertAlmostEqual(float(result.intensity_histogram.sum()), 1.0)
        self.assertAlmostEqual(float(result.lbp_histogram.sum()), 1.0)

    def test_report_compares_at_least_two_images(self) -> None:
        first = analizar_imagen(
            self.first, "Placa A", "Primera placa", "placa_a.jpg"
        )
        second = analizar_imagen(
            self.second, "Placa B", "Segunda placa", "placa_b.jpg"
        )

        report = generar_reporte([first, second])

        self.assertIn("Comparacion de texturas LBP", report)
        self.assertIn("placa_a.jpg", report)
        self.assertIn("placa_b.jpg", report)
        self.assertIn("CC BY 4.0", report)

    def test_empty_or_non_grayscale_images_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            analizar_imagen(np.empty((0, 0), dtype=np.uint8), "Vacia", "Vacia")
        with self.assertRaises(ValueError):
            analizar_imagen(
                np.zeros((10, 10, 3), dtype=np.uint8), "RGB", "No gris"
            )

    def test_report_rejects_fewer_than_two_images(self) -> None:
        result = analizar_imagen(
            self.first, "Placa A", "Primera placa", "placa_a.jpg"
        )

        with self.assertRaises(ValueError):
            generar_reporte([result])

    def test_temporary_uploads_return_metrics_without_writing_deliverables(self) -> None:
        uploads = [
            {"name": f"placa_{index}.png", "data": self._data_url(image)}
            for index, image in enumerate((self.first, self.second), start=1)
        ]

        results = analizar_cargas_temporales(uploads)
        response = serializar_comparacion_temporal(results)

        self.assertEqual(len(response["images"]), 2)
        self.assertEqual(len(response["comparisons"]), 1)
        self.assertTrue(response["preview"].startswith("data:image/png;base64,"))

    def test_temporary_upload_count_and_image_format_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "entre 2 y"):
            analizar_cargas_temporales([])

        uploads = [
            {"name": "dos.gif", "data": "data:image/gif;base64,AAAA"},
            {"name": "uno.png", "data": "data:image/png;base64,AAAA"},
        ]
        with self.assertRaisesRegex(ValueError, "PNG, JPG o WebP"):
            analizar_cargas_temporales(uploads)

        uploads = [
            {"name": "uno.png", "data": "data:image/png;base64,AAAA"},
            {"name": "dos.png", "data": "data:image/png;base64,AAAA"},
        ]
        with self.assertRaisesRegex(ValueError, "No se pudo decodificar"):
            analizar_cargas_temporales(uploads)

        uploads = [
            {"name": f"placa_{index}.png", "data": self._data_url(self.first)}
            for index in range(MAX_UPLOAD_COUNT + 1)
        ]
        with self.assertRaisesRegex(ValueError, "entre 2 y"):
            analizar_cargas_temporales(uploads)

    @staticmethod
    def _data_url(image: np.ndarray) -> str:
        buffer = BytesIO()
        Image.fromarray(image).save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"


if __name__ == "__main__":
    unittest.main()
