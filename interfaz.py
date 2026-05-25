"""
Módulo de la interfaz gráfica.
Pestañas: tareas activas, historial y estadísticas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from tkcalendar import Calendar, DateEntry

from gestor_tareas import GestorTareas
from tarea import Tarea
from tema import obtener_tema
from vista_semanal import VistaSemanal
from formulario_tarea import FormularioTarea
from panel_estadisticas import PanelEstadisticas


class InterfazRecuerdaTec:
    """Clase principal de la aplicación de escritorio."""

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("RecuerdaTec - Gestión de Tareas")
        self.ventana.geometry("1100x900")
        self.ventana.minsize(1000, 780)

        self.gestor = GestorTareas()
        self.id_seleccionado = None
        self.modo_oscuro = False
        self.tema = obtener_tema(self.modo_oscuro)
        self.filtro_categoria = tk.StringVar(value="Todas")
        self.var_filtro_fecha = tk.BooleanVar(value=False)
        self.filtro_historial = tk.StringVar(value="Completada")
        self.botones_tema = []  # Botones que reciben colores del tema

        self._crear_widgets()
        self._configurar_colores_tablas()
        self._aplicar_tema()
        self._refrescar_vista_completa()
        self._mostrar_recordatorios_hoy()

    def _crear_widgets(self):
        self.marco_titulo = tk.Frame(self.ventana)
        self.marco_titulo.pack(fill=tk.X, pady=6)

        self.lbl_titulo = tk.Label(
            self.marco_titulo,
            text="RecuerdaTec - Organiza tus tareas y recordatorios",
            font=("Segoe UI", 14, "bold")
        )
        self.lbl_titulo.pack(side=tk.LEFT, padx=15)

        self.btn_agregar = tk.Button(
            self.marco_titulo, text="Agregar tarea",
            font=("Segoe UI", 10, "bold"),
            command=self._abrir_formulario_agregar
        )
        self.btn_agregar.pack(side=tk.LEFT, padx=10)
        self._registrar_boton(self.btn_agregar)

        self.btn_modo_oscuro = tk.Button(
            self.marco_titulo, text="Modo oscuro",
            command=self._alternar_modo_oscuro
        )
        self.btn_modo_oscuro.pack(side=tk.RIGHT, padx=10)

        self.notebook = ttk.Notebook(self.ventana)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_activas = tk.Frame(self.notebook)
        self.tab_historial = tk.Frame(self.notebook)
        self.tab_estadisticas = tk.Frame(self.notebook)

        self.notebook.add(self.tab_activas, text="Tareas activas")
        self.notebook.add(self.tab_historial, text="Historial")
        self.notebook.add(self.tab_estadisticas, text="Estadisticas")

        self._crear_tab_activas()
        self._crear_tab_historial()
        self.panel_stats = PanelEstadisticas(
            self.tab_estadisticas, self.gestor,
            callback_tema=lambda: self.tema
        )

        self.marco_semanal_padre = tk.Frame(self.ventana)
        self.marco_semanal_padre.pack(fill=tk.BOTH, padx=10, pady=5)
        self.vista_semanal = VistaSemanal(
            self.marco_semanal_padre, self.gestor,
            callback_tema=lambda: self.tema
        )

        self._crear_barra_inferior()

    def _crear_tab_activas(self):
        contenedor = tk.Frame(self.tab_activas)
        contenedor.pack(fill=tk.BOTH, expand=True)

        self._crear_panel_lista(contenedor)
        self._crear_panel_calendario(contenedor)

    def _crear_panel_lista(self, padre):
        self.marco_lista = tk.LabelFrame(
            padre,
            text="Tareas pendientes por fecha (1 clic = resumen, 2 clics = editar)",
            font=("Segoe UI", 10, "bold"), padx=8, pady=8
        )
        self.marco_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.marco_filtros = tk.Frame(self.marco_lista)
        self.marco_filtros.pack(fill=tk.X, pady=4)

        tk.Label(self.marco_filtros, text="Categoria:").pack(side=tk.LEFT)
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
        self._registrar_boton(self.btn_quitar_filtro, 'secundario')

        self.marco_resumen = tk.LabelFrame(
            self.marco_lista, text="Resumen de la tarea seleccionada",
            font=("Segoe UI", 9, "bold"), padx=8, pady=6
        )
        self.marco_resumen.pack(fill=tk.X, pady=4)

        self.contenedor_resumen = tk.Frame(self.marco_resumen)
        self.contenedor_resumen.pack(fill=tk.X, padx=4, pady=4)
        self._mostrar_resumen_vacio()

        self.marco_acciones = tk.Frame(self.marco_lista)
        self.marco_acciones.pack(fill=tk.X, pady=4)

        self.btn_completar = tk.Button(
            self.marco_acciones, text="Marcar completada",
            command=lambda: self._accion_estado('Completada')
        )
        self.btn_completar.pack(side=tk.LEFT, padx=2)
        self._registrar_boton(self.btn_completar)

        self.btn_pendiente = tk.Button(
            self.marco_acciones, text="Marcar pendiente",
            command=lambda: self._accion_estado('Pendiente')
        )
        self.btn_pendiente.pack(side=tk.LEFT, padx=2)
        self._registrar_boton(self.btn_pendiente, 'secundario')

        self.btn_fallida = tk.Button(
            self.marco_acciones, text="Marcar fallida",
            command=lambda: self._accion_estado('Fallida')
        )
        self.btn_fallida.pack(side=tk.LEFT, padx=2)
        self._registrar_boton(self.btn_fallida, 'secundario')

        self.btn_recordatorio = tk.Button(
            self.marco_acciones, text="Alternar recordatorio",
            command=self._accion_recordatorio
        )
        self.btn_recordatorio.pack(side=tk.LEFT, padx=2)
        self._registrar_boton(self.btn_recordatorio, 'secundario')

        self.btn_editar = tk.Button(
            self.marco_acciones, text="Editar",
            command=self._editar_seleccionada
        )
        self.btn_editar.pack(side=tk.LEFT, padx=2)
        self._registrar_boton(self.btn_editar)

        self.btn_eliminar = tk.Button(
            self.marco_acciones, text="Eliminar",
            command=self._eliminar_seleccionada
        )
        self.btn_eliminar.pack(side=tk.LEFT, padx=2)
        self._registrar_boton(self.btn_eliminar, 'peligro')

        # El ID no se muestra; se guarda en el iid de cada fila
        columnas = ("fecha", "titulo", "categoria", "horario", "prioridad", "rep", "rec")
        self.tabla = ttk.Treeview(self.marco_lista, columns=columnas, show="headings", height=14)

        self.tabla.heading("fecha", text="Fecha")
        self.tabla.heading("titulo", text="Titulo")
        self.tabla.heading("categoria", text="Categoria")
        self.tabla.heading("horario", text="Horario")
        self.tabla.heading("prioridad", text="Prioridad")
        self.tabla.heading("rep", text="Rep.")
        self.tabla.heading("rec", text="Rec.")

        self.tabla.column("fecha", width=100, anchor="center")
        self.tabla.column("titulo", width=175)
        self.tabla.column("categoria", width=75, anchor="center")
        self.tabla.column("horario", width=90, anchor="center")
        self.tabla.column("prioridad", width=65, anchor="center")
        self.tabla.column("rep", width=40, anchor="center")
        self.tabla.column("rec", width=40, anchor="center")

        scroll = ttk.Scrollbar(self.marco_lista, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tabla.bind("<ButtonRelease-1>", self._al_clic_seleccionar)
        self.tabla.bind("<Double-1>", self._al_doble_clic_editar)

        self.marco_leyenda = tk.Frame(self.marco_lista)
        self.marco_leyenda.pack(fill=tk.X, pady=4)
        self.lbl_leyenda = tk.Label(self.marco_leyenda, text="Colores por prioridad:", font=("Segoe UI", 8, "bold"))
        self.lbl_leyenda.pack(side=tk.LEFT)
        self.labels_prioridad = []
        for nombre in ['Alta', 'Media', 'Baja']:
            lbl = tk.Label(self.marco_leyenda, text=f" {nombre} ", font=("Segoe UI", 8), relief=tk.GROOVE)
            lbl.pack(side=tk.LEFT, padx=3)
            self.labels_prioridad.append((nombre, lbl))

    def _crear_tab_historial(self):
        self.marco_historial = tk.LabelFrame(
            self.tab_historial,
            text="Tareas completadas y fallidas (fuera de la lista principal)",
            font=("Segoe UI", 10, "bold"), padx=10, pady=10
        )
        self.marco_historial.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        marco_filtro = tk.Frame(self.marco_historial)
        marco_filtro.pack(fill=tk.X, pady=6)

        tk.Label(marco_filtro, text="Mostrar:").pack(side=tk.LEFT)
        self.combo_hist = ttk.Combobox(
            marco_filtro, textvariable=self.filtro_historial,
            values=['Completada', 'Fallida', 'Todas'], state="readonly", width=14
        )
        self.combo_hist.pack(side=tk.LEFT, padx=8)
        self.combo_hist.bind("<<ComboboxSelected>>", lambda e: self._actualizar_historial())

        self.btn_restaurar = tk.Button(
            marco_filtro, text="Volver a pendiente",
            command=self._restaurar_desde_historial
        )
        self.btn_restaurar.pack(side=tk.LEFT, padx=8)
        self._registrar_boton(self.btn_restaurar)

        self.btn_editar_hist = tk.Button(
            marco_filtro, text="Editar seleccionada",
            command=self._editar_seleccionada_historial
        )
        self.btn_editar_hist.pack(side=tk.LEFT, padx=4)
        self._registrar_boton(self.btn_editar_hist, 'secundario')

        cols = ("id", "titulo", "categoria", "estado", "fecha_cierre", "prioridad")
        self.tabla_historial = ttk.Treeview(self.marco_historial, columns=cols, show="headings", height=18)

        for c, txt, w in [
            ("id", "ID", 40), ("titulo", "Titulo", 220), ("categoria", "Cat.", 70),
            ("estado", "Estado", 90), ("fecha_cierre", "Fecha cierre", 100),
            ("prioridad", "Prio.", 60)
        ]:
            self.tabla_historial.heading(c, text=txt)
            self.tabla_historial.column(c, width=w, anchor="center" if c != "titulo" else "w")

        scroll = ttk.Scrollbar(self.marco_historial, orient="vertical", command=self.tabla_historial.yview)
        self.tabla_historial.configure(yscrollcommand=scroll.set)
        self.tabla_historial.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=6)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=6)

        self.tabla_historial.bind("<ButtonRelease-1>", self._al_clic_historial)
        self.tabla_historial.bind("<Double-1>", self._al_doble_clic_historial)

    def _crear_panel_calendario(self, padre):
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
            self.marco_cal, text="Filtrar lista por este dia",
            command=self._filtrar_lista_por_calendario
        )
        self.btn_filtrar_desde_cal.pack(pady=4)
        self._registrar_boton(self.btn_filtrar_desde_cal, 'secundario')

        self.btn_ver_fecha = tk.Button(
            self.marco_cal, text="Ver recordatorios del dia",
            command=self._ver_tareas_fecha_seleccionada
        )
        self.btn_ver_fecha.pack(pady=3)
        self._registrar_boton(self.btn_ver_fecha, 'secundario')

        self.lbl_num_cal = tk.Label(
            self.marco_cal, text="Numero en el dia = tareas pendientes",
            font=("Segoe UI", 8)
        )
        self.lbl_num_cal.pack(anchor="w", padx=4)

        tk.Label(self.marco_cal, text="Recordatorios del dia:",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 0), padx=4)

        self.texto_recordatorios = tk.Text(
            self.marco_cal, width=34, height=12, font=("Segoe UI", 9), wrap=tk.WORD
        )
        self.texto_recordatorios.pack(pady=5, padx=4)
        self.texto_recordatorios.config(state=tk.DISABLED)

    def _crear_barra_inferior(self):
        self.barra = tk.Frame(self.ventana)
        self.barra.pack(fill=tk.X, padx=10, pady=8)

        self.btn_recordatorios_hoy = tk.Button(
            self.barra, text="Recordatorios de hoy",
            font=("Segoe UI", 9), command=self._mostrar_recordatorios_hoy
        )
        self.btn_recordatorios_hoy.pack(side=tk.LEFT, padx=4)
        self._registrar_boton(self.btn_recordatorios_hoy, 'secundario')

        self.btn_refrescar = tk.Button(
            self.barra, text="Refrescar todo",
            font=("Segoe UI", 9), command=self._refrescar_vista_completa
        )
        self.btn_refrescar.pack(side=tk.LEFT, padx=4)
        self._registrar_boton(self.btn_refrescar, 'secundario')

        self._registrar_boton(self.btn_modo_oscuro, 'secundario')

    # ---------- Tema y botones ----------

    def _registrar_boton(self, boton, tipo='primario'):
        """Guarda el boton para aplicarle el tema despues."""
        self.botones_tema.append((boton, tipo))

    def _estilo_boton(self, boton, tipo='primario'):
        t = self.tema
        colores = {
            'primario': (t['boton'], t['boton_texto']),
            'secundario': (t['boton_secundario'], t['boton_texto']),
            'peligro': (t['boton_peligro'], t['boton_texto']),
        }
        bg, fg = colores.get(tipo, colores['primario'])
        boton.configure(bg=bg, fg=fg, activebackground=t['boton_secundario'],
                        activeforeground=fg, relief=tk.FLAT, padx=8, pady=2)

    def _aplicar_estilo_botones(self):
        for boton, tipo in self.botones_tema:
            self._estilo_boton(boton, tipo)

    # ---------- Resumen de tarea ----------

    def _limpiar_contenedor_resumen(self):
        """Quita los widgets del resumen para volver a dibujarlos."""
        for widget in self.contenedor_resumen.winfo_children():
            widget.destroy()

    def _formatear_fecha_corta(self, fecha_str):
        """Convierte 2026-05-21 a 21/05/2026 para mostrar en la lista."""
        try:
            f = datetime.strptime(fecha_str, '%Y-%m-%d')
            return f.strftime('%d/%m/%Y')
        except ValueError:
            return fecha_str

    def _formatear_fecha_tarea(self, tarea):
        """Texto de fecha para la tabla y el resumen."""
        inicio = self._formatear_fecha_corta(tarea.fecha_inicio)
        if tarea.fecha_fin and tarea.fecha_fin != tarea.fecha_inicio:
            fin = self._formatear_fecha_corta(tarea.fecha_fin)
            return f"{inicio} - {fin}"
        return inicio

    def _campo_resumen_horizontal(self, padre, etiqueta, valor):
        """Un dato del resumen en linea: Etiqueta: valor."""
        t = self.tema
        marco = tk.Frame(padre, bg=t['resumen_bg'])
        tk.Label(
            marco, text=f"{etiqueta}: ", font=("Segoe UI", 9, "bold"),
            fg=t['texto_secundario'], bg=t['resumen_bg'], anchor="w"
        ).pack(side=tk.LEFT)
        tk.Label(
            marco, text=valor, font=("Segoe UI", 9),
            fg=t['texto'], bg=t['resumen_bg'], anchor="w"
        ).pack(side=tk.LEFT)
        return marco

    def _fila_campos_resumen(self, padre, campos):
        """Coloca varios campos uno al lado del otro en la misma fila."""
        fila = tk.Frame(padre, bg=self.tema['resumen_bg'])
        fila.pack(fill=tk.X, pady=2)
        for etiqueta, valor in campos:
            bloque = self._campo_resumen_horizontal(fila, etiqueta, valor)
            bloque.pack(side=tk.LEFT, padx=(0, 14))
        return fila

    def _mostrar_resumen_vacio(self):
        self._limpiar_contenedor_resumen()
        t = self.tema
        self.contenedor_resumen.configure(bg=t['resumen_bg'])
        tk.Label(
            self.contenedor_resumen,
            text="Selecciona una tarea con 1 clic para ver su informacion.",
            font=("Segoe UI", 9), fg=t['texto'], bg=t['resumen_bg'], anchor="w"
        ).pack(fill=tk.X, padx=4, pady=2)

    def _mostrar_resumen_tarea(self, tarea):
        """Resumen horizontal: datos a la izquierda, descripcion a la derecha."""
        self._limpiar_contenedor_resumen()
        t = self.tema
        self.contenedor_resumen.configure(bg=t['resumen_bg'])
        self.contenedor_resumen.grid_columnconfigure(1, weight=1)
        self.contenedor_resumen.grid_rowconfigure(1, weight=1)

        tk.Label(
            self.contenedor_resumen, text=tarea.titulo,
            font=("Segoe UI", 11, "bold"), fg=t['texto'], bg=t['resumen_bg'], anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 4))

        marco_datos = tk.Frame(self.contenedor_resumen, bg=t['resumen_bg'])
        marco_datos.grid(row=1, column=0, sticky="nw", padx=(0, 8))

        self._fila_campos_resumen(marco_datos, [
            ("Categoria", tarea.categoria),
            ("Prioridad", tarea.prioridad),
            ("Estado", tarea.estado),
            ("Recordatorio", "Si" if tarea.recordatorio else "No"),
        ])
        self._fila_campos_resumen(marco_datos, [
            ("Fecha", self._formatear_fecha_tarea(tarea)),
            ("Horario", tarea.obtener_horario_texto() or "Sin horario"),
            ("Repeticion", tarea.repetir if tarea.repetir != 'Ninguna' else "No se repite"),
        ])

        marco_desc = tk.Frame(self.contenedor_resumen, bg=t['resumen_bg'])
        marco_desc.grid(row=1, column=1, sticky="nsew", padx=4)
        marco_desc.grid_columnconfigure(0, weight=1)
        marco_desc.grid_rowconfigure(1, weight=1)

        tk.Label(
            marco_desc, text="Descripcion", font=("Segoe UI", 9, "bold"),
            fg=t['texto_secundario'], bg=t['resumen_bg'], anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))

        texto_desc = tarea.descripcion.strip() if tarea.descripcion.strip() else "(Sin descripcion)"
        caja_desc = tk.Text(
            marco_desc, height=3, font=("Segoe UI", 9), wrap=tk.WORD,
            bg=t['entrada_bg'], fg=t['entrada_fg'], relief=tk.SUNKEN,
            bd=1, padx=6, pady=4
        )
        scroll_desc = ttk.Scrollbar(marco_desc, orient="vertical", command=caja_desc.yview)
        caja_desc.configure(yscrollcommand=scroll_desc.set)
        caja_desc.grid(row=1, column=0, sticky="nsew")
        scroll_desc.grid(row=1, column=1, sticky="ns")
        caja_desc.insert("1.0", texto_desc)
        caja_desc.bind("<Key>", lambda e: "break")

    # ---------- Formulario ----------

    def _abrir_formulario_agregar(self):
        FormularioTarea(self.ventana, self.tema, modo='agregar',
                        on_guardar=self._callback_guardar_tarea)

    def _abrir_formulario_editar(self, id_tarea):
        tarea = self.gestor.obtener_por_id(id_tarea)
        if tarea is None:
            messagebox.showwarning("Aviso", "No se encontro la tarea.")
            return
        FormularioTarea(self.ventana, self.tema, modo='editar', tarea=tarea,
                        on_guardar=self._callback_guardar_tarea,
                        on_eliminar=self._callback_eliminar_tarea)

    def _callback_guardar_tarea(self, modo, datos, id_tarea=None):
        if modo == 'agregar':
            datos['estado'] = 'Pendiente'
            self.gestor.agregar_tarea(**datos)
            messagebox.showinfo("Exito", "Tarea agregada correctamente.")
        else:
            if self.gestor.actualizar_tarea(id_tarea, **datos):
                messagebox.showinfo("Exito", "Tarea actualizada.")
            else:
                messagebox.showerror("Error", "No se pudo actualizar.")
        self._refrescar_vista_completa()

    def _callback_eliminar_tarea(self, id_tarea):
        if self.gestor.eliminar_tarea(id_tarea):
            messagebox.showinfo("Exito", "Tarea eliminada.")
            self.id_seleccionado = None
            self._mostrar_resumen_vacio()
            self._refrescar_vista_completa()

    def _eliminar_seleccionada(self):
        """Elimina la tarea seleccionada en la lista principal."""
        if not self._requiere_seleccion():
            return
        tarea = self.gestor.obtener_por_id(self.id_seleccionado)
        nombre = tarea.titulo if tarea else str(self.id_seleccionado)
        if messagebox.askyesno("Confirmar", f"Eliminar la tarea '{nombre}'?"):
            self._callback_eliminar_tarea(self.id_seleccionado)

    # ---------- Clics en listas ----------

    def _es_fila_separador(self, fila_iid):
        """Indica si la fila es un encabezado de fecha (no seleccionable)."""
        tags = self.tabla.item(fila_iid, 'tags')
        return 'separador' in tags

    def _obtener_id_desde_fila(self, fila_iid):
        """Obtiene el ID interno de la tarea desde el iid de la fila."""
        if self._es_fila_separador(fila_iid):
            return None
        try:
            return int(fila_iid)
        except ValueError:
            return None

    def _al_clic_seleccionar(self, evento):
        fila_iid = self.tabla.identify_row(evento.y)
        if not fila_iid or self._es_fila_separador(fila_iid):
            return
        id_tarea = self._obtener_id_desde_fila(fila_iid)
        if id_tarea is None:
            return
        self.id_seleccionado = id_tarea
        tarea = self.gestor.obtener_por_id(self.id_seleccionado)
        if tarea:
            self._mostrar_resumen_tarea(tarea)

    def _al_doble_clic_editar(self, evento):
        fila_iid = self.tabla.identify_row(evento.y)
        if not fila_iid or self._es_fila_separador(fila_iid):
            return
        id_tarea = self._obtener_id_desde_fila(fila_iid)
        if id_tarea is not None:
            self._abrir_formulario_editar(id_tarea)

    def _editar_seleccionada(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Aviso", "Selecciona una tarea primero (1 clic).")
            return
        self._abrir_formulario_editar(self.id_seleccionado)

    def _al_clic_historial(self, evento):
        fila_id = self.tabla_historial.identify_row(evento.y)
        if not fila_id:
            return
        valores = self.tabla_historial.item(fila_id, "values")
        if valores:
            self.id_seleccionado = int(valores[0])

    def _al_doble_clic_historial(self, evento):
        fila_id = self.tabla_historial.identify_row(evento.y)
        if not fila_id:
            return
        valores = self.tabla_historial.item(fila_id, "values")
        if valores:
            self._abrir_formulario_editar(int(valores[0]))

    def _editar_seleccionada_historial(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Aviso", "Selecciona una tarea del historial.")
            return
        self._abrir_formulario_editar(self.id_seleccionado)

    # ---------- Acciones rapidas ----------

    def _requiere_seleccion(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Aviso", "Selecciona una tarea con 1 clic en la lista.")
            return False
        return True

    def _accion_estado(self, estado):
        if not self._requiere_seleccion():
            return
        if self.gestor.cambiar_estado(self.id_seleccionado, estado):
            self.id_seleccionado = None
            self._mostrar_resumen_vacio()
            self._refrescar_vista_completa()
            if estado in ('Completada', 'Fallida'):
                messagebox.showinfo("Listo", f"Tarea movida a historial ({estado}).")
        else:
            messagebox.showerror("Error", "No se pudo cambiar el estado.")

    def _accion_recordatorio(self):
        if not self._requiere_seleccion():
            return
        if self.gestor.alternar_recordatorio(self.id_seleccionado):
            t = self.gestor.obtener_por_id(self.id_seleccionado)
            if t:
                self._mostrar_resumen_tarea(t)
            self._actualizar_lista_tareas()
            if t:
                estado_rec = "activado" if t.recordatorio else "desactivado"
                messagebox.showinfo("Recordatorio", f"Recordatorio {estado_rec}.")

    def _restaurar_desde_historial(self):
        if self.id_seleccionado is None:
            messagebox.showwarning("Aviso", "Selecciona una tarea del historial.")
            return
        if self.gestor.cambiar_estado(self.id_seleccionado, 'Pendiente'):
            messagebox.showinfo("Listo", "Tarea devuelta a pendientes.")
            self.id_seleccionado = None
            self._refrescar_vista_completa()
            self.notebook.select(self.tab_activas)

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
        fecha = self.calendario.get_date()
        self.date_filtro.set_date(datetime.strptime(fecha, '%Y-%m-%d').date())
        self.var_filtro_fecha.set(True)
        self._actualizar_lista_tareas()
        self._mostrar_recordatorios_fecha(fecha)

    def _al_elegir_fecha_calendario(self, evento=None):
        fecha = self.calendario.get_date()
        self.date_filtro.set_date(datetime.strptime(fecha, '%Y-%m-%d').date())
        if self.var_filtro_fecha.get():
            self._actualizar_lista_tareas()
        self._mostrar_recordatorios_fecha(fecha)

    # ---------- Tema ----------

    def _alternar_modo_oscuro(self):
        self.modo_oscuro = not self.modo_oscuro
        self.tema = obtener_tema(self.modo_oscuro)
        self.btn_modo_oscuro.config(text="Modo claro" if self.modo_oscuro else "Modo oscuro")
        self._aplicar_tema()
        self._actualizar_marcadores_calendario()
        self.vista_semanal.cargar_semana()

    def _aplicar_tema(self):
        t = self.tema
        self.ventana.configure(bg=t['fondo'])
        self.marco_titulo.configure(bg=t['fondo'])
        self.lbl_titulo.configure(bg=t['fondo'], fg=t['texto'])
        self.btn_agregar.configure(bg=t['boton'], fg=t['boton_texto'],
                                 activebackground=t['boton_secundario'])
        self._aplicar_estilo_botones()
        self.tab_activas.configure(bg=t['fondo'])
        self.tab_historial.configure(bg=t['fondo'])
        self.tab_estadisticas.configure(bg=t['fondo'])
        self.marco_semanal_padre.configure(bg=t['fondo'])
        self.barra.configure(bg=t['fondo'])

        for marco in [self.marco_lista, self.marco_cal, self.marco_historial]:
            marco.configure(bg=t['panel'], fg=t['texto'])
        self.marco_filtros.configure(bg=t['panel'])
        self.marco_resumen.configure(bg=t['panel'], fg=t['texto'])
        self.marco_acciones.configure(bg=t['panel'])
        self.marco_leyenda.configure(bg=t['panel'])
        self.lbl_leyenda.configure(bg=t['panel'], fg=t['texto'])
        self.contenedor_resumen.configure(bg=t['resumen_bg'])
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
        self.panel_stats.aplicar_tema(t)
        self._configurar_colores_tablas()

        for prioridad in ['Alta', 'Media', 'Baja']:
            self.calendario.tag_config(prioridad, background=t['prioridad'][prioridad])

        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('TNotebook', background=t['fondo'])
        estilo.configure('TNotebook.Tab', background=t['panel'], foreground=t['texto'])
        estilo.configure('Treeview', background=t['entrada_bg'], fieldbackground=t['entrada_bg'],
                         foreground=t['entrada_fg'])
        estilo.configure('Treeview.Heading', background=t['panel'], foreground=t['texto'])

    def _configurar_colores_tablas(self):
        t = self.tema
        for prioridad, color in t['prioridad'].items():
            self.tabla.tag_configure(prioridad, background=color)
        self.tabla.tag_configure('separador', background=t['borde'], foreground=t['texto'])

    # ---------- Actualizar vistas ----------

    def _refrescar_vista_completa(self):
        self._actualizar_lista_tareas()
        self._actualizar_historial()
        self._actualizar_marcadores_calendario()
        self.vista_semanal.cargar_semana()
        self.panel_stats.actualizar()

    def _actualizar_lista_tareas(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        tareas = self.gestor.obtener_todas(
            categoria_filtro=self.filtro_categoria.get(),
            fecha_filtro=self._obtener_fecha_filtro(),
            solo_pendientes=True
        )
        # Ordenar por fecha de inicio y luego por hora
        tareas.sort(key=lambda t: (t.fecha_inicio, t.hora_inicio or '00:00'))

        fecha_grupo_actual = None
        for tarea in tareas:
            if tarea.fecha_inicio != fecha_grupo_actual:
                fecha_grupo_actual = tarea.fecha_inicio
                etiqueta_grupo = self._formatear_fecha_corta(fecha_grupo_actual)
                self.tabla.insert(
                    "", tk.END,
                    iid=f"sep_{fecha_grupo_actual}",
                    values=(f"--- {etiqueta_grupo} ---", "", "", "", "", "", ""),
                    tags=('separador',)
                )

            horario = tarea.obtener_horario_texto() or "-"
            rep = tarea.repetir if tarea.repetir != 'Ninguna' else "-"
            rec = "Si" if tarea.recordatorio else "No"
            self.tabla.insert(
                "", tk.END,
                iid=str(tarea.id_tarea),
                values=(
                    self._formatear_fecha_tarea(tarea),
                    tarea.titulo,
                    tarea.categoria,
                    horario,
                    tarea.prioridad,
                    rep,
                    rec
                ),
                tags=(tarea.prioridad,)
            )

    def _actualizar_historial(self):
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)

        tipo = self.filtro_historial.get()
        for tarea in self.gestor.obtener_historial(tipo):
            fecha_c = tarea.fecha_completada or "-"
            self.tabla_historial.insert(
                "", tk.END,
                values=(tarea.id_tarea, tarea.titulo, tarea.categoria,
                        tarea.estado, fecha_c, tarea.prioridad)
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
        self.texto_recordatorios.insert(tk.END, f"Tareas pendientes activas: {len(todas)}\n")
        self.texto_recordatorios.insert(tk.END, "-" * 28 + "\n")

        if not pendientes:
            self.texto_recordatorios.insert(tk.END, "\nSin recordatorios pendientes.\n")
        else:
            self.texto_recordatorios.insert(tk.END, "\nPendientes con recordatorio:\n\n")
            for t in pendientes:
                hora = t.obtener_horario_texto()
                hora_txt = f" {hora}" if hora else ""
                rep = f" (rep. {t.repetir})" if t.repetir != 'Ninguna' else ''
                self.texto_recordatorios.insert(
                    tk.END, f"- [{t.categoria}] {t.titulo}{rep}{hora_txt}\n")

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
