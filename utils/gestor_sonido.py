"""
utils/gestor_sonido.py
Maneja todos los sonidos del juego usando pygame.
Pygame se usa ÚNICAMENTE para audio.
"""

import os

# Intentar importar pygame; si no está disponible, el juego funciona sin sonido
try:
    import pygame
    PYGAME_DISPONIBLE = True
except ImportError:
    PYGAME_DISPONIBLE = False
    print("[SONIDO] pygame no encontrado. El juego funcionará sin sonido.")


class GestorSonido:
    """
    Clase responsable de reproducir efectos de sonido y música.
    Usa pygame.mixer para el audio.
    """

    def __init__(self):
        """Inicializa pygame mixer si está disponible."""
        self.activo = False

        if PYGAME_DISPONIBLE:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.activo = True
                print("[SONIDO] pygame mixer iniciado correctamente.")
            except Exception as e:
                print(f"[SONIDO] Error al iniciar pygame mixer: {e}")

        # Diccionario de sonidos cargados
        self.sonidos = {}
        self._cargar_sonidos()

    def _cargar_sonidos(self):
        """Intenta cargar los archivos de sonido desde la carpeta /sonidos."""
        if not self.activo:
            return

        # Mapa de nombre -> archivo
        archivos = {
            "disparo": "disparo.wav",
            "explosion": "explosion.wav",
            "victoria": "victoria.wav",
            "derrota": "derrota.wav",
            "clic": "clic.wav",
            "construccion": "construccion.wav",
        }

        carpeta = os.path.join(os.path.dirname(__file__), "..", "sonidos")

        for nombre, archivo in archivos.items():
            ruta = os.path.join(carpeta, archivo)
            if os.path.exists(ruta):
                try:
                    self.sonidos[nombre] = pygame.mixer.Sound(ruta)
                except Exception as e:
                    print(f"[SONIDO] No se pudo cargar {archivo}: {e}")

    def reproducir(self, nombre: str):
        """
        Reproduce un efecto de sonido por nombre.
        Si el sonido no existe o pygame no está activo, no hace nada.
        """
        if not self.activo:
            return
        if nombre in self.sonidos:
            try:
                self.sonidos[nombre].play()
            except Exception:
                pass

    def reproducir_musica(self, archivo: str, loop: bool = True):
        """Reproduce música de fondo."""
        if not self.activo:
            return

        carpeta = os.path.join(os.path.dirname(__file__), "..", "sonidos")
        ruta = os.path.join(carpeta, archivo)

        if os.path.exists(ruta):
            try:
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.play(-1 if loop else 0)
            except Exception as e:
                print(f"[SONIDO] Error al reproducir música: {e}")

    def detener_musica(self):
        """Detiene la música de fondo."""
        if self.activo:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def cerrar(self):
        """Limpia los recursos de pygame."""
        if self.activo and PYGAME_DISPONIBLE:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
