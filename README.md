# Clash of Worlds

Juego de estrategia local para dos jugadores, inspirado en el género de
defensa de base tipo Clash of Clans. Desarrollado en Python con Tkinter
como interfaz gráfica y Pygame para los efectos de sonido.

Proyecto académico para el curso de Introducción a la Programación.

---

## Requisitos

- Python 3.10 o superior
- Tkinter (incluido en la instalación estándar de Python)
- Pygame (opcional, para efectos de sonido y música)
- Pillow (opcional, recomendado para que las cartas de las defensas se
  muestren con su tamaño correcto en el mapa)

Instalación de dependencias opcionales:

```bash
pip install pygame pillow
```

El juego funciona sin estas dos librerías, pero se recomienda instalarlas
para obtener la experiencia completa (sonido y cartas con buena calidad
visual).

---

## Ejecución

Desde la carpeta raíz del proyecto:

```bash
python main.py
```

---

## Estructura del proyecto

```
Clash of Worlds/
│
├── main.py                    Punto de entrada de la aplicación
│
├── clases/
│   ├── juego.py                Controlador principal y flujo de pantallas
│   ├── jugador.py               Datos del jugador durante la partida
│   ├── mapa.py                  Cuadricula de 10x10 y su estado
│   ├── estructuras.py           Base, muros, trampas y torres (herencia)
│   ├── unidades.py               Tropas atacantes (herencia)
│   ├── combate.py                Motor de combate automático
│   ├── canvas_mapa.py             Renderizado del mapa en Tkinter
│   ├── ventana_login.py           Pantallas de inicio de sesion y registro
│   ├── ventana_facciones.py       Seleccion de faccion
│   ├── ventana_juego.py           Pantalla de construccion, ataque y combate
│   └── ventana_ranking.py          Tabla de mejores jugadores
│
├── utils/
│   ├── constantes.py            Configuracion general y datos del juego
│   ├── gestor_datos.py            Persistencia en archivos JSON
│   └── gestor_sonido.py            Manejo de audio con Pygame
│
├── datos/
│   └── jugadores.json           Cuentas y estadisticas (se crea solo)
│
├── imagenes/                   Cartas e ilustraciones de las facciones
└── sonidos/                     Efectos de sonido y musica
```

---

## Flujo del juego

1. Menu principal
2. Inicio de sesion de los dos jugadores (o registro de cuentas nuevas)
3. Seleccion de faccion (cada jugador elige una distinta)
4. Por cada ronda:
   - Fase de construccion: el jugador defensor coloca torres, muros y
     trampas en el mapa
   - Fase de ataque: el jugador atacante despliega tropas en los bordes
     del mapa
   - Combate automatico: las tropas avanzan, las torres disparan y las
     trampas se activan sin intervencion manual
   - Resultado de la ronda y actualizacion del marcador
5. La partida se gana al alcanzar 3 rondas ganadas
6. Pantalla final y actualizacion de estadisticas
7. Tabla de mejores jugadores (defensores y atacantes)

Los roles de defensor y atacante se alternan en cada ronda.

Condiciones de victoria de una ronda:
- El atacante gana si logra destruir la base central
- El defensor gana si elimina a todas las tropas enemigas antes de que
  la base sea destruida

---

## Facciones

El juego incluye tres facciones. La diferencia entre ellas es unicamente
visual (colores, iconos e imagenes de las defensas); las estadisticas y
mecanicas son las mismas para las tres.

| Facción     | Identidad visual                  |
|-------------|------------------------------------|
| Medieval    | Tonos calidos, piedra y madera     |
| Futurista   | Tonos azules y energia             |
| Naturaleza  | Tonos verdes y organicos           |

Los dos jugadores deben elegir facciones distintas.

---

## Defensas

| Defensa          | Costo | Vida | Daño | Alcance | Caracteristica                 |
|------------------|-------|------|------|---------|---------------------------------|
| Torre Arquera    | 50    | 80   | 15   | 3       | Ataque rapido de largo alcance  |
| Torre de Magos   | 80    | 70   | 25   | 2       | Daño en area                    |
| Torre Infernal   | 100   | 90   | 10+  | 2       | El daño aumenta con cada ataque |
| Cañon            | 70    | 120  | 40   | 2       | Daño alto, velocidad de ataque baja |
| Muro             | 10    | 200  | 0    | -       | Bloquea el paso de las tropas   |
| Trampa explosiva | 30    | 1    | 50   | -       | Se activa una sola vez al ser pisada |

