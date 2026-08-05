import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import crear_tablas, obtener_pagos_por_tipo, insertar_pago, validar_usuario
from feriados import dia_habil_para

TIPOS = [
    ("local", "Local"),
    ("boleteria", "Boletería"),
    ("pescaderia", "Pescadería"),
    ("lote6", "Lote 6"),
    ("kiosco", "Kiosco"),
]
TIPOS_MENSUALES = ("boleteria", "pescaderia")
COLUMNAS = ("N° Local", "Fecha", "Mes", "Empresario", "RUT", "Descripción", "Valor", "Fecha Pago", "Folio")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Centro Comercial - Vega")
        self.geometry("1050x520")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tablas = {}

        for valor, nombre in TIPOS:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=nombre)
            self.crear_pestana(frame, valor)

        self.notebook.bind("<<NotebookTabChanged>>", self.al_cambiar_pestana)

    def crear_pestana(self, frame, tipo):
        buscador_frame = ttk.Frame(frame)
        buscador_frame.pack(fill="x", pady=5)

        ttk.Label(buscador_frame, text="N° Local:").pack(side="left", padx=5)
        entry = ttk.Entry(buscador_frame, width=15)
        entry.pack(side="left", padx=5)

        boton_buscar = ttk.Button(buscador_frame, text="Buscar", command=lambda: self.buscar(tipo))
        boton_buscar.pack(side="left", padx=5)

        boton_agregar = ttk.Button(buscador_frame, text="+ Agregar", command=lambda: self.abrir_formulario(tipo))
        boton_agregar.pack(side="right", padx=5)

        tabla = ttk.Treeview(frame, columns=COLUMNAS, show="headings")
        for col in COLUMNAS:
            tabla.heading(col, text=col)
            tabla.column(col, width=100)
        tabla.pack(fill="both", expand=True, padx=5, pady=5)

        self.tablas[tipo] = {"entry": entry, "tabla": tabla}

    def buscar(self, tipo):
        entry = self.tablas[tipo]["entry"]
        tabla = self.tablas[tipo]["tabla"]
        numero = entry.get()

        for fila in tabla.get_children():
            tabla.delete(fila)

        for fila in obtener_pagos_por_tipo(tipo, numero):
            tabla.insert("", "end", values=fila)

    def al_cambiar_pestana(self, event):
        tipo_actual = TIPOS[self.notebook.index("current")][0]
        self.buscar(tipo_actual)

    def abrir_formulario(self, tipo):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar registro")
        ventana.geometry("380x620")
        ventana.resizable(True, True)
        campos = {}

        ttk.Label(ventana, text="Fecha").pack(anchor="w", padx=15, pady=(8, 0))
        selector_fecha = DateEntry(ventana, width=32, date_pattern="yyyy-mm-dd")
        selector_fecha.pack(padx=15)

        etiquetas = [
            ("numero", "N° Local"),
            ("mes", "Mes"),
            ("empresario", "Empresario"),
            ("rut", "RUT"),
            ("descripcion", "Descripción"),
            ("valor", "Valor Mensual" if tipo in TIPOS_MENSUALES else "Valor Diario"),
            ("fecha_pago", "Fecha Pago (YYYY-MM-DD, opcional)"),
            ("folio", "Folio"),
        ]

        for clave, etiqueta in etiquetas:
            ttk.Label(ventana, text=etiqueta).pack(anchor="w", padx=15, pady=(8, 0))
            entry = ttk.Entry(ventana, width=35)
            entry.pack(padx=15)
            campos[clave] = entry

        def guardar():
            fecha_elegida = selector_fecha.get_date()

            if not dia_habil_para(tipo, fecha_elegida):
                messagebox.showerror(
                    "Fecha no válida",
                    "Este tipo de local no paga domingos ni feriados. Elige otro día."
                )
                return

            try:
                insertar_pago(
                    numero_local=campos["numero"].get(),
                    tipo=tipo,
                    fecha=fecha_elegida,
                    mes=campos["mes"].get(),
                    empresario=campos["empresario"].get(),
                    rut=campos["rut"].get(),
                    descripcion=campos["descripcion"].get(),
                    valor=campos["valor"].get(),
                    fecha_pago=campos["fecha_pago"].get(),
                    folio=campos["folio"].get(),
                )
                messagebox.showinfo("Listo", "Registro guardado correctamente.")
                ventana.destroy()
                self.buscar(tipo)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

        ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=15)


class VentanaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Iniciar sesión")
        self.geometry("300x180")
        self.resizable(False, False)
        self.login_exitoso = False

        ttk.Label(self, text="Usuario:").pack(pady=(20, 0))
        self.entry_usuario = ttk.Entry(self, width=25)
        self.entry_usuario.pack()

        ttk.Label(self, text="Contraseña:").pack(pady=(10, 0))
        self.entry_password = ttk.Entry(self, width=25, show="*")
        self.entry_password.pack()

        ttk.Button(self, text="Ingresar", command=self.intentar_login).pack(pady=20)
        self.bind("<Return>", lambda event: self.intentar_login())

    def intentar_login(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()

        if validar_usuario(usuario, password):
            self.login_exitoso = True
            self.destroy()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")


if __name__ == "__main__":
    crear_tablas()

    login = VentanaLogin()
    login.mainloop()

    if login.login_exitoso:
        app = App()
        app.mainloop()