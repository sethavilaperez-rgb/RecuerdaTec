"""
Módulo de la vista semanal de tareas.
Panel embebido en la pantalla principal (lunes a domingo).
"""

import tkinter as tk
from datetime import datetime, timedelta


class VistaSemanal:
    """
    Panel que muestra la cuadrícula semanal dentro de la ventana principal.
    """

    def __init__(self, padre, gestor, callback_tema=None):
        """
        :param padre: Frame contenedor en la ventana principal
        :param gestor: instancia de GestorTareas
        :param callback_tema: función que devuelve el tema actual
        """
        self.gestor = gestor
        self.callback_tema = callback_tema
        self.fecha_actual = datetime.now()

        self.marco = tk.LabelFrame(
            padre, text="Vista semanal",
            font=("Segoe UI", 10, "bold"), padx=8, pady=6
        )
        self.marco.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._crear_controles()
        self.marco_dias = tk.Frame(self.marco)
        self.marco_dias.pack(fill=tk.BOTH, expand=True, pady=5)
        self.celdas = []

    def _obtener_tema(self):
        if self.callback_tema:
            return self.callback_tema()
        return {'fondo': '#f0f4f8', 'panel': '#fff', 'texto': '#2c3e50',
                'texto_secundario': '#7f8c8d', 'entrada_bg': '#fff',
                'entrada_fg': '#2c3e50', 'boton': '#4a90d9',
                'semana_hoy': '#d4edda', 'semana_celda': '#ffffff',
                'prioridad': {'Alta': '#ffcccc', 'Media': '#fff3cd', 'Baja': '#cce5ff'}}

    def _crear_controles(self):
        tema = self._obtener_tema()
        self.marco_controles = tk.Frame(self.marco, bg=tema['panel'])
        self.marco_controles.pack(fill=tk.X, pady=4)

        self.btn_anterior = tk.Button(
            self.marco_controles, text="◀ Semana anterior",
            command=self._semana_anterior
        )
        self.btn_anterior.pack(side=tk.LEFT, padx=5)

        self.etiqueta_rango = tk.Label(
            self.marco_controles, text="",
            font=("Segoe UI", 10, "bold"),
            bg=tema['panel'], fg=tema['texto']
        )
        self.etiqueta_rango.pack(side=tk.LEFT, expand=True)

        self.btn_siguiente = tk.Button(
            self.marco_controles, text="Semana siguiente ▶",
            command=self._semana_siguiente
        )
        self.btn_siguiente.pack(side=tk.LEFT, padx=5)

        self.btn_hoy = tk.Button(
            self.marco_controles, text="Ir a hoy",
            command=self._ir_a_hoy
        )
        self.btn_hoy.pack(side=tk.LEFT, padx=5)

    def _semana_anterior(self):
        self.fecha_actual -= timedelta(days=7)
        self.cargar_semana()

    def _semana_siguiente(self):
        self.fecha_actual += timedelta(days=7)
        self.cargar_semana()

    def _ir_a_hoy(self):
        self.fecha_actual = datetime.now()
        self.cargar_semana()

    def cargar_semana(self):
        """Recarga las 7 columnas con las tareas de la semana."""
        tema = self._obtener_tema()
        self.aplicar_tema(tema)

        for widget in self.marco_dias.winfo_children():
            widget.destroy()
        self.celdas = []

        dias, inicio, fin = self.gestor.obtener_semana(self.fecha_actual)
        self.etiqueta_rango.config(
            text=f"Semana del {inicio} al {fin}",
            bg=tema['panel'], fg=tema['texto']
        )

        hoy = datetime.now().strftime('%Y-%m-%d')

        for i, dia_info in enumerate(dias):
            es_hoy = dia_info['fecha'] == hoy
            color_celda = tema['semana_hoy'] if es_hoy else tema['semana_celda']

            celda = tk.Frame(self.marco_dias, bg=color_celda, relief=tk.RIDGE, bd=2)
            celda.grid(row=0, column=i, sticky='nsew', padx=3, pady=2)
            self.marco_dias.grid_columnconfigure(i, weight=1)
            self.marco_dias.grid_rowconfigure(0, weight=1)

            titulo = f"{dia_info['nombre_dia']}\n{dia_info['fecha']}"
            if es_hoy:
                titulo += "\n(Hoy)"

            tk.Label(
                celda, text=titulo, font=("Segoe UI", 9, "bold"),
                bg=color_celda, fg=tema['texto']
            ).pack(pady=3)

            tk.Label(
                celda, text=f"{len(dia_info['tareas'])} tarea(s)",
                font=("Segoe UI", 8), bg=color_celda, fg=tema['texto_secundario']
            ).pack()

            lista = tk.Listbox(
                celda, height=6, font=("Segoe UI", 8),
                bg=tema['entrada_bg'], fg=tema['entrada_fg'],
                selectbackground=tema['boton']
            )
            lista.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

            for tarea in dia_info['tareas']:
                estado = "✓" if tarea.completada else "○"
                hora = tarea.obtener_horario_texto()
                hora_txt = f" {hora}" if hora else ""
                rep = " ↻" if tarea.repetir != 'Ninguna' else ''
                texto = f"{estado} [{tarea.categoria[0]}]{rep} {tarea.titulo}{hora_txt}"
                lista.insert(tk.END, texto[:42])
                color_prio = tema['prioridad'].get(tarea.prioridad, color_celda)
                lista.itemconfig(tk.END, bg=color_prio)

            self.celdas.append(celda)

    def aplicar_tema(self, tema):
        """Actualiza colores del panel semanal."""
        self.marco.configure(bg=tema['panel'], fg=tema['texto'])
        self.marco_controles.configure(bg=tema['panel'])
        self.marco_dias.configure(bg=tema['panel'])
        self.etiqueta_rango.configure(bg=tema['panel'], fg=tema['texto'])