Para construir, selecciona una defensa en el panel lateral y haz clic en
una celda interior del mapa. La base central no puede sustituirse ni
construirse encima de ella.

---

## Tropas

| Tropa   | Costo | Vida | Daño | Velocidad | Caracteristica           |
|---------|-------|------|------|-----------|---------------------------|
| Duende  | 25    | 40   | 10   | 2         | Movimiento rapido         |
| Gigante | 80    | 200  | 20   | 1         | Prioriza atacar defensas  |
| Arquera | 50    | 60   | 20   | 1         | Ataca a distancia (2 celdas) |
| Pekka   | 150   | 300  | 50   | 1         | Mayor daño y vida del juego |

Para atacar, selecciona una tropa en el panel lateral y haz clic en una
celda del borde del mapa para desplegarla. Cuando termines de desplegar
tropas, presiona el boton para iniciar el combate.

---

## Comportamiento de las tropas en combate

Cada tropa avanza hacia su objetivo (la base central, o la defensa más
cercana en el caso del gigante) buscando el camino más corto y evitando
muros, torres y la base. Si hay un hueco en el cerco, ya sea porque el
defensor lo dejó libre o porque un muro fue destruido durante el combate,
la tropa lo usa para seguir avanzando en lugar de detenerse a atacar.

Un muro solo recibe daño cuando bloquea directamente el avance de la
tropa hacia su objetivo. Si la tropa simplemente pasa junto a un muro, o
lo tiene a un costado del camino sin que le impida seguir, el muro no se
ve afectado.

Para que una tropa no abandone un muro que ya está atacando con el fin
de perseguir una abertura ubicada en una zona lejana del mapa, la
búsqueda de camino tiene un límite de desvío. Este límite se define en
`MAX_DESVIO_RUTA` (`utils/constantes.py`): si la única ruta disponible
exige rodear más casillas que ese valor, la tropa la descarta y sigue
atacando el obstáculo que tiene enfrente. De forma similar, si el muro
que está atacando ya está casi destruido (por debajo del porcentaje de
vida definido en `UMBRAL_MURO_CASI_DESTRUIDO`), la tropa prioriza
terminarlo antes que desviarse, incluso si hay una abertura cercana
disponible. Esto evita que las tropas cambien de objetivo de forma
constante y hace que su recorrido se vea más natural.

---

## Imagenes de las cartas

Las imagenes de las defensas se encuentran en la carpeta `imagenes/` y
siguen la convencion `<Nombre><Sufijo>.png`, donde el sufijo indica la
faccion:

| Sufijo | Faccion     |
|--------|-------------|
| N      | Naturaleza  |
| F      | Futurista   |
| M      | Medieval    |

Ejemplo: `TorreN.png` corresponde a la Torre Arquera de la faccion
Naturaleza.

Mapeo de defensas a archivos:

| Defensa         | Prefijo del archivo |
|-----------------|----------------------|
| Base central    | Ayunta               |
| Torre Arquera   | Torre                |
| Torre de Magos  | Mago                 |
| Torre Infernal  | Infernal             |
| Cañon           | Cañon                |

Al construir, el juego carga automaticamente la imagen correspondiente
segun la faccion del jugador defensor. Si una imagen no se encuentra, la
defensa se dibuja con un color y un icono de respaldo, por lo que el
juego sigue siendo jugable aunque falten archivos.

Las imagenes de muros, trampas, tropas y otros elementos pueden agregarse
mas adelante siguiendo la misma convencion de nombres.

---

## Datos guardados

Las cuentas de los jugadores y sus estadisticas se almacenan en
`datos/jugadores.json`. Las contraseñas se guardan utilizando un hash
SHA-256, nunca en texto plano.

Estadisticas registradas por jugador:
- Victorias como defensor
- Victorias como atacante
- Partidas jugadas

---

## Sonido

Pygame se utiliza unicamente para reproducir audio. Si la libreria no
esta instalada, el juego se ejecuta normalmente sin sonido.

Archivos esperados en la carpeta `sonidos/`:

| Archivo            | Uso                                |
|--------------------|-------------------------------------|
| disparo.wav        | Ataque de una torre                 |
| explosion.wav       | Destruccion de estructuras o trampas |
| victoria.wav        | Victoria en una ronda                |
| derrota.wav         | Derrota en una ronda                 |
| clic.wav            | Interaccion en menus                 |
| construccion.wav    | Colocacion de una defensa            |

---

## Posibles mejoras futuras

- Animaciones durante el combate