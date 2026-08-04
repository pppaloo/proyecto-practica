import tkinter as tk
from tkinter import ttk, messagebox
from database import crear_tablas, obtener_pagos_por_tipo, insertar_pago

TIPOS = [
    ("local", "Local"),
    ("boleteria", "Boletería"),
    ("pescaderia", "Pescadería"),
    ("lote6", "Lote 6"),
    ("kiosco", "Kiosco"),
]

COLUMNAS = ("N° Local", "Fecha", "Mes", "Empresario", "RUT", "Descripción", "Valor Diario", "Fecha Pago", "Folio")


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
        ventana.geometry("380x560")
        ventana.resizable(True, True)
        campos = {}
        etiquetas = [
            ("numero", "N° Local"),
            ("fecha", "Fecha (YYYY-MM-DD)"),
            ("mes", "Mes"),
            ("empresario", "Empresario"),
            ("rut", "RUT"),
            ("descripcion", "Descripción"),
            ("valor_diario", "Valor Diario"),
            ("fecha_pago", "Fecha Pago (YYYY-MM-DD, opcional)"),
            ("folio", "Folio"),
        ]

        for clave, etiqueta in etiquetas:
            ttk.Label(ventana, text=etiqueta).pack(anchor="w", padx=15, pady=(8, 0))
            entry = ttk.Entry(ventana, width=35)
            entry.pack(padx=15)
            campos[clave] = entry

        def guardar():
            try:
                insertar_pago(
                    numero_local=campos["numero"].get(),
                    tipo=tipo,
                    fecha=campos["fecha"].get(),
                    mes=campos["mes"].get(),
                    empresario=campos["empresario"].get(),
                    rut=campos["rut"].get(),
                    descripcion=campos["descripcion"].get(),
                    valor_diario=campos["valor_diario"].get(),
                    fecha_pago=campos["fecha_pago"].get(),
                    folio=campos["folio"].get(),
                )
                messagebox.showinfo("Listo", "Registro guardado correctamente.")
                ventana.destroy()
                self.buscar(tipo)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

        ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=15)


if __name__ == "__main__":
    crear_tablas()
    app = App()
    app.mainloop()