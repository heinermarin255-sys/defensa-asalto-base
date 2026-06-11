"""
utils/gestor_datos.py
Maneja la persistencia de datos usando archivos JSON.
Guarda y carga jugadores y estadísticas.
"""

import json
import os
import hashlib


class GestorDatos:
    """
    Clase que maneja la lectura y escritura de archivos JSON
    para guardar jugadores y sus estadísticas.
    """

    def __init__(self):
        """Inicializa rutas y crea archivos si no existen."""
        # Carpeta de datos relativa al proyecto
        self.carpeta_datos = os.path.join(
            os.path.dirname(__file__), "..", "datos"
        )
        self.archivo_jugadores = os.path.join(self.carpeta_datos, "jugadores.json")

        # Crear carpeta si no existe
        os.makedirs(self.carpeta_datos, exist_ok=True)

        # Crear archivo de jugadores si no existe
        if not os.path.exists(self.archivo_jugadores):
            self._guardar_json(self.archivo_jugadores, {})

    # ──────────────────────────────────────────
    # Métodos de jugadores
    # ──────────────────────────────────────────

    def registrar_jugador(self, username: str, password: str) -> tuple[bool, str]:
        """
        Registra un nuevo jugador.
        Retorna (éxito, mensaje).
        """
        jugadores = self._cargar_json(self.archivo_jugadores)

        if username in jugadores:
            return False, "El usuario ya existe."

        if len(username) < 3:
            return False, "El nombre debe tener al menos 3 caracteres."

        if len(password) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."

        # Guardar con contraseña hasheada
        jugadores[username] = {
            "password": self._hash_password(password),
            "victorias_defensor": 0,
            "victorias_atacante": 0,
            "partidas_jugadas": 0,
        }

        self._guardar_json(self.archivo_jugadores, jugadores)
        return True, "Registro exitoso."

    def login_jugador(self, username: str, password: str) -> tuple[bool, str]:
        """
        Verifica credenciales de un jugador.
        Retorna (éxito, mensaje).
        """
        jugadores = self._cargar_json(self.archivo_jugadores)

        if username not in jugadores:
            return False, "Usuario no encontrado."

        hash_ingresado = self._hash_password(password)
        if jugadores[username]["password"] != hash_ingresado:
            return False, "Contraseña incorrecta."

        return True, "Login exitoso."

    def obtener_jugador(self, username: str) -> dict:
        """Retorna los datos de un jugador."""
        jugadores = self._cargar_json(self.archivo_jugadores)
        return jugadores.get(username, {})

    def actualizar_estadisticas(self, username: str, gano_como: str):
        """
        Actualiza las estadísticas de un jugador.
        gano_como: 'defensor' o 'atacante'
        """
        jugadores = self._cargar_json(self.archivo_jugadores)

        if username not in jugadores:
            return

        jugadores[username]["partidas_jugadas"] += 1

        if gano_como == "defensor":
            jugadores[username]["victorias_defensor"] += 1
        elif gano_como == "atacante":
            jugadores[username]["victorias_atacante"] += 1

        self._guardar_json(self.archivo_jugadores, jugadores)

    def obtener_top_jugadores(self, tipo: str, limite: int = 5) -> list:
        """
        Retorna el top de jugadores por tipo ('defensor' o 'atacante').
        Retorna lista de (username, victorias) ordenada.
        """
        jugadores = self._cargar_json(self.archivo_jugadores)
        campo = f"victorias_{tipo}"

        ranking = [
            (user, datos.get(campo, 0))
            for user, datos in jugadores.items()
        ]

        # Ordenar de mayor a menor
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking[:limite]

    # ──────────────────────────────────────────
    # Métodos auxiliares privados
    # ──────────────────────────────────────────

    def _cargar_json(self, ruta: str) -> dict:
        """Carga y retorna el contenido de un archivo JSON."""
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _guardar_json(self, ruta: str, datos: dict):
        """Guarda un diccionario en un archivo JSON."""
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def _hash_password(self, password: str) -> str:
        """Retorna el hash SHA-256 de una contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
