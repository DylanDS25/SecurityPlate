"""Pruebas funcionales del motor de referencia de SecurityPlate.

Semana 16: Verificacion de normalizacion, recuperacion de fuentes validadas,
exclusion de borradores, abstencion ante preguntas fuera de cobertura o vacias,
y trazabilidad de procedencia.
"""

from pathlib import Path
import sys
import unittest

# Asegurar importacion del modulo motor_referencia desde raiz del proyecto o src
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

from motor_referencia import consultar, normalizar


class MotorReferenciaSecurityPlateTest(unittest.TestCase):
    """Suite de pruebas unitarias para el motor de referencia."""

    def test_normaliza_mayusculas_y_tildes(self):
        """Demuestra normalizacion correcta: conversion a minusculas y eliminacion de tildes."""
        tokens = normalizar("CÁMARA, PREPROCESAMIENTO Y FILTRO DE PLACAS")
        self.assertIn("camara", tokens)
        self.assertIn("preprocesamiento", tokens)
        self.assertIn("filtro", tokens)
        self.assertIn("placas", tokens)

    def test_encuentra_referencia_validada(self):
        """Demuestra consulta con respuesta valida aprobada y estado ENCONTRADA."""
        resultado = consultar("¿Cómo se realiza la captura y el preprocesamiento de la placa con la cámara?")
        self.assertEqual(resultado["estado"], "ENCONTRADA")
        self.assertIsNotNone(resultado["referencia"])
        self.assertEqual(resultado["referencia"]["id"], "REF-SEC-001")
        self.assertIn("escala de grises", resultado["mensaje"])

    def test_identificacion_fuente_utilizada(self):
        """Demuestra identificacion precisa del ID y fuente documental utilizada."""
        resultado = consultar("protocolo autorizacion salida ipcs")
        self.assertEqual(resultado["estado"], "ENCONTRADA")
        ref = resultado["referencia"]
        self.assertIsNotNone(ref)
        self.assertEqual(ref["id"], "REF-SEC-003")
        self.assertEqual(ref["fuente"], "Reglas de Inferencia R1-R7 Semana 13")
        self.assertEqual(ref["titulo"], "Protocolo de autorizacion de salida vehicular IPCS")
        self.assertGreaterEqual(ref["coincidencias"], 3)

    def test_ignora_referencia_no_validada(self):
        """Demuestra que consultas que coinciden con borradores devuelven SIN_REFERENCIA."""
        # 'apertura', 'barrera', 'deteriorada' coinciden con REF-SEC-006 pero validada=False
        resultado = consultar("apertura de barrera deteriorada e ilegible")
        self.assertEqual(resultado["estado"], "SIN_REFERENCIA")
        self.assertIsNone(resultado["referencia"])
        self.assertIn("No hay evidencia validada", resultado["mensaje"])

    def test_pregunta_fuera_del_conocimiento(self):
        """Demuestra que una pregunta fuera de cobertura no inventa respuesta y se abstiene."""
        resultado = consultar("¿Dónde puedo pagar la matrícula académica universitaria?")
        self.assertEqual(resultado["estado"], "SIN_REFERENCIA")
        self.assertIsNone(resultado["referencia"])
        self.assertIn("No hay evidencia validada", resultado["mensaje"])

    def test_rechaza_consulta_vacia(self):
        """Demuestra que una consulta en blanco informa que debe ingresarse una pregunta."""
        resultado = consultar("     \t \n  ")
        self.assertEqual(resultado["estado"], "SIN_DATOS")
        self.assertEqual(resultado["mensaje"], "Escribe una consulta.")
        self.assertIsNone(resultado["referencia"])

    def test_seleccion_por_mayor_coincidencia(self):
        """Demuestra que se selecciona el candidato con mayor cantidad de palabras coincidentes."""
        # Coincide con multiples terminos de REF-SEC-002: umbral, calidad, imagen, confianza, ocr
        resultado = consultar("umbral de calidad de imagen y confianza ocr")
        self.assertEqual(resultado["estado"], "ENCONTRADA")
        self.assertEqual(resultado["referencia"]["id"], "REF-SEC-002")
        self.assertGreaterEqual(resultado["referencia"]["coincidencias"], 4)


if __name__ == "__main__":
    unittest.main()
