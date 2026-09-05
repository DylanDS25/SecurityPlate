"""Sistema hibrido para SecurityPlate.

Integra reglas expertas, recuperacion TF-IDF y clasificacion de casos
relacionados con el control de ingreso y salida de vehiculos.
"""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import KNeighborsClassifier


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
BASE_PATH = ROOT_DIR / "data" / "base_de_conocimiento.txt"
REPORT_PATH = ROOT_DIR / "reports" / "semana05.md"

DEFAULT_DOCUMENTS = [
	"ENTRADA 1\nTema: Captura de la placa en el ingreso\nEnunciado: Cuando un vehiculo ingresa, el sistema captura y guarda la imagen de su placa.",
	"ENTRADA 2\nTema: Registro del conductor\nEnunciado: En el ingreso tambien se captura una imagen del conductor como referencia.",
	"ENTRADA 3\nTema: Validacion de salida\nEnunciado: El sistema compara la placa detectada con la placa registrada en el ingreso.",
	"ENTRADA 4\nTema: Coincidencia del conductor\nEnunciado: Una coincidencia baja del conductor requiere revision manual.",
	"ENTRADA 5\nTema: Confianza del reconocimiento\nEnunciado: Una confianza baja impide tomar una decision automatica.",
	"ENTRADA 6\nTema: Calidad de la imagen\nEnunciado: Una imagen insuficiente requiere solicitar una nueva captura.",
	"ENTRADA 7\nTema: Vehiculo no registrado\nEnunciado: Un vehiculo sin registro activo debe bloquearse y enviarse al personal de seguridad.",
	"ENTRADA 8\nTema: Autorizacion y trazabilidad\nEnunciado: Toda autorizacion, bloqueo o alerta debe quedar almacenada con su motivo.",
]


@dataclass
class ResultadoConsulta:
	consulta: str
	regla: str
	accion: str
	evidencia: str
	similitud: float
	clasificacion: str


def cargar_base_conocimiento() -> list[str]:
	"""Carga cada entrada de la base como un documento recuperable."""
	DATA_DIR.mkdir(parents=True, exist_ok=True)
	if not BASE_PATH.exists():
		BASE_PATH.write_text("\n\n".join(DEFAULT_DOCUMENTS), encoding="utf-8")
	contenido = BASE_PATH.read_text(encoding="utf-8")
	bloques = re.split(r"(?=ENTRADA \d+\s*$)", contenido, flags=re.MULTILINE)
	entradas = [bloque.strip() for bloque in bloques if bloque.strip()]
	if len(entradas) < 8:
		raise ValueError("La base de conocimiento debe contener al menos 8 entradas.")
	return entradas


def construir_clasificador() -> tuple[KNeighborsClassifier, TfidfVectorizer]:
	"""Entrena un clasificador con 15 ejemplos, 10 de ellos del proyecto."""
	ejemplos = [
		"placa reconocida con confianza alta y registro de ingreso activo",
		"placa y conductor coinciden durante la salida",
		"lectura de placa clara con buena iluminacion",
		"salida autorizada por coincidencia de placa",
		"vehiculo registrado solicita salida del parqueadero",
		"imagen del conductor coincide con la referencia",
		"placa detectada sin errores en la entrada",
		"confianza alta permite abrir la barrera",
		"registro de ingreso valido para la placa detectada",
		"coincidencia suficiente para autorizar la salida",
		"placa no coincide con el ingreso almacenado",
		"vehiculo sin registro activo en el parqueadero",
		"imagen borrosa y confianza baja en el reconocimiento",
		"conductor diferente al registrado genera alerta",
		"iluminacion deficiente impide leer la placa",
	]
	etiquetas = [
		"autorizado", "autorizado", "autorizado", "autorizado", "autorizado",
		"autorizado", "autorizado", "autorizado", "autorizado", "autorizado",
		"alerta", "no registrado", "revision", "alerta", "revision",
	]
	vectorizador = TfidfVectorizer(lowercase=True, strip_accents="unicode")
	matriz = vectorizador.fit_transform(ejemplos)
	clasificador = KNeighborsClassifier(n_neighbors=1, metric="cosine")
	clasificador.fit(matriz, etiquetas)
	return clasificador, vectorizador


