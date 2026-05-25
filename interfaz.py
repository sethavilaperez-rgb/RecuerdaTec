"""
Módulo de la interfaz gráfica.
Lista + calendario en pantalla principal; formulario en ventana emergente.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar, DateEntry

from gestor_tareas import GestorTareas
from tarea import Tarea
from tema import obtener_tema
from vista_semanal import VistaSemanal
from formulario_tarea import FormularioTarea


class InterfazRecuerdaTec:
    """Clase principal de la aplicación de escritorio."""

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("RecuerdaTec - Gestión de Tareas")
        self.ventana.geometry("1050x900")
        self.ventana.minsize(900, 720)

        self.gestor = GestorTareas()
        self.modo_oscuro = False
        self.tema = obtener_tema(self.modo_oscuro)
        self.filtro_categoria = tk.StringVar(value="Todas")
        self.var_filtro_fecha = tk.BooleanVar(value=False)

        self._crear_widgets()
        self._configurar_colores_tabla()
        self._aplicar_tema()
        self._refrescar_vista_completa()
        self._mostrar_recordatorios_hoy()

    def _crear_widgets(self):
        """Construye la pantalla principal (sin formulario fijo)."""
        self.marco_titulo = tk.Frame(self.ventana)
        self.marco_titulo.pack(fill=tk.X, pady=6)

        self.lbl_titulo = tk.Label(
            self.marco_titulo,
            text="RecuerdaTec - Organiza tus tareas y recordatorios",
            font=("Segoe UI", 14, "bold")
        )
        self.lbl_titulo.pack(side=tk.LEFT, padx=15)

        self.btn_agregar = tk.Button(
            self.marco_titulo, text="➕ Agregar tarea",
            font=("Segoe UI", 10, "bold"),
            command=self._abrir_formulario_agregar
        )
        self.btn_agregar.pack(side=tk.LEFT, padx=10)

        self.btn_modo_oscuro = tk.Button(
            self.marco_titulo, text="🌙 Modo oscuro",
            command=self._alternar_modo_oscuro
        )
        self.btn_modo_oscuro.pack(side=tk.RIGHT, padx=10)

        self.contenedor = tk.Frame(self.ventana)
        self.contenedor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._crear_panel_lista(self.contenedor)
        self._crear_panel_calendario(self.contenedor)

        self.marco_semanal_padre = tk.Frame(self.ventana)
        self.marco_semanal_padre.pack(fill=tk.BOTH, padx=10, pady=5)
        self.vista_semanal = VistaSemanal(
            self.marco_semanal_padre, self.gestor,
            callback_tema=lambda: self.tema
        )

        self._crear_barra_inferior()

    def _crear_panel_lista(self, padre):
        """Lista de tareas con filtros por categoría y fecha."""
        self.marco_lista = tk.LabelFrame(
            padre, text="Lista de tareas (clic en una fila para editar)",
            font=("Segoe UI", 10, "bold"), padx=8, pady=8
        )
        self.marco_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.marco_filtros = tk.Frame(self.marco_lista)
        self.marco_filtros.pack(fill=tk.X, pady=4)

        tk.Label(self.marco_filtros, text="Categoría:").pack(side=tk.LEFT)
        self.combo_filtro_cat = ttk.Combobox(
            self.marco_filtros, textvariable=self.filtro_categoria,
            values=['Todas'] + Tarea.CATEGORIAS, state="readonly", width=11
        )
        self.combo_filtro_cat.pack(side=tk.LEFT, padx=5)
        self.combo_filtro_cat.bind("<<ComboboxSelected>>", lambda e: self._actualizar_lista_tareas())

        tk.Label(self.marco_filtros, text="  |  Fecha:").pack(side=tk.LEFT, padx=(8, 0))
        self.date_filtro = DateEntry(
            self.marco_filtros, width=12, date_pattern='y-mm-dd',
            state='readonly', font=("Segoe UI", 9)
        )
        self.date_filtro.pack(side=tk.LEFT, padx=4)
        self.date_filtro.bind(
            "<<DateEntrySelected>>",
            lambda e: self._actualizar_lista_tareas() if self.var_filtro_fecha.get() else None
        )

        self.check_filtro_fecha = tk.Checkbutton(
            self.marco_filtros, text="Filtrar por esta fecha",
            variable=self.var_filtro_fecha,
            command=self._actualizar_lista_tareas
        )
        self.check_filtro_fecha.pack(side=tk.LEFT, padx=4)

        self.btn_quitar_filtro = tk.Button(
            self.marco_filtros, text="Quitar filtros",
            command=self._quitar_filtros
        )
        self.btn_quitar_filtro.pack(side=tk.LEFT, padx=6)

        columnas = ("id", "titulo", "categoria", "inicio", "hora", "prioridad", "rep", "estado")
        self.tabla = ttk.Treeview(self.marco_lista, columns=columnas, show="headings", height=20)

        self.tabla.heading("id", text="ID")
        self.tabla.heading("titulo", text="Título")
        self.tabla.heading("categoria", text="Cat.")
        self.tabla.heading("inicio", text="Inicio")
        self.tabla.heading("hora", text="Hora")
        self.tabla.heading("prioridad", text="Prio.")
        self.tabla.heading("rep", text="Rep.")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("id", width=35, anchor="center")
        self.tabla.column("titulo", width=200)
        self.tabla.column("categoria", width=60, anchor="center")
        self.tabla.column("inicio", width=90, anchor="center")
        self.tabla.column("hora", width=90, anchor="center")
        self.tabla.column("prioridad", width=50, anchor="center")
        self.tabla.column("rep", width=40, anchor="center")
        self.tabla.column("estado", width=80, anchor="center")

        scroll = ttk.Scrollbar(self.marco_lista, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Clic en fila abre el formulario de edición
        self.tabla.bind("<ButtonRelease-1>", self._al_clic_en_tarea)

        self.marco_leyenda = tk.Frame(self.marco_lista)
        self.marco_leyenda.pack(fill=tk.X, pady=4)
        self.lbl_leyenda = tk.Label(self.marco_leyenda, text="Colores:", font=("Segoe UI", 8, "bold"))
        self.lbl_leyenda.pack(side=tk.LEFT)
        self.labels_prioridad = []
        for nombre in ['Alta', 'Media', 'Baja']:
            lbl = tk.Label(self.marco_leyenda, text=f" {nombre} ", font=("Segoe UI", 8), relief=tk.GROOVE)
            lbl.pack(side=tk.LEFT, padx=3)
            self.labels_prioridad.append((nombre, lbl))

    def _crear_panel_calendario(self, padre):
        """Calendario y recordatorios del día."""
        self.marco_cal = tk.LabelFrame(
            padre, text="Calendario y recordatorios",
            font=("Segoe UI", 10, "bold"), padx=8, pady=8
        )
        self.marco_cal.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)

        self.calendario = Calendar(
            self.marco_cal, selectmode="day",
            date_pattern="y-mm-dd", font=("Segoe UI", 9), showweeknumbers=False
        )
        self.calendario.pack(pady=5)
        self.calendario.bind("<<CalendarSelected>>", self._al_elegir_fecha_calendario)
        self.calendario.bind("<<CalendarMonthChanged>>", self._actualizar_marcadores_calendario)

        self.btn_filtrar_desde_cal = tk.Button(
            self.marco_cal, text="Filtrar lista por este día",
            command=self._filtrar_lista_por_calendario
        )
        self.btn_filtrar_desde_cal.pack(pady=4)

        self.btn_ver_fecha = tk.Button(
            self.marco_cal, text="Ver recordatorios del día",
            command=self._ver_tareas_fecha_seleccionada
        )
        self.btn_ver_fecha.pack(pady=3)

        self.lbl_num_cal = tk.Label(
            self.marco_cal, text="Número en el día = cantidad de tareas",
            font=("Segoe UI", 8)
        )
        self.lbl_num_cal.pack(anchor="w", padx=4)

        tk.Label(self.marco_cal, text="Recordatorios del día:",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 0), padx=4)

        self.texto_recordatorios = tk.Text(
            self.marco_cal, width=34, height=14, font=("Segoe UI", 9), wrap=tk.WORD
        )
        self.texto_recordatorios.pack(pady=5, padx=4)
        self.texto_recordatorios.config(state=tk.DISABLED)

    def _crear_barra_inferior(self):
        self.barra = tk.Frame(self.ventana)
        self.barra.pack(fill=tk.X, padx=10, pady=8)

        botones = [
            ("📊 Estadísticas", self._mostrar_graficas, "#8e44ad"),
            ("📈 Avance en el tiempo", self._mostrar_grafica_avance, "#2980b9"),
            ("🔔 Recordatorios de hoy", self._mostrar_recordatorios_hoy, "#e67e22"),
            ("🔄 Refrescar", self._refrescar_vista_completa, "#7f8c8d"),
        ]
        self.botones_barra = []
        for texto, comando, color in botones:
            btn = tk.Button(self.barra, text=texto, font=("Segoe UI", 9),
                            bg=color, fg="white", command=comando)
            btn.pack(side=tk.LEFT, padx=4)
            self.botones_barra.append(btn)

    # ---------- Formulario emergente ----------

    def _abrir_formulario_agregar(self):
        """Abre ventana para crear una tarea nueva."""
        FormularioTarea(
            self.ventana, self.tema, modo='agregar',
            on_guardar=self._callback_guardar_tarea
        )

    def _abrir_formulario_editar(self, id_tarea):
        """Abre ventana para editar la tarea indicada."""
        tarea = self.gestor.obtener_por_id(id_tarea)
        if tarea is None:
            messagebox.showwarning("Aviso", "No se encontró la tarea.")
            return
        FormularioTarea(
            self.ventana, self.tema, modo='editar', tarea=tarea,
            on_guardar=self._callback_guardar_tarea,
            on_eliminar=self._callback_eliminar_tarea
        )

    def _callback_guardar_tarea(self, modo, datos, id_tarea=None):
        """Guarda tarea nueva o actualiza una existente."""
        if modo == 'agregar':
            datos.pop('completada', None)
            self.gestor.agregar_tarea(**datos)
            messagebox.showinfo("Éxito", "Tarea agregada correctamente.")
        else:
            if self.gestor.actualizar_tarea(id_tarea, **datos):
                messagebox.showinfo("Éxito", "Tarea actualizada.")
            else:
                messagebox.showerror("Error", "No se pudo actualizar.")
        self._refrescar_vista_completa()

    def _callback_eliminar_tarea(self, id_tarea):
        if self.gestor.eliminar_tarea(id_tarea):
            messagebox.showinfo("Éxito", "Tarea eliminada.")
            self._refrescar_vista_completa()

    def _al_clic_en_tarea(self, evento):
        """Al hacer clic en una fila, abre el formulario de edición."""
        fila_id = self.tabla.identify_row(evento.y)
        if not fila_id:
            return
        valores = self.tabla.item(fila_id, "values")
        if not valores:
            return
        id_tarea = int(valores[0])
        self._abrir_formulario_editar(id_tarea)

    # ---------- Filtros ----------

    def _obtener_fecha_filtro(self):
        if self.var_filtro_fecha.get():
            return self.date_filtro.get_date().strftime('%Y-%m-%d')
        return None

    def _quitar_filtros(self):
        self.filtro_categoria.set("Todas")
        self.var_filtro_fecha.set(False)
        self._actualizar_lista_tareas()

    def _filtrar_lista_por_calendario(self):
        """Usa el día seleccionado en el calendario como filtro de la lista."""
        fecha = self.calendario.get_date()
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        self.date_filtro.set_date(fecha_obj)
        self.var_filtro_fecha.set(True)
        self._actualizar_lista_tareas()
        self._mostrar_recordatorios_fecha(fecha)

    def _al_elegir_fecha_calendario(self, evento=None):
        """Al elegir día en calendario, actualiza filtro de fecha y recordatorios."""
        fecha = self.calendario.get_date()
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        self.date_filtro.set_date(fecha_obj)
        if self.var_filtro_fecha.get():
            self._actualizar_lista_tareas()
        self._mostrar_recordatorios_fecha(fecha)

    # ---------- Tema ----------

    def _alternar_modo_oscuro(self):
        self.modo_oscuro = not self.modo_oscuro
        self.tema = obtener_tema(self.modo_oscuro)
        self.btn_modo_oscuro.config(text="☀️ Modo claro" if self.modo_oscuro else "🌙 Modo oscuro")
        self._aplicar_tema()
        self._actualizar_marcadores_calendario()
        self.vista_semanal.cargar_semana()

    def _aplicar_tema(self):
        t = self.tema
        self.ventana.configure(bg=t['fondo'])
        self.marco_titulo.configure(bg=t['fondo'])
        self.lbl_titulo.configure(bg=t['fondo'], fg=t['texto'])
        self.btn_agregar.configure(bg=t['boton'], fg=t['boton_texto'])
        self.contenedor.configure(bg=t['fondo'])
        self.marco_semanal_padre.configure(bg=t['fondo'])
        self.barra.configure(bg=t['fondo'])

        for marco in [self.marco_lista, self.marco_cal]:
            marco.configure(bg=t['panel'], fg=t['texto'])
        self.marco_filtros.configure(bg=t['panel'])
        self.marco_leyenda.configure(bg=t['panel'])
        self.lbl_leyenda.configure(bg=t['panel'], fg=t['texto'])
        self.lbl_num_cal.configure(bg=t['panel'], fg=t['texto_secundario'])
        self.check_filtro_fecha.configure(bg=t['panel'], fg=t['texto'], selectcolor=t['panel'])

        for nombre, lbl in self.labels_prioridad:
            lbl.configure(bg=t['prioridad'][nombre])

        try:
            self.date_filtro.configure(background=t['entrada_bg'], foreground=t['entrada_fg'])
        except tk.TclError:
            pass

        self.texto_recordatorios.configure(bg=t['entrada_bg'], fg=t['entrada_fg'])
        self.vista_semanal.aplicar_tema(t)
        self._configurar_colores_tabla()

        for prioridad in ['Alta', 'Media', 'Baja']:
            self.calendario.tag_config(prioridad, background=t['prioridad'][prioridad])

        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('Treeview', background=t['entrada_bg'], fieldbackground=t['entrada_bg'],
                         foreground=t['entrada_fg'])
        estilo.configure('Treeview.Heading', background=t['panel'], foreground=t['texto'])

    def _configurar_colores_tabla(self):
        for prioridad, color in self.tema['prioridad'].items():
            self.tabla.tag_configure(prioridad, background=color)

    # ---------- Lista y calendario ----------

    def _refrescar_vista_completa(self):
        self._actualizar_lista_tareas()
        self._actualizar_marcadores_calendario()
        self.vista_semanal.cargar_semana()

    def _actualizar_lista_tareas(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        cat = self.filtro_categoria.get()
        fecha = self._obtener_fecha_filtro()

        for tarea in self.gestor.obtener_todas(categoria_filtro=cat, fecha_filtro=fecha):
            estado = "Completada" if tarea.completada else "Pendiente"
            hora = tarea.obtener_horario_texto() or "-"
            rep = tarea.repetir[0] if tarea.repetir != 'Ninguna' else "-"
            self.tabla.insert(
                "", tk.END,
                values=(tarea.id_tarea, tarea.titulo, tarea.categoria,
                        tarea.fecha_inicio, hora, tarea.prioridad, rep, estado),
                tags=(tarea.prioridad,)
            )

    def _actualizar_marcadores_calendario(self, evento=None):
        self.calendario.calevent_remove('all')
        for fecha_str, datos in self.gestor.obtener_resumen_calendario().items():
            try:
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            self.calendario.calevent_create(
                fecha_obj, str(datos['cantidad']), tags=(datos['prioridad'],)
            )

    def _ver_tareas_fecha_seleccionada(self):
        self._mostrar_recordatorios_fecha(self.calendario.get_date())

    def _mostrar_recordatorios_fecha(self, fecha):
        pendientes = self.gestor.obtener_pendientes_con_recordatorio(fecha)
        todas = self.gestor.obtener_por_fecha(fecha)

        self.texto_recordatorios.config(state=tk.NORMAL)
        self.texto_recordatorios.delete("1.0", tk.END)
        self.texto_recordatorios.insert(tk.END, f"Fecha: {fecha}\n")
        self.texto_recordatorios.insert(tk.END, f"Tareas activas: {len(todas)}\n")
        self.texto_recordatorios.insert(tk.END, "-" * 28 + "\n")

        if not pendientes:
            self.texto_recordatorios.insert(tk.END, "\nSin recordatorios pendientes.\n")
        else:
            self.texto_recordatorios.insert(tk.END, "\nPendientes:\n\n")
            for t in pendientes:
                hora = t.obtener_horario_texto()
                hora_txt = f" {hora}" if hora else ""
                rep = f" [{t.repetir}]" if t.repetir != 'Ninguna' else ''
                self.texto_recordatorios.insert(
                    tk.END, f"• [{t.categoria}] {t.titulo}{rep}{hora_txt}\n")

        completadas = [t for t in todas if t.completada]
        if completadas:
            self.texto_recordatorios.insert(tk.END, "\nCompletadas:\n")
            for t in completadas:
                self.texto_recordatorios.insert(tk.END, f"  ✓ {t.titulo}\n")

        self.texto_recordatorios.config(state=tk.DISABLED)

    def _mostrar_recordatorios_hoy(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        self.calendario.selection_set(hoy)
        self.date_filtro.set_date(datetime.now().date())
        self._mostrar_recordatorios_fecha(hoy)
        pendientes = self.gestor.obtener_pendientes_con_recordatorio(hoy)
        if pendientes:
            mensaje = "Tareas pendientes para hoy:\n\n"
            for t in pendientes:
                hora = t.obtener_horario_texto()
                mensaje += f"- {t.titulo} ({t.categoria}) {hora}\n"
            messagebox.showinfo("Recordatorios de hoy", mensaje)

    # ---------- Gráficas ----------

    def _mostrar_graficas(self):
        stats = self.gestor.obtener_estadisticas()
        if stats['total'] == 0:
            messagebox.showinfo("Sin datos", "Agrega tareas primero.")
            return

        ventana_graf = tk.Toplevel(self.ventana)
        ventana_graf.title("Estadísticas de productividad")
        ventana_graf.geometry("820x460")
        ventana_graf.configure(bg=self.tema['fondo'])

        figura, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
        figura.patch.set_facecolor(self.tema['grafica_fondo'])

        ax1.bar(['Completadas', 'Pendientes'],
                [stats['completadas'], stats['pendientes']],
                color=['#27ae60', '#e74c3c'])
        ax1.set_title('Estado de las tareas', color=self.tema['grafica_ejes'])
        ax1.set_ylabel('Cantidad', color=self.tema['grafica_ejes'])
        ax1.tick_params(colors=self.tema['grafica_ejes'])

        etiquetas_prio = ['Alta', 'Media', 'Baja']
        valores_prio = [stats['alta'], stats['media'], stats['baja']]
        colores_prio = ['#e74c3c', '#f39c12', '#3498db']
        filtradas, valores_f, colores_f = [], [], []
        for i, v in enumerate(valores_prio):
            if v > 0:
                filtradas.append(etiquetas_prio[i])
                valores_f.append(v)
                colores_f.append(colores_prio[i])

        if valores_f:
            ax2.pie(valores_f, labels=filtradas, colors=colores_f,
                    autopct='%1.0f%%', startangle=90)
            ax2.set_title('Tareas por prioridad', color=self.tema['grafica_ejes'])
        else:
            ax2.text(0.5, 0.5, 'Sin datos', ha='center', color=self.tema['grafica_ejes'])

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(figura, master=ventana_graf)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        resumen = (f"Total: {stats['total']} | Completadas: {stats['completadas']} "
                   f"| Pendientes: {stats['pendientes']}")
        tk.Label(ventana_graf, text=resumen, font=("Segoe UI", 10),
                 bg=self.tema['fondo'], fg=self.tema['texto']).pack(pady=5)

    def _mostrar_grafica_avance(self):
        etiquetas, cantidades = self.gestor.obtener_avance_por_semana()
        if not etiquetas or sum(cantidades) == 0:
            messagebox.showinfo(
                "Sin datos",
                "Completa tareas para ver el avance.\n"
                "Al marcar una tarea como completada se registra la fecha."
            )
            return

        ventana = tk.Toplevel(self.ventana)
        ventana.title("Avance en el tiempo")
        ventana.geometry("700x420")
        ventana.configure(bg=self.tema['fondo'])

        figura, ax = plt.subplots(figsize=(7, 4))
        figura.patch.set_facecolor(self.tema['grafica_fondo'])
        ax.plot(etiquetas, cantidades, marker='o', color='#27ae60', linewidth=2)
        ax.fill_between(range(len(cantidades)), cantidades, alpha=0.3, color='#27ae60')
        ax.set_title('Tareas completadas por semana', color=self.tema['grafica_ejes'])
        ax.set_xlabel('Semana (fecha fin)', color=self.tema['grafica_ejes'])
        ax.set_ylabel('Completadas', color=self.tema['grafica_ejes'])
        ax.tick_params(colors=self.tema['grafica_ejes'])
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(figura, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        total = sum(cantidades)
        tk.Label(ventana, text=f"Total completadas en el periodo: {total}",
                 font=("Segoe UI", 10), bg=self.tema['fondo'],
                 fg=self.tema['texto']).pack(pady=5)
