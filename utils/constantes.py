"""
utils/constantes.py
Centraliza todas las constantes y configuración del juego.
"""

# ──────────────────────────────────────────
# MAPA
# ──────────────────────────────────────────
FILAS = 10
COLUMNAS = 10
TAMANO_CELDA = 58          # píxeles por celda en el canvas
MARGEN_CANVAS = 4

# Posición de la base central (fila, col)
BASE_FILA = 4
BASE_COL = 4

# ──────────────────────────────────────────
# JUEGO
# ──────────────────────────────────────────
GEMAS_INICIALES_DEFENSOR = 300
GEMAS_INICIALES_ATACANTE = 250
RONDAS_PARA_GANAR = 3
INTERVALO_COMBATE_MS = 600   # milisegundos entre cada turno de combate

# ──────────────────────────────────────────
# COLORES BASE (tema oscuro)
# ──────────────────────────────────────────
COLOR_FONDO = "#1a1a2e"
COLOR_PANEL = "#16213e"
COLOR_ACENTO = "#e94560"
COLOR_TEXTO = "#eaeaea"
COLOR_BOTON = "#0f3460"
COLOR_BOTON_HOVER = "#e94560"
COLOR_CELDA_VACIA = "#2d4a6e"
COLOR_CELDA_BORDE = "#1a3a5c"
COLOR_CELDA_HOVER = "#3a6b9e"

# ──────────────────────────────────────────
# FACCIONES
# ──────────────────────────────────────────
FACCIONES = {
    "Medieval": {
        "color_torre": "#8B4513",
        "color_muro": "#A0522D",
        "color_tropa": "#CD853F",
        "color_base": "#5C3317",
        "color_trampa": "#8B0000",
        "color_fondo_panel": "#3E1F00",
        "emoji_torre": "🏰",
        "emoji_tropa": "⚔️",
        "emoji_base": "👑",
        "emoji_muro": "🧱",
        "emoji_trampa": "💥",
        "descripcion": "Antigua, resistente y honorable.",
    },
    "Futurista": {
        "color_torre": "#00d4ff",
        "color_muro": "#0080a0",
        "color_tropa": "#00ffaa",
        "color_base": "#003344",
        "color_trampa": "#ff4500",
        "color_fondo_panel": "#001a26",
        "emoji_torre": "🔭",
        "emoji_tropa": "🤖",
        "emoji_base": "⚡",
        "emoji_muro": "🔷",
        "emoji_trampa": "💣",
        "descripcion": "Tecnología avanzada y energía pura.",
    },
    "Naturaleza": {
        "color_torre": "#228B22",
        "color_muro": "#2E8B57",
        "color_tropa": "#90EE90",
        "color_base": "#013220",
        "color_trampa": "#8B6914",
        "color_fondo_panel": "#0a2a0a",
        "emoji_torre": "🌲",
        "emoji_tropa": "🌿",
        "emoji_base": "🌳",
        "emoji_muro": "🍀",
        "emoji_trampa": "🍄",
        "descripcion": "Fuerza de la naturaleza y vida salvaje.",
    },
}

# ──────────────────────────────────────────
# DEFENSAS - Estadísticas base
# ──────────────────────────────────────────
DEFENSAS = {
    "Torre Arquera": {
        "costo": 50,
        "vida": 80,
        "dano": 15,
        "alcance": 3,
        "velocidad_ataque": 1,     # cada cuántos turnos ataca
        "habilidad": "Ataque rápido de largo alcance",
        "tipo": "torre_arquera",
    },
    "Torre de Magos": {
        "costo": 80,
        "vida": 70,
        "dano": 25,
        "alcance": 2,
        "velocidad_ataque": 2,
        "habilidad": "Daño en área (afecta casillas adyacentes)",
        "tipo": "torre_magos",
    },
    "Torre Infernal": {
        "costo": 100,
        "vida": 90,
        "dano": 10,        # sube con el tiempo
        "alcance": 2,
        "velocidad_ataque": 1,
        "habilidad": "Daño acumulativo contra mismo objetivo",
        "tipo": "torre_infernal",
    },
    "Cañón": {
        "costo": 70,
        "vida": 120,
        "dano": 40,
        "alcance": 2,
        "velocidad_ataque": 3,
        "habilidad": "Gran daño, ataque lento",
        "tipo": "canon",
    },
    "Muro": {
        "costo": 20,
        "vida": 200,
        "dano": 0,
        "alcance": 0,
        "velocidad_ataque": 0,
        "habilidad": "Bloquea el paso de tropas",
        "tipo": "muro",
    },
    "Trampa Explosiva": {
        "costo": 30,
        "vida": 1,
        "dano": 50,
        "alcance": 1,
        "velocidad_ataque": 0,
        "habilidad": "Se activa una sola vez al ser pisada",
        "tipo": "trampa",
    },
}

# ──────────────────────────────────────────
# TROPAS - Estadísticas base
# ──────────────────────────────────────────
TROPAS = {
    "Duende": {
        "costo": 25,
        "vida": 40,
        "dano": 10,
        "velocidad": 2,     # casillas por turno
        "habilidad": "Muy rápido, busca recursos",
        "tipo": "duende",
    },
    "Gigante": {
        "costo": 80,
        "vida": 200,
        "dano": 20,
        "velocidad": 1,
        "habilidad": "Prioriza defensas enemigas",
        "tipo": "gigante",
    },
    "Arquera": {
        "costo": 50,
        "vida": 60,
        "dano": 20,
        "velocidad": 1,
        "habilidad": "Ataca a distancia desde 2 casillas",
        "tipo": "arquera",
    },
    "Pekka": {
        "costo": 150,
        "vida": 300,
        "dano": 50,
        "velocidad": 1,
        "habilidad": "Máximo daño y vida, muy costosa",
        "tipo": "pekka",
    },
}
