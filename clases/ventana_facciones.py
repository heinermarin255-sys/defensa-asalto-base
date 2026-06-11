"""
clases/ventana_facciones.py
Ventana para que cada jugador elija su facción.
Los dos jugadores no pueden elegir la misma.
"""

import tkinter as tk
from utils.constantes import COLOR_FONDO, COLOR_PANEL, COLOR_ACENTO, COLOR_TEXTO, COLOR_BOTON, FACCIONES


class VentanaFacciones:
    """
    Muestra las 3 facciones disponibles.
    Cada jugador elige en orden; no pueden repetir.
    """

    def __init__(self, padre: tk.Widget, username1: str, username2: str, callback_exito):
        """
        Args:
            callback_exito: función(username1, faccion1, username2, faccion2)
        """
        self.padre = padre
        self.username1 = username1
        self.username2 = username2
        self.callback_exito = callback_exito

        self.faccion_j1 = None
        self.faccion_j2 = None

        self._construir_ui()

    def _construir_ui(self):
        self.frame = tk.Frame(self.padre, bg=COLOR_FONDO)
        self.frame.pack(fill="both", expand=True)

        tk.Label(
            self.frame,
            text="🏰 ELIGE TU FACCIÓN",
            font=("Courier", 24, "bold"),
            bg=COLOR_FONDO, fg=COLOR_ACENTO
        ).pack(pady=(40, 5))

        self.lbl_turno = tk.Label(
            self.frame,
            text=f"{self.username1} elige primero",
            font=("Courier", 13),
            bg=COLOR_FONDO, fg=COLOR_TEXTO
        )
        self.lbl_turno.pack(pady=(0, 25))

        # Contenedor de tarjetas de facción
        self.frame_facciones = tk.Frame(self.frame, bg=COLOR_FONDO)
        self.frame_facciones.pack()

        self.botones_faccion = {}
        self._dibujar_facciones()

        # Panel de selecciones actuales
        self.lbl_selecciones = tk.Label(
            self.frame,
            text="",
            font=("Courier", 11),
            bg=COLOR_FONDO, fg="#aaaaaa"
        )
        self.lbl_selecciones.pack(pady=20)

    def _dibujar_facciones(self):
        """Dibuja las tarjetas de cada facción."""
        for widget in self.frame_facciones.winfo_children():
            widget.destroy()

        for nombre, datos in FACCIONES.items():
            tarjeta = tk.Frame(
                self.frame_facciones,
                bg=datos["color_fondo_panel"],
                padx=20, pady=20,
                relief="groove", bd=2,
                width=200
            )
            tarjeta.pack(side="left", padx=15, pady=10)

            # Emoji representativo
            tk.Label(
                tarjeta, text=datos["emoji_base"],
                font=("Courier", 36),
                bg=datos["color_fondo_panel"]
            ).pack()

            tk.Label(
                tarjeta, text=nombre,
                font=("Courier", 14, "bold"),
                bg=datos["color_fondo_panel"],
                fg=datos["color_torre"]
            ).pack(pady=(5, 2))

            tk.Label(
                tarjeta, text=datos["descripcion"],
                font=("Courier", 9),
                bg=datos["color_fondo_panel"],
                fg=COLOR_TEXTO,
                wraplength=160
            ).pack(pady=(0, 10))

            # Muestra de colores de la facción
            muestra = tk.Frame(tarjeta, bg=datos["color_fondo_panel"])
            muestra.pack(pady=(0, 10))
            for color in [datos["color_torre"], datos["color_tropa"], datos["color_muro"]]:
                tk.Label(muestra, bg=color, width=3, height=1).pack(side="left", padx=2)

            # Estado del botón
            ya_elegida = (nombre == self.faccion_j1 or nombre == self.faccion_j2)
            estado = "disabled" if ya_elegida else "normal"
            texto_btn = "✓ Elegida" if ya_elegida else f"Elegir {nombre}"
            color_btn = "#555555" if ya_elegida else COLOR_ACENTO

            btn = tk.Button(
                tarjeta,
                text=texto_btn,
                font=("Courier", 10, "bold"),
                bg=color_btn, fg="white",
                relief="flat", cursor="hand2" if not ya_elegida else "arrow",
                state=estado,
                command=lambda n=nombre: self._elegir_faccion(n)
            )
            btn.pack(fill="x")
            self.botones_faccion[nombre] = btn

    def _elegir_faccion(self, nombre: str):
        """Procesa la selección de una facción."""
        # Turno del jugador 1
        if self.faccion_j1 is None:
            self.faccion_j1 = nombre
            self.lbl_turno.config(
                text=f"{self.username2} elige ahora",
                fg=COLOR_ACENTO
            )
            self.lbl_selecciones.config(
                text=f"{self.username1}: {nombre}  |  {self.username2}: pendiente"
            )
            self._dibujar_facciones()

        # Turno del jugador 2
        elif self.faccion_j2 is None and nombre != self.faccion_j1:
            self.faccion_j2 = nombre
            self.lbl_selecciones.config(
                text=f"{self.username1}: {self.faccion_j1}  |  {self.username2}: {nombre}"
            )

            # Breve pausa y continuar
            self.frame.after(800, self._continuar)

    def _continuar(self):
        """Llama al callback con las facciones elegidas."""
        self.frame.destroy()
        self.callback_exito(
            self.username1, self.faccion_j1,
            self.username2, self.faccion_j2
        )
