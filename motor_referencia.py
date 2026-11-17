"""Motor de referencia para el proyecto SecurityPlate.

Semana 16: Diseño de sistemas inteligentes - Arquitectura y motor de referencia.
Responsable de normalizar texto, comparar palabras clave, evaluar coincidencias,
excluir registros no validados y seleccionar la referencia con trazabilidad.
"""

from pathlib import Path
import re
import sys
import unicodedata

# Asegurar importacion portable de base_conocimiento
RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

from base_conocimiento import REFERENCIAS


def normalizar(texto: str) -> set[str]:
    """Convierte texto a palabras alfanumericas sin mayusculas ni marcas de acento."""
    descompuesto = unicodedata.normalize("NFD", texto.casefold())
    sin_tildes = "".join(
        caracter for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    )
    return set(re.findall(r"[a-z0-9]+", sin_tildes))


def consultar(pregunta: str) -> dict:
    """Busca y selecciona la referencia validada con mas coincidencias de palabras clave.

    Retorna un diccionario estructurado con:
    - estado: 'ENCONTRADA', 'SIN_REFERENCIA' o 'SIN_DATOS'
    - mensaje: Texto de respuesta o indicacion de abstencion
    - referencia: Metadatos de la fuente aprobada (id, titulo, fuente, coincidencias) o None
    """
    palabras = normalizar(pregunta)
    if not palabras:
        return {
            "estado": "SIN_DATOS",
            "mensaje": "Escribe una consulta.",
            "referencia": None,
        }

    candidatos = []
    for referencia in REFERENCIAS:
        # Excluir explicitamente cualquier referencia no aprobada
        if not referencia["validada"]:
            continue
        coincidencias = palabras.intersection(referencia["claves"])
        if coincidencias:
            candidatos.append((len(coincidencias), referencia["id"], referencia))

    if not candidatos:
        return {
            "estado": "SIN_REFERENCIA",
            "mensaje": "No hay evidencia validada; consulta con una persona responsable.",
            "referencia": None,
        }

    # Ordenar por coincidencias descendentes (-item[0]) y desempate por id ascendente (item[1])
    candidatos.sort(key=lambda item: (-item[0], item[1]))
    puntuacion, _, mejor = candidatos[0]

    return {
        "estado": "ENCONTRADA",
        "mensaje": mejor["respuesta"],
        "referencia": {
            "id": mejor["id"],
            "titulo": mejor["titulo"],
            "fuente": mejor["fuente"],
            "coincidencias": puntuacion,
        },
    }
