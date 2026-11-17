"""Pruebas unitarias de la Base de Conocimiento de SecurityPlate.

Semana 15: Verificacion de persistencia, aislamiento de entorno mediante
bases temporales, reglas editoriales (BORRADOR -> VALIDADO) e integridad referencial.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import sys
import unittest

# Asegurar importacion del modulo desde src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from base_conocimiento import (  # noqa: E402
    buscar_articulos,
    conectar,
    inicializar,
    obtener_articulo,
    registrar_articulo,
    validar_articulo,
)


class TestBaseConocimientoSecurityPlate(unittest.TestCase):
    """Suite de pruebas unitarias sobre base de datos SQLite temporal."""

    def setUp(self):
        """Crea una base de datos SQLite temporal aislada para cada prueba."""
        self.temporal = TemporaryDirectory()
        self.ruta = Path(self.temporal.name) / "test_conocimiento.db"
        inicializar(self.ruta)

    def tearDown(self):
        """Limpia el directorio temporal al finalizar cada caso de prueba."""
        self.temporal.cleanup()

    def test_solo_articulos_validados(self):
        """Verifica que las consultas publicas solo retornen articulos con estado VALIDADO."""
        # Dominio 1: 'Vision por Computador' tiene 2 articulos iniciales VALIDADOS
        articulos_vision = buscar_articulos("Vision por Computador", ruta=self.ruta)
        self.assertEqual(len(articulos_vision), 2)
        for art in articulos_vision:
            self.assertEqual(art["estado"], "VALIDADO")
            self.assertIsNotNone(art["responsable"])
            self.assertIsNotNone(art["fuente"])

        # Dominio 3: 'Auditoria y Trazabilidad' solo tiene un articulo en estado BORRADOR
        articulos_auditoria = buscar_articulos("Auditoria y Trazabilidad", ruta=self.ruta)
        self.assertEqual(len(articulos_auditoria), 0)

    def test_ciclo_registro_validacion(self):
        """Verifica el ciclo completo: registro inicial como BORRADOR y publicacion tras validacion."""
        # 1. Registrar nuevo articulo (debe crearse como BORRADOR)
        nuevo_id = registrar_articulo(
            titulo="Protocolo de calibracion nocturna de camaras LPR",
            contenido="Configurar iluminadores infrarrojos y tiempo de exposicion 1/1000s para evitar desenfoque por movimiento de placas.",
            dominio_id=1,
            experto_id=1,
            fuente="Manual de Hardware SecurityPlate 2026",
            aplicacion_id=2,
            herramienta_id=2,
            ruta=self.ruta,
        )

        # 2. Verificar que se guardo internamente con estado BORRADOR
        articulo_creado = obtener_articulo(nuevo_id, ruta=self.ruta)
        self.assertEqual(articulo_creado["estado"], "BORRADOR")

        # 3. Comprobar que aun NO aparece en busqueda de articulos validados
        validados_antes = buscar_articulos("Vision por Computador", ruta=self.ruta)
        titulos_antes = [a["titulo"] for a in validados_antes]
        self.assertNotIn("Protocolo de calibracion nocturna de camaras LPR", titulos_antes)
        self.assertEqual(len(validados_antes), 2)

        # 4. Validar el articulo
        validar_articulo(nuevo_id, ruta=self.ruta)

        # 5. Comprobar que ahora SI aparece publicado
        validados_despues = buscar_articulos("Vision por Computador", ruta=self.ruta)
        titulos_despues = [a["titulo"] for a in validados_despues]
        self.assertIn("Protocolo de calibracion nocturna de camaras LPR", titulos_despues)
        self.assertEqual(len(validados_despues), 3)

        # 6. Verificar persistencia del nuevo estado
        articulo_actualizado = obtener_articulo(nuevo_id, ruta=self.ruta)
        self.assertEqual(articulo_actualizado["estado"], "VALIDADO")

    def test_dato_obligatorio(self):
        """Verifica que titulo, contenido o fuente vacios o con espacios lancen ValueError."""
        # Titulo vacio
        with self.assertRaises(ValueError):
            registrar_articulo(
                titulo="",
                contenido="Contenido de prueba",
                dominio_id=1,
                experto_id=1,
                fuente="Fuente valida",
                ruta=self.ruta,
            )

        # Contenido solo espacios
        with self.assertRaises(ValueError):
            registrar_articulo(
                titulo="Titulo valido",
                contenido="   \t\n  ",
                dominio_id=1,
                experto_id=1,
                fuente="Fuente valida",
                ruta=self.ruta,
            )

        # Fuente vacia
        with self.assertRaises(ValueError):
            registrar_articulo(
                titulo="Titulo valido",
                contenido="Contenido valido",
                dominio_id=1,
                experto_id=1,
                fuente="   ",
                ruta=self.ruta,
            )

    def test_referencia_dominio_inexistente(self):
        """Verifica que una clave foranea de dominio_id inexistente lance IntegrityError."""
        with self.assertRaises(sqlite3.IntegrityError):
            registrar_articulo(
                titulo="Articulo con dominio huerfano",
                contenido="Texto del articulo",
                dominio_id=999,  # No existe en la tabla dominio
                experto_id=1,
                fuente="Fuente de prueba",
                ruta=self.ruta,
            )

    def test_referencia_experto_inexistente(self):
        """Verifica que una clave foranea de experto_id inexistente lance IntegrityError."""
        with self.assertRaises(sqlite3.IntegrityError):
            registrar_articulo(
                titulo="Articulo con experto no registrado",
                contenido="Texto del articulo",
                dominio_id=1,
                experto_id=888,  # No existe en la tabla experto
                fuente="Fuente de prueba",
                ruta=self.ruta,
            )

    def test_id_no_existente_al_validar(self):
        """Verifica que intentar validar un articulo con ID inexistente lance ValueError."""
        with self.assertRaises(ValueError):
            validar_articulo(99999, ruta=self.ruta)

    def test_titulo_duplicado_en_mismo_dominio(self):
        """Verifica la restriccion UNIQUE(titulo, dominio_id) ante duplicados."""
        # Intentar insertar un articulo con un titulo que ya existe en el dominio 1
        with self.assertRaises(sqlite3.IntegrityError):
            registrar_articulo(
                titulo="Procedimiento de captura y preprocesamiento de placas",
                contenido="Texto duplicado",
                dominio_id=1,
                experto_id=1,
                fuente="Fuente duplicada",
                ruta=self.ruta,
            )


if __name__ == "__main__":
    unittest.main()
