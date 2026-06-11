"""
clases/ventana_juego.py
Ventana principal del juego.
Maneja la fase de construcción, la fase de ataque y el combate automático.
"""

import tkinter as tk
from tkinter import messagebox

from clases.mapa import Mapa
from clases.canvas_mapa import CanvasMapa
from clases.estructuras import crear_estructura
from clases.unidades import crear_unidad
from clases.combate import MotorCombate
from utils.constantes import (
    COLOR_FONDO, COLOR_PANEL, COLOR_ACENTO, COLOR_TEXTO, COLOR_BOTON,
    DEFENSAS, TROPAS, FACCIONES, INTERVALO_COMBATE_MS,
    FILAS, COLUMNAS, BASE_FILA, BASE_COL
)


class VentanaJuego:
    """
    Pantalla principal de juego.
    Ciclo: construcción → ataque → combate → resultado.
    """

    def __init__(self, padre: tk.Widget, jugador1, jugador2,
                 gestor_sonido, callback_resultado):
        """
        Args:
            jugador1, jugador2: Instancias de Jugador.
            callback_resultado: función(ganador_username, perdedor_username)
        """
        self.padre = padre
        self.j1 = jugador1
        self.j2 = jugador2
        self.gestor_sonido = gestor_sonido
        self.callback_resultado = callback_resultado

        # Estado interno
        self.mapa = Mapa()
        self.fase = "construccion"        # 'construccion', 'ataque', 'combate'
        self.item_seleccionado = None     # qué se va a construir/desplegar
        self.defensor = None
        self.atacante = None
        self.motor_combate = None
        self._job_combate = None          # referencia a after()

        # Determinar roles iniciales
        self._asignar_roles()
        self._construir_ui()

    # ──────────────────────────────────────────
    # INICIALIZACIÓN
    # ──────────────────────────────────────────

    def _asignar_roles(self):
        """Asigna defensor y atacante según el rol actual."""
        if self.j1.rol == "defensor":
            self.defensor = self.j1
            self.atacante = self.j2
        else:
            self.defensor = self.j2
            self.atacante = self.j1

    def _construir_ui(self):
        """Construye la interfaz completa del juego."""
        self.frame = tk.Frame(self.padre, bg=COLOR_FONDO)
        self.frame.pack(fill="both", expand=True)

        # ── Barra superior (HUD) ──
        self._crear_hud()

        # ── Área central: mapa + panel lateral ──
        area_central = tk.Frame(self.frame, bg=COLOR_FONDO)
        area_central.pack(fill="both", expand=True, padx=10, pady=5)

        # Panel lateral izquierdo
        self.panel_lateral = tk.Frame(area_central, bg=COLOR_PANEL, width=200, padx=10, pady=10)
        self.panel_lateral.pack(side="left", fill="y", padx=(0, 10))
        self.panel_lateral.pack_propagate(False)

        # Canvas del mapa
        frame_mapa = tk.Frame(area_central, bg=COLOR_FONDO)
        frame_mapa.pack(side="left")

        self.canvas_mapa = CanvasMapa(
            frame_mapa, self.mapa,
            self.defensor.faccion,
            callback_clic=self._on_clic_mapa
        )

        # Panel de log derecho
        frame_log = tk.Frame(area_central, bg=COLOR_PANEL, width=200, padx=8, pady=8)
        frame_log.pack(side="left", fill="y", padx=(10, 0))
        frame_log.pack_propagate(False)

        tk.Label(frame_log, text="📋 REGISTRO", font=("Courier", 10, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).pack()

        self.texto_log = tk.Text(
            frame_log, font=("Courier", 8),
            bg="#0d1b2e", fg="#aaffaa",
            wrap="word", state="disabled",
            relief="flat", width=24
        )
        self.texto_log.pack(fill="both", expand=True, pady=(5, 0))

        # Iniciar fase de construcción
        self._iniciar_fase_construccion()

    def _crear_hud(self):
        """Crea la barra superior con información del juego."""
        hud = tk.Frame(self.frame, bg=COLOR_PANEL, padx=15, pady=8)
        hud.pack(fill="x")

        # Jugador 1
        tk.Label(hud, text=f"⚔️  {self.j1.username}",
                 font=("Courier", 11, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).pack(side="left")

        tk.Label(hud, text=f"({self.j1.faccion})",
                 font=("Courier", 9),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(side="left", padx=(4, 20))

        # Gemas J1
        self.lbl_gemas_j1 = tk.Label(hud, text=f"💎 {self.j1.gemas}",
                                      font=("Courier", 11),
                                      bg=COLOR_PANEL, fg="#88ddff")
        self.lbl_gemas_j1.pack(side="left", padx=(0, 30))

        # Fase actual
        self.lbl_fase = tk.Label(hud, text="📐 CONSTRUCCIÓN",
                                  font=("Courier", 12, "bold"),
                                  bg=COLOR_PANEL, fg="white")
        self.lbl_fase.pack(side="left", expand=True)

        # Gemas J2
        self.lbl_gemas_j2 = tk.Label(hud, text=f"💎 {self.j2.gemas}",
                                      font=("Courier", 11),
                                      bg=COLOR_PANEL, fg="#88ddff")
        self.lbl_gemas_j2.pack(side="right", padx=(30, 0))

        # Jugador 2
        tk.Label(hud, text=f"({self.j2.faccion})",
                 font=("Courier", 9),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(side="right", padx=(4, 0))

        tk.Label(hud, text=f"🛡️  {self.j2.username}",
                 font=("Courier", 11, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).pack(side="right")

    # ──────────────────────────────────────────
    # FASE DE CONSTRUCCIÓN
    # ──────────────────────────────────────────

    def _iniciar_fase_construccion(self):
        """Prepara la fase de construcción del defensor."""
        self.fase = "construccion"
        self.defensor.iniciar_como_defensor()
        self.atacante.iniciar_como_atacante()

        self.lbl_fase.config(text=f"📐 CONSTRUCCIÓN — {self.defensor.username}")
        self._actualizar_gemas()
        self._poblar_panel_construccion()
        self._log(f"=== FASE DE CONSTRUCCIÓN ===")
        self._log(f"{self.defensor.username} construye su base.")
        self._log(f"Gemas disponibles: {self.defensor.gemas}")

    def _poblar_panel_construccion(self):
        """Llena el panel lateral con botones de estructuras."""
        for widget in self.panel_lateral.winfo_children():
            widget.destroy()

        tk.Label(self.panel_lateral, text="🏗️ CONSTRUCCIÓN",
                 font=("Courier", 10, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).pack(pady=(0, 8))

        tk.Label(self.panel_lateral,
                 text=f"Defensor:\n{self.defensor.username}",
                 font=("Courier", 9),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(0, 5))

        # Separador
        tk.Frame(self.panel_lateral, bg=COLOR_ACENTO, height=1).pack(fill="x", pady=5)

        # Botón de selección para cada defensa
        self.botones_defensa = {}
        for nombre, datos in DEFENSAS.items():
            btn = tk.Button(
                self.panel_lateral,
                text=f"{nombre}\n💎{datos['costo']}",
                font=("Courier", 8),
                bg=COLOR_BOTON, fg="white",
                relief="flat", cursor="hand2",
                wraplength=160, pady=4,
                command=lambda n=nombre, t=datos["tipo"]: self._seleccionar_item(n, t)
            )
            btn.pack(fill="x", pady=2)
            self.botones_defensa[nombre] = btn

        # Separador
        tk.Frame(self.panel_lateral, bg="#333", height=1).pack(fill="x", pady=8)

        # Botón para terminar construcción
        tk.Button(
            self.panel_lateral,
            text="✅ TERMINAR\nCONSTRUCCIÓN",
            font=("Courier", 9, "bold"),
            bg="#005500", fg="white",
            relief="flat", cursor="hand2",
            pady=6,
            command=self._terminar_construccion
        ).pack(fill="x", pady=4)

        # Etiqueta de ítem seleccionado
        self.lbl_seleccionado = tk.Label(
            self.panel_lateral, text="Clic en el mapa\npara construir",
            font=("Courier", 8), bg=COLOR_PANEL, fg="#aaaaaa", wraplength=170
        )
        self.lbl_seleccionado.pack(pady=5)

    def _seleccionar_item(self, nombre: str, tipo: str):
        """Selecciona el ítem a construir."""
        self.item_seleccionado = {"nombre": nombre, "tipo": tipo}
        self.lbl_seleccionado.config(
            text=f"Seleccionado:\n{nombre}",
            fg=COLOR_ACENTO
        )
        # Resaltar botón activo
        for n, btn in self.botones_defensa.items():
            btn.config(bg=COLOR_ACENTO if n == nombre else COLOR_BOTON)

    def _terminar_construccion(self):
        """Pasa a la fase de ataque."""
        self._iniciar_fase_ataque()

    # ──────────────────────────────────────────
    # FASE DE ATAQUE
    # ──────────────────────────────────────────

    def _iniciar_fase_ataque(self):
        """Prepara la fase de ataque."""
        self.fase = "ataque"
        self.item_seleccionado = None
        self.lbl_fase.config(text=f"⚔️  ATAQUE — {self.atacante.username}")
        self._actualizar_gemas()
        self._poblar_panel_ataque()
        self._log(f"\n=== FASE DE ATAQUE ===")
        self._log(f"{self.atacante.username} despliega tropas.")

    def _poblar_panel_ataque(self):
        """Llena el panel lateral con botones de tropas."""
        for widget in self.panel_lateral.winfo_children():
            widget.destroy()

        tk.Label(self.panel_lateral, text="⚔️  TROPAS",
                 font=("Courier", 10, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).pack(pady=(0, 8))

        tk.Label(self.panel_lateral,
                 text=f"Atacante:\n{self.atacante.username}",
                 font=("Courier", 9),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(0, 5))

        tk.Frame(self.panel_lateral, bg=COLOR_ACENTO, height=1).pack(fill="x", pady=5)

        self.botones_tropa = {}
        for nombre, datos in TROPAS.items():
            btn = tk.Button(
                self.panel_lateral,
                text=f"{nombre}\n💎{datos['costo']}",
                font=("Courier", 8),
                bg=COLOR_BOTON, fg="white",
                relief="flat", cursor="hand2",
                wraplength=160, pady=4,
                command=lambda n=nombre, t=datos["tipo"]: self._seleccionar_tropa(n, t)
            )
            btn.pack(fill="x", pady=2)
            self.botones_tropa[nombre] = btn

        tk.Frame(self.panel_lateral, bg="#333", height=1).pack(fill="x", pady=8)

        tk.Button(
            self.panel_lateral,
            text="⚔️  INICIAR\nCOMBATE",
            font=("Courier", 9, "bold"),
            bg="#660000", fg="white",
            relief="flat", cursor="hand2",
            pady=6,
            command=self._iniciar_combate
        ).pack(fill="x", pady=4)

        tk.Label(self.panel_lateral,
                 text="Clic en borde del\nmapa para desplegar",
                 font=("Courier", 8),
                 bg=COLOR_PANEL, fg="#aaaaaa").pack(pady=5)

    def _seleccionar_tropa(self, nombre: str, tipo: str):
        """Selecciona la tropa a desplegar."""
        self.item_seleccionado = {"nombre": nombre, "tipo": tipo}
        for n, btn in self.botones_tropa.items():
            btn.config(bg=COLOR_ACENTO if n == nombre else COLOR_BOTON)

    # ──────────────────────────────────────────
    # CLIC EN EL MAPA
    # ──────────────────────────────────────────

    def _on_clic_mapa(self, fila: int, col: int):
        """Maneja el clic en una celda del mapa."""
        if not self.item_seleccionado:
            return

        if self.fase == "construccion":
            self._colocar_estructura(fila, col)
        elif self.fase == "ataque":
            self._colocar_tropa(fila, col)

    def _colocar_estructura(self, fila: int, col: int):
        """Intenta colocar la estructura seleccionada en (fila, col)."""
        datos = DEFENSAS[self.item_seleccionado["nombre"]]
        costo = datos["costo"]

        # Verificar gemas
        if self.defensor.gemas < costo:
            self._log(f"❌ Sin gemas para {self.item_seleccionado['nombre']} (costo: {costo})")
            return

        # No sobre la base
        if fila == BASE_FILA and col == BASE_COL:
            self._log("❌ No puedes construir sobre la base central.")
            return

        # Crear y colocar
        est = crear_estructura(self.item_seleccionado["tipo"], fila, col)
        if est and self.mapa.colocar_estructura(est):
            self.defensor.gastar_gemas(costo)
            self._actualizar_gemas()
            self.canvas_mapa.actualizar()
            self._log(f"✅ {self.item_seleccionado['nombre']} en ({fila},{col})")
            self.gestor_sonido.reproducir("construccion")
        else:
            self._log(f"❌ No se puede construir en ({fila},{col})")

    def _colocar_tropa(self, fila: int, col: int):
        """Intenta desplegar la tropa seleccionada en el borde."""
        if not self.mapa.es_borde(fila, col):
            self._log("❌ Las tropas solo se despliegan en los bordes del mapa.")
            return

        datos = TROPAS[self.item_seleccionado["nombre"]]
        costo = datos["costo"]

        if self.atacante.gemas < costo:
            self._log(f"❌ Sin gemas para {self.item_seleccionado['nombre']} (costo: {costo})")
            return

        unidad = crear_unidad(self.item_seleccionado["tipo"], fila, col)
        if unidad and self.mapa.agregar_unidad(unidad):
            self.atacante.gastar_gemas(costo)
            self._actualizar_gemas()
            self.canvas_mapa.actualizar()
            self._log(f"✅ {self.item_seleccionado['nombre']} desplegado en ({fila},{col})")
        else:
            self._log(f"❌ No se puede desplegar en ({fila},{col})")

    # ──────────────────────────────────────────
    # COMBATE AUTOMÁTICO
    # ──────────────────────────────────────────

    def _iniciar_combate(self):
        """Inicia el combate automático."""
        if len(self.mapa.unidades_vivas()) == 0:
            messagebox.showinfo("Ataque", "Debes desplegar al menos una tropa primero.")
            return

        self.fase = "combate"
        self.canvas_mapa.deshabilitar_clic()
        self.lbl_fase.config(text="💥 COMBATE EN PROGRESO")

        # Deshabilitar panel
        for widget in self.panel_lateral.winfo_children():
            widget.config(state="disabled") if hasattr(widget, 'config') else None

        # Mostrar mensaje
        tk.Label(self.panel_lateral, text="⚔️  COMBATE\nEN PROGRESO...",
                 font=("Courier", 11, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).pack(pady=20)

        # Crear motor de combate
        self.motor_combate = MotorCombate(
            self.mapa,
            callback_log=self._log,
            callback_sonido=self.gestor_sonido.reproducir
        )
        self.motor_combate.iniciar()

        self._log("\n=== ¡COMBATE INICIADO! ===")

        # Iniciar loop de combate
        self._turno_combate()

    def _turno_combate(self):
        """Ejecuta un turno de combate y programa el siguiente."""
        if not self.motor_combate:
            return

        resultado = self.motor_combate.ejecutar_turno()
        self.canvas_mapa.actualizar()

        if resultado == "continua":
            # Programar el siguiente turno
            self._job_combate = self.padre.after(INTERVALO_COMBATE_MS, self._turno_combate)
        else:
            # Combate terminado
            self._finalizar_ronda(resultado)

    def _finalizar_ronda(self, resultado: str):
        """Procesa el resultado de la ronda."""
        if resultado == "atacante_gana":
            ganador = self.atacante
            perdedor = self.defensor
            razon = "¡La base fue destruida!"
            self.gestor_sonido.reproducir("explosion")
        else:
            ganador = self.defensor
            perdedor = self.atacante
            razon = "¡Todas las tropas fueron eliminadas!"
            self.gestor_sonido.reproducir("victoria")

        self._log(f"\n🏆 ¡{ganador.username} GANÓ LA RONDA!")
        self._log(razon)

        ganador.ganar_ronda()

        # Destruir el frame actual y notificar
        self.padre.after(1500, lambda: self._notificar_resultado(ganador, perdedor))

    def _notificar_resultado(self, ganador, perdedor):
        """Limpia y llama al callback de resultado."""
        if self._job_combate:
            self.padre.after_cancel(self._job_combate)
        self.frame.destroy()
        self.callback_resultado(ganador.username, perdedor.username)

    # ──────────────────────────────────────────
    # UTILIDADES
    # ──────────────────────────────────────────

    def _actualizar_gemas(self):
        """Actualiza los labels de gemas en el HUD."""
        self.lbl_gemas_j1.config(text=f"💎 {self.j1.gemas}")
        self.lbl_gemas_j2.config(text=f"💎 {self.j2.gemas}")

    def _log(self, mensaje: str):
        """Agrega un mensaje al panel de log."""
        self.texto_log.config(state="normal")
        self.texto_log.insert("end", mensaje + "\n")
        self.texto_log.see("end")
        self.texto_log.config(state="disabled")
