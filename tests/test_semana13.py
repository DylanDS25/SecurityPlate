"""Pruebas para la ingenieria del conocimiento de Semana 13."""

import json
import tempfile
import unittest
from unittest.mock import patch

from src.securityplate_conocimiento import (
    CasoSalida,
    construir_hechos_salida,
)
from src import semana13_conocimiento as semana13


class Semana13ConocimientoTests(unittest.TestCase):
    def caso(self, **changes: object) -> CasoSalida:
        values = {
            "identificador": "99",
            "descripcion": "Caso de prueba",
            "placa_coincide": True,
            "conductor_coincide": True,
            "confianza_ocr": 0.93,
            "calidad_imagen": 0.88,
            "registro_activo": True,
            "secuencia": "IPCS",
            "resultado_simbolico": "autorizar_salida",
            "aceptada_automata": True,
        }
        values.update(changes)
        return CasoSalida(**values)

    def test_complete_case_reaches_authorization_with_trace(self) -> None:
        result = semana13.evaluar_caso(self.caso())

        self.assertEqual(result["conclusion_inferida"], "autorizar_salida")
        self.assertEqual(result["protocolo_aceptado"], True)
        self.assertEqual(result["estado"], "Correcto")
        self.assertEqual(len(result["trazas"]), 7)

    def test_missing_driver_uses_review_without_new_authorization(self) -> None:
        result = semana13.evaluar_caso(
            self.caso(conductor_coincide=False, resultado_simbolico="enviar_a_revision")
        )

        self.assertEqual(result["conclusion_inferida"], "enviar_a_revision")
        self.assertNotIn("autorizar_salida", result["hechos_finales"])
        self.assertEqual(result["estado"], "Correcto")

    def test_incomplete_procedure_does_not_add_protocol_fact(self) -> None:
        result = semana13.evaluar_caso(
            self.caso(secuencia="IPC", aceptada_automata=False,
                      resultado_simbolico="enviar_a_revision")
        )

        self.assertFalse(result["protocolo_aceptado"])
        self.assertNotIn("protocolo_aceptado", result["hechos_iniciales"])
        self.assertNotIn("autorizar_salida", result["hechos_finales"])
        self.assertEqual(result["estado"], "Correcto")

    def test_inference_does_not_mutate_initial_facts_or_loop(self) -> None:
        inicial = {"placa_coincide", "conductor_coincide"}
        copy = set(inicial)
        final, trazas = semana13.inferir(
            inicial,
            semana13.construir_reglas_securityplate(),
        )

        self.assertEqual(inicial, copy)
        self.assertIn("correspondencia_confirmada", final)
        self.assertLessEqual(len(trazas), 7)

    def test_thresholds_and_empty_premise_validation(self) -> None:
        hechos = construir_hechos_salida(True, True, 0.85, 0.80, True)
        self.assertIn("confianza_ocr_alta", hechos)
        self.assertIn("imagen_suficiente", hechos)

        below = construir_hechos_salida(True, True, 0.849, 0.799, True)
        self.assertNotIn("confianza_ocr_alta", below)
        self.assertNotIn("imagen_suficiente", below)

        with self.assertRaisesRegex(ValueError, "premisas vacias"):
            semana13.inferir(
                set(),
                [semana13.Regla("R0", frozenset(), "conclusion")],
            )

    def test_existing_cases_generate_only_json_artifact(self) -> None:
        casos = semana13.cargar_casos_salida()
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_dir = __import__("pathlib").Path(temp_dir) / "artifacts"
            artifact_path = artifact_dir / "semana13_inferencia.json"
            report_path = __import__("pathlib").Path(temp_dir) / "semana13.md"
            with patch.object(semana13, "ARTIFACTS_DIR", artifact_dir), patch.object(
                semana13, "ARTIFACT_PATH", artifact_path
            ), patch.object(
                semana13, "REPORT_PATH", report_path
            ):
                artifact = semana13.generar_artefacto(casos)
            data = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertEqual(data["flujo"], "salida")
        self.assertEqual(data["resumen"]["total"], 5)
        self.assertEqual(data["resumen"]["correctos"], 5)
        self.assertEqual(artifact["entrada"], "data/casos_semana07.csv")


if __name__ == "__main__":
    unittest.main()
