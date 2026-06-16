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
        self.dano_total_atacante = 0    # daño acumulado por el atacante en esta ronda
        self.unidades_eliminadas = 0    # unidades que mató el defensor en esta ronda

    def iniciar(self):
        """Marca el combate como activo."""
        self.combate_activo = True
        self.turno = 0
        self.dano_total_atacante = 0
        self.unidades_eliminadas = 0

    def ejecutar_turno(self) -> str:
        """
        Ejecuta un turno completo de combate.
        Retorna el estado: 'continua', 'atacante_gana', 'defensor_gana'.
        """
        self.turno += 1

        if not self.combate_activo:
            return "continua"

        # Las trampas que explotaron el turno anterior se retiran ahora,
        # antes de procesar nada nuevo, para que se vean un turno completo.
        self._retirar_trampas_explotadas()

        # 1. Mover unidades
        self._mover_unidades()

        # 2. Activar trampas
        self._verificar_trampas()

        # 3. Torres atacan
        self._torres_atacan()

        # 4. Unidades atacan estructuras adyacentes
        self._unidades_atacan()

        # 5. Contabilizar bajas del defensor antes de limpiar
        muertas_antes = len([u for u in self.mapa.unidades if u.muerta])
        self.mapa.limpiar_unidades_muertas()
        self._limpiar_estructuras_destruidas()

        # 6. Verificar condición de victoria
        return self._verificar_resultado()

    # ──────────────────────────────────────────
    # FASE 1: Movimiento de tropas
    # ──────────────────────────────────────────

    def _mover_unidades(self):
        """Mueve cada unidad viva hacia su objetivo."""
        for unidad in self.mapa.unidades_vivas():
            if hasattr(unidad, 'prioriza_defensas') and unidad.prioriza_defensas:
                destino = self._buscar_defensa_mas_cercana(unidad)
            else:
                destino = (BASE_FILA, BASE_COL)

            df, dc = destino

            def celda_bloqueada(fila, col):
                est = self.mapa.obtener_estructura(fila, col)
                if not est or not est.esta_viva():
                    return False
                return est.tipo != "trampa"

            # Si ya está pegada al objetivo, no se mueve: ataca en la
            # siguiente fase.
            if abs(unidad.fila - df) + abs(unidad.col - dc) <= 1:
                continue

            paso = self.mapa.siguiente_paso_bfs(unidad.fila, unidad.col, df, dc)

            if paso is not None:
                # Hay un camino libre (por ejemplo, un hueco en el cerco):
                # la unidad lo sigue en lugar de atacar un muro.
                unidad._turno_interno += 1
                if unidad.puede_moverse_este_turno():
                    unidad.fila, unidad.col = paso
                    unidad.turnos_sin_mover = 0
            else:
                # Sin camino libre: avanza directo hacia el destino,
                # lo que la deja adyacente al obstáculo que la bloquea
                # para poder atacarlo en la fase de ataque.
                unidad.mover_hacia(df, dc, celda_bloqueada)

    def _buscar_defensa_mas_cercana(self, unidad) -> tuple:
        """
        Busca la torre o defensa más cercana al gigante.
        Excluye la base central para que siempre priorice defensas primero.
        """
        torres = [t for t in self.mapa.todas_las_torres()
                  if t.tipo != "base" and t.tipo != "muro"]
        if not torres:
            # Si no quedan defensas, entonces va a por la base
            return (BASE_FILA, BASE_COL)

        def distancia(t):
            return abs(t.fila - unidad.fila) + abs(t.col - unidad.col)

        torre_cercana = min(torres, key=distancia)
        return (torre_cercana.fila, torre_cercana.col)

    # ──────────────────────────────────────────
    # FASE 2: Trampas
    # ──────────────────────────────────────────

    def _verificar_trampas(self):
        """Activa trampas donde haya tropas. Se ven un turno antes de quitarse."""
        for unidad in self.mapa.unidades_vivas():
            trampa = self.mapa.verificar_trampa(unidad.fila, unidad.col)
            if trampa:
                dano = trampa.activar()
                if dano > 0:
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

            unidades_en_rango = self.mapa.obtener_unidades_en_alcance(
                torre.fila, torre.col, torre.alcance
            )

            if not unidades_en_rango:
                if torre.tipo == "torre_infernal" and torre.objetivo_actual is not None:
                    torre.resetear_dano()
                    torre.objetivo_actual = None
                continue

            objetivo = min(unidades_en_rango, key=lambda u: u.vida)

            if torre.tipo == "torre_infernal":
                if torre.objetivo_actual != objetivo:
                    torre.resetear_dano()
                    torre.objetivo_actual = objetivo

            dano = torre.calcular_dano()

            if hasattr(torre, 'es_area') and torre.es_area:
                for u in unidades_en_rango:
                    vida_antes = u.vida
                    u.recibir_dano(dano)
                    self.unidades_eliminadas += (1 if u.muerta else 0)
                self.log(f"🔮 {torre.nombre} daña a {len(unidades_en_rango)} tropas ({dano} c/u)")
            else:
                vida_antes = objetivo.vida
                objetivo.recibir_dano(dano)
                if objetivo.muerta:
                    self.unidades_eliminadas += 1
                self.log(f"🏹 {torre.nombre} → {objetivo.nombre}: {dano} daño")

            self.sonido("disparo")

    # ──────────────────────────────────────────
    # FASE 4: Unidades atacan
    # ──────────────────────────────────────────

    def _unidades_atacan(self):
        for unidad in self.mapa.unidades_vivas():
            if hasattr(unidad, 'alcance_ataque'):
                estructura = self._buscar_estructura_en_rango(unidad)
            else:
                estructura = self._objetivo_adyacente(unidad)

            if estructura and estructura.esta_viva():
                dano_aplicado = unidad.atacar_estructura(estructura)
                self.dano_total_atacante += dano_aplicado
                self.log(f"⚔️  {unidad.nombre} ataca {estructura.nombre}: {unidad.dano} daño")
                if estructura.destruida:
                    self.log(f"💀 ¡{estructura.nombre} destruida!")
                    self.sonido("explosion")

    def _objetivo_adyacente(self, unidad):
        """
        Retorna la estructura adyacente de mayor prioridad para atacar.
        Prioridad: torres/defensas > muros (solo si bloquean) > base.
        """
        direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        candidatos = []
        for df, dc in direcciones:
            nf, nc = unidad.fila + df, unidad.col + dc
            if self.mapa.celda_valida(nf, nc):
                est = self.mapa.celdas[nf][nc]
                if est and est.esta_viva() and est.tipo != "trampa":
                    candidatos.append(est)

        if not candidatos:
            return None

        objetivo_previo = getattr(unidad, "_objetivo_actual", None)
        if objetivo_previo and objetivo_previo in candidatos and objetivo_previo.esta_viva():
            return objetivo_previo

        es_gigante = hasattr(unidad, 'prioriza_defensas') and unidad.prioriza_defensas

        def prioridad(e):
            if es_gigante:
                # El gigante ataca primero torres, luego muros si bloquean, base al final
                if e.tipo.startswith("torre") or e.tipo == "canon":
                    return 0
                if e.tipo == "muro":
                    return 1
                if e.tipo == "base":
                    return 3
                return 2
            else:
                if e.tipo == "base":
                    return 0
                if e.tipo.startswith("torre") or e.tipo == "canon":
                    return 1
                return 2

        objetivo = min(candidatos, key=prioridad)
        unidad._objetivo_actual = objetivo
        return objetivo

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

    def _retirar_trampas_explotadas(self):
        """Quita del mapa las trampas que ya se vieron explotar."""
        from utils.constantes import FILAS, COLUMNAS
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                est = self.mapa.celdas[fila][col]
                if est and est.tipo == "trampa" and est.activada:
                    self.mapa.celdas[fila][col] = None

    def _limpiar_estructuras_destruidas(self):
        """Elimina del mapa las estructuras destruidas (torres, muros)."""
        from utils.constantes import FILAS, COLUMNAS
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                est = self.mapa.celdas[fila][col]
                if est and est.destruida and est.tipo not in ("base", "trampa"):
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
