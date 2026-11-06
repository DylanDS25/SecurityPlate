"""Motor generico de inferencia por reglas para SecurityPlate."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Regla:
    """Representa una regla positiva P1 AND ... AND Pn -> conclusion."""

    nombre: str
    premisas: frozenset[str]
    conclusion: str


def inferir(
    hechos_iniciales: set[str],
    reglas: list[Regla],
) -> tuple[set[str], list[str]]:
    """Aplica encadenamiento hacia adelante hasta alcanzar un punto fijo."""
    if not isinstance(hechos_iniciales, set):
        raise ValueError("Los hechos iniciales deben entregarse como un conjunto.")
    for regla in reglas:
        if not regla.premisas:
            raise ValueError("Una regla no puede tener premisas vacias.")

    hechos = set(hechos_iniciales)
    trazas: list[str] = []
    cambios = True
    while cambios:
        cambios = False
        for regla in reglas:
            if (
                regla.premisas.issubset(hechos)
                and regla.conclusion not in hechos
            ):
                hechos.add(regla.conclusion)
                premisas = ", ".join(sorted(regla.premisas))
                trazas.append(
                    f"{regla.nombre}: {premisas} => {regla.conclusion}"
                )
                cambios = True
    return hechos, trazas
