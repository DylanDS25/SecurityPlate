"""Red semantica aplicada a la verificacion de salida de SecurityPlate."""

import json
from pathlib import Path

if __package__:
    from .red_semantica import RedSemantica, Triple, interpretar
    from .securityplate_conocimiento import (
        IMAGE_SUFFICIENT_QUALITY,
        CasoSalida,
        acepta_protocolo_salida,
        cargar_casos_salida,
    )
else:
    from red_semantica import RedSemantica, Triple, interpretar
    from securityplate_conocimiento import (
        IMAGE_SUFFICIENT_QUALITY,
        CasoSalida,
        acepta_protocolo_salida,
        cargar_casos_salida,
    )


ROOT_DIR = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT_DIR / "artifacts" / "semana14_red_semantica.json"
REPORT_PATH = ROOT_DIR / "reports" / "reporte_semana14.md"


def construir_red_base() -> RedSemantica:
    """Construye el dominio propio de SecurityPlate y su jerarquia."""
    red = RedSemantica()
    hechos = [
        ("moto", "tiene", "placa"),
        ("vehiculo", "tiene", "placa"),
        ("placa", "requiere", "foto_placa"),
        ("foto_placa", "habilita", "comparacion_placa"),
        ("comparacion_placa", "produce", "resultado_visual"),
        ("resultado_visual", "puede_ser", "coincide"),
        ("resultado_visual", "puede_ser", "no_coincide"),
        ("comparacion_placa", "requiere_revision", "verificacion_manual"),
        ("personal_seguridad", "realiza", "verificacion_manual"),
        ("placa_moto", "es_un", "placa"),
        ("placa", "es_un", "identificador_vehicular"),
        ("identificador_vehicular", "es_un", "dato_verificacion"),
    ]
    for sujeto, relacion, objeto in hechos:
        red.agregar(sujeto, relacion, objeto)
    return red


def evaluar_caso(caso: CasoSalida) -> dict[str, object]:
    """Construye hechos y consultas semanticas para un caso de salida."""
    red = construir_red_base()
    hechos_explicitos: list[Triple] = []

    if caso.placa_coincide:
        hechos_explicitos.append(
            red.agregar("placa", "corresponde_a", "moto")
        )
    if caso.calidad_imagen >= IMAGE_SUFFICIENT_QUALITY:
        hechos_explicitos.append(
            red.agregar("foto_placa", "calidad_suficiente", "si")
        )
    else:
        hechos_explicitos.append(
            red.agregar("foto_placa", "calidad_suficiente", "no")
        )

    foto_adecuada = caso.calidad_imagen >= IMAGE_SUFFICIENT_QUALITY
    protocolo_aceptado = acepta_protocolo_salida(caso.secuencia)
    puede_autorizar = (
        foto_adecuada
        and caso.placa_coincide
        and caso.conductor_coincide
        and caso.registro_activo
        and protocolo_aceptado
    )
    if puede_autorizar:
        triple_inferido = red.agregar(
            "comparacion_placa",
            "resultado",
            "placa_corresponde_a_moto",
        )
        conclusion = "autorizar_salida"
        motivo = None
    else:
        triple_inferido = red.agregar(
            "comparacion_placa",
            "resultado",
            "llamar_personal_verificacion_manual",
        )
        conclusion = "llamar_personal_verificacion_manual"
        if not foto_adecuada:
            motivo = "La foto no alcanza el umbral de calidad 0.80."
        elif not caso.placa_coincide:
            motivo = (
                "La placa no corresponde al registro de la moto; no se puede "
                "demostrar la coincidencia."
            )
        elif not caso.conductor_coincide:
            motivo = (
                "El conductor no coincide; se requiere verificacion manual."
            )
        elif not caso.registro_activo:
            motivo = (
                "El vehiculo no tiene registro activo; se requiere "
                "verificacion manual."
            )
        else:
            motivo = (
                "El protocolo observado no coincide con IPCS; se requiere "
                "verificacion manual."
            )

    resultado_equivalente = (
        "autorizar_salida"
        if conclusion == "autorizar_salida"
        else "enviar_a_revision"
    )
    ruta_placa_moto = red.ruta_triplos("placa", "moto")
    ruta_revision = red.ruta_triplos(
        "comparacion_placa",
        "verificacion_manual",
    )
    jerarquia = red.hay_relacion_es_un(
        "placa_moto",
        "dato_verificacion",
    )

    return {
        "id": caso.identificador,
        "descripcion": caso.descripcion,
        "hechos_explicitos": [
            {
                "sujeto": triple.sujeto,
                "relacion": triple.relacion,
                "objeto": triple.objeto,
            }
            for triple in hechos_explicitos
        ],
        "hecho_inferido": {
            "sujeto": triple_inferido.sujeto,
            "relacion": triple_inferido.relacion,
            "objeto": triple_inferido.objeto,
        },
        "calidad_imagen": caso.calidad_imagen,
        "foto_adecuada": foto_adecuada,
        "placa_coincide": caso.placa_coincide,
        "ruta_placa_moto": (
            None
            if ruta_placa_moto is None
            else [
                {
                    "sujeto": triple.sujeto,
                    "relacion": triple.relacion,
                    "objeto": triple.objeto,
                }
                for triple in ruta_placa_moto
            ]
        ),
        "ruta_revision": (
            None
            if ruta_revision is None
            else [
                {
                    "sujeto": triple.sujeto,
                    "relacion": triple.relacion,
                    "objeto": triple.objeto,
                }
                for triple in ruta_revision
            ]
        ),
        "transitividad_placa_moto": jerarquia,
        "conclusion": conclusion,
        "motivo_revision": motivo,
        "resultado_esperado": caso.resultado_simbolico,
        "estado": (
            "Correcto"
            if resultado_equivalente == caso.resultado_simbolico
            else "Revisar"
        ),
    }


