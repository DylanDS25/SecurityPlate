"""
SEMANA 04: A* - Normalización Progresiva de Matrícula
Marco Tecnológico de IA

Problema: Encontrar secuencia óptima de transformaciones 
para normalizar una matrícula distorsionada

Ejecutar: python semana04_astar.py
"""

import heapq
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ============================================================================
# COMPONENTES DEL ESTADO
# ============================================================================

@dataclass
class EstadoMatricula:
    """Representa estado actual de la matrícula"""
    rotacion: float = 0.0          # Grados (-30 a 30)
    brillo: float = 0.0            # Porcentaje (-50 a 50)
    contraste: float = 0.0         # Porcentaje (-50 a 50)
    denoise: bool = False          # Filtro aplicado (True/False)
    confianza_ocr: float = 45.0    # Confianza 0-100%
    
    def __hash__(self):
        return hash((round(self.rotacion, 1), round(self.brillo, 1), 
                    round(self.contraste, 1), self.denoise))
    
    def __eq__(self, other):
        if not isinstance(other, EstadoMatricula):
            return False
        return (abs(self.rotacion - other.rotacion) < 0.1 and
                abs(self.brillo - other.brillo) < 0.1 and
                abs(self.contraste - other.contraste) < 0.1 and
                self.denoise == other.denoise)
    
    def __lt__(self, other):
        return self.confianza_ocr > other.confianza_ocr
    
    def __repr__(self):
        return f"Estado(rot={self.rotacion:.1f}°, brillo={self.brillo:.1f}%, " \
               f"contraste={self.contraste:.1f}%, denoise={self.denoise}, " \
               f"conf={self.confianza_ocr:.1f}%)"


@dataclass
class NodoAStar:
    """Nodo del árbol de búsqueda A*"""
    estado: EstadoMatricula
    g_costo: float = 0.0           # Costo acumulado desde inicio
    h_heuristica: float = 0.0      # Heurística (estimación)
    f_evaluacion: float = 0.0      # f = g + h
    padre: Optional['NodoAStar'] = None
    accion: str = ""               # Descripción de acción realizada
    
    def __lt__(self, other):
        return self.f_evaluacion < other.f_evaluacion


# ============================================================================
# FUNCIONES DE TRANSFORMACIÓN (Simuladores)
# ============================================================================

def simular_confianza_ocr(rot: float, brillo: float, contraste: float, 
                         denoise: bool) -> float:
    """
    Simula confianza OCR basada en transformaciones
    
    Interpretación física:
    - Rotar: alinea matrícula, mejora ~7% confianza
    - Brillo: si está oscura/clara, mejora ~4% por cada 20%
    - Contraste: diferencia caracteres-fondo, mejora ~5% por cada 20%
    - Denoise: elimina ruido, mejora ~25% (muy efectivo)
    """
    confianza = 45.0  # Base (matrícula distorsionada)
    
    # Efecto de rotación
    if rot != 0:
        confianza += abs(rot) * 0.5  # Máx +15% si rot=30°
    
    # Efecto de brillo
    if brillo != 0:
        confianza += abs(brillo) * 0.08  # Máx +4% si brillo=50%
    
    # Efecto de contraste
    if contraste != 0:
        confianza += abs(contraste) * 0.1  # Máx +5% si contraste=50%
    
    # Efecto de denoise (muy potente)
    if denoise:
        confianza += 25.0
    
    # Límite máximo
    return min(confianza, 99.0)


def calcular_heuristica(confianza_actual: float, meta: float = 90.0) -> float:
    """
    Heurística admisible: (100 - confianza_actual) / 10
    
    Interpretación:
    - Asume que cada acción mejora ~10% confianza
    - Nunca sobrestima (es lower bound)
    - Ayuda a A* a explorar nodos prometedores primero
    """
    diferencia = max(0, meta - confianza_actual)
    h = diferencia / 10.0
    return h


