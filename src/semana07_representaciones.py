"""Representaciones de reconocimiento aplicadas a SecurityPlate."""

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

if __package__:
    from .securityplate_conocimiento import (
        ALFABETO_AUTOMATA,
        TRANSICIONES_AUTOMATA,
        aplicar_regla_autorizacion,
        construir_hechos_salida,
        convertir_booleano,
        acepta_protocolo_salida,
    )
else:
    from securityplate_conocimiento import (
        ALFABETO_AUTOMATA,
        TRANSICIONES_AUTOMATA,
        aplicar_regla_autorizacion,
        construir_hechos_salida,
        convertir_booleano,
        acepta_protocolo_salida,
    )


ROOT_DIR = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT_DIR / "data" / "casos_semana07.csv"
REPORT_PATH = ROOT_DIR / "reports" / "semana07.md"


@dataclass(frozen=True)
class CasoPrueba:
    """Caso de prueba cargado desde el CSV de Semana 7."""

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


def cargar_casos_prueba() -> list[CasoPrueba]:
    """Carga y valida los escenarios de reconocimiento desde el CSV."""
    if not CASES_PATH.exists():
        raise FileNotFoundError(f"No existe el archivo de casos: {CASES_PATH}")

    with CASES_PATH.open("r", encoding="utf-8-sig", newline="") as archivo:
        filas = csv.DictReader(archivo)
        campos_requeridos = {
            "id", "descripcion", "placa_coincide", "conductor_coincide",
            "confianza_ocr", "calidad_imagen", "registro_activo", "secuencia",
            "resultado_simbolico", "aceptada_automata",
        }
        if not filas.fieldnames or not campos_requeridos.issubset(filas.fieldnames):
            raise ValueError("El CSV no contiene todas las columnas requeridas.")

        casos = []
        for fila in filas:
            confianza = float(fila["confianza_ocr"])
            calidad = float(fila["calidad_imagen"])
            if not 0 <= confianza <= 1 or not 0 <= calidad <= 1:
                raise ValueError("confianza_ocr y calidad_imagen deben estar entre 0 y 1.")
            casos.append(
                CasoPrueba(
                    fila["id"], fila["descripcion"],
                    convertir_booleano(fila["placa_coincide"], "placa_coincide"),
                    convertir_booleano(fila["conductor_coincide"], "conductor_coincide"),
                    confianza, calidad,
                    convertir_booleano(fila["registro_activo"], "registro_activo"),
                    fila["secuencia"].strip(), fila["resultado_simbolico"].strip(),
                    convertir_booleano(fila["aceptada_automata"], "aceptada_automata"),
                )
            )
    if not casos:
        raise ValueError("El CSV de Semana 7 no contiene casos.")
    return casos


def vectorizar_caso(
    confianza_ocr: float,
    coincidencia_conductor: float,
    calidad_imagen: float,
    registro_activo: bool,
) -> np.ndarray:
    """Convierte un caso de salida en un vector de caracteristicas normalizado."""
    valores = np.array(
        [
            confianza_ocr,
            coincidencia_conductor,
            calidad_imagen,
            float(registro_activo),
        ],
        dtype=float,
    )
    if np.any(valores < 0) or np.any(valores > 1):
        raise ValueError("Las caracteristicas deben estar entre 0 y 1.")
    return valores


def distancia_euclidiana(actual: np.ndarray, referencia: np.ndarray) -> float:
    """Calcula la distancia entre dos casos representados numericamente."""
    if actual.shape != referencia.shape:
        raise ValueError("Los vectores deben tener la misma cantidad de caracteristicas.")
    return float(np.linalg.norm(actual - referencia))


def ejecutar_representacion_numerica() -> tuple[float, float]:
    """Compara un caso autorizado y un caso con alerta contra un patron valido."""
    patron_autorizado = vectorizar_caso(0.95, 0.92, 0.90, True)
    caso_autorizado = vectorizar_caso(0.93, 0.89, 0.88, True)
    caso_alerta = vectorizar_caso(0.61, 0.35, 0.52, False)

    distancia_autorizado = distancia_euclidiana(caso_autorizado, patron_autorizado)
    distancia_alerta = distancia_euclidiana(caso_alerta, patron_autorizado)
    return distancia_autorizado, distancia_alerta


def ejecutar_representacion_simbolica() -> tuple[set[str], str]:
    """Evalua un caso de salida mediante hechos y una regla."""
    hechos = construir_hechos_salida(True, True, 0.93, 0.88, True)
    return hechos, aplicar_regla_autorizacion(hechos)


