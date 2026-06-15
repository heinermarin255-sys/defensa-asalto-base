"""
clases/jugador.py
Define la clase Jugador con sus atributos durante la partida.
"""

from utils.constantes import (
    DINERO_INICIAL_DEFENSOR,
    DINERO_INICIAL_ATACANTE,
    DINERO_POR_RONDA,
)


class Jugador:
    """
    Representa a un jugador durante una partida.
    Guarda su username, facción, dinero y rol actual.
    """

    def __init__(self, username: str, faccion: str):
        """
        Inicializa un jugador.

        Args:
            username: Nombre del jugador (desde login).
            faccion: Facción elegida ('Medieval', 'Futurista', 'Naturaleza').
        """
        self.username = username
        self.faccion = faccion

        # Rol en la ronda actual: 'defensor' o 'atacante'
        self.rol = None

        # Moneda de la ronda (antes llamada gemas, ahora representa dinero)
        self.gemas = 0

        # Rondas ganadas en la partida
        self.rondas_ganadas = 0

        # Dinero extra acumulado entre rondas (daño infligido / bajas conseguidas)
        self.bonus_dinero = 0

    def iniciar_como_defensor(self):
        """Prepara al jugador para la fase de construcción."""
        self.rol = "defensor"
        self.gemas = DINERO_INICIAL_DEFENSOR + DINERO_POR_RONDA + self.bonus_dinero
        self.bonus_dinero = 0

    def iniciar_como_atacante(self):
        """Prepara al jugador para la fase de ataque."""
        self.rol = "atacante"
        self.gemas = DINERO_INICIAL_ATACANTE + DINERO_POR_RONDA + self.bonus_dinero
        self.bonus_dinero = 0

    def gastar_gemas(self, cantidad: int) -> bool:
        """
        Intenta gastar dinero.
        Retorna True si tenía suficiente, False si no.
        """
        if self.gemas >= cantidad:
            self.gemas -= cantidad
            return True
        return False

    def agregar_bonus(self, cantidad: int):
        """Agrega dinero bonus para la próxima ronda."""
        self.bonus_dinero += cantidad

    def ganar_ronda(self):
        """Registra una victoria de ronda."""
        self.rondas_ganadas += 1

    def __str__(self):
        return f"{self.username} ({self.faccion}) | Rondas: {self.rondas_ganadas} | Dinero: {self.gemas}"