def obtener_sucesores(estado: EstadoMatricula) -> List[Tuple[EstadoMatricula, str, float]]:
    """
    Genera estados sucesores (vecinos en espacio de estados)
    
    Retorna: Lista de (nuevo_estado, descripción_acción, costo_acción)
    """
    sucesores = []
    
    # Acciones de rotación (costo = 1)
    for delta_rot in [-15, -10, -5, 5, 10, 15]:
        nueva_rot = estado.rotacion + delta_rot
        if -30 <= nueva_rot <= 30:
            nuevo_estado = EstadoMatricula(
                rotacion=nueva_rot,
                brillo=estado.brillo,
                contraste=estado.contraste,
                denoise=estado.denoise
            )
            nueva_conf = simular_confianza_ocr(nueva_rot, estado.brillo, 
                                               estado.contraste, estado.denoise)
            nuevo_estado.confianza_ocr = nueva_conf
            
            accion = f"Rotar {delta_rot:+d}° → conf={nueva_conf:.1f}%"
            sucesores.append((nuevo_estado, accion, 1))
    
    # Acciones de brillo (costo = 1)
    for delta_brillo in [-20, -10, 10, 20]:
        nuevo_brillo = estado.brillo + delta_brillo
        if -50 <= nuevo_brillo <= 50:
            nuevo_estado = EstadoMatricula(
                rotacion=estado.rotacion,
                brillo=nuevo_brillo,
                contraste=estado.contraste,
                denoise=estado.denoise
            )
            nueva_conf = simular_confianza_ocr(estado.rotacion, nuevo_brillo,
                                               estado.contraste, estado.denoise)
            nuevo_estado.confianza_ocr = nueva_conf
            
            accion = f"Brillo {delta_brillo:+d}% → conf={nueva_conf:.1f}%"
            sucesores.append((nuevo_estado, accion, 1))
    
    # Acciones de contraste (costo = 1)
    for delta_contraste in [-20, -10, 10, 20]:
        nuevo_contraste = estado.contraste + delta_contraste
        if -50 <= nuevo_contraste <= 50:
            nuevo_estado = EstadoMatricula(
                rotacion=estado.rotacion,
                brillo=estado.brillo,
                contraste=nuevo_contraste,
                denoise=estado.denoise
            )
            nueva_conf = simular_confianza_ocr(estado.rotacion, estado.brillo,
                                               nuevo_contraste, estado.denoise)
            nuevo_estado.confianza_ocr = nueva_conf
            
            accion = f"Contraste {delta_contraste:+d}% → conf={nueva_conf:.1f}%"
            sucesores.append((nuevo_estado, accion, 1))
    
    # Acción denoise (costo = 2, muy efectivo)
    if not estado.denoise:
        nuevo_estado = EstadoMatricula(
            rotacion=estado.rotacion,
            brillo=estado.brillo,
            contraste=estado.contraste,
            denoise=True
        )
        nueva_conf = simular_confianza_ocr(estado.rotacion, estado.brillo,
                                           estado.contraste, True)
        nuevo_estado.confianza_ocr = nueva_conf
        
        accion = f"Aplicar Denoise → conf={nueva_conf:.1f}%"
        sucesores.append((nuevo_estado, accion, 2))
    
    return sucesores


# ============================================================================
# ALGORITMO A*
# ============================================================================

