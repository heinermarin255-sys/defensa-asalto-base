"""
clases/juego.py
Clase principal del juego. Orquesta todas las pantallas y la lógica de rondas.
"""

import tkinter as tk
from tkinter import messagebox

from clases.jugador import Jugador
from clases.ventana_login import VentanaLogin
from clases.ventana_facciones import VentanaFacciones
from clases.ventana_juego import VentanaJuego
from clases.ventana_ranking import VentanaRanking
from utils.constantes import (
    COLOR_FONDO, COLOR_PANEL, COLOR_ACENTO, COLOR_TEXTO, COLOR_BOTON,
    RONDAS_PARA_GANAR
)


class Juego:
    """
    Controlador principal del juego.
    Maneja el flujo entre pantallas y el estado global de la partida.
    """

    def __init__(self, ventana: tk.Tk, gestor_sonido, gestor_datos):
        self.ventana = ventana
        self.gestor_sonido = gestor_sonido
        self.gestor_datos = gestor_datos

        # Jugadores activos (instancias de Jugador)
        self.jugador1: Jugador = None
        self.jugador2: Jugador = None

        # Número de ronda actual
        self.ronda_actual = 1

        # Quién es defensor en la ronda 1 (alternará)
        self._turno_defensor = 1     # 1 o 2 (índice de jugador)

    # ──────────────────────────────────────────
    # MENÚ PRINCIPAL
    # ──────────────────────────────────────────

    def mostrar_menu_principal(self):
        """Muestra el menú principal del juego."""
        self._limpiar_ventana()

        frame = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True)

        # Título
        tk.Label(
            frame,
            text="⚔️",
            font=("Courier", 60),
            bg=COLOR_FONDO
        ).pack(pady=(60, 5))

        tk.Label(
            frame,
            text=" Defensa y Asalto de Base",
            font=("Courier", 30, "bold"),
            bg=COLOR_FONDO, fg=COLOR_ACENTO
        ).pack()

        tk.Label(
            frame,
            text="Juego de Estrategia — 2 Jugadores Locales",
            font=("Courier", 12),
            bg=COLOR_FONDO, fg=COLOR_TEXTO
        ).pack(pady=(5, 50))

        # Botones del menú
        botones = [
            ("🎮  NUEVA PARTIDA", self._iniciar_flujo_partida, COLOR_ACENTO),
            ("🏆  RANKINGS", self._mostrar_rankings, COLOR_BOTON),
            ("❌  SALIR", self.ventana.quit, "#333333"),
        ]

        for texto, comando, color in botones:
            tk.Button(
                frame,
                text=texto,
                font=("Courier", 13, "bold"),
                bg=color, fg="white",
                width=24, pady=10,
                relief="flat", cursor="hand2",
                command=comando
            ).pack(pady=8)

        # Versión
        tk.Label(
            frame,
            text="Defensa y Asalto de Base — Intro a la Programación",
            font=("Courier", 9),
            bg=COLOR_FONDO, fg="#555555"
        ).pack(side="bottom", pady=15)

    # ──────────────────────────────────────────
    # FLUJO DE PARTIDA
    # ──────────────────────────────────────────

    def _iniciar_flujo_partida(self):
        """Inicia el flujo: login → facciones → ronda."""
        self._limpiar_ventana()
        VentanaLogin(
            self.ventana,
            self.gestor_datos,
            callback_exito=self._despues_del_login
        )

    def _despues_del_login(self, username1: str, username2: str):
        """Llamado tras login exitoso. Muestra selección de facciones."""
        self._limpiar_ventana()
        VentanaFacciones(
            self.ventana,
            username1, username2,
            callback_exito=self._despues_de_facciones
        )

    def _despues_de_facciones(self, u1: str, f1: str, u2: str, f2: str):
        """Llamado tras elegir facciones. Crea jugadores e inicia ronda 1."""
        self.jugador1 = Jugador(u1, f1)
        self.jugador2 = Jugador(u2, f2)
        self.ronda_actual = 1
        self._turno_defensor = 1

        self._iniciar_ronda()

    def _iniciar_ronda(self):
        """Configura e inicia una ronda."""
        self._limpiar_ventana()

        # Asignar roles según turno
        if self._turno_defensor == 1:
            self.jugador1.rol = "defensor"
            self.jugador2.rol = "atacante"
        else:
            self.jugador1.rol = "atacante"
            self.jugador2.rol = "defensor"

        # Mostrar pantalla de inicio de ronda
        self._mostrar_inicio_ronda()

    def _mostrar_inicio_ronda(self):
        """Pantalla breve que muestra quién es defensor y quién atacante."""
        frame = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True)

        defensor = self.jugador1 if self.jugador1.rol == "defensor" else self.jugador2
        atacante = self.jugador1 if self.jugador1.rol == "atacante" else self.jugador2

        tk.Label(frame, text=f"⚔️  RONDA {self.ronda_actual}",
                 font=("Courier", 30, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_ACENTO).pack(pady=(80, 20))

        # Marcador de rondas
        marcador = tk.Frame(frame, bg=COLOR_PANEL, padx=30, pady=15)
        marcador.pack(pady=10)

        tk.Label(marcador,
                 text=f"{self.jugador1.username}: {self.jugador1.rondas_ganadas} rondas",
                 font=("Courier", 13),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack()
        tk.Label(marcador,
                 text=f"{self.jugador2.username}: {self.jugador2.rondas_ganadas} rondas",
                 font=("Courier", 13),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack()

        tk.Label(frame, text=" ", bg=COLOR_FONDO).pack(pady=10)

        # Roles
        tk.Label(frame,
                 text=f"🛡️  DEFENSOR:  {defensor.username}  ({defensor.faccion})",
                 font=("Courier", 14, "bold"),
                 bg=COLOR_FONDO, fg="#44aaff").pack(pady=5)

        tk.Label(frame,
                 text=f"⚔️   ATACANTE:  {atacante.username}  ({atacante.faccion})",
                 font=("Courier", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_ACENTO).pack(pady=5)

        tk.Button(
            frame,
            text="▶  COMENZAR RONDA",
            font=("Courier", 13, "bold"),
            bg=COLOR_ACENTO, fg="white",
            width=22, pady=10,
            relief="flat", cursor="hand2",
            command=lambda: self._comenzar_ronda(frame)
        ).pack(pady=40)

    def _comenzar_ronda(self, frame_intro):
        """Destruye la intro y lanza la ventana de juego."""
        frame_intro.destroy()

        VentanaJuego(
            self.ventana,
            self.jugador1, self.jugador2,
            self.gestor_sonido,
            callback_resultado=self._resultado_ronda
        )

    def _resultado_ronda(self, username_ganador: str, username_perdedor: str):
        """Llamado tras finalizar el combate de una ronda."""
        self._limpiar_ventana()

        # Mostrar resultado
        self._mostrar_resultado_ronda(username_ganador, username_perdedor)

    def _mostrar_resultado_ronda(self, ganador: str, perdedor: str):
        """Pantalla de resultado de la ronda."""
        frame = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="🏆 RESULTADO DE RONDA",
                 font=("Courier", 22, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_ACENTO).pack(pady=(60, 20))

        tk.Label(frame, text=f"¡{ganador} ganó esta ronda!",
                 font=("Courier", 18),
                 bg=COLOR_FONDO, fg="#00ff88").pack(pady=10)

        # Marcador actual
        panel = tk.Frame(frame, bg=COLOR_PANEL, padx=40, pady=20)
        panel.pack(pady=20)

        for jugador in [self.jugador1, self.jugador2]:
            color = COLOR_ACENTO if jugador.username == ganador else COLOR_TEXTO
            tk.Label(panel,
                     text=f"{jugador.username}: {jugador.rondas_ganadas} / {RONDAS_PARA_GANAR} rondas",
                     font=("Courier", 14, "bold"),
                     bg=COLOR_PANEL, fg=color).pack(pady=5)

        # Verificar si alguien ganó la partida
        ganador_obj = self.jugador1 if self.jugador1.username == ganador else self.jugador2

        if ganador_obj.rondas_ganadas >= RONDAS_PARA_GANAR:
            perdedor_obj = self.jugador2 if ganador_obj == self.jugador1 else self.jugador1
            self._programar_fin_partida(frame, ganador_obj, perdedor_obj)
        else:
            # Continuar con siguiente ronda
            tk.Button(
                frame,
                text="SIGUIENTE RONDA →",
                font=("Courier", 13, "bold"),
                bg=COLOR_BOTON, fg="white",
                width=20, pady=10,
                relief="flat", cursor="hand2",
                command=lambda: self._siguiente_ronda(frame)
            ).pack(pady=30)

    def _programar_fin_partida(self, frame, ganador, perdedor):
        """Muestra botón para ir a la pantalla final."""
        tk.Label(frame, text="🎉 ¡PARTIDA TERMINADA!",
                 font=("Courier", 16, "bold"),
                 bg=COLOR_FONDO, fg="#ffdd00").pack(pady=10)

        tk.Button(
            frame,
            text="VER PANTALLA FINAL →",
            font=("Courier", 13, "bold"),
            bg=COLOR_ACENTO, fg="white",
            width=22, pady=10,
            relief="flat", cursor="hand2",
            command=lambda: self._pantalla_final(frame, ganador, perdedor)
        ).pack(pady=20)

    def _siguiente_ronda(self, frame_resultado):
        """Prepara la siguiente ronda alternando el rol de defensor."""
        frame_resultado.destroy()
        self.ronda_actual += 1
        # Alternar: si el 1 fue defensor, ahora el 2 lo es
        self._turno_defensor = 2 if self._turno_defensor == 1 else 1
        self._iniciar_ronda()

    # ──────────────────────────────────────────
    # FIN DE PARTIDA
    # ──────────────────────────────────────────

    def _pantalla_final(self, frame_resultado, ganador: Jugador, perdedor: Jugador):
        """Muestra la pantalla de ganador final y guarda estadísticas."""
        frame_resultado.destroy()
        self._limpiar_ventana()

        # Guardar estadísticas
        # El ganador puede haber ganado como defensor o atacante en su última ronda
        # Para simplificar: guardamos una victoria genérica en su rol más reciente
        rol_ganador = ganador.rol or "atacante"
        self.gestor_datos.actualizar_estadisticas(ganador.username, rol_ganador)
        self.gestor_datos.actualizar_estadisticas(perdedor.username, perdedor.rol or "defensor")

        # Pantalla final
        frame = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="🏆", font=("Courier", 70), bg=COLOR_FONDO).pack(pady=(50, 5))

        tk.Label(frame,
                 text=f"¡{ganador.username} GANÓ LA PARTIDA!",
                 font=("Courier", 24, "bold"),
                 bg=COLOR_FONDO, fg="#ffdd00").pack(pady=5)

        tk.Label(frame,
                 text=f"Facción: {ganador.faccion}  |  {ganador.rondas_ganadas} rondas ganadas",
                 font=("Courier", 13),
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=(5, 30))

        # Botones finales
        tk.Button(
            frame,
            text="🎮  NUEVA PARTIDA",
            font=("Courier", 12, "bold"),
            bg=COLOR_ACENTO, fg="white",
            width=20, pady=8,
            relief="flat", cursor="hand2",
            command=self._iniciar_flujo_partida
        ).pack(pady=8)

        tk.Button(
            frame,
            text="🏆  VER RANKINGS",
            font=("Courier", 12, "bold"),
            bg=COLOR_BOTON, fg="white",
            width=20, pady=8,
            relief="flat", cursor="hand2",
            command=self._mostrar_rankings
        ).pack(pady=8)

        tk.Button(
            frame,
            text="🏠  MENÚ PRINCIPAL",
            font=("Courier", 12, "bold"),
            bg="#333333", fg="white",
            width=20, pady=8,
            relief="flat", cursor="hand2",
            command=self.mostrar_menu_principal
        ).pack(pady=8)

    # ──────────────────────────────────────────
    # RANKINGS
    # ──────────────────────────────────────────

    def _mostrar_rankings(self):
        """Abre la ventana de rankings."""
        self._limpiar_ventana()
        VentanaRanking(
            self.ventana,
            self.gestor_datos,
            callback_volver=self.mostrar_menu_principal
        )

    # ──────────────────────────────────────────
    # UTILIDADES
    # ──────────────────────────────────────────

    def _limpiar_ventana(self):
        """Elimina todos los widgets de la ventana principal."""
        for widget in self.ventana.winfo_children():
            widget.destroy()
