"""
clases/combate.py
Motor de combate automático.
Procesa cada turno: movimiento de tropas, ataques de torres, trampas.
"""

from clases.mapa import Mapa
from utils.constantes import BASE_FILA, BASE_COL


class MotorCombate:
    """
    Ejecuta un turno de combate completo.
    Llamado repetidamente por window.after() desde la interfaz.
    """

    def __init__(self, mapa: Mapa, callback_log, callback_sonido):
        """
        Args:
            mapa: El mapa de juego actual.
            callback_log: Función para mostrar mensajes de log en la UI.
            callback_sonido: Función para reproducir efectos de sonido.
        """
        self.mapa = mapa
        self.log = callback_log
        self.sonido = callback_sonido
        self.turno = 0
        self.combate_activo = False

    def iniciar(self):
        """Marca el combate como activo."""
        self.combate_activo = True
        self.turno = 0

    def ejecutar_turno(self) -> str:
        """
        Ejecuta un turno completo de combate.
        Retorna el estado: 'continua', 'atacante_gana', 'defensor_gana'.
        """
        self.turno += 1

        if not self.combate_activo:
            return "continua"

        # 1. Mover unidades
        self._mover_unidades()

        # 2. Activar trampas
        self._verificar_trampas()

        # 3. Torres atacan
        self._torres_atacan()

        # 4. Unidades atacan estructuras adyacentes
        self._unidades_atacan()

        # 5. Limpiar muertos
        self.mapa.limpiar_unidades_muertas()
        self._limpiar_estructuras_destruidas()

        # 6. Verificar condición de victoria
        return self._verificar_resultado()

    # ──────────────────────────────────────────
    # FASE 1: Movimiento de tropas
    # ──────────────────────────────────────────

    def _mover_unidades(self):
        """Mueve cada unidad viva un paso hacia su objetivo."""
        for unidad in self.mapa.unidades_vivas():
            # Determinar destino
            if hasattr(unidad, 'prioriza_defensas') and unidad.prioriza_defensas:
                destino = self._buscar_defensa_mas_cercana(unidad)
            else:
                destino = (BASE_FILA, BASE_COL)

            df, dc = destino

            # Función de colisión: evitar celdas con estructuras (excepto trampa)
            def celda_bloqueada(fila, col):
                est = self.mapa.obtener_estructura(fila, col)
                if est and est.tipo != "trampa" and est.esta_viva():
                    return True
                return False

            unidad.mover_hacia(df, dc, celda_bloqueada)

    def _buscar_defensa_mas_cercana(self, unidad) -> tuple:
        """Busca la torre o defensa más cercana a la unidad."""
        torres = self.mapa.todas_las_torres()
        if not torres:
            return (BASE_FILA, BASE_COL)

        def distancia(t):
            return abs(t.fila - unidad.fila) + abs(t.col - unidad.col)

        torre_cercana = min(torres, key=distancia)
        return (torre_cercana.fila, torre_cercana.col)

    # ──────────────────────────────────────────
    # FASE 2: Trampas
    # ──────────────────────────────────────────

    def _verificar_trampas(self):
        """Activa trampas donde haya tropas."""
        for unidad in self.mapa.unidades_vivas():
            trampa = self.mapa.verificar_trampa(unidad.fila, unidad.col)
            if trampa:
                dano = trampa.activar()
                unidad.recibir_dano(dano)
                self.log(f"💥 ¡Trampa! {unidad.nombre} recibe {dano} de daño!")
                self.sonido("explosion")

    # ──────────────────────────────────────────
    # FASE 3: Torres atacan
    # ──────────────────────────────────────────

    def _torres_atacan(self):
        """Cada torre ataca la unidad más cercana en su alcance."""
        torres = self.mapa.todas_las_torres()

        for torre in torres:
            torre.avanzar_turno()
            if not torre.puede_atacar():
                continue

            # Buscar unidades en alcance
            unidades_en_rango = self.mapa.obtener_unidades_en_alcance(
                torre.fila, torre.col, torre.alcance
            )

            if not unidades_en_rango:
                # Reiniciar daño acumulado de Torre Infernal si no hay objetivo
                if torre.tipo == "torre_infernal" and torre.objetivo_actual is not None:
                    torre.resetear_dano()
                    torre.objetivo_actual = None
                continue

            # Seleccionar objetivo: la unidad con menos vida (prioriza matar)
            objetivo = min(unidades_en_rango, key=lambda u: u.vida)

            # Torre Infernal: rastrear si cambió de objetivo
            if torre.tipo == "torre_infernal":
                if torre.objetivo_actual != objetivo:
                    torre.resetear_dano()
                    torre.objetivo_actual = objetivo

            dano = torre.calcular_dano()

            # Torre de Magos: daño en área
            if hasattr(torre, 'es_area') and torre.es_area:
                for u in unidades_en_rango:
                    u.recibir_dano(dano)
                self.log(f"🔮 {torre.nombre} daña a {len(unidades_en_rango)} tropas ({dano} c/u)")
            else:
                objetivo.recibir_dano(dano)
                self.log(f"🏹 {torre.nombre} → {objetivo.nombre}: {dano} daño")

            self.sonido("disparo")

    # ──────────────────────────────────────────
    # FASE 4: Unidades atacan
    # ──────────────────────────────────────────

    def _unidades_atacan(self):
        """Las unidades atacan estructuras adyacentes o en rango."""
        for unidad in self.mapa.unidades_vivas():
            # Arqueras pueden atacar a distancia
            if hasattr(unidad, 'alcance_ataque'):
                estructura = self._buscar_estructura_en_rango(unidad)
            else:
                estructura = self.mapa.obtener_estructura_adyacente(unidad.fila, unidad.col)

            if estructura and estructura.esta_viva():
                unidad.atacar_estructura(estructura)
                self.log(f"⚔️  {unidad.nombre} ataca {estructura.nombre}: {unidad.dano} daño")

                if estructura.destruida:
                    self.log(f"💀 ¡{estructura.nombre} destruida!")
                    self.sonido("explosion")

    def _buscar_estructura_en_rango(self, unidad):
        """Busca la estructura más cercana dentro del alcance de la unidad."""
        alcance = getattr(unidad, 'alcance_ataque', 1)
        mejor = None
        menor_dist = float('inf')

        from utils.constantes import FILAS, COLUMNAS
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                est = self.mapa.obtener_estructura(fila, col)
                if est and est.esta_viva() and est.tipo != "trampa":
                    dist = abs(unidad.fila - fila) + abs(unidad.col - col)
                    if dist <= alcance and dist < menor_dist:
                        menor_dist = dist
                        mejor = est
        return mejor

    # ──────────────────────────────────────────
    # LIMPIEZA
    # ──────────────────────────────────────────

    def _limpiar_estructuras_destruidas(self):
        """Elimina del mapa las estructuras que fueron destruidas."""
        from utils.constantes import FILAS, COLUMNAS
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                est = self.mapa.celdas[fila][col]
                if est and est.destruida and est.tipo != "base":
                    self.mapa.celdas[fila][col] = None

    # ──────────────────────────────────────────
    # VERIFICAR RESULTADO
    # ──────────────────────────────────────────

    def _verificar_resultado(self) -> str:
        """
        Determina el resultado del combate.
        Retorna:
            'atacante_gana' - base destruida
            'defensor_gana' - no quedan tropas
            'continua'      - el combate sigue
        """
        if self.mapa.base_destruida():
            self.combate_activo = False
            return "atacante_gana"

        if len(self.mapa.unidades_vivas()) == 0:
            self.combate_activo = False
            return "defensor_gana"

        return "continua"
