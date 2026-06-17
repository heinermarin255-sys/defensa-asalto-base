"""
Segundo Proyecto - introduccion a la programacion
integrantes:
- Eyner Jose Marin Hernandez 2024345046
- Axel Marenco Rohas 2026010082

Nombre del proyecto: Clash of Worlds 

"""

import tkinter as tk
from utils.gestor_sonido import GestorSonido
from utils.gestor_datos import GestorDatos
from clases.juego import Juego


def main():
    """Función principal que inicia la aplicación."""
    # Crear ventana raíz de Tkinter
    ventana_raiz = tk.Tk()
    ventana_raiz.title("Clash of Worlds")
    ventana_raiz.geometry("1100x720")
    ventana_raiz.resizable(False, False)
    ventana_raiz.configure(bg="#1a1a2e")

    # Centrar la ventana en la pantalla
    ventana_raiz.update_idletasks()
    x = (ventana_raiz.winfo_screenwidth() // 2) - (1100 // 2)
    y = (ventana_raiz.winfo_screenheight() // 2) - (720 // 2)
    ventana_raiz.geometry(f"1100x720+{x}+{y}")

    # Inicializar el gestor de sonido (pygame)
    gestor_sonido = GestorSonido()

    # Inicializar el gestor de datos (JSON)
    gestor_datos = GestorDatos()

    # Crear e iniciar el juego principal
    juego = Juego(ventana_raiz, gestor_sonido, gestor_datos)
    juego.mostrar_menu_principal()

    # Iniciar el bucle principal de Tkinter
    ventana_raiz.mainloop()

    # Al cerrar, limpiar recursos de pygame
    gestor_sonido.cerrar()


if __name__ == "__main__":
    main()

#py -3.12 main.py