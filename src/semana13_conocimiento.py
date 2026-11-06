"""Ingenieria del conocimiento aplicada al flujo de salida de SecurityPlate."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

if __package__:
    from .securityplate_conocimiento import (
        CasoSalida,
        acepta_protocolo_salida,
        cargar_casos_salida,
        construir_hechos_salida,
    )
    from .motor_inferencia import Regla, inferir
else:
    from securityplate_conocimiento import (
        CasoSalida,
        acepta_protocolo_salida,
        cargar_casos_salida,
        construir_hechos_salida,
    )
    from motor_inferencia import Regla, inferir


ROOT_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
ARTIFACT_PATH = ARTIFACTS_DIR / "semana13_inferencia.json"
REPORT_PATH = ROOT_DIR / "reports" / "semana13.md"
EXACT_REPORT_PATH = ROOT_DIR / "reports" / "reporte_semana13.md"


def construir_reglas_securityplate() -> list[Regla]:
    """Construye las reglas declarativas del flujo de salida."""
    return [
        Regla(
            "R1",
            frozenset({"placa_coincide", "conductor_coincide"}),
            "correspondencia_confirmada",
        ),
        Regla(
            "R2",
            frozenset({"confianza_ocr_alta", "imagen_suficiente"}),
            "lectura_visual_suficiente",
        ),
        Regla(
            "R3",
            frozenset({"registro_activo"}),
            "registro_confirmado",
        ),
        Regla(
            "R4",
            frozenset({"correspondencia_confirmada", "lectura_visual_suficiente"}),
            "identidad_visual_confirmada",
        ),
        Regla(
            "R5",
            frozenset({"identidad_visual_confirmada", "registro_confirmado"}),
            "evidencia_salida_suficiente",
        ),
        Regla(
            "R6",
            frozenset({"evidencia_salida_suficiente", "protocolo_aceptado"}),
            "operacion_salida_habilitada",
        ),
        Regla(
            "R7",
            frozenset({"operacion_salida_habilitada"}),
            "autorizar_salida",
        ),
    ]


def evaluar_caso(caso: CasoSalida) -> dict[str, object]:
    """Evalua un caso con hechos existentes y agrega el hecho del protocolo."""
    hechos_iniciales = construir_hechos_salida(
        caso.placa_coincide,
        caso.conductor_coincide,
        caso.confianza_ocr,
        caso.calidad_imagen,
        caso.registro_activo,
    )
    protocolo_aceptado = acepta_protocolo_salida(caso.secuencia)
    if protocolo_aceptado:
        hechos_iniciales.add("protocolo_aceptado")

    hechos_finales, trazas = inferir(
        hechos_iniciales,
        construir_reglas_securityplate(),
    )
    conclusion = (
        "autorizar_salida"
        if "autorizar_salida" in hechos_finales
        else "enviar_a_revision"
    )

    return {
        "id": caso.identificador,
        "descripcion": caso.descripcion,
        "hechos_iniciales": sorted(hechos_iniciales),
        "hechos_finales": sorted(hechos_finales),
        "trazas": trazas,
        "protocolo": caso.secuencia,
        "protocolo_aceptado": protocolo_aceptado,
        "conclusion_inferida": conclusion,
        "resultado_esperado": caso.resultado_simbolico,
        "protocolo_esperado": caso.aceptada_automata,
        "estado": (
            "Correcto"
            if conclusion == caso.resultado_simbolico
            and protocolo_aceptado == caso.aceptada_automata
            else "Revisar"
        ),
        "observaciones": {
            "confianza_ocr": caso.confianza_ocr,
            "calidad_imagen": caso.calidad_imagen,
            "placa_coincide": caso.placa_coincide,
            "conductor_coincide": caso.conductor_coincide,
            "registro_activo": caso.registro_activo,
        },
    }


def generar_artefacto(casos: list[CasoSalida] | None = None) -> dict[str, object]:
    """Evalua casos y genera evidencia JSON reproducible."""
    casos_evaluados = casos if casos is not None else cargar_casos_salida()
    resultados = [evaluar_caso(caso) for caso in casos_evaluados]
    correctos = sum(
        resultado["estado"] == "Correcto"
        for resultado in resultados
    )
    artefacto: dict[str, object] = {
        "titulo": "Semana 13 - Ingenieria del conocimiento SecurityPlate",
        "entrada": "data/casos_semana07.csv",
        "flujo": "salida",
        "umbrales": {
            "confianza_ocr_alta": 0.85,
            "imagen_suficiente": 0.80,
            "protocolo_valido": "IPCS",
        },
        "reglas": [
            {
                "nombre": regla.nombre,
                "premisas": sorted(regla.premisas),
                "conclusion": regla.conclusion,
            }
            for regla in construir_reglas_securityplate()
        ],
        "casos": resultados,
        "resumen": {
            "total": len(resultados),
            "correctos": correctos,
            "incorrectos": len(resultados) - correctos,
        },
    }
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(
        json.dumps(artefacto, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    generar_reporte(artefacto)
    return artefacto


def generar_reporte(artefacto: dict[str, object]) -> None:
    """Genera el reporte tecnico derivado del artefacto JSON."""
    resumen = artefacto["resumen"]
    casos = artefacto["casos"]
    lines = [
        "# Semana 13 - Ingenieria del conocimiento SecurityPlate",
        "",
        "## 1. Analisis del dominio",
        "",
        "**Problema:** determinar si una salida vehicular posee evidencia suficiente",
        "para autorizarla o debe enviarse a revision manual.",
        "",
        "**Conceptos principales:** hechos, regla, premisa, conclusion, protocolo",
        "`IPCS`, encadenamiento hacia adelante, punto fijo y trazabilidad.",
        "",
        "**Hechos iniciales:** coincidencia de placa, coincidencia de conductor,",
        "confianza OCR, calidad de imagen, registro activo y protocolo observado.",
        "",
        "**Conclusion esperada:** `autorizar_salida` solo cuando las siete reglas",
        "pueden encadenarse; de lo contrario, `enviar_a_revision`.",
        "",
        "## Alcance",
        "",
        "Practica de inferencia limitada al flujo de salida. La entrada es "
        "`data/casos_semana07.csv`; no sustituye ni modifica el modelo de Semana 07.",
        "",
        "## 2. Reglas logicas",
        "",
        "| Regla | Premisas | Conclusion |",
        "|---|---|---|",
    ]
    for regla in artefacto["reglas"]:
        lines.append(
            f"| {regla['nombre']} | {'; '.join(regla['premisas'])} | "
            f"{regla['conclusion']} |"
        )
    lines += [
        "",
        "## Resultados",
        "",
        "| Caso | Protocolo | Conclusion | Esperado | Estado |",
        "|---|---|---|---|---|",
    ]
    for caso in casos:
        lines.append(
            f"| {caso['id']} | {caso['protocolo']} | "
            f"{caso['conclusion_inferida']} | {caso['resultado_esperado']} | "
            f"{caso['estado']} |"
        )
    lines += [
        "",
        "## 3. Pruebas funcionales",
        "",
        "- **Caso demostrado:** el caso 1 activa las siete reglas y concluye",
        "  `autorizar_salida`.",
        "- **Caso no demostrado:** la evidencia incompleta concluye",
        "  `enviar_a_revision`; la conclusion positiva no se inventa.",
        "- **Conservacion:** `inferir` copia el conjunto inicial y no lo modifica.",
        "- **Ciclos:** el motor repite hasta punto fijo y evita conclusiones duplicadas.",
        "- **Validacion:** unittest cubre conclusiones, conservacion, duplicados,",
        "  premisas vacias y reglas circulares.",
        "",
        "## 4. Trazabilidad por caso",
        "",
    ]
    for caso in casos:
        lines.append(f"### Caso {caso['id']}: {caso['descripcion']}")
        lines.append("")
        lines.append(
            "**Hechos iniciales:** " + ", ".join(caso["hechos_iniciales"]) + "."
        )
        lines.append("")
        lines.append("**Trazas:**")
        lines.append("")
        if caso["trazas"]:
            for trace in caso["trazas"]:
                lines.append(f"- `{trace}`")
        else:
            lines.append("- Ninguna regla pudo activarse.")
        lines.append("")
        lines.append(
            f"**Conclusion:** `{caso['conclusion_inferida']}`. "
            f"**Estado:** {caso['estado']}."
        )
        lines.append("")
    lines += [
        f"Casos correctos: **{resumen['correctos']}/{resumen['total']}**.",
        "",
        "## Limite",
        "",
        "El motor verifica la aplicacion reproducible de reglas. No valida por si "
        "solo que las reglas representen una politica real de autorizacion.",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(report, encoding="utf-8")
    EXACT_REPORT_PATH.write_text(report, encoding="utf-8")


def ejecutar_servidor(host: str = "127.0.0.1", port: int = 8001) -> None:
    """Sirve el dashboard independiente desde la raiz del repositorio."""
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT_DIR))
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Dashboard Semana 13: http://{host}:{port}/dashboard_semana13/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    artefacto = generar_artefacto()
    print(
        "Semana 13: "
        f"{artefacto['resumen']['correctos']}/{artefacto['resumen']['total']} casos correctos"
    )
    print(f"Artefacto generado: {ARTIFACT_PATH.relative_to(ROOT_DIR)}")

    for caso in artefacto["casos"][:2]:
        print(f"\nCaso {caso['id']}: {caso['descripcion']}")
        print("Hechos iniciales:", ", ".join(caso["hechos_iniciales"]))
        for trace in caso["trazas"]:
            print("Trazabilidad:", trace)
        print("Conclusion:", caso["conclusion_inferida"])

    if args.serve:
        ejecutar_servidor(args.host, args.port)


if __name__ == "__main__":
    main()
