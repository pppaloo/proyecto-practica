import tkinter as tk
from tkinter import ttk
from database import crear_tablas, obtener_pagos_por_tipo

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
        self.geometry("1000x500")

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

        boton = ttk.Button(buscador_frame, text="Buscar", command=lambda: self.buscar(tipo))
        boton.pack(side="left", padx=5)

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


if __name__ == "__main__":
    crear_tablas()
    app = App()
    app.mainloop()