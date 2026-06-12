"""
clases/canvas_mapa.py
Renderiza el mapa 10x10 usando tkinter.Canvas.
Dibuja celdas, estructuras y unidades.
"""

import os
import tkinter as tk
from utils.constantes import (
    FILAS, COLUMNAS, TAMANO_CELDA,
    COLOR_CELDA_VACIA, COLOR_CELDA_BORDE, COLOR_ACENTO,
    FACCIONES, BASE_FILA, BASE_COL,
    SUFIJO_FACCION, IMAGENES_DEFENSAS
)

# Pillow se usa (si está disponible) para escalar las imágenes de las
# cartas al tamaño exacto de cada celda. Si no está instalado, el juego
# sigue funcionando con el dibujo de respaldo (colores + emojis).
try:
    from PIL import Image, ImageTk
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False


class CanvasMapa:
    """
    Widget de canvas que dibuja el mapa del juego.
    Se actualiza llamando a actualizar().
    """

    ANCHO = COLUMNAS * TAMANO_CELDA
    ALTO = FILAS * TAMANO_CELDA

    def __init__(self, padre: tk.Widget, mapa, faccion_defensor: str,
                 callback_clic=None):
        """
        Args:
            padre: Frame contenedor.
            mapa: Instancia de Mapa.
            faccion_defensor: Nombre de la facción del defensor.
            callback_clic: función(fila, col) al hacer clic en el mapa.
        """
        self.mapa = mapa
        self.faccion = faccion_defensor
        self.colores = FACCIONES[faccion_defensor]
        self.callback_clic = callback_clic
        self.celda_hover = None

        self.canvas = tk.Canvas(
            padre,
            width=self.ANCHO,
            height=self.ALTO,
            bg="#0d1b2e",
            highlightthickness=2,
            highlightbackground=COLOR_ACENTO
        )
        self.canvas.pack()

        if callback_clic:
            self.canvas.bind("<Button-1>", self._on_clic)
            self.canvas.bind("<Motion>", self._on_hover)
            self.canvas.bind("<Leave>", self._on_leave)

        # Cargar las imágenes de las defensas según la facción del defensor
        self.imagenes_defensas = {}
        self._cargar_imagenes_defensas()

        self.dibujar()

    def _cargar_imagenes_defensas(self):
        """
        Carga las imágenes de las cartas de defensa correspondientes a la
        facción del defensor (sufijo N = Naturaleza, F = Futurista,
        M = Medieval) y las escala al tamaño de una celda del mapa.
        """
        sufijo = SUFIJO_FACCION.get(self.faccion, "M")
        carpeta = os.path.join(os.path.dirname(__file__), "..", "imagenes")
        tamano = TAMANO_CELDA - 6  # pequeño margen respecto al borde de la celda

        for tipo, prefijo in IMAGENES_DEFENSAS.items():
            ruta = os.path.join(carpeta, f"{prefijo}{sufijo}.png")

            if not os.path.exists(ruta):
                continue

            try:
                if PIL_DISPONIBLE:
                    imagen = Image.open(ruta).convert("RGBA")
                    imagen = imagen.resize((tamano, tamano), Image.LANCZOS)
                    self.imagenes_defensas[tipo] = ImageTk.PhotoImage(imagen)
                else:
                    # Sin Pillow: reducir con subsample (factores enteros)
                    imagen = tk.PhotoImage(file=ruta)
                    factor = max(1, imagen.width() // tamano)
                    if factor > 1:
                        imagen = imagen.subsample(factor, factor)
                    self.imagenes_defensas[tipo] = imagen
            except Exception as e:
                print(f"[MAPA] No se pudo cargar la imagen {ruta}: {e}")

    # ──────────────────────────────────────────
    # DIBUJO PRINCIPAL
    # ──────────────────────────────────────────

    def dibujar(self):
        """Redibuja todo el mapa."""
        self.canvas.delete("all")

        for fila in range(FILAS):
            for col in range(COLUMNAS):
                self._dibujar_celda(fila, col)

        # Dibujar unidades encima de todo
        for unidad in self.mapa.unidades_vivas():
            self._dibujar_unidad(unidad)

    def _dibujar_celda(self, fila: int, col: int):
        """Dibuja una celda individual con su contenido."""
        x0 = col * TAMANO_CELDA
        y0 = fila * TAMANO_CELDA
        x1 = x0 + TAMANO_CELDA
        y1 = y0 + TAMANO_CELDA
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        es_borde = (fila == 0 or fila == FILAS - 1 or col == 0 or col == COLUMNAS - 1)
        estructura = self.mapa.celdas[fila][col]

        # Color de fondo de la celda
        if self.celda_hover == (fila, col) and self.callback_clic:
            color_fondo = "#3a6b9e"
        elif es_borde:
            color_fondo = "#1a3352"
        else:
            color_fondo = COLOR_CELDA_VACIA

        # Dibujar fondo
        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=color_fondo,
            outline=COLOR_CELDA_BORDE,
            width=1
        )

        # Dibujar contenido
        if estructura:
            self._dibujar_estructura(estructura, x0, y0, x1, y1, cx, cy)
        elif es_borde:
            # Indicador de borde (zona de despliegue de tropas)
            self.canvas.create_text(
                cx, cy, text="·",
                font=("Courier", 8), fill="#2a4a6e"
            )

    def _dibujar_estructura(self, est, x0, y0, x1, y1, cx, cy):
        """Dibuja una estructura dentro de su celda."""
        tipo = est.tipo
        colores = self.colores
        porcentaje = est.porcentaje_vida()

        # Si existe una imagen de carta para esta defensa, usarla
        if tipo in self.imagenes_defensas:
            self.canvas.create_image(cx, cy - 2, image=self.imagenes_defensas[tipo])
            self._dibujar_barra_vida(x0, y1 - 8, x1, y1 - 2, porcentaje)
            return

        # ── Dibujo de respaldo (sin imagen disponible) ──
        # Color de fondo según tipo
        colores_fondo = {
            "base": colores["color_base"],
            "muro": colores["color_muro"],
            "trampa": colores["color_trampa"],
            "torre_arquera": colores["color_torre"],
            "torre_magos": "#6b2fa0",
            "torre_infernal": "#8b0000",
            "canon": "#4a4a4a",
        }

        emojis = {
            "base": colores["emoji_base"],
            "muro": colores["emoji_muro"],
            "trampa": colores["emoji_trampa"],
            "torre_arquera": colores["emoji_torre"],
            "torre_magos": "🔮",
            "torre_infernal": "🔥",
            "canon": "💂",
        }

        color = colores_fondo.get(tipo, "#555555")
        emoji = emojis.get(tipo, "?")

        # Fondo de la estructura
        margen = 3
        self.canvas.create_rectangle(
            x0 + margen, y0 + margen, x1 - margen, y1 - margen,
            fill=color, outline="white", width=1
        )

        # Emoji/símbolo
        self.canvas.create_text(
            cx, cy - 4, text=emoji,
            font=("Courier", 14)
        )

        # Barra de vida
        self._dibujar_barra_vida(x0, y1 - 8, x1, y1 - 2, porcentaje)

    def _dibujar_barra_vida(self, x0, y0, x1, y1, porcentaje: float):
        """Dibuja una pequeña barra de vida."""
        self.canvas.create_rectangle(x0 + 2, y0, x1 - 2, y1, fill="#333333", outline="")
        ancho_vida = int((x1 - x0 - 4) * porcentaje)
        if ancho_vida > 0:
            color_vida = "#00ff44" if porcentaje > 0.5 else ("#ffaa00" if porcentaje > 0.25 else "#ff2244")
            self.canvas.create_rectangle(x0 + 2, y0, x0 + 2 + ancho_vida, y1, fill=color_vida, outline="")

    def _dibujar_unidad(self, unidad):
        """Dibuja una unidad sobre el mapa."""
        x0 = unidad.col * TAMANO_CELDA
        y0 = unidad.fila * TAMANO_CELDA
        cx = x0 + TAMANO_CELDA // 2
        cy = y0 + TAMANO_CELDA // 2

        # Círculo de la unidad
        radio = TAMANO_CELDA // 3
        self.canvas.create_oval(
            cx - radio, cy - radio - 4,
            cx + radio, cy + radio - 4,
            fill=self.colores["color_tropa"],
            outline="white", width=1
        )

        # Símbolo de la unidad
        emojis_unidad = {
            "duende": "👺",
            "gigante": "🦍",
            "arquera": "🏹",
            "pekka": "⚡",
        }
        emoji = emojis_unidad.get(unidad.tipo, "★")
        self.canvas.create_text(cx, cy - 4, text=emoji, font=("Courier", 10))

        # Barra de vida pequeña
        self._dibujar_barra_vida(
            x0, y0 + TAMANO_CELDA - 7,
            x0 + TAMANO_CELDA, y0 + TAMANO_CELDA - 2,
            unidad.porcentaje_vida()
        )

    # ──────────────────────────────────────────
    # EVENTOS
    # ──────────────────────────────────────────

    def _on_clic(self, evento):
        """Convierte coordenadas de píxeles a celda y llama al callback."""
        fila = evento.y // TAMANO_CELDA
        col = evento.x // TAMANO_CELDA
        if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
            if self.callback_clic:
                self.callback_clic(fila, col)

    def _on_hover(self, evento):
        fila = evento.y // TAMANO_CELDA
        col = evento.x // TAMANO_CELDA
        nueva = (fila, col) if (0 <= fila < FILAS and 0 <= col < COLUMNAS) else None
        if nueva != self.celda_hover:
            self.celda_hover = nueva
            self.dibujar()

    def _on_leave(self, _):
        self.celda_hover = None
        self.dibujar()

    def actualizar(self):
        """Actualiza el canvas (redibuja)."""
        self.dibujar()

    def deshabilitar_clic(self):
        """Desactiva los clics en el mapa (durante combate)."""
        self.callback_clic = None

    def habilitar_clic(self, callback):
        """Activa los clics con un nuevo callback."""
        self.callback_clic = callback
