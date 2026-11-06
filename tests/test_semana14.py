"""Pruebas funcionales de redes semanticas en SecurityPlate."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.securityplate_conocimiento import CasoSalida
from src import semana14_redes_semanticas as semana14


class Semana14RedesSemanticasTests(unittest.TestCase):
    def caso(self, **changes: object) -> CasoSalida:
        valores = {
            "identificador": "14",
            "descripcion": "Caso semantico de prueba",
            "placa_coincide": True,
            "conductor_coincide": True,
            "confianza_ocr": 0.93,
            "calidad_imagen": 0.88,
            "registro_activo": True,
            "secuencia": "IPCS",
            "resultado_simbolico": "autorizar_salida",
            "aceptada_automata": True,
        }
        valores.update(changes)
        return CasoSalida(**valores)

    def test_case_with_plate_and_photo_authorizes(self) -> None:
        resultado = semana14.evaluar_caso(self.caso())

        self.assertTrue(resultado["foto_adecuada"])
        self.assertTrue(resultado["placa_coincide"])
        self.assertEqual(resultado["conclusion"], "autorizar_salida")
        self.assertEqual(resultado["estado"], "Correcto")

    def test_plate_without_match_calls_manual_review(self) -> None:
        resultado = semana14.evaluar_caso(
            self.caso(
                placa_coincide=False,
                resultado_simbolico="enviar_a_revision",
            )
        )

        self.assertEqual(
            resultado["conclusion"],
            "llamar_personal_verificacion_manual",
        )
        self.assertIn("no corresponde", resultado["motivo_revision"])

    def test_blurry_photo_calls_manual_review(self) -> None:
        resultado = semana14.evaluar_caso(
            self.caso(
                calidad_imagen=0.799,
                resultado_simbolico="enviar_a_revision",
            )
        )

        self.assertFalse(resultado["foto_adecuada"])
        self.assertEqual(
            resultado["conclusion"],
            "llamar_personal_verificacion_manual",
        )
        self.assertIn("umbral", resultado["motivo_revision"])

    def test_exact_quality_threshold_is_adequate(self) -> None:
        resultado = semana14.evaluar_caso(
            self.caso(calidad_imagen=0.80)
        )
        self.assertTrue(resultado["foto_adecuada"])

    def test_inference_is_supported_by_hierarchy(self) -> None:
        resultado = semana14.evaluar_caso(self.caso())
        self.assertTrue(resultado["transitividad_placa_moto"])

    def test_existing_cases_generate_json_and_report(self) -> None:
        casos = semana14.cargar_casos_salida()
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            artifact_path = raiz / "semana14.json"
            report_path = raiz / "reporte_semana14.md"
            with patch.object(
                semana14,
                "ARTIFACT_PATH",
                artifact_path,
            ), patch.object(
                semana14,
                "REPORT_PATH",
                report_path,
            ):
                artefacto = semana14.generar_artefacto(casos)

            data = json.loads(
                artifact_path.read_text(encoding="utf-8")
            )
            report_generated = report_path.exists()

        self.assertEqual(data["semana"], 14)
        self.assertEqual(data["resumen"]["total"], 5)
        self.assertEqual(data["resumen"]["correctos"], 5)
        self.assertEqual(len(artefacto["conceptos"]), 8)
        self.assertTrue(report_generated)


if __name__ == "__main__":
    unittest.main()