def ejecutar_representacion_automata() -> dict[str, bool]:
    """Prueba secuencias validas e invalidas del protocolo de salida."""
    return {
        "IPCS": acepta_protocolo_salida("IPCS"),
        "IPSS": acepta_protocolo_salida("IPSS"),
        "IPS": acepta_protocolo_salida("IPS"),
    }


def evaluar_caso(caso: CasoPrueba) -> dict[str, object]:
    """Ejecuta las tres representaciones sobre un caso del CSV."""
    patron = vectorizar_caso(0.95, 0.92, 0.90, True)
    vector = vectorizar_caso(
        caso.confianza_ocr, float(caso.conductor_coincide),
        caso.calidad_imagen, caso.registro_activo,
    )
    hechos = construir_hechos_salida(
        caso.placa_coincide, caso.conductor_coincide,
        caso.confianza_ocr, caso.calidad_imagen, caso.registro_activo,
    )
    return {
        "distancia": distancia_euclidiana(vector, patron),
        "hechos": hechos,
        "conclusion": aplicar_regla_autorizacion(hechos),
        "aceptada": acepta_protocolo_salida(caso.secuencia),
    }


def generar_reporte(casos: list[CasoPrueba], resultados: list[dict[str, object]]) -> None:
    """Genera el reporte Markdown con la evidencia producida por el CSV."""
    lineas = [
        "# Semana 07 - Representaciones del reconocimiento", "",
        "Reporte generado automáticamente desde `data/casos_semana07.csv`.", "",
        "## Resultados de los casos de prueba", "",
        "| Caso | Distancia numérica | Regla simbólica | Autómata | Esperado | Estado |",
        "|---:|---:|---|---|---|---|",
    ]
    for caso, resultado in zip(casos, resultados):
        automata = "Aceptada" if resultado["aceptada"] else "Rechazada"
        esperado = "Aceptada" if caso.aceptada_automata else "Rechazada"
        estado = "Correcto" if (
            resultado["conclusion"] == caso.resultado_simbolico
            and resultado["aceptada"] == caso.aceptada_automata
        ) else "Revisar"
        lineas.append(
            f"| {caso.identificador} | {resultado['distancia']:.3f} | "
            f"`{resultado['conclusion']}` | {automata} | {esperado} | {estado} |"
        )
    correctos = sum(
        resultado["conclusion"] == caso.resultado_simbolico
        and resultado["aceptada"] == caso.aceptada_automata
        for caso, resultado in zip(casos, resultados)
    )
    lineas += [
        "", f"Casos correctos: **{correctos}/{len(casos)}**.", "",
        "## Interpretación", "",
        "- La distancia numérica compara cada vector con el patrón de salida autorizada.",
        "- La representación simbólica aplica hechos y la regla `autorizar_salida`.",
        "- El autómata acepta únicamente el protocolo `IPCS`.", "",
        "## Comparación de representaciones", "",
        "| Representación | Información utilizada | Puede reconocer | Ventaja | Limitación | Información que puede perderse |",
        "|---|---|---|---|---|---|",
        "| Numérica | Confianza OCR, conductor, imagen y registro | Similitud con un patrón válido | Compara magnitudes | No explica por sí sola la decisión | Significado de cada característica y contexto del caso |",
        "| Simbólica | Hechos y regla de autorización | Condiciones explícitas | Es interpretable y auditable | Depende de umbrales manuales | Gradaciones de confianza y relaciones no expresadas como hechos |",
        "| Autómata | Símbolos y estados del protocolo | Secuencias válidas | Controla el orden de eventos | No calcula confianza | Detalles visuales, niveles de confianza y causas de una transición |", "",
        "## Limitaciones", "",
        "La distancia depende de características normalizadas y no explica por sí sola una decisión. "
        "Los hechos usan umbrales definidos manualmente y el autómata verifica el orden, pero no la calidad de la evidencia.",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> None:
    casos = cargar_casos_prueba()
    resultados = [evaluar_caso(caso) for caso in casos]
    generar_reporte(casos, resultados)
    print("=== Semana 07 - Casos de prueba SecurityPlate ===")
    for caso, resultado in zip(casos, resultados):
        print(
            f"Caso {caso.identificador}: distancia={resultado['distancia']:.3f}, "
            f"regla={resultado['conclusion']}, "
            f"automata={'aceptada' if resultado['aceptada'] else 'rechazada'}"
        )
    print(f"Reporte generado: {REPORT_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