def evaluar_reglas(consulta: str) -> tuple[str, str]:
	"""Aplica cinco reglas expertas propias y devuelve regla y recomendacion."""
	texto = consulta.lower()
	reglas: list[tuple[Callable[[str], bool], tuple[str, str]]] = [
		(
			lambda valor: all(
				termino in valor
				for termino in ("placa coincide", "conductor coincide", "confianza alta")
			),
			(
				"R1 - Autorizar salida con coincidencia completa",
				"Autorizar la salida y registrar la trazabilidad.",
			),
		),
		(
			lambda valor: "placa no coincide" in valor or "placa diferente" in valor,
			(
				"R2 - Bloquear placa no coincidente",
				"Bloquear la salida y generar una alerta para el personal de seguridad.",
			),
		),
		(
			lambda valor: any(
				termino in valor
				for termino in ("borrosa", "desenfoque", "iluminacion deficiente", "confianza baja")
			),
			(
				"R3 - Solicitar nueva captura por baja calidad",
				"Solicitar una nueva captura antes de decidir.",
			),
		),
		(
			lambda valor: "sin registro" in valor or "no registrado" in valor,
			(
				"R4 - Enviar vehiculo no registrado a revision",
				"Bloquear la autorizacion automatica y enviar a revision manual.",
			),
		),
		(
			lambda valor: "conductor diferente" in valor or "coincidencia baja" in valor,
			(
				"R5 - Revisar identidad del conductor",
				"Mantener la barrera cerrada y verificar la identidad manualmente.",
			),
		),
	]
	for condicion, (nombre, accion) in reglas:
		if condicion(texto):
			return nombre, accion
	return "R6 - Revision preventiva por condicion no concluyente", "Solicitar validacion manual del caso."


def recuperar_informacion(consulta: str, entradas: list[str], vectorizador: TfidfVectorizer) -> tuple[str, float]:
	"""Recupera la entrada mas cercana usando TF-IDF y similitud coseno."""
	doc_matrix = vectorizador.fit_transform(entradas)
	similitudes = cosine_similarity(
		vectorizador.transform([consulta]),
		doc_matrix,
	)[0]
	best_index = int(similitudes.argmax())
	return entradas[best_index], float(similitudes[best_index])


def answer(query: str, entradas: list[str]) -> dict[str, object]:
	"""Integra reglas, recuperacion de evidencia y clasificacion."""
	q = query.lower()
	regla, accion = evaluar_reglas(q)
	vectorizador = TfidfVectorizer(lowercase=True, strip_accents="unicode")
	evidencia, similitud = recuperar_informacion(q, entradas, vectorizador)
	clasificador, vectorizador_clasificacion = construir_clasificador()
	clase = str(
		clasificador.predict(vectorizador_clasificacion.transform([q]))[0]
	)
	return {
		"reglas": [regla],
		"accion": accion,
		"evidencia": evidencia,
		"similitud": similitud,
		"clase": clase,
	}


def procesar_consulta(consulta: str, entradas: list[str]) -> ResultadoConsulta:
	resultado = answer(consulta, entradas)
	return ResultadoConsulta(
		consulta,
		str(resultado["reglas"][0]),
		str(resultado["accion"]),
		str(resultado["evidencia"]),
		float(resultado["similitud"]),
		str(resultado["clase"]),
	)


def write_report(rows: list[tuple[str, dict[str, object]]]) -> None:
	"""Escribe el reporte a partir de consultas y respuestas integradas."""
	lineas = [
		"# Semana 05 - Sistema hibrido",
		"",
	]
	for indice, (consulta, resultado) in enumerate(rows, start=1):
		reglas = ", ".join(str(regla) for regla in resultado["reglas"]) or "ninguna"
		lineas += [
			f"## Consulta {indice}",
			f"- Entrada: {consulta}",
			f"- Reglas: {reglas}",
			f"- Accion: {resultado['accion']}",
			f"- Evidencia: {resultado['evidencia']}",
			f"- Similitud: {float(resultado['similitud']):.3f}",
			f"- Clase: {resultado['clase']}",
			"",
		]
	REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
	REPORT_PATH.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def generar_reporte(resultados: list[ResultadoConsulta]) -> None:
	"""Genera el reporte exigido con evidencia explicable de cada prueba."""
	rows = [
		(
			resultado.consulta,
			{
				"reglas": [resultado.regla],
				"accion": resultado.accion,
				"evidencia": resultado.evidencia,
				"similitud": resultado.similitud,
				"clase": resultado.clasificacion,
			},
		)
		for resultado in resultados
	]
	write_report(rows)


def main() -> None:
	entradas = cargar_base_conocimiento()
	consultas = [
		"placa coincide, conductor coincide y confianza alta para autorizar salida",
		"placa no coincide con el registro de ingreso",
		"imagen borrosa, iluminacion deficiente y confianza baja",
	]
	resultados = [procesar_consulta(consulta, entradas) for consulta in consultas]
	generar_reporte(resultados)

	print("=== Sistema hibrido SecurityPlate ===")
	for resultado in resultados:
		print(f"\nConsulta: {resultado.consulta}")
		print(f"Regla: {resultado.regla}")
		print(f"Accion: {resultado.accion}")
		print(f"Informacion recuperada: {resultado.evidencia.splitlines()[0]}")
		print(f"Similitud: {resultado.similitud:.4f}")
		print(f"Clase predicha: {resultado.clasificacion}")
	print(f"\nReporte generado en: {REPORT_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
	main()
