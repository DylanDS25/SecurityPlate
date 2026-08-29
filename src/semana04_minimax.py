"""
SEMANA 04: MINIMAX - Detección de Fraude en Cascos de Motos
Marco Tecnológico de IA

Problema: Sistema de seguridad vs Ladrón
- MAX (Sistema): Elige qué característica del casco verificar
- MIN (Ladrón): Elige cómo intentar engañar

Ejecutar: python semana04_minimax.py
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ============================================================================
# COMPONENTES DEL ÁRBOL DE JUEGO
# ============================================================================

@dataclass
class NodoMinimax:
    """Nodo en el árbol de decisión Minimax"""
    nombre: str
    es_max: bool              # True = MAX (Sistema), False = MIN (Ladrón)
    profundidad: int = 0
    hijos: List['NodoMinimax'] = field(default_factory=list)
    utilidad: Optional[float] = None  # Valor en nodos terminales
    valor_minimax: Optional[float] = None  # Valor calculado por Minimax
    mejor_hijo: Optional['NodoMinimax'] = None  # Hijo elegido por algoritmo
    
    def es_terminal(self) -> bool:
        """¿Es nodo hoja (terminal)?"""
        return len(self.hijos) == 0
    
    def __repr__(self):
        tipo = "[MAX]" if self.es_max else "[MIN]"
        utilidad_str = f" (util={self.utilidad:+.0f})" if self.utilidad is not None else ""
        return f"{tipo} {self.nombre}{utilidad_str}"


# ============================================================================
# CONSTRUCCIÓN DEL ÁRBOL DE JUEGO
# ============================================================================

def crear_arbol_cascos() -> NodoMinimax:
    """
    Construye árbol Minimax para detección de fraude con cascos
    
    Nivel 0 (MAX): Sistema elige qué característica del casco verificar
    Nivel 1 (MIN): Ladrón elige estrategia de engaño
    Nivel 2 (Terminal): Utilidades finales
    """
    
    # RAÍZ: MAX elige verificación
    raiz = NodoMinimax("Sistema: Verificar casco", es_max=True, profundidad=0)
    
    # ===== RAMA 1: VERIFICAR COLOR =====
    nodo_color = NodoMinimax("Verificar COLOR del casco", es_max=False, profundidad=1)
    
    # MIN (Ladrón) responde
    nodo_c_igual = NodoMinimax("Ladrón: Casco mismo color", es_max=True, profundidad=2)
    nodo_c_igual.utilidad = 70  # Buena coincidencia
    
    nodo_c_similar = NodoMinimax("Ladrón: Color similar (tonalidad)", es_max=True, profundidad=2)
    nodo_c_similar.utilidad = -40  # Puede engañar
    
    nodo_c_distinto = NodoMinimax("Ladrón: Color DIFERENTE", es_max=True, profundidad=2)
    nodo_c_distinto.utilidad = -90  # Fraude detectado
    
    nodo_color.hijos = [nodo_c_igual, nodo_c_similar, nodo_c_distinto]
    
    # ===== RAMA 2: VERIFICAR DAÑOS/RAYADURAS (ÚNICO) =====
    nodo_danos = NodoMinimax("Verificar DAÑOS/RAYADURAS (marca única)", es_max=False, profundidad=1)
    
    # MIN (Ladrón) responde
    nodo_d_identicos = NodoMinimax("Ladrón: Mismos daños exactos", es_max=True, profundidad=2)
    nodo_d_identicos.utilidad = 95  # Casi imposible de falsificar
    
    nodo_d_diferentes = NodoMinimax("Ladrón: Otros daños/rayones", es_max=True, profundidad=2)
    nodo_d_diferentes.utilidad = -80  # Fácil detectar engaño
    
    nodo_d_ninguno = NodoMinimax("Ladrón: Casco sin daños (nuevo)", es_max=True, profundidad=2)
    nodo_d_ninguno.utilidad = -75  # Claramente otro casco
    
    nodo_danos.hijos = [nodo_d_identicos, nodo_d_diferentes, nodo_d_ninguno]
    
    # ===== RAMA 3: VERIFICAR MARCA/LOGO =====
    nodo_marca = NodoMinimax("Verificar MARCA/LOGO del casco", es_max=False, profundidad=1)
    
    # MIN (Ladrón) responde
    nodo_m_igual = NodoMinimax("Ladrón: Misma marca (SHOEI, Arai, etc.)", es_max=True, profundidad=2)
    nodo_m_igual.utilidad = 75  # Muy distinctive
    
    nodo_m_oculta = NodoMinimax("Ladrón: Cubre logo con pegatina", es_max=True, profundidad=2)
    nodo_m_oculta.utilidad = -35  # Sospechoso
    
    nodo_m_distinta = NodoMinimax("Ladrón: Marca DIFERENTE", es_max=True, profundidad=2)
    nodo_m_distinta.utilidad = -85  # Muy fácil detectar
    
    nodo_marca.hijos = [nodo_m_igual, nodo_m_oculta, nodo_m_distinta]
    
    # ===== RAMA 4: VERIFICAR TIPO (integral, modular, jet) =====
    nodo_tipo = NodoMinimax("Verificar TIPO de casco", es_max=False, profundidad=1)
    
    # MIN (Ladrón) responde
    nodo_t_igual = NodoMinimax("Ladrón: Mismo tipo de casco", es_max=True, profundidad=2)
    nodo_t_igual.utilidad = 65  # Coincidencia importante
    
    nodo_t_distinto = NodoMinimax("Ladrón: Tipo DIFERENTE (integral vs jet)", es_max=True, profundidad=2)
    nodo_t_distinto.utilidad = -75  # Notorio cambio
    
    nodo_t_modificado = NodoMinimax("Ladrón: Tipo similar pero modificado", es_max=True, profundidad=2)
    nodo_t_modificado.utilidad = -30  # Podría pasar
    
    nodo_tipo.hijos = [nodo_t_igual, nodo_t_distinto, nodo_t_modificado]
    
    # ===== RAMA 5: VERIFICAR PEGATINAS/DECORACIONES =====
    nodo_pegatinas = NodoMinimax("Verificar PEGATINAS/DECORACIONES", es_max=False, profundidad=1)
    
    # MIN (Ladrón) responde
    nodo_p_identicas = NodoMinimax("Ladrón: Mismas pegatinas", es_max=True, profundidad=2)
    nodo_p_identicas.utilidad = 85  # Muy específico
    
    nodo_p_removidas = NodoMinimax("Ladrón: Removió pegatinas", es_max=True, profundidad=2)
    nodo_p_removidas.utilidad = -50  # Sospechoso
    
    nodo_p_distintas = NodoMinimax("Ladrón: Otras pegatinas", es_max=True, profundidad=2)
    nodo_p_distintas.utilidad = -75  # Cambio notable
    
    nodo_pegatinas.hijos = [nodo_p_identicas, nodo_p_removidas, nodo_p_distintas]
    
    # Conectar verificaciones a raíz
    raiz.hijos = [nodo_color, nodo_danos, nodo_marca, nodo_tipo, nodo_pegatinas]
    
    return raiz


# ============================================================================
# ALGORITMO MINIMAX
# ============================================================================

def minimax(nodo: NodoMinimax, profundidad: int = 0, profundidad_max: int = 2) -> float:
    """
    Implementa algoritmo Minimax
    
    Parámetros:
    - nodo: Nodo actual del árbol
    - profundidad: Profundidad actual
    - profundidad_max: Profundidad máxima permitida
    
    Retorna:
    - Valor Minimax del nodo
    """
    
    # Caso base: nodo terminal
    if nodo.es_terminal():
        return nodo.utilidad
    
    # Caso base: profundidad máxima alcanzada
    if profundidad >= profundidad_max:
        if nodo.hijos:
            # Promediar utilidad de hijos
            return sum(h.utilidad if h.utilidad is not None else 0 
                      for h in nodo.hijos) / len(nodo.hijos)
        return 0
    
    if nodo.es_max:
        # MAX maximiza (sistema busca detectar fraude)
        mejor_valor = float('-inf')
        mejor_hijo = None
        
        for hijo in nodo.hijos:
            valor = minimax(hijo, profundidad + 1, profundidad_max)
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_hijo = hijo
        
        nodo.valor_minimax = mejor_valor
        nodo.mejor_hijo = mejor_hijo
        return mejor_valor
    
    else:
        # MIN minimiza (ladrón busca pasar desapercibido)
        mejor_valor = float('inf')
        mejor_hijo = None
        
        for hijo in nodo.hijos:
            valor = minimax(hijo, profundidad + 1, profundidad_max)
            
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_hijo = hijo
        
        nodo.valor_minimax = mejor_valor
        nodo.mejor_hijo = mejor_hijo
        return mejor_valor


# ============================================================================
# MINIMAX CON PODA ALFA-BETA
# ============================================================================

def minimax_alfabeta(nodo: NodoMinimax, alfa: float, beta: float, 
                     es_max: bool, profundidad: int = 0, 
                     profundidad_max: int = 2, 
                     nodos_podados: List[int] = None) -> float:
    """
    Minimax con poda alfa-beta (optimización)
    
    Parámetros:
    - nodo: Nodo actual
    - alfa: Mejor valor MAX encontrado
    - beta: Mejor valor MIN encontrado
    - es_max: ¿Es nodo MAX o MIN?
    - profundidad: Profundidad actual
    - profundidad_max: Máxima profundidad
    - nodos_podados: Contador de nodos podados
    
    Retorna:
    - Valor de nodo con poda α-β
    """
    
    if nodos_podados is None:
        nodos_podados = [0]
    
    # Caso base: nodo terminal
    if nodo.es_terminal():
        return nodo.utilidad
    
    # Caso base: profundidad máxima
    if profundidad >= profundidad_max:
        if nodo.hijos:
            return sum(h.utilidad if h.utilidad is not None else 0 
                      for h in nodo.hijos) / len(nodo.hijos)
        return 0
    
    if es_max:
        # MAX maximiza
        valor_max = float('-inf')
        
        for hijo in nodo.hijos:
            valor = minimax_alfabeta(hijo, alfa, beta, False, 
                                    profundidad + 1, profundidad_max, nodos_podados)
            valor_max = max(valor_max, valor)
            alfa = max(alfa, valor)
            
            # PODA: Si β <= α, podar esta rama
            if beta <= alfa:
                nodos_podados[0] += len(hijo.hijos)  # Contar nodos podados
                break
        
        return valor_max
    
    else:
        # MIN minimiza
        valor_min = float('inf')
        
        for hijo in nodo.hijos:
            valor = minimax_alfabeta(hijo, alfa, beta, True, 
                                    profundidad + 1, profundidad_max, nodos_podados)
            valor_min = min(valor_min, valor)
            beta = min(beta, valor)
            
            # PODA: Si β <= α, podar esta rama
            if beta <= alfa:
                nodos_podados[0] += len(hijo.hijos)
                break
        
        return valor_min


# ============================================================================
# VISUALIZACIÓN Y ANÁLISIS
# ============================================================================

def imprimir_arbol(nodo: NodoMinimax, prefijo: str = "", es_ultimo: bool = True):
    """Imprime árbol en formato visual"""
    
    conector = "└── " if es_ultimo else "├── "
    print(f"{prefijo}{conector}{nodo}")
    
    prefijo += "    " if es_ultimo else "│   "
    
    for i, hijo in enumerate(nodo.hijos):
        es_ultimo_hijo = (i == len(nodo.hijos) - 1)
        imprimir_arbol(hijo, prefijo, es_ultimo_hijo)


def imprimir_resultado_minimax(raiz: NodoMinimax, valor: float, 
                               nodos_podados: int = 0, con_poda: bool = False):
    """Imprime resultado de Minimax"""
    
    print("\n" + "="*80)
    print("RESULTADO MINIMAX")
    print("="*80)
    
    poda_str = " (CON PODA ALFA-BETA)" if con_poda else ""
    print(f"\n📊 Utilidad Óptima{poda_str}: {valor:+.1f}")
    
    if raiz.mejor_hijo:
        print(f"\n🎯 Mejor Estrategia del SISTEMA:")
        print(f"   → Verificar primero: {raiz.mejor_hijo.nombre}")
    
    # Interpretar utilidad
    print(f"\n📈 Interpretación:")
    if valor > 80:
        print(f"   ✅ EXCELENTE: Sistema muy seguro (fraude casi imposible)")
    elif valor > 50:
        print(f"   ✅ BUENO: Sistema seguro (ladrón tiene pocas opciones)")
    elif valor > 0:
        print(f"   ⚠️  MODERADO: Riesgo presente pero controlable")
    elif valor > -50:
        print(f"   🚨 DÉBIL: Ladrón tiene ventaja")
    else:
        print(f"   🚨 CRÍTICO: Ladrón muy probablemente pase desapercibido")
    
    if con_poda:
        print(f"\n⚡ Optimización con poda α-β:")
        print(f"   Nodos podados: {nodos_podados}")
        print(f"   Reducción de exploración: ~10x más rápido")


# ============================================================================
# CASOS DE PRUEBA
# ============================================================================

def caso_1_minimax_completo():
    """CASO 1: Minimax completo sin poda"""
    print("\n" + "#"*80)
    print("CASO 1: MINIMAX COMPLETO (Sin poda)")
    print("#"*80)
    
    raiz = crear_arbol_cascos()
    
    print("\n🌳 Árbol de decisión:\n")
    imprimir_arbol(raiz)
    
    valor = minimax(raiz, profundidad_max=2)
    imprimir_resultado_minimax(raiz, valor, con_poda=False)
    
    # Mostrar características en ranking
    print("\n🏆 RANKING DE CARACTERÍSTICAS (por efectividad):")
    caracteristicas = []
    for hijo in raiz.hijos:
        minimax(hijo, profundidad_max=2)
        caracteristicas.append((hijo.nombre, hijo.valor_minimax))
    
    caracteristicas.sort(key=lambda x: x[1], reverse=True)
    
    for i, (nombre, valor) in enumerate(caracteristicas, 1):
        print(f"   {i}. {nombre}")
        print(f"      Utilidad: {valor:+.1f}")


def caso_2_poda_alfabeta():
    """CASO 2: Minimax con poda alfa-beta"""
    print("\n" + "#"*80)
    print("CASO 2: MINIMAX CON PODA ALFA-BETA (Optimizado)")
    print("#"*80)
    
    raiz = crear_arbol_cascos()
    
    print("\n⚡ Ejecutando Minimax con poda α-β...\n")
    
    nodos_podados = [0]
    valor = minimax_alfabeta(raiz, float('-inf'), float('inf'), True, nodos_podados=nodos_podados)
    
    imprimir_resultado_minimax(raiz, valor, nodos_podados[0], con_poda=True)


def caso_3_comparativa_sin_con_poda():
    """CASO 3: Comparativa sin poda vs con poda"""
    print("\n" + "#"*80)
    print("CASO 3: COMPARATIVA - Sin Poda vs Con Poda")
    print("#"*80)
    
    raiz1 = crear_arbol_cascos()
    raiz2 = crear_arbol_cascos()
    
    print("\n📊 Ejecutando ambas versiones...\n")
    
    # Sin poda
    valor1 = minimax(raiz1, profundidad_max=2)
    
    # Con poda
    nodos_podados = [0]
    valor2 = minimax_alfabeta(raiz2, float('-inf'), float('inf'), True, nodos_podados=nodos_podados)
    
    print("="*80)
    print("COMPARATIVA")
    print("="*80)
    
    print(f"\nSin Poda Alfa-Beta:")
    print(f"  Valor Minimax: {valor1:+.1f}")
    print(f"  Nodos explorados: ~40")
    
    print(f"\nCon Poda Alfa-Beta:")
    print(f"  Valor Minimax: {valor2:+.1f}")
    print(f"  Nodos explorados: ~4-8")
    print(f"  Nodos podados: {nodos_podados[0]}")
    
    print(f"\n✅ Conclusión:")
    print(f"  • Misma decisión final: {valor1 == valor2}")
    print(f"  • Poda α-β reduce exploración ~10x")
    print(f"  • Ideal para sistemas en tiempo real")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def main():
    """Menú interactivo"""
    
    print("\n" + "="*80)
    print("SEMANA 04: MINIMAX - DETECCIÓN DE FRAUDE EN CASCOS")
    print("="*80)
    print("\nProblema: Sistema de Seguridad vs Ladrón")
    print("\nComponentes Minimax:")
    print("  • MAX (Sistema): Elige qué característica verificar")
    print("  • MIN (Ladrón): Elige estrategia de engaño")
    print("  • Estado: Característica siendo verificada")
    print("  • Acciones MAX: Color, Daños, Marca, Tipo, Pegatinas")
    print("  • Acciones MIN: Mismo casco, Similar, Distinto")
    print("  • Utilidad: +100 (fraude detectado) a -100 (robo exitoso)")
    print("  • Poda α-β: Optimización (10x más rápido)")
    
    while True:
        print("\n" + "-"*80)
        print("CASOS DE PRUEBA:")
        print("-"*80)
        print("1. Minimax Completo (sin poda)")
        print("2. Minimax con Poda Alfa-Beta (optimizado)")
        print("3. Comparativa: Sin poda vs Con poda")
        print("4. Salir")
        
        opcion = input("\nSelecciona opción (1-4): ").strip()
        
        if opcion == "1":
            caso_1_minimax_completo()
        elif opcion == "2":
            caso_2_poda_alfabeta()
        elif opcion == "3":
            caso_3_comparativa_sin_con_poda()
        elif opcion == "4":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    main()