def astar_normalizar_matricula(estado_inicial: EstadoMatricula, 
                               meta_confianza: float = 90.0,
                               verbose: bool = True) -> Tuple[Optional[NodoAStar], int]:
    """
    Implementa algoritmo A* para normalizar matrícula
    
    Parámetros:
    - estado_inicial: Estado de partida
    - meta_confianza: Confianza OCR objetivo (default 90%)
    - verbose: Mostrar información de búsqueda
    
    Retorna:
    - (nodo_solución, nodos_explorados)
    """
    
    # Inicialización
    open_set = []  # Cola de prioridad (min-heap por f)
    closed_set = set()  # Nodos ya explorados
    nodos_explorados = 0
    
    # Crear nodo inicial
    nodo_inicial = NodoAStar(estado=estado_inicial)
    nodo_inicial.h_heuristica = calcular_heuristica(estado_inicial.confianza_ocr, meta_confianza)
    nodo_inicial.f_evaluacion = nodo_inicial.g_costo + nodo_inicial.h_heuristica
    
    heapq.heappush(open_set, nodo_inicial)
    
    if verbose:
        print("\n🔍 Iniciando A*...")
        print(f"   Estado inicial: {estado_inicial}")
        print(f"   Meta: confianza >= {meta_confianza}%")
        print(f"   Heurística inicial h(n): {nodo_inicial.h_heuristica:.2f}")
    
    # Búsqueda
    while open_set:
        # Expandir nodo con menor f(n)
        nodo_actual = heapq.heappop(open_set)
        nodos_explorados += 1
        
        if verbose and nodos_explorados % 5 == 0:
            print(f"   [{nodos_explorados}] Expandiendo: f={nodo_actual.f_evaluacion:.2f}, "
                  f"g={nodo_actual.g_costo}, conf={nodo_actual.estado.confianza_ocr:.1f}%")
        
        # ¿Llegamos a la meta?
        if nodo_actual.estado.confianza_ocr >= meta_confianza:
            if verbose:
                print(f"\n✅ META ALCANZADA en nodo {nodos_explorados}")
                print(f"   Confianza final: {nodo_actual.estado.confianza_ocr:.1f}%")
            return nodo_actual, nodos_explorados
        
        # Marcar como explorado
        closed_set.add(nodo_actual.estado)
        
        # Explorar sucesores
        for nuevo_estado, descripcion_accion, costo_accion in obtener_sucesores(nodo_actual.estado):
            # Si ya lo exploramos, saltar
            if nuevo_estado in closed_set:
                continue
            
            # Calcular costo del nuevo nodo
            nuevo_g = nodo_actual.g_costo + costo_accion
            nuevo_h = calcular_heuristica(nuevo_estado.confianza_ocr, meta_confianza)
            nuevo_f = nuevo_g + nuevo_h
            
            # Crear nodo sucesor
            nodo_sucesor = NodoAStar(
                estado=nuevo_estado,
                g_costo=nuevo_g,
                h_heuristica=nuevo_h,
                f_evaluacion=nuevo_f,
                padre=nodo_actual,
                accion=descripcion_accion
            )
            
            heapq.heappush(open_set, nodo_sucesor)
    
    if verbose:
        print("\n❌ No se encontró solución")
    return None, nodos_explorados


# ============================================================================
# RECONSTRUCCIÓN Y ANÁLISIS DE CAMINO
# ============================================================================

def reconstruir_camino(nodo_solucion: NodoAStar) -> List[Tuple[EstadoMatricula, str, float]]:
    """Reconstruye camino desde inicio hasta solución"""
    camino = []
    nodo_actual = nodo_solucion
    
    while nodo_actual is not None:
        camino.append((nodo_actual.estado, nodo_actual.accion, nodo_actual.g_costo))
        nodo_actual = nodo_actual.padre
    
    return list(reversed(camino))


