"""Demostracion de la red semantica de la Semana 14."""

from src.red_semantica import RedSemantica, interpretar
from src.semana14_redes_semanticas import (
    construir_red_base,
    generar_artefacto,
)


def main() -> None:
    print("Semana 14 - Red semantica SecurityPlate")
    print("--------------------------------------")

    red = construir_red_base()
    triple = interpretar("La placa corresponde a la moto")
    red.agregar_triple(triple)
    print(f"Triple interpretado: {triple}")

    print(
        "Consulta transitiva placa_moto -> dato_verificacion:",
        red.hay_relacion_es_un(
            "placa_moto",
            "dato_verificacion",
        ),
    )
    print(
        "Propiedades heredadas por placa_moto (requiere):",
        red.propiedad_heredada("placa_moto", "requiere"),
    )

    artefacto = generar_artefacto()
    print("Casos evaluados:")
    for caso in artefacto["casos"]:
        print(
            f"- Caso {caso['id']}: {caso['conclusion']} "
            f"({caso['estado']})"
        )
    print(
        "Evidencia JSON: artifacts/semana14_red_semantica.json"
    )


if __name__ == "__main__":
    main()
