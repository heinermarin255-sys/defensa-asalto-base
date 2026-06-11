# ⚔️ Defensa y Asalto de Base

Juego de estrategia local para 2 jugadores inspirado en Clash of Clans.
Desarrollado como proyecto universitario de Introducción a la Programación.

---

## 🚀 Cómo ejecutar

```bash
python main.py
```

### Requisitos

- Python 3.10 o superior
- `tkinter` (incluido en Python estándar)
- `pygame` (opcional, para sonidos): `pip install pygame`

---

## 📁 Estructura del proyecto

```
Defensa y Asalto de Base/
│
├── main.py                    ← Archivo principal (ejecutar este)
│
├── clases/
│   ├── juego.py               ← Orquestador principal del juego
│   ├── jugador.py             ← Clase Jugador
│   ├── mapa.py                ← Cuadrícula 10x10
│   ├── estructuras.py         ← Torres, Muros, Trampas, Base (con herencia)
│   ├── unidades.py            ← Tropas atacantes (con herencia)
│   ├── combate.py             ← Motor de combate automático
│   ├── canvas_mapa.py         ← Renderizado del mapa en Tkinter Canvas
│   ├── ventana_login.py       ← Pantallas de Login y Registro
│   ├── ventana_facciones.py   ← Selección de facción
│   ├── ventana_juego.py       ← Pantalla principal de juego
│   └── ventana_ranking.py     ← Top jugadores
│
├── utils/
│   ├── constantes.py          ← Todas las constantes y configuración
│   ├── gestor_datos.py        ← Lectura/escritura JSON
│   └── gestor_sonido.py       ← Audio con pygame
│
├── datos/
│   └── jugadores.json         ← Creado automáticamente al registrarse
│
├── imagenes/                  ← Para agregar sprites futuros
└── sonidos/                   ← Archivos .wav para efectos de sonido
```

---

## 🎮 Cómo jugar

### Flujo general

1. **Menú Principal** → Nueva Partida
2. **Login** → Ambos jugadores inician sesión (o se registran)
3. **Selección de Facción** → Cada jugador elige una facción diferente
4. **Rondas** (necesitas ganar 3 para ganar la partida):
   - **Fase de Construcción**: El defensor construye torres, muros y trampas
   - **Fase de Ataque**: El atacante despliega tropas en los bordes del mapa
   - **Combate automático**: Las tropas avanzan y las torres disparan solas
   - **Resultado**: Se muestra quién ganó la ronda

### Roles

- Los roles se **alternan cada ronda** (el defensor pasa a ser atacante y viceversa)
- **Defensor**: gana si todas las tropas mueren antes de destruir la base
- **Atacante**: gana si destruye la **Base Central** (celda central del mapa)

---

## 🏰 Defensas disponibles (Defensor)

| Defensa          | Costo | Vida | Daño | Alcance | Especial                      |
|------------------|-------|------|------|---------|-------------------------------|
| Torre Arquera    | 50    | 80   | 15   | 3       | Ataque rápido                 |
| Torre de Magos   | 80    | 70   | 25   | 2       | Daño en área                  |
| Torre Infernal   | 100   | 90   | 10+  | 2       | Daño acumulativo              |
| Cañón            | 70    | 120  | 40   | 2       | Gran daño, lento              |
| Muro             | 20    | 200  | 0    | —       | Bloquea tropas                |
| Trampa Explosiva | 30    | 1    | 50   | —       | Se activa una vez al pisarla  |

### Cómo construir

- Selecciona una defensa del panel lateral
- Haz clic en cualquier celda interior del mapa (no en los bordes)
- No puedes construir sobre la base central

---

## ⚔️ Tropas disponibles (Atacante)

| Tropa   | Costo | Vida | Daño | Velocidad | Especial                   |
|---------|-------|------|------|-----------|----------------------------|
| Duende  | 25    | 40   | 10   | 2         | Muy rápido                 |
| Gigante | 80    | 200  | 20   | 1         | Prioriza defensas          |
| Arquera | 50    | 60   | 20   | 1         | Ataca a 2 casillas         |
| Pekka   | 150   | 300  | 50   | 1         | Máximo daño y vida         |

### Cómo desplegar tropas

- Selecciona una tropa del panel lateral
- Haz clic en cualquier celda del **borde** del mapa
- Cuando estés listo, presiona "INICIAR COMBATE"

---

## 🌍 Facciones

| Facción     | Descripción                        |
|-------------|------------------------------------|
| Medieval    | Colores cálidos, madera y piedra   |
| Futurista   | Colores cian y neón                |
| Naturaleza  | Tonos verdes y orgánicos           |

Las facciones son solo **visuales** — no cambian las mecánicas.

---

## 🔊 Agregar sonidos

Coloca archivos `.wav` en la carpeta `sonidos/` con estos nombres:
- `disparo.wav` — al atacar torres
- `explosion.wav` — al destruir estructuras o activar trampas
- `victoria.wav` — al ganar una ronda
- `derrota.wav` — al perder
- `clic.wav` — al hacer clic en menús
- `construccion.wav` — al construir

El juego funciona correctamente sin estos archivos.

---

## 💾 Datos guardados

Los jugadores y estadísticas se guardan en `datos/jugadores.json`.
Las contraseñas se guardan hasheadas con SHA-256.

---
