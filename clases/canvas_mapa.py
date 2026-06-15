"""
clases/canvas_mapa.py
Renderiza el mapa 10x10 usando tkinter.Canvas.
"""

import os
import tkinter as tk
from utils.constantes import (
    FILAS, COLUMNAS, TAMANO_CELDA,
    COLOR_CELDA_BORDE, COLOR_ACENTO,
    FACCIONES, SUFIJO_FACCION, IMAGENES_DEFENSAS, IMAGENES_UNIDADES
)

try:
    from PIL import Image, ImageTk
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

_TERRENO_FACCION = {
    "Naturaleza": "Naturaleza.png",
    "Futurista":  "Futuro.png",
    "Medieval":   "Medieval.png",
}

_OPACIDAD_TERRENO = {
    "Naturaleza": 255,
    "Futurista":  140,
    "Medieval":   140,
}

_RANGO_BOMBA = 1


class CanvasMapa:

    ANCHO = COLUMNAS * TAMANO_CELDA
    ALTO  = FILAS   * TAMANO_CELDA

    def __init__(self, padre: tk.Widget, mapa, faccion_defensor: str,
                 callback_clic=None, faccion_atacante: str = None,
                 fase_ref: list = None):
        self.mapa             = mapa
        self.faccion          = faccion_defensor
        self.faccion_atacante = faccion_atacante or faccion_defensor
        self.colores          = FACCIONES[faccion_defensor]
        self.colores_atacante = FACCIONES[self.faccion_atacante]
        self.callback_clic    = callback_clic
        self.celda_hover      = None
        # lista mutable de un elemento para leer la fase actual desde ventana_juego
        self._fase_ref        = fase_ref if fase_ref is not None else ["construccion"]

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
            self.canvas.bind("<Motion>",   self._on_hover)
            self.canvas.bind("<Leave>",    self._on_leave)

        self.imagen_terreno = None
        self.tiles_terreno  = {}
        self._cargar_imagen_terreno()

        self.imagenes_defensas = {}
        self._cargar_imagenes_defensas()

        self.imagenes_unidades = {}
        self._cargar_imagenes_unidades()

        self.dibujar()

    # ── Carga de recursos ──

    def _cargar_imagen_terreno(self):
        nombre_archivo = _TERRENO_FACCION.get(self.faccion)
        if not nombre_archivo:
            return

        carpeta = os.path.join(os.path.dirname(__file__), "..", "imagenes")
        ruta    = os.path.join(carpeta, nombre_archivo)

        if not PIL_DISPONIBLE:
            if os.path.exists(ruta):
                try:
                    img = tk.PhotoImage(file=ruta)
                    f   = min(max(1, img.width() // self.ANCHO), max(1, img.height() // self.ALTO))
                    if f > 1:
                        img = img.subsample(f, f)
                    self.imagen_terreno = img
                except Exception as e:
                    print(f"[MAPA] {e}")
            return

        if not os.path.exists(ruta):
            return

        try:
            img_src  = Image.open(ruta).convert("RGBA")
            img_full = img_src.resize((self.ANCHO, self.ALTO), Image.LANCZOS)

            # Futurista: reducir saturación y aplicar leve desenfoque
            if self.faccion == "Futurista" and PIL_DISPONIBLE:
                from PIL import ImageEnhance, ImageFilter
                rgb  = img_full.convert("RGB")
                rgb  = ImageEnhance.Color(rgb).enhance(0.45)       # desaturar
                rgb  = ImageEnhance.Brightness(rgb).enhance(0.75)  # oscurecer
                rgb  = rgb.filter(ImageFilter.GaussianBlur(radius=1.2))
                r, g, b = rgb.split()
                _, _, _, a = img_full.split()
                img_full = Image.merge("RGBA", (r, g, b, a))

            opacidad = _OPACIDAD_TERRENO.get(self.faccion, 255)
            if opacidad < 255:
                r, g, b, a = img_full.split()
                a = a.point(lambda v: int(v * opacidad / 255))
                img_full = Image.merge("RGBA", (r, g, b, a))

            tc = TAMANO_CELDA
            for fila in range(FILAS):
                for col in range(COLUMNAS):
                    x0   = col  * tc
                    y0   = fila * tc
                    tile = img_full.crop((x0, y0, x0 + tc, y0 + tc))
                    self.tiles_terreno[(fila, col)] = ImageTk.PhotoImage(tile)

        except Exception as e:
            print(f"[MAPA] {e}")

    def _cargar_imagenes_defensas(self):
        sufijo  = SUFIJO_FACCION.get(self.faccion, "M")
        carpeta = os.path.join(os.path.dirname(__file__), "..", "imagenes")
        tamano        = TAMANO_CELDA - 6
        tamano_muro   = TAMANO_CELDA - 22   # muros más pequeños visualmente

        for tipo, prefijo in IMAGENES_DEFENSAS.items():
            ruta = os.path.join(carpeta, f"{prefijo}{sufijo}.png")
            if not os.path.exists(ruta):
                continue
            t = tamano_muro if tipo == "muro" else tamano
            try:
                if PIL_DISPONIBLE:
                    img = Image.open(ruta).convert("RGBA").resize((t, t), Image.LANCZOS)
                    self.imagenes_defensas[tipo] = ImageTk.PhotoImage(img)
                else:
                    img = tk.PhotoImage(file=ruta)
                    f   = max(1, img.width() // t)
                    self.imagenes_defensas[tipo] = img.subsample(f, f) if f > 1 else img
            except Exception as e:
                print(f"[MAPA] {e}")

    def _cargar_imagenes_unidades(self):
        sufijo  = SUFIJO_FACCION.get(self.faccion_atacante, "M")
        carpeta = os.path.join(os.path.dirname(__file__), "..", "imagenes")
        tamano  = TAMANO_CELDA - 6

        for tipo, prefijo in IMAGENES_UNIDADES.items():
            ruta = os.path.join(carpeta, f"{prefijo}{sufijo}.png")
            if not os.path.exists(ruta):
                continue
            try:
                if PIL_DISPONIBLE:
                    img = Image.open(ruta).convert("RGBA").resize((tamano, tamano), Image.LANCZOS)
                    self.imagenes_unidades[tipo] = ImageTk.PhotoImage(img)
                else:
                    img = tk.PhotoImage(file=ruta)
                    f   = max(1, img.width() // tamano)
                    self.imagenes_unidades[tipo] = img.subsample(f, f) if f > 1 else img
            except Exception as e:
                print(f"[MAPA] {e}")

    # ── Visibilidad de bombas ──

    def _bomba_visible(self, fila: int, col: int) -> bool:
        # Las bombas solo pueden revelarse durante el combate
        if self._fase_ref[0] != "combate":
            return False
        for unidad in self.mapa.unidades_vivas():
            if abs(unidad.fila - fila) + abs(unidad.col - col) <= _RANGO_BOMBA:
                return True
        return False

    # ── Dibujo ──

    def dibujar(self):
        self.canvas.delete("all")

        if self.tiles_terreno:
            for (fila, col), tile in self.tiles_terreno.items():
                self.canvas.create_image(col * TAMANO_CELDA, fila * TAMANO_CELDA,
                                         anchor="nw", image=tile)
        elif self.imagen_terreno:
            self.canvas.create_image(0, 0, anchor="nw", image=self.imagen_terreno)

        for fila in range(FILAS):
            for col in range(COLUMNAS):
                self._dibujar_celda(fila, col)

        for unidad in self.mapa.unidades_vivas():
            self._dibujar_unidad(unidad)

    def _dibujar_celda(self, fila: int, col: int):
        x0 = col  * TAMANO_CELDA
        y0 = fila * TAMANO_CELDA
        x1 = x0 + TAMANO_CELDA
        y1 = y0 + TAMANO_CELDA
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        es_borde  = (fila == 0 or fila == FILAS - 1 or col == 0 or col == COLUMNAS - 1)
        estructura = self.mapa.celdas[fila][col]

        if self.celda_hover == (fila, col) and self.callback_clic:
            self.canvas.create_rectangle(x0, y0, x1, y1,
                fill="#3a6b9e", stipple="gray50", outline=COLOR_CELDA_BORDE, width=1)
        elif es_borde:
            self.canvas.create_rectangle(x0, y0, x1, y1,
                fill="#000000", stipple="gray25", outline=COLOR_CELDA_BORDE, width=1)
        else:
            self.canvas.create_rectangle(x0, y0, x1, y1,
                fill="", outline=COLOR_CELDA_BORDE, width=1)

        if estructura:
            if estructura.tipo == "trampa" and not self._bomba_visible(fila, col):
                return
            self._dibujar_estructura(estructura, x0, y0, x1, y1, cx, cy)
        elif es_borde:
            self.canvas.create_text(cx, cy, text="·", font=("Courier", 8), fill="#2a4a6e")

    def _dibujar_estructura(self, est, x0, y0, x1, y1, cx, cy):
        tipo       = est.tipo
        porcentaje = est.porcentaje_vida()

        if tipo in self.imagenes_defensas:
            self.canvas.create_image(cx, cy - 2, image=self.imagenes_defensas[tipo])
            self._dibujar_barra_vida(x0, y1 - 8, x1, y1 - 2, porcentaje)
            return

        colores = self.colores
        colores_fondo = {
            "base":          colores["color_base"],
            "muro":          colores["color_muro"],
            "trampa":        colores["color_trampa"],
            "torre_arquera": colores["color_torre"],
            "torre_magos":   "#6b2fa0",
            "torre_infernal":"#8b0000",
            "canon":         "#4a4a4a",
        }
        emojis = {
            "base":          "🏛️",
            "muro":          "🧱",
            "trampa":        "💥",
            "torre_arquera": "🗼",
            "torre_magos":   "🔮",
            "torre_infernal":"🔥",
            "canon":         "💂",
        }

        self.canvas.create_rectangle(
            x0 + 3, y0 + 3, x1 - 3, y1 - 3,
            fill=colores_fondo.get(tipo, "#555555"), outline="white", width=1
        )
        self.canvas.create_text(cx, cy - 4, text=emojis.get(tipo, "?"), font=("Courier", 14))
        self._dibujar_barra_vida(x0, y1 - 8, x1, y1 - 2, porcentaje)

    def _dibujar_barra_vida(self, x0, y0, x1, y1, porcentaje: float):
        self.canvas.create_rectangle(x0 + 2, y0, x1 - 2, y1, fill="#333333", outline="")
        ancho = int((x1 - x0 - 4) * porcentaje)
        if ancho > 0:
            color = "#00ff44" if porcentaje > 0.5 else ("#ffaa00" if porcentaje > 0.25 else "#ff2244")
            self.canvas.create_rectangle(x0 + 2, y0, x0 + 2 + ancho, y1, fill=color, outline="")

    def _dibujar_unidad(self, unidad):
        x0 = unidad.col  * TAMANO_CELDA
        y0 = unidad.fila * TAMANO_CELDA
        cx = x0 + TAMANO_CELDA // 2
        cy = y0 + TAMANO_CELDA // 2

        if unidad.tipo in self.imagenes_unidades:
            self.canvas.create_image(cx, cy - 2, image=self.imagenes_unidades[unidad.tipo])
            self._dibujar_barra_vida(x0, y0 + TAMANO_CELDA - 7,
                                     x0 + TAMANO_CELDA, y0 + TAMANO_CELDA - 2,
                                     unidad.porcentaje_vida())
            return

        radio = TAMANO_CELDA // 3
        self.canvas.create_oval(cx - radio, cy - radio - 4, cx + radio, cy + radio - 4,
                                fill=self.colores_atacante["color_tropa"], outline="white", width=1)
        emojis_unidad = {"duende": "👺", "gigante": "🦍", "arquera": "🏹", "pekka": "⚡"}
        self.canvas.create_text(cx, cy - 4, text=emojis_unidad.get(unidad.tipo, "★"),
                                font=("Courier", 10))
        self._dibujar_barra_vida(x0, y0 + TAMANO_CELDA - 7,
                                 x0 + TAMANO_CELDA, y0 + TAMANO_CELDA - 2,
                                 unidad.porcentaje_vida())

    # ── Eventos ──

    def _on_clic(self, evento):
        fila = evento.y // TAMANO_CELDA
        col  = evento.x // TAMANO_CELDA
        if 0 <= fila < FILAS and 0 <= col < COLUMNAS and self.callback_clic:
            self.callback_clic(fila, col)

    def _on_hover(self, evento):
        fila  = evento.y // TAMANO_CELDA
        col   = evento.x // TAMANO_CELDA
        nueva = (fila, col) if (0 <= fila < FILAS and 0 <= col < COLUMNAS) else None
        if nueva != self.celda_hover:
            self.celda_hover = nueva
            self.dibujar()

    def _on_leave(self, _):
        self.celda_hover = None
        self.dibujar()

    def actualizar(self):
        self.dibujar()

    def deshabilitar_clic(self):
        self.callback_clic = None

    def habilitar_clic(self, callback):
        self.callback_clic = callback
