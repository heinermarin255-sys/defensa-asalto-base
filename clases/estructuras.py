"""
clases/estructuras.py
Define las clases de estructuras defensivas del mapa.
Usa herencia: EstructuraBase -> Torre, Muro, Trampa, Base.
"""


class EstructuraBase:
    """
    Clase padre para todas las estructuras del mapa.
    Contiene atributos comunes: posición, vida, nombre.
    """

    def __init__(self, fila: int, col: int, nombre: str, vida: int, tipo: str):
        self.fila = fila
        self.col = col
        self.nombre = nombre
        self.vida_max = vida
        self.vida = vida
        self.tipo = tipo          # identificador de tipo para lógica del juego
        self.destruida = False

    def recibir_dano(self, cantidad: int):
        """Aplica daño a la estructura."""
        self.vida -= cantidad
        if self.vida <= 0:
            self.vida = 0
            self.destruida = True

    def esta_viva(self) -> bool:
        return not self.destruida

    def porcentaje_vida(self) -> float:
        """Retorna el porcentaje de vida restante (0.0 a 1.0)."""
        return self.vida / self.vida_max if self.vida_max > 0 else 0.0

    def __str__(self):
        return f"{self.nombre} en ({self.fila},{self.col}) | Vida: {self.vida}/{self.vida_max}"


# ──────────────────────────────────────────
# BASE CENTRAL
# ──────────────────────────────────────────

class Base(EstructuraBase):
    """
    Base central del defensor.
    Si es destruida, el atacante gana la ronda.
    """

    def __init__(self, fila: int, col: int):
        super().__init__(fila, col, "Base Central", vida=500, tipo="base")


# ──────────────────────────────────────────
# MURO
# ──────────────────────────────────────────

class Muro(EstructuraBase):
    """
    Muro que bloquea el paso de tropas.
    Alta vida, no ataca.
    Tiene una orientación visual ("horizontal" o "vertical") que se usa
    para rotar la imagen de la carta y lograr que los muros conecten
    visualmente entre sí al colocarlos en fila o en columna.
    """

    def __init__(self, fila: int, col: int, costo: int = 20, vida: int = 200,
                 orientacion: str = "horizontal"):
        super().__init__(fila, col, "Muro", vida=vida, tipo="muro")
        self.costo = costo
        self.dano = 0
        self.alcance = 0
        self.orientacion = orientacion if orientacion in ("horizontal", "vertical") else "horizontal"


# ──────────────────────────────────────────
# TRAMPAS
# ──────────────────────────────────────────

class Trampa(EstructuraBase):
    """
    Trampa que se activa una sola vez cuando una tropa pisa la casilla.
    """

    def __init__(self, fila: int, col: int, costo: int = 30, dano: int = 50):
        super().__init__(fila, col, "Trampa Explosiva", vida=1, tipo="trampa")
        self.costo = costo
        self.dano = dano
        self.activada = False

    def activar(self) -> int:
        """Activa la trampa y retorna el daño. Solo se activa una vez."""
        if self.activada:
            return 0
        self.activada = True
        return self.dano


# ──────────────────────────────────────────
# TORRES (jerarquía de herencia)
# ──────────────────────────────────────────

class Torre(EstructuraBase):
    """
    Clase base para todas las torres defensivas.
    Contiene atributos de combate: daño, alcance, velocidad.
    """

    def __init__(self, fila: int, col: int, nombre: str, vida: int,
                 dano: int, alcance: int, velocidad_ataque: int,
                 costo: int, tipo: str):
        super().__init__(fila, col, nombre, vida, tipo)
        self.dano = dano
        self.alcance = alcance
        self.velocidad_ataque = velocidad_ataque   # cada cuántos turnos ataca
        self.costo = costo
        self.turno_actual = 0                       # contador de turnos
        self.objetivo_actual = None                 # referencia a la tropa objetivo

    def puede_atacar(self) -> bool:
        """Retorna True si es turno de atacar."""
        return self.turno_actual % max(1, self.velocidad_ataque) == 0

    def avanzar_turno(self):
        """Avanza el contador de turnos."""
        self.turno_actual += 1

    def esta_en_alcance(self, fila_obj: int, col_obj: int) -> bool:
        """Verifica si una posición está dentro del alcance de la torre."""
        distancia = abs(self.fila - fila_obj) + abs(self.col - col_obj)
        return distancia <= self.alcance

    def calcular_dano(self) -> int:
        """Retorna el daño a infligir (puede ser sobreescrito)."""
        return self.dano


class TorreArquera(Torre):
    """Torre rápida de largo alcance y daño medio."""

    def __init__(self, fila: int, col: int):
        super().__init__(
            fila, col,
            nombre="Torre Arquera",
            vida=80, dano=15, alcance=3,
            velocidad_ataque=1, costo=50,
            tipo="torre_arquera"
        )


class TorreMagos(Torre):
    """Torre de área: daña a todas las tropas en rango."""

    def __init__(self, fila: int, col: int):
        super().__init__(
            fila, col,
            nombre="Torre de Magos",
            vida=70, dano=25, alcance=2,
            velocidad_ataque=2, costo=80,
            tipo="torre_magos"
        )
        self.es_area = True  # flag especial para lógica de combate


class TorreInfernal(Torre):
    """Torre cuyo daño aumenta cada turno que ataca al mismo objetivo."""

    def __init__(self, fila: int, col: int):
        super().__init__(
            fila, col,
            nombre="Torre Infernal",
            vida=90, dano=10, alcance=2,
            velocidad_ataque=1, costo=100,
            tipo="torre_infernal"
        )
        self.dano_acumulado = 0

    def calcular_dano(self) -> int:
        """El daño aumenta 5 por turno de ataque continuo."""
        self.dano_acumulado += 5
        return self.dano + self.dano_acumulado

    def resetear_dano(self):
        """Se llama cuando cambia de objetivo."""
        self.dano_acumulado = 0


class Canon(Torre):
    """Cañón: gran daño pero ataque muy lento."""

    def __init__(self, fila: int, col: int):
        super().__init__(
            fila, col,
            nombre="Cañón",
            vida=120, dano=40, alcance=2,
            velocidad_ataque=3, costo=70,
            tipo="canon"
        )


# ──────────────────────────────────────────
# FÁBRICA DE ESTRUCTURAS
# ──────────────────────────────────────────

def crear_estructura(tipo: str, fila: int, col: int, orientacion: str = "horizontal"):
    """
    Función fábrica: crea la estructura correcta según el tipo.
    Simplifica la creación desde el panel de construcción.
    """
    mapa_clases = {
        "torre_arquera": TorreArquera,
        "torre_magos": TorreMagos,
        "torre_infernal": TorreInfernal,
        "canon": Canon,
        "muro": Muro,
        "trampa": Trampa,
    }

    clase = mapa_clases.get(tipo)
    if clase is None:
        return None

    if tipo == "muro":
        return Muro(fila, col, orientacion=orientacion)

    return clase(fila, col)
