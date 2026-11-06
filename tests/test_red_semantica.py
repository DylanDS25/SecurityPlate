"""Pruebas de la red semantica de SecurityPlate."""

import unittest

from src.red_semantica import (
    RedSemantica,
    Triple,
    interpretar,
    normalizar,
)


class RedSemanticaTests(unittest.TestCase):
    def test_agrega_y_consulta_un_triple(self) -> None:
        red = RedSemantica()
        red.agregar("La moto", "tiene", "una placa")

        self.assertTrue(red.existe("moto", "tiene", "placa"))
        self.assertEqual(red.consultar_relacion("moto", "tiene"), ["placa"])

    def test_no_duplica_triples(self) -> None:
        red = RedSemantica()
        red.agregar("moto", "tiene", "placa")
        red.agregar("moto", "tiene", "placa")

        self.assertEqual(len(red.triples), 1)

    def test_normaliza_tildes_y_mayusculas(self) -> None:
        self.assertEqual(normalizar("  ¡Placa Moto!  "), "placa moto")

    def test_interpreta_oracion_simple(self) -> None:
        triple = interpretar("La placa corresponde a la moto")
        self.assertEqual(
            triple,
            Triple("placa", "corresponde_a", "moto"),
        )

    def test_rechaza_oracion_no_admitida(self) -> None:
        with self.assertRaisesRegex(ValueError, "no coincide"):
            interpretar("La moto conduce alegremente por la ciudad")

    def test_consulta_sin_evidencia_devuelve_lista_vacia(self) -> None:
        red = RedSemantica()
        self.assertEqual(red.consultar_relacion("placa_999", "corresponde_a"), [])

    def test_busca_ruta_y_evita_ciclos(self) -> None:
        red = RedSemantica()
        red.agregar("placa_moto", "es_un", "placa")
        red.agregar("placa", "es_un", "identificador_vehicular")
        red.agregar("identificador_vehicular", "es_un", "dato_verificacion")
        red.agregar("dato_verificacion", "es_un", "placa_moto")

        self.assertTrue(
            red.hay_relacion_es_un(
                "placa_moto",
                "dato_verificacion",
            )
        )
        ruta = red.ruta_triplos("placa_moto", "dato_verificacion")
        self.assertIsNotNone(ruta)
        self.assertLessEqual(len(ruta or []), 3)

    def test_no_confunde_otra_relacion_con_jerarquia(self) -> None:
        red = RedSemantica()
        red.agregar("placa_moto", "tiene", "foto")
        red.agregar("foto", "permite", "comparacion")

        self.assertFalse(
            red.hay_relacion_es_un("placa_moto", "comparacion")
        )

    def test_hereda_propiedad_desde_un_ancestro(self) -> None:
        red = RedSemantica()
        red.agregar("placa_moto", "es_un", "placa")
        red.agregar("placa", "requiere", "foto_placa")

        self.assertEqual(
            red.propiedad_heredada("placa_moto", "requiere"),
            ["foto_placa"],
        )

    def test_valida_triple_vacio(self) -> None:
        with self.assertRaisesRegex(ValueError, "sujeto"):
            Triple("", "tiene", "placa")


if __name__ == "__main__":
    unittest.main()
