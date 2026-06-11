"""
clases/mapa.py
Gestiona la cuadrícula 10x10 del juego.
Mantiene referencias a estructuras y unidades en cada casilla.
"""

from utils.constantes import FILAS, COLUMNAS, BASE_FILA, BASE_COL
from clases.estructuras import Base


class Mapa:
    """
    Representa el mapa de juego como una matriz de 10x10.
    Cada celda puede contener una estructura o estar vacía.
    Las unidades se gestionan en una lista separada pero se ubican por coordenadas.
    """

    def __init__(self):
        """Inicializa el mapa vacío y coloca la base central."""
        # Matriz principal: guarda estructuras (Torres, Muros, Trampas, Base)
        self.celdas = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]

        # Lista de unidades activas en el mapa
        self.unidades = []

        # Colocar la base central automáticamente
        self.base = Base(BASE_FILA, BASE_COL)
        self.celdas[BASE_FILA][BASE_COL] = self.base

    # ──────────────────────────────────────────
    # Consultas del mapa
    # ──────────────────────────────────────────

    def celda_valida(self, fila: int, col: int) -> bool:
        """Verifica si la coordenada existe dentro del mapa."""
        return 0 <= fila < FILAS and 0 <= col < COLUMNAS

    def celda_libre(self, fila: int, col: int) -> bool:
        """Retorna True si la celda no tiene estructura."""
        if not self.celda_valida(fila, col):
            return False
        return self.celdas[fila][col] is None

    def celda_ocupada_por_unidad(self, fila: int, col: int) -> bool:
        """Retorna True si alguna unidad viva está en esa posición."""
        for unidad in self.unidades:
            if unidad.esta_viva() and unidad.fila == fila and unidad.col == col:
                return True
        return False

    def es_borde(self, fila: int, col: int) -> bool:
        """Retorna True si la celda está en el borde del mapa."""
        return fila == 0 or fila == FILAS - 1 or col == 0 or col == COLUMNAS - 1

    # ──────────────────────────────────────────
    # Colocación de estructuras
    # ──────────────────────────────────────────

    def colocar_estructura(self, estructura) -> bool:
        """
        Intenta colocar una estructura en el mapa.
        Retorna True si se colocó con éxito.
        """
        fila, col = estructura.fila, estructura.col

        # Validar posición
        if not self.celda_valida(fila, col):
            return False

        # No se puede colocar sobre otra estructura
        if not self.celda_libre(fila, col):
            return False

        # No se puede colocar en los bordes (son de entrada de tropas)
        if self.es_borde(fila, col):
            return False

        self.celdas[fila][col] = estructura
        return True

    def eliminar_estructura(self, fila: int, col: int):
        """Elimina la estructura en la posición indicada (excepto la base)."""
        if self.celda_valida(fila, col):
            if self.celdas[fila][col] and self.celdas[fila][col].tipo != "base":
                self.celdas[fila][col] = None

    def obtener_estructura(self, fila: int, col: int):
        """Retorna la estructura en la posición o None."""
        if self.celda_valida(fila, col):
            return self.celdas[fila][col]
        return None

    # ──────────────────────────────────────────
    # Gestión de unidades
    # ──────────────────────────────────────────

    def agregar_unidad(self, unidad) -> bool:
        """
        Agrega una unidad al mapa en una posición de borde.
        Retorna True si se pudo colocar.
        """
        if not self.es_borde(unidad.fila, unidad.col):
            return False

        # Verificar que no haya otra unidad exactamente ahí
        if self.celda_ocupada_por_unidad(unidad.fila, unidad.col):
            return False

        self.unidades.append(unidad)
        return True

    def unidades_vivas(self) -> list:
        """Retorna lista de unidades que siguen vivas."""
        return [u for u in self.unidades if u.esta_viva()]

    def limpiar_unidades_muertas(self):
        """Elimina las unidades muertas de la lista."""
        self.unidades = [u for u in self.unidades if u.esta_viva()]

    # ──────────────────────────────────────────
    # Búsqueda de objetivos para torres
    # ──────────────────────────────────────────

    def obtener_unidades_en_alcance(self, fila: int, col: int, alcance: int) -> list:
        """
        Retorna todas las unidades vivas dentro del alcance (distancia Manhattan).
        """
        resultado = []
        for unidad in self.unidades:
            if unidad.esta_viva():
                dist = abs(unidad.fila - fila) + abs(unidad.col - col)
                if dist <= alcance:
                    resultado.append(unidad)
        return resultado

    def obtener_estructura_adyacente(self, fila: int, col: int):
        """
        Retorna la primera estructura (no trampa) adyacente a la posición.
        Usado por tropas para saber qué atacar.
        """
        direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for df, dc in direcciones:
            nf, nc = fila + df, col + dc
            if self.celda_valida(nf, nc):
                est = self.celdas[nf][nc]
                if est and est.esta_viva() and est.tipo != "trampa":
                    return est
        return None

    def verificar_trampa(self, fila: int, col: int):
        """
        Verifica si hay una trampa en la posición.
        Si existe y no está activada, la retorna.
        """
        est = self.obtener_estructura(fila, col)
        if est and est.tipo == "trampa" and not est.destruida:
            return est
        return None

    def base_destruida(self) -> bool:
        """Retorna True si la base central fue destruida."""
        return self.base.destruida

    def todas_las_torres(self) -> list:
        """Retorna lista de todas las torres vivas en el mapa."""
        torres = []
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                est = self.celdas[fila][col]
                if est and est.esta_viva() and est.tipo not in ("muro", "trampa", "base"):
                    torres.append(est)
        return torres

    def reiniciar(self):
        """Limpia el mapa completamente y recoloca la base."""
        self.celdas = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.unidades = []
        self.base = Base(BASE_FILA, BASE_COL)
        self.celdas[BASE_FILA][BASE_COL] = self.base
