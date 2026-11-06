"""Red semantica reutilizable para conceptos SecurityPlate."""

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Triple:
    sujeto: str
    relacion: str
    objeto: str

    def __post_init__(self) -> None:
        for campo, valor in (
            ("sujeto", self.sujeto),
            ("relacion", self.relacion),
            ("objeto", self.objeto),
        ):
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"El {campo} del triple no puede estar vacio.")


def normalizar(texto: str) -> str:
    """Normaliza texto para comparacion y construccion de triples."""
    if not isinstance(texto, str):
        raise ValueError("El texto debe ser una cadena.")
    base = unicodedata.normalize("NFD", texto.strip().casefold())
    sin_tildes = "".join(
        caracter
        for caracter in base
        if unicodedata.category(caracter) != "Mn"
    )
    sin_tildes = re.sub(r"[^\w\s]", " ", sin_tildes)
    return re.sub(r"\s+", " ", sin_tildes).strip()


def _espacios_a_guiones(texto: str) -> str:
    normalizado = normalizar(texto)
    normalizado = re.sub(
        r"^(?:la|el|los|las|un|una|unos|unas)\s+",
        "",
        normalizado,
    )
    return "_".join(normalizado.split())


def interpretar(oracion: str) -> Triple:
    """Convierte un patron simple aceptado a un triple."""
    texto = normalizar(oracion).strip()
    patrones = {
        r"^la moto tiene una placa$": ("moto", "tiene", "placa"),
        r"^la placa corresponde a la moto$": (
            "placa",
            "corresponde_a",
            "moto",
        ),
        r"^la foto tiene calidad suficiente$": (
            "foto_placa",
            "calidad_suficiente",
            "si",
        ),
        r"^la placa requiere una foto adecuada$": (
            "placa",
            "requiere",
            "foto_adecuada",
        ),
        r"^la comparacion requiere revision manual$": (
            "comparacion_placa",
            "requiere_revision",
            "verificacion_manual",
        ),
        r"^la placa moto es un identificador vehicular$": (
            "placa_moto",
            "es_un",
            "identificador_vehicular",
        ),
    }
    for patron, componentes in patrones.items():
        if re.match(patron, texto):
            return Triple(*componentes)
    raise ValueError(
        "La oracion no coincide con un patron admitido por la red "
        "semantica de SecurityPlate."
    )


class RedSemantica:
    """Grafo dirigido de conceptos y relaciones."""

    def __init__(self) -> None:
        self._triples: set[Triple] = set()
        self._nodos: set[str] = set()

    @property
    def triples(self) -> frozenset[Triple]:
        return frozenset(self._triples)

    @property
    def nodos(self) -> frozenset[str]:
        return frozenset(self._nodos)

    def agregar(self, sujeto: str, relacion: str, objeto: str) -> Triple:
        triple = Triple(
            _espacios_a_guiones(sujeto),
            _espacios_a_guiones(relacion),
            _espacios_a_guiones(objeto),
        )
        self._triples.add(triple)
        self._nodos.update((triple.sujeto, triple.objeto))
        return triple

    def agregar_triple(self, triple: Triple) -> Triple:
        return self.agregar(triple.sujeto, triple.relacion, triple.objeto)

    def existe(self, sujeto: str, relacion: str, objeto: str) -> bool:
        triple = Triple(
            _espacios_a_guiones(sujeto),
            _espacios_a_guiones(relacion),
            _espacios_a_guiones(objeto),
        )
        return triple in self._triples

    def consultar_relacion(self, sujeto: str, relacion: str) -> list[str]:
        sujeto_normalizado = _espacios_a_guiones(sujeto)
        relacion_normalizada = _espacios_a_guiones(relacion)
        return sorted(
            triple.objeto
            for triple in self._triples
            if triple.sujeto == sujeto_normalizado
            and triple.relacion == relacion_normalizada
        )

    def vecinos(self, nodo: str) -> list[str]:
        nodo_normalizado = _espacios_a_guiones(nodo)
        return sorted(
            {
                triple.objeto
                for triple in self._triples
                if triple.sujeto == nodo_normalizado
            }
        )

    def ruta(self, origen: str, destino: str) -> list[str] | None:
        """Busca una ruta dirigida usando visitados para evitar ciclos."""
        inicio = _espacios_a_guiones(origen)
        fin = _espacios_a_guiones(destino)
        if inicio == fin:
            return [inicio]

        cola: list[tuple[str, list[str]]] = [(inicio, [inicio])]
        visitados = {inicio}
        while cola:
            actual, camino = cola.pop(0)
            for vecino in self.vecinos(actual):
                if vecino == fin:
                    return camino + [vecino]
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append((vecino, camino + [vecino]))
        return None

    def ruta_triplos(
        self, origen: str, destino: str
    ) -> list[Triple] | None:
        inicio = _espacios_a_guiones(origen)
        fin = _espacios_a_guiones(destino)
        cola: list[tuple[str, list[Triple]]] = [(inicio, [])]
        visitados = {inicio}
        while cola:
            actual, ruta = cola.pop(0)
            for triple in sorted(
                self._triples,
                key=lambda item: (
                    item.sujeto,
                    item.relacion,
                    item.objeto,
                ),
            ):
                if triple.sujeto != actual:
                    continue
                if triple.objeto in visitados:
                    continue
                nueva_ruta = ruta + [triple]
                if triple.objeto == fin:
                    return nueva_ruta
                visitados.add(triple.objeto)
                cola.append((triple.objeto, nueva_ruta))
        return None

    def hay_relacion_es_un(self, origen: str, destino: str) -> bool:
        """Consulta transitividad solo para relaciones jerarquicas es_un."""
        inicio = _espacios_a_guiones(origen)
        fin = _espacios_a_guiones(destino)
        if inicio == fin:
            return True
        cola = [inicio]
        visitados = {inicio}
        while cola:
            actual = cola.pop(0)
            for triple in self._triples:
                if triple.sujeto != actual or triple.relacion != "es_un":
                    continue
                if triple.objeto == fin:
                    return True
                if triple.objeto not in visitados:
                    visitados.add(triple.objeto)
                    cola.append(triple.objeto)
        return False

    def ancestros_es_un(self, concepto: str) -> list[str]:
        actual = _espacios_a_guiones(concepto)
        visitados: set[str] = set()
        ancestros: list[str] = []

        def recorrer(nodo: str) -> None:
            if nodo in visitados:
                return
            visitados.add(nodo)
            for triple in self._triples:
                if triple.sujeto == nodo and triple.relacion == "es_un":
                    if triple.objeto not in ancestros:
                        ancestros.append(triple.objeto)
                    recorrer(triple.objeto)

        recorrer(actual)
        return sorted(ancestros)

    def propiedad_heredada(
        self,
        subtipo: str,
        relacion: str,
    ) -> list[str]:
        """Hereda una propiedad de un ancestro de subtipo."""
        subtipo_normalizado = _espacios_a_guiones(subtipo)
        relacion_normalizada = _espacios_a_guiones(relacion)
        resultados: set[str] = set()
        resultados.update(
            self.consultar_relacion(subtipo_normalizado, relacion_normalizada)
        )
        for candidato in self.ancestros_es_un(subtipo_normalizado):
            resultados.update(
                self.consultar_relacion(candidato, relacion_normalizada)
            )
        return sorted(resultados)
