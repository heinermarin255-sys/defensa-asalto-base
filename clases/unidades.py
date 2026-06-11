"""
clases/unidades.py
Define las clases de tropas atacantes.
Usa herencia: UnidadBase -> Duende, Gigante, Arquera, Pekka.
"""


class UnidadBase:
    """
    Clase padre para todas las tropas del atacante.
    Maneja posición, movimiento y combate básico.
    """

    def __init__(self, fila: int, col: int, nombre: str,
                 vida: int, dano: int, velocidad: int, costo: int, tipo: str):
        self.fila = fila
        self.col = col
        self.nombre = nombre
        self.vida_max = vida
        self.vida = vida
        self.dano = dano
        self.velocidad = velocidad      # casillas que avanza por turno
        self.costo = costo
        self.tipo = tipo
        self.muerta = False
        self.turnos_sin_mover = 0       # para detectar unidades bloqueadas

    def recibir_dano(self, cantidad: int):
        """Aplica daño a la unidad."""
        self.vida -= cantidad
        if self.vida <= 0:
            self.vida = 0
            self.muerta = True

    def esta_viva(self) -> bool:
        return not self.muerta

    def porcentaje_vida(self) -> float:
        return self.vida / self.vida_max if self.vida_max > 0 else 0.0

    def mover_hacia(self, fila_destino: int, col_destino: int, mapa_ocupado) -> bool:
        """
        Mueve la unidad un paso hacia el destino.
        mapa_ocupado: función que recibe (fila, col) y dice si está bloqueada.
        Retorna True si se movió.
        """
        moved = False
        pasos = self.velocidad

        for _ in range(pasos):
            df = fila_destino - self.fila
            dc = col_destino - self.col

            if df == 0 and dc == 0:
                break

            # Intentar moverse hacia el destino
            nueva_fila = self.fila
            nueva_col = self.col

            # Priorizar el eje con mayor distancia
            if abs(df) >= abs(dc):
                nueva_fila += (1 if df > 0 else -1)
            else:
                nueva_col += (1 if dc > 0 else -1)

            # Verificar si la celda está libre
            if not mapa_ocupado(nueva_fila, nueva_col):
                self.fila = nueva_fila
                self.col = nueva_col
                moved = True
                self.turnos_sin_mover = 0
            else:
                # Intentar el otro eje
                nueva_fila2 = self.fila
                nueva_col2 = self.col

                if abs(df) >= abs(dc):
                    nueva_col2 += (1 if dc > 0 else (-1 if dc < 0 else 0))
                else:
                    nueva_fila2 += (1 if df > 0 else (-1 if df > 0 else 0))

                if nueva_fila2 != self.fila or nueva_col2 != self.col:
                    if not mapa_ocupado(nueva_fila2, nueva_col2):
                        self.fila = nueva_fila2
                        self.col = nueva_col2
                        moved = True
                        self.turnos_sin_mover = 0
                    else:
                        self.turnos_sin_mover += 1
                else:
                    self.turnos_sin_mover += 1

        return moved

    def atacar_estructura(self, estructura) -> int:
        """Ataca una estructura adyacente y retorna daño infligido."""
        estructura.recibir_dano(self.dano)
        return self.dano

    def esta_adyacente(self, fila: int, col: int) -> bool:
        """Verifica si una posición es adyacente (distancia Manhattan <= 1)."""
        return abs(self.fila - fila) + abs(self.col - col) <= 1

    def __str__(self):
        return f"{self.nombre} en ({self.fila},{self.col}) | Vida: {self.vida}/{self.vida_max}"


# ──────────────────────────────────────────
# TIPOS CONCRETOS DE TROPAS
# ──────────────────────────────────────────

class Duende(UnidadBase):
    """Tropa rápida, barata y con poca vida."""

    def __init__(self, fila: int, col: int):
        super().__init__(
            fila, col,
            nombre="Duende",
            vida=40, dano=10, velocidad=2,
            costo=25, tipo="duende"
        )


class Gigante(UnidadBase):
    """
    Tropa lenta con mucha vida.
    Prioriza atacar defensas sobre la base.
    """

    def __init__(self, fila: int, col: int):
        super().__init__(
            fila, col,
            nombre="Gigante",
            vida=200, dano=20, velocidad=1,
            costo=80, tipo="gigante"
        )
        self.prioriza_defensas = True


class Arquera(UnidadBase):
    """
    Tropa con alcance de ataque de 2 casillas.
    No necesita estar adyacente para atacar.
    """

    def __init__(self, fila: int, col: int):
        super().__init__(
            fila, col,
            nombre="Arquera",
            vida=60, dano=20, velocidad=1,
            costo=50, tipo="arquera"
        )
        self.alcance_ataque = 2

    def puede_atacar_desde(self, fila: int, col: int) -> bool:
        """Verifica si puede atacar un objetivo a distancia."""
        return abs(self.fila - fila) + abs(self.col - col) <= self.alcance_ataque


class Pekka(UnidadBase):
    """Tropa más poderosa del juego: mucha vida y mucho daño."""

    def __init__(self, fila: int, col: int):
        super().__init__(
            fila, col,
            nombre="Pekka",
            vida=300, dano=50, velocidad=1,
            costo=150, tipo="pekka"
        )


# ──────────────────────────────────────────
# FÁBRICA DE UNIDADES
# ──────────────────────────────────────────

def crear_unidad(tipo: str, fila: int, col: int):
    """
    Función fábrica: crea la unidad correcta según el tipo.
    """
    mapa_clases = {
        "duende": Duende,
        "gigante": Gigante,
        "arquera": Arquera,
        "pekka": Pekka,
    }

    clase = mapa_clases.get(tipo)
    if clase:
        return clase(fila, col)
    return None
