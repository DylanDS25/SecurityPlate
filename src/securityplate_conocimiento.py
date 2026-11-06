"""Utilidades compartidas para representar y evaluar la salida de SecurityPlate."""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT_DIR = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT_DIR / "data" / "casos_semana07.csv"
OCR_HIGH_CONFIDENCE = 0.85
IMAGE_SUFFICIENT_QUALITY = 0.80
ALFABETO_AUTOMATA = {"I", "P", "C", "S"}
TRANSICIONES_AUTOMATA = {
    ("q0", "I"): "q1",
    ("q1", "P"): "q2",
    ("q2", "C"): "q3",
    ("q3", "S"): "q4",
}


@dataclass(frozen=True)
class CasoSalida:
    """Caso de salida compartido por las semanas 07 y 13."""

    identificador: str
    descripcion: str
    placa_coincide: bool
    conductor_coincide: bool
    confianza_ocr: float
    calidad_imagen: float
    registro_activo: bool
    secuencia: str
    resultado_simbolico: str
    aceptada_automata: bool


def convertir_booleano(valor: str, campo: str) -> bool:
    """Convierte si/no y rechaza valores ambiguos."""
    normalizado = valor.strip().lower()
    if normalizado == "si":
        return True
    if normalizado == "no":
        return False
    raise ValueError(f"El campo {campo} debe ser 'si' o 'no'.")


def cargar_casos_salida(path: Path | None = None) -> list[CasoSalida]:
    """Carga y valida los casos existentes de salida de SecurityPlate."""
    cases_path = path or CASES_PATH
    if not cases_path.exists():
        raise FileNotFoundError(f"No existe el archivo de casos: {cases_path}")

    required = {
        "id", "descripcion", "placa_coincide", "conductor_coincide",
        "confianza_ocr", "calidad_imagen", "registro_activo", "secuencia",
        "resultado_simbolico", "aceptada_automata",
    }
    with cases_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("El CSV no contiene todas las columnas requeridas.")

        casos: list[CasoSalida] = []
        for row in reader:
            confianza = float(row["confianza_ocr"])
            calidad = float(row["calidad_imagen"])
            if not 0 <= confianza <= 1 or not 0 <= calidad <= 1:
                raise ValueError("confianza_ocr y calidad_imagen deben estar entre 0 y 1.")
            casos.append(
                CasoSalida(
                    identificador=row["id"],
                    descripcion=row["descripcion"],
                    placa_coincide=convertir_booleano(
                        row["placa_coincide"], "placa_coincide"
                    ),
                    conductor_coincide=convertir_booleano(
                        row["conductor_coincide"], "conductor_coincide"
                    ),
                    confianza_ocr=confianza,
                    calidad_imagen=calidad,
                    registro_activo=convertir_booleano(
                        row["registro_activo"], "registro_activo"
                    ),
                    secuencia=row["secuencia"].strip(),
                    resultado_simbolico=row["resultado_simbolico"].strip(),
                    aceptada_automata=convertir_booleano(
                        row["aceptada_automata"], "aceptada_automata"
                    ),
                )
            )
    if not casos:
        raise ValueError("El CSV de casos de salida no contiene casos.")
    return casos


def construir_hechos_salida(
    placa_coincide: bool,
    conductor_coincide: bool,
    confianza_ocr: float,
    calidad_imagen: float,
    registro_activo: bool,
) -> set[str]:
    """Convierte observaciones numéricas y booleanas en hechos positivos."""
    hechos: set[str] = set()
    if placa_coincide:
        hechos.add("placa_coincide")
    if conductor_coincide:
        hechos.add("conductor_coincide")
    if confianza_ocr >= OCR_HIGH_CONFIDENCE:
        hechos.add("confianza_ocr_alta")
    if calidad_imagen >= IMAGE_SUFFICIENT_QUALITY:
        hechos.add("imagen_suficiente")
    if registro_activo:
        hechos.add("registro_activo")
    return hechos


def aplicar_regla_autorizacion(hechos: Iterable[str]) -> str:
    """Mantiene compatible la decisión simbólica de Semana 07."""
    condiciones = {
        "placa_coincide",
        "conductor_coincide",
        "confianza_ocr_alta",
        "imagen_suficiente",
        "registro_activo",
    }
    if condiciones.issubset(set(hechos)):
        return "autorizar_salida"
    return "enviar_a_revision"


def acepta_protocolo_salida(secuencia: str) -> bool:
    """Acepta solamente la secuencia IPCS completa."""
    estado = "q0"
    for simbolo in secuencia:
        if simbolo not in ALFABETO_AUTOMATA:
            return False
        estado = TRANSICIONES_AUTOMATA.get((estado, simbolo), "rechazo")
        if estado == "rechazo":
            return False
    return estado == "q4"
