"""Interfaz de consola para el motor de referencia de SecurityPlate.

Semana 16: Diseño de sistemas inteligentes - Arquitectura y motor de referencia.
Permite ingresar preguntas, consultar fuentes aprobadas y mostrar procedencia.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from motor_referencia import consultar


def ejecutar_interactivo() -> None:
    """Bucle interactivo de atencion al usuario."""
    print("=" * 70)
    print("ASISTENTE DE CONSULTA TECNICA - PROYECTO SECURITYPLATE")
    print("Semana 16: Arquitectura de Sistemas Inteligentes y Motor de Referencia")
    print("=" * 70)
    print("Escribe tu pregunta sobre el sistema o escribe 'salir' para terminar.\n")

    while True:
        try:
            pregunta = input("Tu pregunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSesion finalizada.")
            break

        if pregunta.casefold() == "salir":
            print("Cerrando asistente. Hasta pronto.")
            break

        resultado = consultar(pregunta)
        print("Estado   :", resultado["estado"])
        print("Respuesta:", resultado["mensaje"])
        if resultado["referencia"] is not None:
            ref = resultado["referencia"]
            print(f"Fuente   : {ref['id']} - {ref['fuente']}")
            print(f"Detalle  : {ref['titulo']} (coincidencias: {ref['coincidencias']})")
        print("-" * 70)


def ejecutar_demostracion() -> None:
    """Ejecuta una demostracion controlada de los escenarios de la arquitectura."""
    escenarios = [
        (
            "Consulta exitosa sobre captura y filtros (VALIDADA)",
            "¿Cómo se realiza la captura y el preprocesamiento de la placa con la cámara?",
        ),
        (
            "Consulta sobre umbrales de decision visual (VALIDADA)",
            "¿Cuáles son los umbrales de calidad de imagen y confianza para el reconocimiento OCR?",
        ),
        (
            "Consulta sobre protocolo de salida vehicular (VALIDADA)",
            "¿Cómo funciona la secuencia y el protocolo de autorizacion de salida IPCS?",
        ),
        (
            "Consulta que coincide solo con borrador no aprobado (EXCLUSION)",
            "apertura de barrera deteriorada e ilegible",
        ),
        (
            "Consulta fuera del dominio de conocimiento (ABSTENCION)",
            "¿Dónde puedo consultar el calendario de matrícula académica?",
        ),
        (
            "Consulta vacia o con espacios en blanco (CONTROL DE ENTRADA)",
            "      ",
        ),
    ]

    print("=" * 70)
    print("DEMOSTRACION DE ARQUITECTURA Y MOTOR DE REFERENCIA - SECURITYPLATE")
    print("=" * 70)

    for i, (nombre, pregunta) in enumerate(escenarios, 1):
        print(f"\n[Escenario {i}]: {nombre}")
        print(f"Entrada  : '{pregunta}'")
        res = consultar(pregunta)
        print(f"Estado   : {res['estado']}")
        print(f"Respuesta: {res['mensaje']}")
        if res["referencia"]:
            ref = res["referencia"]
            print(f"Fuente   : {ref['id']} - {ref['fuente']} | Coincidencias: {ref['coincidencias']}")
        print("-" * 70)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in ("--demo", "-d"):
        ejecutar_demostracion()
    else:
        # Si no esta en una terminal interactiva (stdin redirigido), correr demo
        if not sys.stdin.isatty():
            ejecutar_demostracion()
        else:
            ejecutar_interactivo()


if __name__ == "__main__":
    main()
