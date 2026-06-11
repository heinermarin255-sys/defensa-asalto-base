"""
clases/jugador.py
Define la clase Jugador con sus atributos durante la partida.
"""

from utils.constantes import GEMAS_INICIALES_DEFENSOR, GEMAS_INICIALES_ATACANTE


class Jugador:
    """
    Representa a un jugador durante una partida.
    Guarda su username, facción, gemas y rol actual.
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

        # Moneda de la ronda
        self.gemas = 0

        # Rondas ganadas en la partida
        self.rondas_ganadas = 0

    def iniciar_como_defensor(self):
        """Prepara al jugador para la fase de construcción."""
        self.rol = "defensor"
        self.gemas = GEMAS_INICIALES_DEFENSOR

    def iniciar_como_atacante(self):
        """Prepara al jugador para la fase de ataque."""
        self.rol = "atacante"
        self.gemas = GEMAS_INICIALES_ATACANTE

    def gastar_gemas(self, cantidad: int) -> bool:
        """
        Intenta gastar gemas.
        Retorna True si tenía suficientes, False si no.
        """
        if self.gemas >= cantidad:
            self.gemas -= cantidad
            return True
        return False

    def ganar_ronda(self):
        """Registra una victoria de ronda."""
        self.rondas_ganadas += 1

    def __str__(self):
        return f"{self.username} ({self.faccion}) | Rondas: {self.rondas_ganadas} | Gemas: {self.gemas}"
