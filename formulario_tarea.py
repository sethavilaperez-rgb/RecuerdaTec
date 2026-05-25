"""
Ventana emergente para agregar o editar una tarea.
Todas las fechas y horas se eligen con widgets (sin escribir).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from tkcalendar import DateEntry
from tarea import Tarea


class FormularioTarea:
    """
    Formulario en ventana secundaria (Toplevel).
    modo='agregar' crea tarea nueva; modo='editar' modifica una existente.
    """

    HORAS = [f"{h:02d}" for h in range(24)]
    MINUTOS = [f"{m:02d}" for m in range(0, 60, 5)]

    def __init__(self, ventana_padre, tema, modo='agregar', tarea=None,
                 on_guardar=None, on_eliminar=None):
        """
        :param ventana_padre: ventana principal
        :param tema: diccionario de colores
        :param modo: 'agregar' o 'editar'
        :param tarea: objeto Tarea si es edición
        :param on_guardar: función(datos_dict) al guardar
        :param on_eliminar: función(id) al eliminar (solo edición)
        """
        self.ventana_padre = ventana_padre
        self.tema = tema
        self.modo = modo
        self.tarea = tarea
        self.on_guardar = on_guardar
        self.on_eliminar = on_eliminar

        self.ventana = tk.Toplevel(ventana_padre)
        titulo = "Editar tarea" if modo == 'editar' else "Agregar tarea"
        self.ventana.title(titulo)
        self.ventana.geometry("420x620")
        self.ventana.resizable(False, False)
        self.ventana.grab_set()  # Enfoca esta ventana hasta cerrarla

        self._crear_formulario()
        self._aplicar_tema()
        if modo == 'editar' and tarea:
            self._cargar_tarea(tarea)
        else:
            self._valores_por_defecto()

    def _crear_formulario(self):
        marco = tk.Frame(self.ventana, padx=12, pady=10)
        marco.pack(fill=tk.BOTH, expand=True)

        fila = 0
        tk.Label(marco, text="Título:").grid(row=fila, column=0, sticky="w", pady=4)
        self.entrada_titulo = tk.Entry(marco, width=32, font=("Segoe UI", 10))
        self.entrada_titulo.grid(row=fila, column=1, pady=4)
        fila += 1

        tk.Label(marco, text="Descripción:").grid(row=fila, column=0, sticky="nw", pady=4)
        self.entrada_descripcion = tk.Text(marco, width=32, height=3, font=("Segoe UI", 10))
        self.entrada_descripcion.grid(row=fila, column=1, pady=4)
        fila += 1

        tk.Label(marco, text="Categoría:").grid(row=fila, column=0, sticky="w", pady=4)
        self.combo_categoria = ttk.Combobox(
            marco, values=Tarea.CATEGORIAS, state="readonly", width=30
        )
        self.combo_categoria.current(2)
        self.combo_categoria.grid(row=fila, column=1, pady=4)
        fila += 1

        tk.Label(marco, text="Fecha inicio:").grid(row=fila, column=0, sticky="w", pady=4)
        self.date_inicio = DateEntry(
            marco, width=28, date_pattern='y-mm-dd', state='readonly',
            font=("Segoe UI", 10)
        )
        self.date_inicio.grid(row=fila, column=1, sticky="w", pady=4)
        fila += 1

        tk.Label(marco, text="Fecha término:").grid(row=fila, column=0, sticky="w", pady=4)
        self.date_fin = DateEntry(
            marco, width=28, date_pattern='y-mm-dd', state='readonly',
            font=("Segoe UI", 10)
        )
        self.date_fin.grid(row=fila, column=1, sticky="w", pady=4)
        fila += 1

        self.var_sin_fecha_fin = tk.BooleanVar(value=True)
        self.check_sin_fin = tk.Checkbutton(
            marco, text="Sin fecha de término (un solo día)",
            variable=self.var_sin_fecha_fin, command=self._toggle_fecha_fin
        )
        self.check_sin_fin.grid(row=fila, column=1, sticky="w", pady=2)
        fila += 1

        # Hora inicio con combobox
        tk.Label(marco, text="Hora inicio:").grid(row=fila, column=0, sticky="w", pady=4)
        marco_hi = tk.Frame(marco)
        marco_hi.grid(row=fila, column=1, sticky="w", pady=4)
        self.combo_hora_ini_h = ttk.Combobox(
            marco_hi, values=self.HORAS, state="readonly", width=4
        )
        self.combo_hora_ini_h.pack(side=tk.LEFT)
        tk.Label(marco_hi, text=":").pack(side=tk.LEFT)
        self.combo_hora_ini_m = ttk.Combobox(
            marco_hi, values=self.MINUTOS, state="readonly", width=4
        )
        self.combo_hora_ini_m.pack(side=tk.LEFT, padx=2)
        self.var_sin_hora_inicio = tk.BooleanVar(value=True)
        tk.Checkbutton(
            marco_hi, text="Sin hora", variable=self.var_sin_hora_inicio,
            command=self._toggle_hora_inicio
        ).pack(side=tk.LEFT, padx=6)
        fila += 1

        tk.Label(marco, text="Hora término:").grid(row=fila, column=0, sticky="w", pady=4)
        marco_hf = tk.Frame(marco)
        marco_hf.grid(row=fila, column=1, sticky="w", pady=4)
        self.combo_hora_fin_h = ttk.Combobox(
            marco_hf, values=self.HORAS, state="readonly", width=4
        )
        self.combo_hora_fin_h.pack(side=tk.LEFT)
        tk.Label(marco_hf, text=":").pack(side=tk.LEFT)
        self.combo_hora_fin_m = ttk.Combobox(
            marco_hf, values=self.MINUTOS, state="readonly", width=4
        )
        self.combo_hora_fin_m.pack(side=tk.LEFT, padx=2)
        self.var_sin_hora_fin = tk.BooleanVar(value=True)
        tk.Checkbutton(
            marco_hf, text="Sin hora", variable=self.var_sin_hora_fin,
            command=self._toggle_hora_fin
        ).pack(side=tk.LEFT, padx=6)
        fila += 1

        tk.Label(marco, text="Prioridad:").grid(row=fila, column=0, sticky="w", pady=4)
        self.combo_prioridad = ttk.Combobox(
            marco, values=["Alta", "Media", "Baja"], state="readonly", width=30
        )
        self.combo_prioridad.current(1)
        self.combo_prioridad.grid(row=fila, column=1, pady=4)
        self.combo_prioridad.bind("<<ComboboxSelected>>", self._actualizar_color_prioridad)
        fila += 1

        self.etiqueta_color = tk.Label(marco, text="  Color: Media  ", font=("Segoe UI", 9))
        self.etiqueta_color.grid(row=fila, column=1, sticky="w", pady=2)
        fila += 1

        tk.Label(marco, text="Repetir:").grid(row=fila, column=0, sticky="w", pady=4)
        self.combo_repetir = ttk.Combobox(
            marco, values=Tarea.TIPOS_REPETICION, state="readonly", width=30
        )
        self.combo_repetir.current(0)
        self.combo_repetir.grid(row=fila, column=1, pady=4)
        fila += 1

        self.var_completada = tk.BooleanVar(value=False)
        tk.Checkbutton(
            marco, text="Tarea completada", variable=self.var_completada
        ).grid(row=fila, column=1, sticky="w", pady=4)
        fila += 1

        self.var_recordatorio = tk.BooleanVar(value=True)
        tk.Checkbutton(
            marco, text="Activar recordatorio", variable=self.var_recordatorio
        ).grid(row=fila, column=1, sticky="w", pady=4)
        fila += 1

        marco_btn = tk.Frame(marco)
        marco_btn.grid(row=fila, column=0, columnspan=2, pady=12)

        texto_guardar = "Guardar cambios" if self.modo == 'editar' else "Agregar tarea"
        tk.Button(
            marco_btn, text=texto_guardar, width=14,
            bg=self.tema['boton'], fg=self.tema['boton_texto'],
            command=self._guardar
        ).pack(side=tk.LEFT, padx=4)

        if self.modo == 'editar':
            tk.Button(
                marco_btn, text="Eliminar", width=10,
                bg="#e74c3c", fg="white",
                command=self._eliminar
            ).pack(side=tk.LEFT, padx=4)

        tk.Button(marco_btn, text="Cancelar", width=10, command=self.ventana.destroy).pack(
            side=tk.LEFT, padx=4
        )

        self.marco_form = marco
        self._toggle_fecha_fin()
        self._toggle_hora_inicio()
        self._toggle_hora_fin()

    def _aplicar_tema(self):
        t = self.tema
        self.ventana.configure(bg=t['fondo'])
        self.marco_form.configure(bg=t['panel'])
        for w in self.marco_form.winfo_children():
            if isinstance(w, tk.Label):
                w.configure(bg=t['panel'], fg=t['texto'])
            elif isinstance(w, (tk.Checkbutton, tk.Frame)):
                try:
                    w.configure(bg=t['panel'])
                except tk.TclError:
                    pass
        self.entrada_titulo.configure(bg=t['entrada_bg'], fg=t['entrada_fg'])
        self.entrada_descripcion.configure(bg=t['entrada_bg'], fg=t['entrada_fg'])
        try:
            self.date_inicio.configure(background=t['entrada_bg'], foreground=t['entrada_fg'])
            self.date_fin.configure(background=t['entrada_bg'], foreground=t['entrada_fg'])
        except tk.TclError:
            pass
        self._actualizar_color_prioridad()

    def _actualizar_color_prioridad(self, evento=None):
        p = self.combo_prioridad.get()
        self.etiqueta_color.config(
            text=f"  Color: {p}  ",
            bg=self.tema['prioridad'].get(p, '#fff'),
            fg=self.tema['texto']
        )

    def _toggle_fecha_fin(self):
        self.date_fin.config(state='disabled' if self.var_sin_fecha_fin.get() else 'readonly')

    def _toggle_hora_inicio(self):
        estado = 'disabled' if self.var_sin_hora_inicio.get() else 'readonly'
        self.combo_hora_ini_h.config(state=estado)
        self.combo_hora_ini_m.config(state=estado)

    def _toggle_hora_fin(self):
        estado = 'disabled' if self.var_sin_hora_fin.get() else 'readonly'
        self.combo_hora_fin_h.config(state=estado)
        self.combo_hora_fin_m.config(state=estado)

    def _valores_por_defecto(self):
        hoy = datetime.now().date()
        self.date_inicio.set_date(hoy)
        self.date_fin.set_date(hoy)
        self.combo_hora_ini_h.current(9)
        self.combo_hora_ini_m.current(0)
        self.combo_hora_fin_h.current(18)
        self.combo_hora_fin_m.current(0)

    def _parsear_hora_guardada(self, hora_str):
        """Convierte '09:30' en (hora, minuto) para los combobox."""
        if not hora_str:
            return None, None
        partes = hora_str.split(':')
        h, m = partes[0], partes[1]
        if m not in self.MINUTOS:
            cercano = min(self.MINUTOS, key=lambda x: abs(int(x) - int(m)))
            m = cercano
        return h, m

    def _establecer_hora_widgets(self, hora_str, es_inicio=True):
        if not hora_str:
            if es_inicio:
                self.var_sin_hora_inicio.set(True)
            else:
                self.var_sin_hora_fin.set(True)
            return
        h, m = self._parsear_hora_guardada(hora_str)
        if es_inicio:
            self.var_sin_hora_inicio.set(False)
            self.combo_hora_ini_h.set(h)
            self.combo_hora_ini_m.set(m)
        else:
            self.var_sin_hora_fin.set(False)
            self.combo_hora_fin_h.set(h)
            self.combo_hora_fin_m.set(m)

    def _cargar_tarea(self, tarea):
        self.entrada_titulo.insert(0, tarea.titulo)
        self.entrada_descripcion.insert("1.0", tarea.descripcion)
        if tarea.categoria in Tarea.CATEGORIAS:
            self.combo_categoria.current(Tarea.CATEGORIAS.index(tarea.categoria))

        self.date_inicio.set_date(datetime.strptime(tarea.fecha_inicio, '%Y-%m-%d').date())
        if tarea.fecha_fin:
            self.var_sin_fecha_fin.set(False)
            self.date_fin.set_date(datetime.strptime(tarea.fecha_fin, '%Y-%m-%d').date())
        self._toggle_fecha_fin()

        self._establecer_hora_widgets(tarea.hora_inicio, True)
        self._establecer_hora_widgets(tarea.hora_fin, False)
        self._toggle_hora_inicio()
        self._toggle_hora_fin()

        if tarea.prioridad in ["Alta", "Media", "Baja"]:
            self.combo_prioridad.current(["Alta", "Media", "Baja"].index(tarea.prioridad))
        if tarea.repetir in Tarea.TIPOS_REPETICION:
            self.combo_repetir.current(Tarea.TIPOS_REPETICION.index(tarea.repetir))

        self.var_completada.set(tarea.completada)
        self.var_recordatorio.set(tarea.recordatorio)
        self._actualizar_color_prioridad()

    def _obtener_fecha_inicio(self):
        return self.date_inicio.get_date().strftime('%Y-%m-%d')

    def _obtener_fecha_fin(self):
        if self.var_sin_fecha_fin.get():
            return ''
        return self.date_fin.get_date().strftime('%Y-%m-%d')

    def _obtener_hora_inicio(self):
        if self.var_sin_hora_inicio.get():
            return ''
        return f"{self.combo_hora_ini_h.get()}:{self.combo_hora_ini_m.get()}"

    def _obtener_hora_fin(self):
        if self.var_sin_hora_fin.get():
            return ''
        return f"{self.combo_hora_fin_h.get()}:{self.combo_hora_fin_m.get()}"

    def _validar(self):
        if not self.entrada_titulo.get().strip():
            messagebox.showwarning("Aviso", "El título no puede estar vacío.", parent=self.ventana)
            return False

        fecha_inicio = self._obtener_fecha_inicio()
        fecha_fin = self._obtener_fecha_fin()
        if fecha_fin and fecha_fin < fecha_inicio:
            messagebox.showwarning(
                "Aviso", "La fecha de término no puede ser anterior a la de inicio.",
                parent=self.ventana
            )
            return False

        hora_inicio = self._obtener_hora_inicio()
        hora_fin = self._obtener_hora_fin()
        if hora_inicio and hora_fin and hora_fin < hora_inicio:
            messagebox.showwarning(
                "Aviso", "La hora de término no puede ser anterior a la de inicio.",
                parent=self.ventana
            )
            return False
        return True

    def _obtener_datos(self):
        return {
            'titulo': self.entrada_titulo.get().strip(),
            'descripcion': self.entrada_descripcion.get("1.0", tk.END).strip(),
            'fecha_inicio': self._obtener_fecha_inicio(),
            'fecha_fin': self._obtener_fecha_fin(),
            'hora_inicio': self._obtener_hora_inicio(),
            'hora_fin': self._obtener_hora_fin(),
            'categoria': self.combo_categoria.get(),
            'prioridad': self.combo_prioridad.get(),
            'completada': self.var_completada.get(),
            'recordatorio': self.var_recordatorio.get(),
            'repetir': self.combo_repetir.get()
        }

    def _guardar(self):
        if not self._validar():
            return
        datos = self._obtener_datos()
        if self.on_guardar:
            self.on_guardar(self.modo, datos, self.tarea.id_tarea if self.tarea else None)
        self.ventana.destroy()

    def _eliminar(self):
        if self.tarea and self.on_eliminar:
            if messagebox.askyesno(
                "Confirmar", f"¿Eliminar la tarea '{self.tarea.titulo}'?",
                parent=self.ventana
            ):
                self.on_eliminar(self.tarea.id_tarea)
                self.ventana.destroy()