def generar_artefacto(
    casos: list[CasoSalida] | None = None,
) -> dict[str, object]:
    casos_evaluados = casos if casos is not None else cargar_casos_salida()
    resultados = [evaluar_caso(caso) for caso in casos_evaluados]
    red = construir_red_base()
    artefacto: dict[str, object] = {
        "titulo": "Semana 14 - Redes semanticas SecurityPlate",
        "semana": 14,
        "dominio": "verificacion de salida de moto",
        "entrada": "data/casos_semana07.csv",
        "umbral_foto_adecuada": IMAGE_SUFFICIENT_QUALITY,
        "conceptos": [
            "moto",
            "vehiculo",
            "placa",
            "foto_placa",
            "comparacion_placa",
            "resultado_visual",
            "personal_seguridad",
            "verificacion_manual",
        ],
        "triples_explicitamente_modelados": [
            {
                "sujeto": triple.sujeto,
                "relacion": triple.relacion,
                "objeto": triple.objeto,
            }
            for triple in sorted(
                red.triples,
                key=lambda item: (
                    item.sujeto,
                    item.relacion,
                    item.objeto,
                ),
            )
        ],
        "casos": resultados,
        "consulta_sin_evidencia": {
            "pregunta": "¿La placa corresponde al vehiculo 999?",
            "respuesta": None,
            "interpretacion": (
                "No existe evidencia suficiente; la ausencia de un triple "
                "no constituye una negacion universal."
            ),
        },
        "resumen": {
            "total": len(resultados),
            "correctos": sum(
                resultado["estado"] == "Correcto"
                for resultado in resultados
            ),
        },
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(
        json.dumps(artefacto, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    generar_reporte(artefacto)
    return artefacto


def generar_reporte(artefacto: dict[str, object]) -> None:
    casos = artefacto["casos"]
    lines = [
        "# Semana 14 - Redes semanticas SecurityPlate",
        "",
        "## Objetivo",
        "",
        "Representar conceptos propios de SecurityPlate mediante nodos, aristas",
        "dirigidas y triples. La red interpreta frases simples, consulta rutas,",
        "demuestra jerarquia con `es_un`, herencia explicita y control de ciclos.",
        "",
        "## Conceptos",
        "",
        ", ".join(artefacto["conceptos"]) + ".",
        "",
        "## Umbral",
        "",
        f"Una foto se considera adecuada con calidad >= "
        f"{artefacto['umbral_foto_adecuada']}.",
        "",
        "## Relacion y conclusion",
        "",
        "Si la foto es adecuada y la placa coincide, el sistema infiere",
        "`placa_corresponde_a_moto`. En otro caso se infiere",
        "`llamar_personal_verificacion_manual`.",
        "",
        "## Resultados por caso",
        "",
        "| Caso | Placa coincide | Foto adecuada | Conclusion | Estado |",
        "|---|---|---|---|---|",
    ]
    for caso in casos:
        lines.append(
            f"| {caso['id']} | {caso['placa_coincide']} | "
            f"{caso['foto_adecuada']} | {caso['conclusion']} | "
            f"{caso['estado']} |"
        )
    lines += [
        "",
        "## Evidencia de entrada y salida",
        "",
        "- Entrada: `data/casos_semana07.csv`.",
        "- JSON: `artifacts/semana14_red_semantica.json`.",
        "- Motor: `src/red_semantica.py`.",
        "- Integracion: `src/semana14_redes_semanticas.py`.",
        "",
        "## Limitaciones",
        "",
        "- El parser reconoce patrones simples, no lenguaje natural general.",
        "- Una consulta sin evidencia devuelve resultado no demostrado.",
        "- La transitividad se aplica solamente a relaciones `es_un`.",
        "- La revision manual conserva la decision humana como validacion final.",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