def imprimir_solucion(nodo_solucion: NodoAStar, nodos_explorados: int):
    """Imprime solución en formato legible"""
    
    camino = reconstruir_camino(nodo_solucion)
    
    print("\n" + "="*80)
    print("SOLUCIÓN A*")
    print("="*80)
    
    print(f"\n📊 Estadísticas:")
    print(f"   Nodos explorados: {nodos_explorados}")
    print(f"   Longitud del camino: {len(camino)} pasos")
    print(f"   Costo total g(n): {nodo_solucion.g_costo}")
    print(f"   Confianza alcanzada: {nodo_solucion.estado.confianza_ocr:.1f}%")
    
    print(f"\n📝 Camino de transformaciones:")
    for i, (estado, accion, g) in enumerate(camino):
        if i == 0:
            print(f"   {i}. [INICIO] {estado}")
        else:
            print(f"   {i}. {accion}")
            print(f"      → {estado}")
    
    print(f"\n✅ Estado final:")
    print(f"   Matrícula normalizada con {nodo_solucion.estado.confianza_ocr:.1f}% confianza")
    print(f"   Transformaciones aplicadas: {int(nodo_solucion.g_costo)} acciones")


# ============================================================================
# CASOS DE PRUEBA
# ============================================================================

def caso_1_busqueda_normal():
    """CASO 1: Búsqueda normal A*"""
    print("\n" + "#"*80)
    print("CASO 1: Búsqueda Normal A*")
    print("#"*80)
    
    estado_inicial = EstadoMatricula(
        rotacion=0, brillo=0, contraste=0, denoise=False, confianza_ocr=45
    )
    
    solucion, nodos = astar_normalizar_matricula(estado_inicial, meta_confianza=90)
    
    if solucion:
        imprimir_solucion(solucion, nodos)
    else:
        print("❌ No se encontró solución")


def caso_2_matricula_muy_distorsionada():
    """CASO 2: Matrícula muy distorsionada (meta más alta)"""
    print("\n" + "#"*80)
    print("CASO 2: Matrícula Muy Distorsionada (Meta: 95%)")
    print("#"*80)
    
    estado_inicial = EstadoMatricula(
        rotacion=0, brillo=0, contraste=0, denoise=False, confianza_ocr=35
    )
    
    solucion, nodos = astar_normalizar_matricula(estado_inicial, meta_confianza=95)
    
    if solucion:
        imprimir_solucion(solucion, nodos)
    else:
        print("❌ No se encontró solución")


def caso_3_meta_baja():
    """CASO 3: Meta baja (más fácil)"""
    print("\n" + "#"*80)
    print("CASO 3: Meta Baja (80% confianza)")
    print("#"*80)
    
    estado_inicial = EstadoMatricula(
        rotacion=0, brillo=0, contraste=0, denoise=False, confianza_ocr=45
    )
    
    solucion, nodos = astar_normalizar_matricula(estado_inicial, meta_confianza=80)
    
    if solucion:
        imprimir_solucion(solucion, nodos)
    else:
        print("❌ No se encontró solución")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def main():
    """Menú interactivo"""
    
    print("\n" + "="*80)
    print("SEMANA 04: A* - NORMALIZACIÓN DE MATRÍCULA")
    print("="*80)
    print("\nProblema: Encontrar secuencia óptima de transformaciones")
    print("para normalizar una matrícula distorsionada")
    print("\nComponentes A*:")
    print("  • Estado: (rotación, brillo, contraste, denoise)")
    print("  • Acciones: Rotar, ajustar brillo/contraste, denoise")
    print("  • Costo g(n): Número de acciones (denoise=2, resto=1)")
    print("  • Heurística h(n): (100 - confianza) / 10")
    print("  • Meta: confianza >= 90%")
    print("  • f(n) = g(n) + h(n)")
    
    while True:
        print("\n" + "-"*80)
        print("CASOS DE PRUEBA:")
        print("-"*80)
        print("1. Búsqueda Normal A* (matrícula estándar)")
        print("2. Matrícula Muy Distorsionada (meta: 95%)")
        print("3. Meta Baja (meta: 80%, más fácil)")
        print("4. Salir")
        
        opcion = input("\nSelecciona opción (1-4): ").strip()
        
        if opcion == "1":
            caso_1_busqueda_normal()
        elif opcion == "2":
            caso_2_matricula_muy_distorsionada()
        elif opcion == "3":
            caso_3_meta_baja()
        elif opcion == "4":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    main()
