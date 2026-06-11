"""
clases/ventana_ranking.py
Muestra el top de jugadores defensores y atacantes.
Lee datos desde el JSON.
"""

import tkinter as tk
from utils.constantes import COLOR_FONDO, COLOR_PANEL, COLOR_ACENTO, COLOR_TEXTO, COLOR_BOTON


class VentanaRanking:
    """Pantalla de rankings con top 5 defensores y atacantes."""

    def __init__(self, padre: tk.Widget, gestor_datos, callback_volver):
        self.padre = padre
        self.gestor_datos = gestor_datos
        self.callback_volver = callback_volver
        self._construir_ui()

    def _construir_ui(self):
        self.frame = tk.Frame(self.padre, bg=COLOR_FONDO)
        self.frame.pack(fill="both", expand=True)

        tk.Label(
            self.frame,
            text="🏆 TOP JUGADORES",
            font=("Courier", 26, "bold"),
            bg=COLOR_FONDO, fg=COLOR_ACENTO
        ).pack(pady=(40, 30))

        contenedor = tk.Frame(self.frame, bg=COLOR_FONDO)
        contenedor.pack()

        # Top defensores
        self._crear_tabla(contenedor, "🛡️  Top Defensores", "defensor", side="left")

        # Separador
        tk.Frame(contenedor, bg=COLOR_ACENTO, width=2).pack(side="left", fill="y", padx=30, pady=10)

        # Top atacantes
        self._crear_tabla(contenedor, "⚔️  Top Atacantes", "atacante", side="left")

        # Botón volver
        tk.Button(
            self.frame,
            text="← VOLVER AL MENÚ",
            font=("Courier", 12, "bold"),
            bg=COLOR_BOTON, fg="white",
            relief="flat", cursor="hand2",
            padx=20, pady=8,
            command=self._volver
        ).pack(pady=40)

    def _crear_tabla(self, padre, titulo: str, tipo: str, side: str):
        """Crea una tabla de ranking para un tipo de jugador."""
        panel = tk.Frame(padre, bg=COLOR_PANEL, padx=30, pady=20)
        panel.pack(side=side)

        tk.Label(panel, text=titulo,
                 font=("Courier", 14, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).pack(pady=(0, 15))

        # Cabecera
        cab = tk.Frame(panel, bg=COLOR_PANEL)
        cab.pack(fill="x")
        tk.Label(cab, text="Pos", width=4, font=("Courier", 10, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(side="left")
        tk.Label(cab, text="Jugador", width=14, font=("Courier", 10, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(side="left")
        tk.Label(cab, text="Victorias", width=9, font=("Courier", 10, "bold"),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(side="left")

        tk.Frame(panel, bg="#444", height=1).pack(fill="x", pady=5)

        # Datos
        ranking = self.gestor_datos.obtener_top_jugadores(tipo, limite=5)

        medallas = ["🥇", "🥈", "🥉", "4️⃣ ", "5️⃣ "]

        if not ranking or all(v == 0 for _, v in ranking):
            tk.Label(panel, text="Sin datos aún",
                     font=("Courier", 10), bg=COLOR_PANEL, fg="#666666").pack(pady=10)
            return

        for i, (username, victorias) in enumerate(ranking):
            fila = tk.Frame(panel, bg=COLOR_PANEL)
            fila.pack(fill="x", pady=2)

            medalla = medallas[i] if i < len(medallas) else f"{i+1}.  "
            color_fila = COLOR_ACENTO if i == 0 else COLOR_TEXTO

            tk.Label(fila, text=medalla, width=4,
                     font=("Courier", 10),
                     bg=COLOR_PANEL, fg=color_fila).pack(side="left")
            tk.Label(fila, text=username, width=14,
                     font=("Courier", 10),
                     bg=COLOR_PANEL, fg=color_fila).pack(side="left")
            tk.Label(fila, text=str(victorias), width=9,
                     font=("Courier", 10),
                     bg=COLOR_PANEL, fg=color_fila).pack(side="left")

    def _volver(self):
        self.frame.destroy()
        self.callback_volver()
