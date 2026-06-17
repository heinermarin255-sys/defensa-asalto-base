"""
clases/ventana_login.py
Ventanas de Login y Registro de jugadores.
"""

import tkinter as tk
from tkinter import messagebox
from utils.constantes import COLOR_FONDO, COLOR_PANEL, COLOR_ACENTO, COLOR_TEXTO, COLOR_BOTON


class VentanaLogin:
    """
    Ventana de inicio de sesión.
    Permite a dos jugadores autenticarse antes de la partida.
    """

    def __init__(self, padre: tk.Widget, gestor_datos, callback_exito):
        """
        Args:
            padre: Widget padre (ventana raíz).
            gestor_datos: Instancia de GestorDatos.
            callback_exito: Función a llamar con (username1, username2) al éxito.
        """
        self.padre = padre
        self.gestor_datos = gestor_datos
        self.callback_exito = callback_exito

        # Nombres de los jugadores autenticados
        self.jugador1 = None
        self.jugador2 = None

        self._construir_ui()

    def _construir_ui(self):
        """Construye la interfaz completa de login."""
        self.frame = tk.Frame(self.padre, bg=COLOR_FONDO)
        self.frame.pack(fill="both", expand=True)

        # Título
        tk.Label(
            self.frame,
            text="⚔️  CLASH OF WORLDS",
            font=("Courier", 28, "bold"),
            bg=COLOR_FONDO, fg=COLOR_ACENTO
        ).pack(pady=(40, 5))

        tk.Label(
            self.frame,
            text="Inicio de Sesión — 2 Jugadores",
            font=("Courier", 13),
            bg=COLOR_FONDO, fg=COLOR_TEXTO
        ).pack(pady=(0, 30))

        # Contenedor de los dos paneles de login
        contenedor = tk.Frame(self.frame, bg=COLOR_FONDO)
        contenedor.pack()

        self._panel_jugador(contenedor, 1, "Jugador 1", side="left")
        self._separador(contenedor)
        self._panel_jugador(contenedor, 2, "Jugador 2", side="left")

        # Botón continuar
        tk.Button(
            self.frame,
            text="CONTINUAR →",
            font=("Courier", 13, "bold"),
            bg=COLOR_ACENTO, fg="white",
            width=20, pady=8,
            relief="flat", cursor="hand2",
            command=self._intentar_continuar
        ).pack(pady=30)

        # Enlace a registro
        tk.Button(
            self.frame,
            text="¿No tienes cuenta? Registrarse",
            font=("Courier", 10),
            bg=COLOR_FONDO, fg="#aaaaaa",
            relief="flat", cursor="hand2",
            command=self._abrir_registro
        ).pack()

    def _panel_jugador(self, padre, numero: int, titulo: str, side: str):
        """Crea el panel de login de un jugador."""
        panel = tk.Frame(padre, bg=COLOR_PANEL, padx=30, pady=25, relief="groove", bd=1)
        panel.pack(side=side, padx=20)

        tk.Label(
            panel, text=titulo,
            font=("Courier", 14, "bold"),
            bg=COLOR_PANEL, fg=COLOR_ACENTO
        ).pack(pady=(0, 15))

        # Usuario
        tk.Label(panel, text="Usuario:", font=("Courier", 11),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(anchor="w")
        entry_user = tk.Entry(panel, font=("Courier", 11), width=20,
                              bg="#0d1b2e", fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO,
                              relief="flat", bd=5)
        entry_user.pack(pady=(2, 10))

        # Contraseña
        tk.Label(panel, text="Contraseña:", font=("Courier", 11),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(anchor="w")
        entry_pass = tk.Entry(panel, font=("Courier", 11), width=20,
                              show="*", bg="#0d1b2e", fg=COLOR_TEXTO,
                              insertbackground=COLOR_TEXTO, relief="flat", bd=5)
        entry_pass.pack(pady=(2, 10))

        # Etiqueta de estado
        lbl_estado = tk.Label(panel, text="", font=("Courier", 9),
                              bg=COLOR_PANEL, fg="#00ff88", width=22, wraplength=180)
        lbl_estado.pack()

        # Botón de login individual
        btn = tk.Button(
            panel,
            text=f"Verificar {titulo}",
            font=("Courier", 10, "bold"),
            bg=COLOR_BOTON, fg="white",
            relief="flat", cursor="hand2",
            command=lambda n=numero, eu=entry_user, ep=entry_pass, lbl=lbl_estado:
                self._verificar_jugador(n, eu.get(), ep.get(), lbl)
        )
        btn.pack(pady=(10, 0))

        # Guardar referencias
        if numero == 1:
            self.entry_user1 = entry_user
            self.entry_pass1 = entry_pass
            self.lbl_estado1 = lbl_estado
        else:
            self.entry_user2 = entry_user
            self.entry_pass2 = entry_pass
            self.lbl_estado2 = lbl_estado

    def _separador(self, padre):
        """Línea separadora vertical."""
        tk.Label(padre, text="VS", font=("Courier", 20, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_ACENTO).pack(side="left", padx=15, pady=40)

    def _verificar_jugador(self, numero: int, username: str, password: str, lbl):
        """Intenta autenticar a un jugador y actualiza la etiqueta de estado."""
        exito, msg = self.gestor_datos.login_jugador(username, password)
        if exito:
            if numero == 1:
                self.jugador1 = username
            else:
                self.jugador2 = username
            lbl.config(text=f"✓ {username} autenticado", fg="#00ff88")
        else:
            lbl.config(text=f"✗ {msg}", fg=COLOR_ACENTO)

    def _intentar_continuar(self):
        """Verifica que ambos jugadores estén autenticados y continúa."""
        if not self.jugador1:
            messagebox.showwarning("Login", "El Jugador 1 no ha iniciado sesión.")
            return
        if not self.jugador2:
            messagebox.showwarning("Login", "El Jugador 2 no ha iniciado sesión.")
            return
        if self.jugador1 == self.jugador2:
            messagebox.showwarning("Login", "Los dos jugadores deben ser diferentes.")
            return

        self.frame.destroy()
        self.callback_exito(self.jugador1, self.jugador2)

    def _abrir_registro(self):
        """Abre la ventana de registro."""
        self.frame.destroy()
        VentanaRegistro(self.padre, self.gestor_datos, self._volver_al_login)

    def _volver_al_login(self):
        """Regresa a la pantalla de login."""
        self._construir_ui()


class VentanaRegistro:
    """Ventana para registrar un nuevo jugador."""

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
            text="📝 REGISTRO DE JUGADOR",
            font=("Courier", 24, "bold"),
            bg=COLOR_FONDO, fg=COLOR_ACENTO
        ).pack(pady=(60, 30))

        panel = tk.Frame(self.frame, bg=COLOR_PANEL, padx=40, pady=30)
        panel.pack()

        # Campos
        campos = [("Nombre de usuario:", "entry_user"), ("Contraseña:", "entry_pass"),
                  ("Confirmar contraseña:", "entry_pass2")]

        for texto, attr in campos:
            tk.Label(panel, text=texto, font=("Courier", 11),
                     bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(anchor="w", pady=(8, 2))
            mostrar = "*" if "pass" in attr else ""
            entry = tk.Entry(panel, font=("Courier", 11), width=25,
                             show=mostrar, bg="#0d1b2e", fg=COLOR_TEXTO,
                             insertbackground=COLOR_TEXTO, relief="flat", bd=5)
            entry.pack()
            setattr(self, attr, entry)

        # Mensaje de resultado
        self.lbl_msg = tk.Label(panel, text="", font=("Courier", 10),
                                bg=COLOR_PANEL, fg="#00ff88", wraplength=300)
        self.lbl_msg.pack(pady=10)

        # Botones
        frame_btn = tk.Frame(panel, bg=COLOR_PANEL)
        frame_btn.pack()

        tk.Button(
            frame_btn, text="REGISTRAR",
            font=("Courier", 11, "bold"),
            bg=COLOR_ACENTO, fg="white",
            relief="flat", cursor="hand2", padx=15, pady=6,
            command=self._registrar
        ).pack(side="left", padx=10)

        tk.Button(
            frame_btn, text="← Volver",
            font=("Courier", 11),
            bg=COLOR_BOTON, fg="white",
            relief="flat", cursor="hand2", padx=15, pady=6,
            command=self._volver
        ).pack(side="left", padx=10)

    def _registrar(self):
        """Intenta registrar el nuevo jugador."""
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get()
        pwd2 = self.entry_pass2.get()

        if pwd != pwd2:
            self.lbl_msg.config(text="Las contraseñas no coinciden.", fg=COLOR_ACENTO)
            return

        exito, msg = self.gestor_datos.registrar_jugador(user, pwd)
        if exito:
            self.lbl_msg.config(text=f"✓ {msg} ¡Ya puedes iniciar sesión!", fg="#00ff88")
        else:
            self.lbl_msg.config(text=f"✗ {msg}", fg=COLOR_ACENTO)

    def _volver(self):
        self.frame.destroy()
        self.callback_volver()
